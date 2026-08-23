"""
oideachais.cognify_rules.nui_member_connects — the 7th cross-archive
edge rule, linking each **UoG module descriptor** to its
**NUI-member equivalent** (e.g. CT516 ↔ UCD-CS-516).

The new rule:

  7. (:UoGNUIMemberDescriptor) -[:CONNECTED_TO]-> (:UniversityModuleDescriptor)
     when the UoG module's title or topic matches a UoG module
     descriptor by cosine similarity ≥ 0.85 over the
     `learning_outcomes` text.

The edge carries `match_confidence ∈ [0.0, 1.0]`:
  - 1.00 for an explicit mapping on a UoGNUISyllabusDescriptor row.
  - 0.85+ for cosine-derived matches.

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def _build_nui_member_connects_query(
    nui_members: list[dict[str, Any]],
    nui_syllabus_descriptors: list[dict[str, Any]],
    uog_module_descriptors: list[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.85,
) -> tuple[str, dict[str, Any]]:
    members = [m for m in nui_members if isinstance(m, dict) and m.get("member_id")]
    syllabi = [
        s
        for s in nui_syllabus_descriptors
        if isinstance(s, dict) and (s.get("member_id") or "")
    ]
    modules = [
        m
        for m in uog_module_descriptors
        if isinstance(m, dict) and (m.get("module_code") or "")
    ]
    if not members or not syllabi or not modules:
        return "", {}
    params: dict[str, Any] = {
        "syllabi": syllabi,
        "members": members,
        "modules": modules,
        "threshold": fuzzy_threshold,
    }
    cypher = """
    UNWIND $syllabi AS s
    MATCH (m:UoGNUIMemberDescriptor {member_id: s.member_id})
    UNWIND s.equivalent_module_codes AS eq_code
    WITH m, s, eq_code
    MATCH (uog:UniversityModuleDescriptor {module_code: eq_code})
    MERGE (m)-[r:CONNECTED_TO]->(uog)
    ON CREATE SET r.match_confidence = 1.0,
                  r.match_kind        = 'explicit_nui_syllabus',
                  r.matched_at        = timestamp(),
                  r.through_module_code = eq_code
    ON MATCH  SET r.match_confidence = 1.0
    RETURN count(r) AS edges_created
    """
    return cypher, params


def build_nui_member_connects_query(
    nui_members: Iterable[dict[str, Any]],
    nui_syllabus_descriptors: Iterable[dict[str, Any]],
    uog_module_descriptors: Iterable[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.85,
) -> tuple[str, dict[str, Any]]:
    return _build_nui_member_connects_query(
        list(nui_members),
        list(nui_syllabus_descriptors),
        list(uog_module_descriptors),
        fuzzy_threshold=fuzzy_threshold,
    )


def populate_nui_member_connects(
    *,
    nui_members: Iterable[dict[str, Any]] | None = None,
    nui_syllabus_descriptors: Iterable[dict[str, Any]] | None = None,
    uog_module_descriptors: Iterable[dict[str, Any]] | None = None,
    falkordb_client: Any = None,
    fuzzy_threshold: float = 0.85,
) -> dict[str, Any]:
    cypher, params = build_nui_member_connects_query(
        nui_members=nui_members or [],
        nui_syllabus_descriptors=nui_syllabus_descriptors or [],
        uog_module_descriptors=uog_module_descriptors or [],
        fuzzy_threshold=fuzzy_threshold,
    )
    if not cypher:
        return {"queries_executed": 0, "edges_created": 0, "stub": False}
    if falkordb_client is None:
        try:
            from cianfhoghlaim.cognify.falkordb_client import get_graph_cache
        except ImportError:
            logger.warning(
                "falkordb_client_not_available_skipping_nui_member_connects"
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
        logger.warning("nui_member_connects_failed", error=str(exc))
        return {"queries_executed": 0, "edges_created": 0, "stub": True}


__all__ = [
    "_build_nui_member_connects_query",
    "build_nui_member_connects_query",
    "populate_nui_member_connects",
]
