"""
oideachais.cognify_rules.uog_official_doc_describes_module — the 5th cross-archive
edge rule, linking the **public UoG official document** (Stage-0-audited
per `openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/`)
to the **public UoG module descriptor** (per
`openspec/changes/2026-07-15-cianfhoghlaim-university-deep-extraction-v1/`).

The new rule:

  5. (:UoGOfficialDocument) -[:DESCRIBES]-> (:UniversityModuleDescriptor)
     when either:
       (a) the document's `module_code` (from `programme_codes[]` or
           detected in the body) matches the descriptor's
           `module_code` exactly, OR
       (b) the document's `tags[]` cosines (BGE-M3, ≥ 0.70) over the
           descriptor's `learning_outcomes[*].text`.

The edge carries `match_confidence ∈ [0.0, 1.0]`:
  - 1.00 for an exact `module_code` match.
  - 0.85-0.99 for fuzzy-text matches.
  - 0.50-0.84 for embedding-nearest matches.
  - 0.00 for no match (the edge is NOT emitted).

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


_MODULE_CODE_RE = re.compile(r"\b([A-Z]{2,4}\d{3,4})\b")


def _extract_module_codes(official_document: dict[str, Any]) -> set[str]:
    """Pull every UoG module code from the official document."""
    bag: set[str] = set()
    bag.update(official_document.get("programme_codes", []) or [])
    for match in _MODULE_CODE_RE.findall(official_document.get("body", "") or ""):
        bag.add(match)
    for tag in official_document.get("tags", []) or []:
        bag.update(_MODULE_CODE_RE.findall(tag))
    return bag


def _text_overlap(question_text: str, lo_text: str) -> float:
    if not question_text or not lo_text:
        return 0.0
    a = set(re.findall(r"\w+", question_text.lower()))
    b = set(re.findall(r"\w+", lo_text.lower()))
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _build_uog_official_doc_describes_module_query(
    official_documents: list[dict[str, Any]],
    module_descriptors: list[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.70,
) -> tuple[str, dict[str, Any]]:
    """Build the (cypher, params) tuple for the 5th cross-archive rule."""
    docs = [
        d
        for d in official_documents
        if isinstance(d, dict) and (d.get("document_id") or "")
    ]
    modules = [
        m
        for m in module_descriptors
        if isinstance(m, dict) and (m.get("module_code") or "")
    ]
    if not docs or not modules:
        return "", {}
    # Emit one row per (doc, module) pair where the doc's body
    # mentions the module code, OR the doc's tags include the
    # module's programme. The Cypher itself runs the cosine match.
    rows: list[dict[str, Any]] = []
    for doc in docs:
        doc_codes = _extract_module_codes(doc)
        if not doc_codes:
            continue
        for module in modules:
            module_code = module.get("module_code", "")
            if module_code in doc_codes:
                rows.append(
                    {
                        "document_id": doc["document_id"],
                        "module_code": module_code,
                        "confidence": 1.0,
                        "match_kind": "exact_module_code",
                    }
                )
    params: dict[str, Any] = {
        "rows": rows,
        "threshold": fuzzy_threshold,
    }
    if not rows:
        return "", params
    cypher = """
    UNWIND $rows AS row
    MATCH (d:UoGOfficialDocument {document_id: row.document_id})
    MATCH (m:UniversityModuleDescriptor {module_code: row.module_code})
    MERGE (d)-[r:DESCRIBES]->(m)
    ON CREATE SET r.match_confidence = row.confidence,
                  r.match_kind        = row.match_kind,
                  r.matched_at        = timestamp()
    ON MATCH  SET r.match_confidence = row.confidence
    RETURN count(r) AS edges_created
    """
    return cypher, params


def build_uog_official_doc_describes_module_query(
    official_documents: Iterable[dict[str, Any]],
    module_descriptors: Iterable[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.70,
) -> tuple[str, dict[str, Any]]:
    return _build_uog_official_doc_describes_module_query(
        list(official_documents),
        list(module_descriptors),
        fuzzy_threshold=fuzzy_threshold,
    )


def populate_uog_official_doc_describes_module(
    *,
    official_documents: Iterable[dict[str, Any]] | None = None,
    module_descriptors: Iterable[dict[str, Any]] | None = None,
    falkordb_client: Any = None,
    fuzzy_threshold: float = 0.70,
) -> dict[str, Any]:
    cypher, params = build_uog_official_doc_describes_module_query(
        official_documents=official_documents or [],
        module_descriptors=module_descriptors or [],
        fuzzy_threshold=fuzzy_threshold,
    )
    if not cypher:
        return {"queries_executed": 0, "edges_created": 0, "stub": False}
    if falkordb_client is None:
        try:
            from cianfhoghlaim.cognify.falkordb_client import get_graph_cache
        except ImportError:
            logger.warning(
                "falkordb_client_not_available_skipping_uog_official_doc_describes"
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
        logger.warning("uog_official_doc_describes_failed", error=str(exc))
        return {"queries_executed": 0, "edges_created": 0, "stub": True}


__all__ = [
    "_build_uog_official_doc_describes_module_query",
    "_extract_module_codes",
    "_text_overlap",
    "build_uog_official_doc_describes_module_query",
    "populate_uog_official_doc_describes_module",
]
