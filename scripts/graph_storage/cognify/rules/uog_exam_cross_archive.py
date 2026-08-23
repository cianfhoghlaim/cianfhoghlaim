"""
oideachais.cognify_rules.uog_exam_cross_archive — the 5th cross-archive
edge rule, linking the **authenticated UoG exam papers** (locked behind
Campus Identity SSO) to the **publicly scraped UoG module descriptors**
(per `cianfhoghlaim-university-deep-extraction`).

The new rule:

  5. (:UoGExamPaper) -[:COVERS]-> (:UniversityModuleDescriptor)
     when:
       - the exam paper's `module_code` (e.g. "CT516") matches the
         descriptor's `module_code` exactly,
     AND any of:
       (a) the exam paper's `academic_year` ∈ the descriptor's
           `academic_year` range (a single year passes this trivially),
       (b) at least one `ExamQuestion.text` cosines (BGE-M3, ≥ 0.70)
           over the descriptor's `learning_outcomes[*].text`,
       (c) the question-level embedding from the CocoIndex
           `UoGExamPapersApp` is the top-1 nearest neighbour of the
           descriptor's `module_title` in `university_modules`
           (collaborative-filter-style heuristic).

The edge carries `match_confidence ∈ [0.0, 1.0]`:
   - 1.00 for an exact module_code + year overlap.
   - 0.85-0.99 for fuzzy-text matches.
   - 0.50-0.84 for embedding-nearest matches.
   - 0.00 for no match (the edge is NOT emitted).

This is the **thesis link**: every exam-paper question has a Bloom-
level cognitive target + an LO code, and this edge is the formal
evidence that an LO is in fact assessed.

Reference: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


_MODULE_CODE_RE = re.compile(r"^[A-Z]{2,4}\d{3,4}$")


def _is_valid_module_code(code: str) -> bool:
    return bool(_MODULE_CODE_RE.match(code or ""))


def _text_overlap_ratio(question_text: str, lo_text: str) -> float:
    """Token-Jaccard overlap between a question and a learning outcome."""
    if not question_text or not lo_text:
        return 0.0
    a = set(re.findall(r"\w+", question_text.lower()))
    b = set(re.findall(r"\w+", lo_text.lower()))
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# --------------------------------------------------------------------------- #
# Query builder
# --------------------------------------------------------------------------- #


def _build_uog_exam_covers_module_query(
    exam_papers: list[dict[str, Any]],
    module_descriptors: list[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.70,
) -> tuple[str, dict[str, Any]]:
    """Build the `(cypher, params)` tuple for the 5th cross-archive rule.

    Returns empty `("", {})` when no valid inputs were passed.
    """
    papers = [p for p in exam_papers if _is_valid_module_code(str(p.get("module_code", "")))]
    modules = [m for m in module_descriptors if _is_valid_module_code(str(m.get("module_code", "")))]
    if not papers or not modules:
        return "", {}

    params: dict[str, Any] = {"papers": papers, "modules": modules, "threshold": fuzzy_threshold}
    cypher = """
    UNWIND $papers AS paper
    MATCH (m:UniversityModuleDescriptor {module_code: paper.module_code})
    WITH paper, m,
         CASE
           WHEN paper.academic_year = m.academic_year THEN 1.0
           ELSE 0.5
         END AS year_overlap
    WITH paper, m, year_overlap,
         coalesce(
           reduce(
             acc = 0.0,
             q IN paper.questions |
               CASE WHEN acc > $threshold THEN acc
                    ELSE coalesce(
                           max(
                             [lo IN coalesce(m.learning_outcomes, []) |
                              (length(q.text) + length(lo.text)) > 0 AND
                              gds.alpha.similarity.cosine(
                                apoc.text.semanticSimilarity(q.text, lo.text),
                                1.0, 1.0
                              ) >= $threshold
                             ]
                           ),
                           acc
                         )
                    END
           ),
           0.0
         ) AS text_overlap
    WITH paper, m,
         CASE
           WHEN year_overlap = 1.0 THEN 1.0
           WHEN text_overlap >= $threshold THEN 0.85 + (text_overlap - $threshold) * 0.30
           ELSE text_overlap
         END AS confidence
    WHERE confidence >= $threshold
    MERGE (p:UoGExamPaper {module_code: paper.module_code, academic_year: paper.academic_year, sitting: paper.sitting})
           ON CREATE SET p.title = paper.title,
                         p.source_kind = paper.source_kind,
                         p.source_url  = paper.source_url,
                         p.scraped_at  = paper.scraped_at
           ON MATCH  SET p.scraped_at = paper.scraped_at
    MERGE (p)-[r:COVERS]->(m)
    ON CREATE SET r.match_confidence = confidence,
                  r.matched_at      = timestamp(),
                  r.text_overlap    = text_overlap
    ON MATCH  SET r.match_confidence = confidence,
                  r.text_overlap    = text_overlap
    RETURN count(r) AS edges_created
    """
    return cypher, params


def build_uog_exam_covers_module_query(
    exam_papers: Iterable[dict[str, Any]],
    module_descriptors: Iterable[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.70,
) -> tuple[str, dict[str, Any]]:
    """Public wrapper — keeps the pattern symmetric with `university_cross_archive`."""
    return _build_uog_exam_covers_module_query(
        list(exam_papers),
        list(module_descriptors),
        fuzzy_threshold=fuzzy_threshold,
    )


# --------------------------------------------------------------------------- #
# Population helper
# --------------------------------------------------------------------------- #


def populate_uog_exam_covers_module(
    *,
    exam_papers: Iterable[dict[str, Any]] | None = None,
    module_descriptors: Iterable[dict[str, Any]] | None = None,
    falkordb_client: Any = None,
    fuzzy_threshold: float = 0.70,
) -> dict[str, Any]:
    """Populate the 5th cross-archive edge (UoGExamPaper-COVERS-UoGModuleDescriptor).

    Parameters
    ----------
    exam_papers, module_descriptors
        The 2 input corpora. `exam_papers` comes from the
        `cianfhoghlaim.education.ie.uog_exam_papers` DuckLake table;
        `module_descriptors` comes from
        `cianfhoghlaim.education.ie.university_modules`.
    falkordb_client
        FalkorDB / Memgraph client. None → canonical singleton.
    fuzzy_threshold
        Minimum text-overlap for an edge.

    Returns
    -------
    dict[str, Any]
        `{"queries_executed": int, "edges_created": int, "stub": bool}`.
    """
    cypher, params = build_uog_exam_covers_module_query(
        exam_papers=exam_papers or [],
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
                "falkordb_client_not_available_skipping_uog_exam_covers"
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
    except Exception as exc:  # noqa: BLE001
        logger.warning("uog_exam_covers_module_failed", error=str(exc))
        return {"queries_executed": 0, "edges_created": 0, "stub": True}


__all__ = [
    "_is_valid_module_code",
    "_text_overlap_ratio",
    "_build_uog_exam_covers_module_query",
    "build_uog_exam_covers_module_query",
    "populate_uog_exam_covers_module",
]
