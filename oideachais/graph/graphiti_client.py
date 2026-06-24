"""
oideachais.graph.graphiti_client — Real Graphiti 0.5 client.

The previous `oideachais/graph/temporal.py` was a hand-rolled
Graphiti-in-pure-Python implementation that did NOT actually
connect to a graph database. REFACTORING.md item 7 marked it as
a candidate for deletion; this change replaces it with the real
`graphiti_core` 0.5 client (the production-supported version
per `docs.falkordb.com/agentic-memory/graphiti.html`).

The 0.5 release introduced **FalkorDB Lite** support — an
embedded, zero-config mode that runs in-process (per
`github.com/getzep/graphiti/issues/1240`). The KCG
`graphiti_client.py` uses FalkorDB Lite as the local-dev fallback
when the production FalkorDB compose stack is unreachable.

Usage:
    from oideachais.graph.graphiti_client import GraphitiClient

    async with GraphitiClient.connect() as client:
        await client.add_episode(
            name="Aistear:Wellbeing",
            body="Wellbeing is the 1st of 4 Aistear themes...",
            source_description="aistear.gov.ie",
        )
        results = await client.search("Aistear themes")
"""
from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

logger = logging.getLogger(__name__)

# Graphiti is optional — degrade gracefully if not installed.
try:
    from graphiti_core import Graphiti  # type: ignore[import-not-found]

    GRAPHITI_AVAILABLE = True
except ImportError as e:
    Graphiti = None  # type: ignore[assignment]
    GRAPHITI_AVAILABLE = False
    logger.warning("graphiti_core_not_available: %s", e)


# The production FalkorDB compose stack URI.
# `falkordb.cianfhoghlaim.ie:6379` is the canonical endpoint.
DEFAULT_FALKORDB_URI = os.getenv("FALKORDB_URI", "falkordb://falkordb:6379")

# The local-dev fallback (FalkorDB Lite, the embedded mode from
# `graphiti-core` 0.5+).
DEFAULT_FALKORDB_LITE_PATH = os.getenv("FALKORDB_LITE_PATH", "/tmp/falkordb_lite")


