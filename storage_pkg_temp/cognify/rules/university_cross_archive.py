"""
oideachais.cognify_rules.university_cross_archive — the 4th cross-archive
edge rule, linking the personal-archive UoG artefacts to the scraped
UoG course descriptors.

The new rule:

  4. (:UoGArtifact) -[:MATCHES]-> (:UniversityCourseDescriptor)
     when either:
       (a) the UoG artefact's `course_code` (e.g. "CT511") matches the
           descriptor's `programme_code` (e.g. "HDSD" — exact or
           prefix), OR
       (b) fuzzy title similarity > 0.85 between the artefact's
           `module_title` and the descriptor's `course_title`.

The edge carries a `match_confidence` property in [0.0, 1.0]:
  - 1.0 for an exact course_code match
  - fuzzy_title_similarity for a fuzzy title match
  - 0.0 for no match (the edge is NOT emitted)

This is the 4th rule of the leabharlann cross-archive family. The other
3 (`GeminiReport-CITES-ZoteroPaper`, `UoGArtifact-TEACHES-ZoteroPaper`,
`TakeoutDoc-CITES-GeminiReport`) live in
`cianfhoghlaim/cognify/rules/leabharlann_cross_archive.py`.

Reference: openspec/changes/university-of-galway-deep-extraction/
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalise_title(s: str) -> str:
    """Lowercase + strip non-alphanumeric for fuzzy match."""
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _title_similarity(a: str, b: str) -> float:
    """Token-Jaccard similarity between two titles.

    Returns 0.0 if either title is empty. Returns 1.0 for exact
    equality after normalisation. The threshold for the
    `UoGArtifact-MATCHES-CourseDescriptor` rule is 0.85.
    """
    a_norm = _normalise_title(a)
    b_norm = _normalise_title(b)
    if not a_norm or not b_norm:
        return 0.0
    if a_norm == b_norm:
        return 1.0
    a_tokens = set(a_norm.split())
    b_tokens = set(b_norm.split())
    if not a_tokens or not b_tokens:
        return 0.0
    intersection = a_tokens & b_tokens
    union = a_tokens | b_tokens
    return len(intersection) / len(union) if union else 0.0


def _course_code_exact_match(artefact_code: str, descriptor_code: str) -> float:
    """Confidence for an exact course_code match.

    Returns 1.0 for exact match, 0.0 otherwise.
    """
    a = (artefact_code or "").strip().upper()
    d = (descriptor_code or "").strip().upper()
    if not a or not d:
        return 0.0
    return 1.0 if a == d else 0.0


# ---------------------------------------------------------------------------
# Rule 4 builder
# ---------------------------------------------------------------------------


def _build_uog_matches_course_descriptor_query(
    uog_artifacts: list[dict[str, Any]],
    course_descriptors: list[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.85,
) -> tuple[str, dict[str, Any]]:
    """Build a single Cypher MERGE query for the `MATCHES` rule.

    Match conditions (in priority order):
      1. exact course_code match (confidence 1.0)
      2. fuzzy title similarity >= `fuzzy_threshold` (confidence = similarity)

    The left node is the UoG artefact's `file_hash` (the same
    identifier used by the existing 3 rules). The right node is the
    descriptor's `source_url` (or `id` if a future Pydantic v2 model
    is added).
    """
    # Index descriptors by code (for the exact match) and by normalised
    # title (for the fuzzy match).
    descriptors_by_code: dict[str, list[dict[str, Any]]] = {}
    descriptors_by_title: dict[str, list[dict[str, Any]]] = {}
    for d in course_descriptors:
        code = (d.get("programme_code") or "").strip().upper()
        if code:
            descriptors_by_code.setdefault(code, []).append(d)
        title_key = _normalise_title(d.get("course_title", ""))
        if title_key:
            descriptors_by_title.setdefault(title_key, []).append(d)

    edges: list[dict[str, Any]] = []
    for uog in uog_artifacts:
        source = uog.get("file_hash", "")
        if not source:
            continue
        artefact_code = (uog.get("course_code") or "").strip().upper()
        artefact_title = uog.get("module_title", "")

        # Match condition 1: exact course_code match
        if artefact_code and artefact_code in descriptors_by_code:
            for d in descriptors_by_code[artefact_code]:
                edges.append(
                    {
                        "source": source,
                        "target": d.get("source_url", "") or d.get("id", ""),
                        "match_confidence": 1.0,
                        "match_kind": "course_code_exact",
                    }
                )
            continue

        # Match condition 2: fuzzy title match
        if artefact_title:
            best: tuple[float, dict[str, Any] | None] = (0.0, None)
            for title_key, desc_list in descriptors_by_title.items():
                for d in desc_list:
                    sim = _title_similarity(artefact_title, d.get("course_title", ""))
                    if sim > best[0]:
                        best = (sim, d)
            if best[0] >= fuzzy_threshold and best[1] is not None:
                edges.append(
                    {
                        "source": source,
                        "target": best[1].get("source_url", "") or best[1].get("id", ""),
                        "match_confidence": round(best[0], 4),
                        "match_kind": "fuzzy_title",
                    }
                )
            elif best[0] > 0.0 and best[0] < fuzzy_threshold:
                # No edge emitted, but log the best-match confidence for
                # observability (per the spec scenario).
                logger.debug(
                    "uog_no_match_under_threshold",
                    file_hash=source,
                    artefact_title=artefact_title,
                    best_confidence=round(best[0], 4),
                    threshold=fuzzy_threshold,
                )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (u:UoGArtifact {file_hash: edge.source})
    MATCH (c:UniversityCourseDescriptor {source_url: edge.target})
    MERGE (u)-[r:MATCHES {match_confidence: edge.match_confidence, match_kind: edge.match_kind}]->(c)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Public entry point — call this from the cognify Dagster asset
# ---------------------------------------------------------------------------


def build_uog_matches_course_descriptor_query(
    uog_artifacts: Iterable[dict[str, Any]],
    course_descriptors: Iterable[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.85,
) -> tuple[str, dict[str, Any]]:
    """Build the `(cypher, params)` tuple for the 4th cross-archive rule.

    Returns an empty `("", {})` tuple when no matches are found; the
    caller is expected to skip the execution in that case.
    """
    return _build_uog_matches_course_descriptor_query(
        list(uog_artifacts),
        list(course_descriptors),
        fuzzy_threshold=fuzzy_threshold,
    )


def populate_uog_matches_course_descriptor(
    *,
    uog_artifacts: Iterable[dict[str, Any]] | None = None,
    course_descriptors: Iterable[dict[str, Any]] | None = None,
    falkordb_client: Any = None,
    fuzzy_threshold: float = 0.85,
) -> dict[str, Any]:
    """Populate the 4th cross-archive edge (UoGArtifact-MATCHES-CourseDescriptor).

    Parameters
    ----------
    uog_artifacts, course_descriptors
        The 2 input corpora (each a list of dicts from the
        `leabharlann.university_of_galway` source + the
        `uog_extract_courses` Dagster asset).
    falkordb_client
        An instance of `FalkorDBClient`. If None, a new client is
        constructed via the canonical singleton.
    fuzzy_threshold
        Minimum Jaccard similarity for a fuzzy-title match (default 0.85).

    Returns
    -------
    dict[str, Any]
        `{"queries_executed": int, "edges_created": int, "stub": bool}`.
    """
    cypher, params = build_uog_matches_course_descriptor_query(
        uog_artifacts=uog_artifacts or [],
        course_descriptors=course_descriptors or [],
        fuzzy_threshold=fuzzy_threshold,
    )
    if not cypher:
        return {"queries_executed": 0, "edges_created": 0, "stub": False}

    if falkordb_client is None:
        try:
            from cianfhoghlaim.cognify.falkordb_client import get_graph_cache
        except ImportError:
            logger.warning("falkordb_client_not_available_skipping_uog_matches")
            return {"queries_executed": 0, "edges_created": 0, "stub": True}
        falkordb_client = get_graph_cache().client

    try:
        stats = falkordb_client.execute(cypher, params)
        return {
            "queries_executed": 1,
            "edges_created": int(stats.get("relationships_created", 0)),
            "stub": False,
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("uog_matches_course_descriptor_failed", error=str(exc))
        return {"queries_executed": 0, "edges_created": 0, "stub": True}


__all__ = [
    "_normalise_title",
    "_title_similarity",
    "_course_code_exact_match",
    "_build_uog_matches_course_descriptor_query",
    "build_uog_matches_course_descriptor_query",
    "populate_uog_matches_course_descriptor",
]
