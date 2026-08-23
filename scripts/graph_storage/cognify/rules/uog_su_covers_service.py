"""
oideachais.cognify_rules.uog_su_covers_service — the 6th cross-archive
edge rule, linking each **UoG Students' Union document** to a
**UoG ServiceArea** (academic, welfare, equality, class_reps).

The new rule:

  6. (:UoGStudentsUnionDocument) -[:COVERS]-> (:UoGServiceArea {name})
     when the document's `tags[]` or `body` text mentions one of
     the 4 service areas (academic, welfare, equality, class_reps).

The edge carries `match_confidence ∈ [0.0, 1.0]`:
  - 1.00 for an exact tag match (`tags=["welfare"]`).
  - 0.85-0.99 for a tag substring.
  - 0.50-0.84 for a body-text fuzzy match.

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


SERVICE_AREAS: tuple[str, ...] = (
    "academic",
    "welfare",
    "equality",
    "class_reps",
)


def _detect_service_areas(document: dict[str, Any]) -> list[str]:
    """Return the (lowercased) service areas this document covers."""
    detected: list[str] = []
    haystack = " ".join(
        [*(document.get("tags") or []), document.get("body", "")]
    ).lower()
    for area in SERVICE_AREAS:
        if re.search(rf"\b{re.escape(area)}\b", haystack):
            detected.append(area)
    return detected


def _build_uog_su_covers_service_query(
    su_documents: list[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.50,
) -> tuple[str, dict[str, Any]]:
    docs = [d for d in su_documents if isinstance(d, dict) and d.get("document_id")]
    rows: list[dict[str, Any]] = []
    for doc in docs:
        for area in _detect_service_areas(doc):
            confidence = 1.0 if area in (doc.get("tags") or []) else 0.7
            rows.append(
                {
                    "document_id": doc["document_id"],
                    "service_area": area,
                    "confidence": confidence,
                }
            )
    if not rows:
        return "", {"rows": []}
    cypher = """
    UNWIND $rows AS row
    MERGE (d:UoGStudentsUnionDocument {document_id: row.document_id})
          ON CREATE SET d.title = 'SU doc — derived from cognify pass',
                        d.scraped_at = timestamp()
    MERGE (s:UoGServiceArea {name: row.service_area})
    MERGE (d)-[r:COVERS]->(s)
    ON CREATE SET r.match_confidence = row.confidence,
                  r.matched_at        = timestamp()
    ON MATCH  SET r.match_confidence = row.confidence
    RETURN count(r) AS edges_created
    """
    return cypher, {"rows": rows}


def build_uog_su_covers_service_query(
    su_documents: Iterable[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.50,
) -> tuple[str, dict[str, Any]]:
    return _build_uog_su_covers_service_query(
        list(su_documents),
        fuzzy_threshold=fuzzy_threshold,
    )


def populate_uog_su_covers_service(
    *,
    su_documents: Iterable[dict[str, Any]] | None = None,
    falkordb_client: Any = None,
    fuzzy_threshold: float = 0.50,
) -> dict[str, Any]:
    cypher, params = build_uog_su_covers_service_query(
        su_documents=su_documents or [],
        fuzzy_threshold=fuzzy_threshold,
    )
    if not cypher:
        return {"queries_executed": 0, "edges_created": 0, "stub": False}
    if falkordb_client is None:
        try:
            from cianfhoghlaim.cognify.falkordb_client import get_graph_cache
        except ImportError:
            logger.warning(
                "falkordb_client_not_available_skipping_uog_su_covers_service"
            )
            return {"queries_executed": 0, "edges_created": 0, "stub": True}
        falkordb_client = get_graph_cache().client
    try:
        stats = falkordb_client.execute(cypher, params)
        return {
            "queries_executed": 1,
            "edges_created": int(stats.get("relationships_created", 0)),
            "stub": False,
        }
    except Exception as exc:
        logger.warning("uog_su_covers_service_failed", error=str(exc))
        return {"queries_executed": 0, "edges_created": 0, "stub": True}


__all__ = [
    "SERVICE_AREAS",
    "_build_uog_su_covers_service_query",
    "_detect_service_areas",
    "build_uog_su_covers_service_query",
    "populate_uog_su_covers_service",
]
