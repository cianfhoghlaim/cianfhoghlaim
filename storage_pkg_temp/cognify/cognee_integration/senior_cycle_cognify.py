"""
oideachais.cognee_integration.senior_cycle_cognify — Stage 4 cognify
adapter for the Senior Cycle / Leaving Certificate Cognee dataset.

Stage 4 of the 5-stage curriculum pipeline (per
openspec/specs/oideachais-cognify-knowledge-graph/spec.md
Requirement "5-stage cross-stage knowledge graph").

The Irish Senior Cycle (NCCA, 2017 + Subject Specifications)
covers the Leaving Certificate (established) + Leaving Certificate
Applied (LCA) + Leaving Certificate Vocational Programme (LCVP).
This adapter cognifies the BAML-extracted ``SCLearningOutcome``
rows into the ``oideachais_senior_cycle`` Cognee dataset with
7 edge types:

  * (:SCLearningOutcome) -[:BELONGS_TO]-> (:LCSubject)
  * (:SCLearningOutcome) -[:ASSESSED_BY]-> (:ExamQuestion)
  * (:SCLearningOutcome) -[:STAGE_OF]-> (:YearGroup)
  * (:SCLearningOutcome) -[:STRAND_OF]-> (:Strand)
  * (:SCLearningOutcome) -[:BUILDS_ON]-> (:JCLearningOutcome)
  * (:SCLearningOutcome) -[:DEVELOPS]-> (:KeyCompetency)
  * (:LCSubject) -[:HAS_LEVEL]-> (:LCLevel)  # Higher / Ordinary / Foundation

The function is a no-op in stub mode
(``USE_LOCAL_SCRAPES=true``, the CI default) and a real
``cognee.add()`` + ``cognee.cognify()`` call in production.

Reference: openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/
"""
from __future__ import annotations

import json
import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


DATASET_SENIOR_CYCLE = "oideachais_senior_cycle"


EDGE_TYPES = [
    "SCLearningOutcome->BELONGS_TO->LCSubject",
    "SCLearningOutcome->ASSESSED_BY->ExamQuestion",
    "SCLearningOutcome->STAGE_OF->YearGroup",
    "SCLearningOutcome->STRAND_OF->Strand",
    "SCLearningOutcome->BUILDS_ON->JCLearningOutcome",
    "SCLearningOutcome->DEVELOPS->KeyCompetency",
    "LCSubject->HAS_LEVEL->LCLevel",
]


STAGE_META = {
    "stage_id": "stage_4_senior_cycle",
    "stage_name": "Senior Cycle",
    "stage_name_ga": "An Timpeallán Sinsearach",
    "age_range": "15-18",
    "node_count_estimate": 1800,  # ~600 LOs × 3 year groups
    "lc_subjects_count": 42,  # 28 LC established + 14 LCA + LCVP strands
    "year_groups": ["5th Year", "6th Year (LC1)", "6th Year (LC2)"],
    "lc_levels": ["Higher", "Ordinary", "Foundation"],
}


async def cognify_senior_cycle_rows(
    rows: list[dict[str, Any]],
    *,
    locale: str = "en",
) -> dict[str, Any]:
    """Cognify a batch of BAML-extracted SCLearningOutcome rows.

    Parameters
    ----------
    rows
        A list of dicts. Expected shape is the BAML-extracted
        ``SCLearningOutcome`` row produced by
        ``cianfhoghlaim.dlt.british_isles.ireland.education.stages.senior_cycle``.
    locale
        ``"en"`` (English) or ``"ga"`` (Gaeilge). Defaults to ``"en"``.

    Returns
    -------
    dict[str, Any]
        ``{"dataset": str, "stage": str, "rows": int, "edges": int, "stub": bool}``.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "senior_cycle_cognify_skipped_stub_mode",
            dataset=DATASET_SENIOR_CYCLE,
            rows=len(rows),
            locale=locale,
        )
        return {
            "dataset": DATASET_SENIOR_CYCLE,
            "stage": STAGE_META["stage_id"],
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    try:
        import cognee  # type: ignore[import-not-found]
    except ImportError:
        logger.warning(
            "cognee_not_available_skipping_cognify",
            dataset=DATASET_SENIOR_CYCLE,
        )
        return {
            "dataset": DATASET_SENIOR_CYCLE,
            "stage": STAGE_META["stage_id"],
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    for row in rows:
        enriched = {**row, "_stage": STAGE_META["stage_id"], "_locale": locale}
        payload = json.dumps(enriched, default=str)
        await cognee.add(payload, dataset_name=DATASET_SENIOR_CYCLE)
    await cognee.cognify()
    return {
        "dataset": DATASET_SENIOR_CYCLE,
        "stage": STAGE_META["stage_id"],
        "rows": len(rows),
        "edges": len(rows) * len(EDGE_TYPES),
        "stub": False,
    }


def senior_cycle_priority_subjects() -> list[str]:
    """Return the 6 BIEP Leaving Certificate priority subjects (per BIEP v1)."""
    return [
        "Mathematics",
        "Chemistry",
        "Geography",
        "Gaeilge",
        "English",
        "Computer Science",
    ]


def senior_cycle_priority_subjects_ga() -> list[str]:
    """Return the 6 BIEP Leaving Certificate priority subjects (GA / Gaeilge)."""
    return [
        "Matamaitic",
        "Ceimic",
        "Tíreolaíocht",
        "Gaeilge",
        "Béarla",
        "Ríomheolaíocht",
    ]


__all__ = [
    "DATASET_SENIOR_CYCLE",
    "EDGE_TYPES",
    "STAGE_META",
    "cognify_senior_cycle_rows",
    "senior_cycle_priority_subjects",
    "senior_cycle_priority_subjects_ga",
]