class GraphitiClient:
    """Thin async wrapper around `graphiti_core.Graphiti`.

    Auto-falls-back to FalkorDB Lite if the production FalkorDB
    compose stack is unreachable. The fallback uses the
    `falkordb_lite` Python package introduced in 2026-05.
    """

    def __init__(self, graphiti: Any) -> None:
        self._graphiti = graphiti
        self._is_lite = False

    @classmethod
    async def connect(
        cls,
        uri: str | None = None,
        *,
        use_lite_fallback: bool = True,
    ) -> "GraphitiClient":
        """Connect to the production FalkorDB stack, or fall back to FalkorDB Lite.

        Args:
            uri: The FalkorDB URI. Default `falkordb://falkordb:6379`.
            use_lite_fallback: If True, fall back to FalkorDB Lite
                               if the production stack is
                               unreachable. Default True (the
                               local-dev default).

        Returns:
            A `GraphitiClient` instance.

        Raises:
            RuntimeError: If Graphiti is not installed and no fallback
                         is available.
        """
        if not GRAPHITI_AVAILABLE:
            raise RuntimeError(
                "graphiti-core is not installed; pip install graphiti-core[falkordb]"
            )
        uri = uri or DEFAULT_FALKORDB_URI
        try:
            graphiti = Graphiti(uri=uri)
            await graphiti.build_indices_and_constraints()
            return cls(graphiti)
        except Exception as exc:  # pragma: no cover - network dependent
            if not use_lite_fallback:
                raise
            logger.warning(
                f"FalkorDB production stack unreachable ({exc}); "
                f"falling back to FalkorDB Lite at {DEFAULT_FALKORDB_LITE_PATH}"
            )
            return await cls._connect_lite(DEFAULT_FALKORDB_LITE_PATH)

    @classmethod
    async def _connect_lite(cls, path: str) -> "GraphitiClient":
        """Connect to the FalkorDB Lite embedded mode.

        Per `github.com/getzep/graphiti/issues/1240`:
        > "FalkorDB Lite is for embedded, zero-config graph storage"
        """
        try:
            from falkordb_lite import FalkorDBLite  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "FalkorDB Lite is not installed; pip install falkordb-lite"
            ) from exc
        # The falkordb_lite + graphiti_core 0.5 integration uses
        # the in-process SQLite-backed FalkorDB driver.
        lite = FalkorDBLite(path=path)
        graphiti = Graphiti(falkordb_lite=lite)
        await graphiti.build_indices_and_constraints()
        instance = cls(graphiti)
        instance._is_lite = True
        return instance

    async def add_episode(
        self,
        name: str,
        body: str,
        *,
        source_description: str = "oideachais",
        source_type: str = "document",
        reference_time: Any | None = None,
    ) -> str:
        """Add an episode to the knowledge graph.

        Args:
            name: Episode name (e.g. "Aistear:Wellbeing").
            body: Episode body (the text content).
            source_description: Free-form description of the source.
            source_type: One of "document", "conversation",
                         "extraction", "agent", etc.
            reference_time: Optional `datetime` for the
                            reference time. Default is now.

        Returns:
            The episode UUID.
        """
        if not GRAPHITI_AVAILABLE:
            return ""
        return await self._graphiti.add_episode(
            name=name,
            episode_body=body,
            source_description=source_description,
            source=source_type,
            reference_time=reference_time,
        )

    async def add_triplet(
        self,
        source_node: str,
        relation: str,
        target_node: str,
        *,
        source_node_type: str = "Entity",
        target_node_type: str = "Entity",
    ) -> str:
        """Add a triplet (source -[relation]-> target) to the graph.

        Args:
            source_node: The source node name.
            relation: The edge label (e.g. "PREREQUISITE_OF").
            target_node: The target node name.
            source_node_type: The source node label. Default "Entity".
            target_node_type: The target node label. Default "Entity".

        Returns:
            The edge UUID.
        """
        if not GRAPHITI_AVAILABLE:
            return ""
        return await self._graphiti.add_triplet(
            source_node_name=source_node,
            source_node_type=source_node_type,
            source_node_summary=f"{source_node} ({source_node_type})",
            target_node_name=target_node,
            target_node_type=target_node_type,
            target_node_summary=f"{target_node} ({target_node_type})",
            relation_type=relation,
        )

    async def search(
        self,
        query: str,
        *,
        top_k: int = 10,
        group_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Search the knowledge graph for edges matching the query.

        Args:
            query: The search query (natural language).
            top_k: The maximum number of edges to return. Default 10.
            group_ids: Optional list of group IDs to filter by.

        Returns:
            A list of edge dicts.
        """
        if not GRAPHITI_AVAILABLE:
            return []
        edges = await self._graphiti.search(
            query=query,
            top_k=top_k,
            group_ids=group_ids or [],
        )
        return [
            {
                "uuid": getattr(e, "uuid", ""),
                "source": getattr(e, "source_node_name", ""),
                "target": getattr(e, "target_node_name", ""),
                "relation": getattr(e, "relation_type", ""),
                "fact": getattr(e, "fact", ""),
            }
            for e in edges
        ]

    async def close(self) -> None:
        """Close the underlying connection."""
        if not GRAPHITI_AVAILABLE:
            return
        if hasattr(self._graphiti, "close"):
            await self._graphiti.close()

    @property
    def is_lite(self) -> bool:
        """Return True if this client is using the FalkorDB Lite fallback."""
        return self._is_lite


@asynccontextmanager
async def graphiti_client(
    uri: str | None = None,
    *,
    use_lite_fallback: bool = True,
) -> AsyncIterator[GraphitiClient]:
    """Async context manager for the canonical Graphiti client.

    Usage:
        from oideachais.graph.graphiti_client import graphiti_client

        async with graphiti_client() as client:
            await client.add_episode(...)
    """
    client = await GraphitiClient.connect(uri=uri, use_lite_fallback=use_lite_fallback)
    try:
        yield client
    finally:
        await client.close()


__all__ = [
    "GraphitiClient",
    "graphiti_client",
    "GRAPHITI_AVAILABLE",
    "DEFAULT_FALKORDB_URI",
    "DEFAULT_FALKORDB_LITE_PATH",
]
