"""
Cross-archive graph API routes.

Exposes a FastAPI route `GET /cross-archive-graph/{query}` that runs a
FalkorDB query across the leabharlann corpora (books, zotero, takeout)
and the curriculum corpora (aistear, primary, JC, SC, tertiary).

The route uses `oideachais.graph.falkordb_client.FalkorDBClient.query()`
under the hood and returns a JSON node+edge payload for the web frontend.

Reference: openspec/changes/leabharlann-cognify-and-cross-archive-edges/
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["cross-archive-graph"])


# =============================================================================
# Pydantic models
# =============================================================================


class GraphNode(BaseModel):
    """A single node in the cross-archive graph."""

    id: str
    label: str  # node label, e.g. "ZoteroPaper"
    properties: dict[str, Any] = {}


class GraphEdge(BaseModel):
    """A single edge in the cross-archive graph."""

    source: str  # node id
    target: str  # node id
    type: str  # e.g. "CITES", "TEACHES"
    properties: dict[str, Any] = {}


class GraphResponse(BaseModel):
    """The full graph response."""

    query: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    total: int


# =============================================================================
# Helpers
# =============================================================================


def _get_falkordb_client() -> Any:
    """Return a FalkorDBClient or None when falkordb is unavailable."""
    try:
        from cianfhoghlaim.observability.falkordb_client import get_graph_cache
    except ImportError:
        return None
    try:
        return get_graph_cache().client
    except Exception:
        return None


def _search_cypher(query: str, limit: int) -> str:
    """Build a Cypher query that does a full-text-ish search across
    the cross-archive graph nodes.

    The match is intentionally simple (CONTAINS on the lowercased title /
    name) — FalkorDB's full-text index is per-node-label and not
    available across all labels. Production would migrate to a
    multi-label full-text index; the current query is good enough for
    the demo and the cron sensor.
    """
    q = query.replace("'", "\\'")
    return f"""
    MATCH (n)
    WHERE toLower(coalesce(n.title, n.name, n.text, '')) CONTAINS toLower('{q}')
       OR toLower(coalesce(n.abstract, n.summary, n.content, '')) CONTAINS toLower('{q}')
    OPTIONAL MATCH (n)-[r]->(m)
    WITH n, r, m
    LIMIT {limit}
    RETURN n, r, m
    """


def _row_to_node(node: Any) -> GraphNode | None:
    if node is None:
        return None
    if isinstance(node, dict):
        nid = str(node.get("id") or node.get("file_hash") or node.get("arxiv_id") or node.get("name") or "")
        label = node.get("_label", "Node")
        return GraphNode(id=nid, label=str(label), properties=node)
    # FalkorDB Node / Edge types expose .properties
    if hasattr(node, "properties"):
        props = dict(node.properties)
        nid = str(props.get("id") or props.get("file_hash") or props.get("arxiv_id") or props.get("name") or "")
        label = (
            node.__class__.__name__
            if hasattr(node, "__class__")
            else "Node"
        )
        return GraphNode(id=nid, label=label, properties=props)
    return None


# =============================================================================
# Routes
# =============================================================================


@router.get("/cross-archive-graph/{query}", response_model=GraphResponse)
async def cross_archive_graph(
    query: str,
    limit: int = Query(25, ge=1, le=100),
) -> GraphResponse:
    """Live query against the FalkorDB cross-archive graph.

    Returns a JSON node+edge payload for the top-`limit` matches.

    When FalkorDB is not available, returns an empty graph with
    `total=0` (graceful degradation).
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="query parameter is required")

    client = _get_falkordb_client()
    if client is None:
        logger.info("cross_archive_graph_falkordb_unavailable")
        return GraphResponse(query=query, nodes=[], edges=[], total=0)

    cypher = _search_cypher(query, limit)
    try:
        rows = client.query(cypher)
    except Exception as e:
        logger.warning("cross_archive_graph_query_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"FalkorDB query failed: {e}")

    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []
    for row in rows:
        # The query returns (n, r, m); row may be a list or dict
        if isinstance(row, dict):
            n, r, m = row.get("n"), row.get("r"), row.get("m")
        else:
            n, r, m = ([*list(row), None, None, None])[:3]
        for node in (n, m):
            gn = _row_to_node(node)
            if gn and gn.id and gn.id not in nodes:
                nodes[gn.id] = gn
        if r is not None and hasattr(r, "properties"):
            rprops = dict(r.properties)
            source_id = ""
            target_id = ""
            try:
                source_id = str(r.nodes[0].id) if hasattr(r, "nodes") and r.nodes else rprops.get("source", "")
                target_id = str(r.nodes[1].id) if hasattr(r, "nodes") and r.nodes else rprops.get("target", "")
            except Exception:
                pass
            edges.append(
                GraphEdge(
                    source=source_id,
                    target=target_id,
                    type=rprops.get("type", "RELATED"),
                    properties=rprops,
                )
            )

    return GraphResponse(
        query=query,
        nodes=list(nodes.values()),
        edges=edges,
        total=len(nodes) + len(edges),
    )


@router.get("/cross-archive-graph/health")
async def cross_archive_graph_health() -> dict[str, Any]:
    """Health check for the cross-archive FalkorDB connection."""
    client = _get_falkordb_client()
    if client is None:
        return {
            "status": "unavailable",
            "reason": "falkordb_client_not_available",
            "url": os.environ.get("FALKORDB_URL", "redis://localhost:6379"),
        }
    try:
        ok = client.health_check()
        return {"status": "ok" if ok else "degraded", "url": client.config.url}
    except Exception as e:
        return {"status": "error", "error": str(e)}


__all__ = ["GraphEdge", "GraphNode", "GraphResponse", "router"]
