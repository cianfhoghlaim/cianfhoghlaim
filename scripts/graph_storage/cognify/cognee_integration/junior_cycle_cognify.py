"""
oideachais.cognee_integration.junior_cycle_cognify — Stage 3 cognify
adapter for the Junior Cycle curriculum Cognee dataset.

Stage 3 of the 5-stage curriculum pipeline (per
openspec/specs/oideachais-cognify-knowledge-graph/spec.md
Requirement "5-stage cross-stage knowledge graph").

The Irish Junior Cycle (NCCA, 2014 + Framework 2024 refresh)
covers ~21 subjects (English, Gaeilge, Mathematics, Science,
History, Geography, CSPE, SPHE, PE, + ~12 optional subjects)
across 3 years (1st Year → 3rd Year / JCPA). This adapter
cognifies the BAML-extracted ``JCLearningOutcome`` rows into
the ``oideachais_junior_cycle`` Cognee dataset with 6 edge
types:

  * (:JCLearningOutcome) -[:BELONGS_TO]-> (:JCSubject)
  * (:JCLearningOutcome) -[:CONTRIBUTES_TO-> (:JCKeySkill)
  * (:JCLearningOutcome) -[:STAGE_OF]-> (:YearGroup)
  * (:JCLearningOutcome) -[:STRAND_OF]-> (:Strand)
  * (:JCLearningOutcome) -[:ASSESSED_VIA]-> (:JCATask)
  * (:JCLearningOutcome) -[:PREPARES_FOR]-> (:SCLearningOutcome)

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


DATASET_JUNIOR_CYCLE = "oideachais_junior_cycle"


EDGE_TYPES = [
    "JCLearningOutcome->BELONGS_TO->JCSubject",
    "JCLearningOutcome->CONTRIBUTES_TO->JCKeySkill",
    "JCLearningOutcome->STAGE_OF->YearGroup",
    "JCLearningOutcome->STRAND_OF->Strand",
    "JCLearningOutcome->ASSESSED_VIA->JCATask",
    "JCLearningOutcome->PREPARES_FOR->SCLearningOutcome",
]


STAGE_META = {
    "stage_id": "stage_3_junior_cycle",
    "stage_name": "Junior Cycle",
    "stage_name_ga": "An Timpeallán Sóisearach",
    "age_range": "12-15",
    "node_count_estimate": 1200,  # ~400 LOs × 3 year groups
    "subject_count": 21,
    "year_groups": ["1st Year", "2nd Year", "3rd Year (JCPA)"],
}


async def cognify_junior_cycle_rows(
    rows: list[dict[str, Any]],
    *,
    locale: str = "en",
) -> dict[str, Any]:
    """Cognify a batch of BAML-extracted JCLearningOutcome rows.

    Parameters
    ----------
    rows
        A list of dicts. Expected shape is the BAML-extracted
        ``JCLearningOutcome`` row produced by
        ``cianfhoghlaim.dlt.british_isles.ireland.education.stages.junior_cycle``.
    locale
        ``"en"`` (English) or ``"ga"`` (Gaeilge). Defaults to ``"en"``.

    Returns
    -------
    dict[str, Any]
        ``{"dataset": str, "stage": str, "rows": int, "edges": int, "stub": bool}``.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "junior_cycle_cognify_skipped_stub_mode",
            dataset=DATASET_JUNIOR_CYCLE,
            rows=len(rows),
            locale=locale,
        )
        return {
            "dataset": DATASET_JUNIOR_CYCLE,
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
            dataset=DATASET_JUNIOR_CYCLE,
        )
        return {
            "dataset": DATASET_JUNIOR_CYCLE,
            "stage": STAGE_META["stage_id"],
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    for row in rows:
        enriched = {**row, "_stage": STAGE_META["stage_id"], "_locale": locale}
        payload = json.dumps(enriched, default=str)
        await cognee.add(payload, dataset_name=DATASET_JUNIOR_CYCLE)
    await cognee.cognify()
    return {
        "dataset": DATASET_JUNIOR_CYCLE,
        "stage": STAGE_META["stage_id"],
        "rows": len(rows),
        "edges": len(rows) * len(EDGE_TYPES),
        "stub": False,
    }


def junior_cycle_priority_subjects() -> list[str]:
    """Return the 6 BIEP Junior Cycle priority subjects (per BIEP v1)."""
    return [
        "Mathematics",
        "Science",
        "English",
        "Gaeilge",
        "History",
        "Geography",
    ]


def junior_cycle_priority_subjects_ga() -> list[str]:
    """Return the 6 BIEP Junior Cycle priority subjects (GA / Gaeilge)."""
    return [
        "Matamaitic",
        "Eolaíocht",
        "Béarla",
        "Gaeilge",
        "Stair",
        "Tíreolaíocht",
    ]


__all__ = [
    "DATASET_JUNIOR_CYCLE",
    "EDGE_TYPES",
    "STAGE_META",
    "cognify_junior_cycle_rows",
    "junior_cycle_priority_subjects",
    "junior_cycle_priority_subjects_ga",
]