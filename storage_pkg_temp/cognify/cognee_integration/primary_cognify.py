"""
oideachais.cognee_integration.primary_cognify — Stage 2 cognify
adapter for the Primary curriculum Cognee dataset.

Stage 2 of the 5-stage curriculum pipeline (per
openspec/specs/oideachais-cognify-knowledge-graph/spec.md
Requirement "5-stage cross-stage knowledge graph").

The Irish Primary Curriculum (NCCA, 1999 + 2023 refresh) spans
8 stages (Junior Infants → 6th Class) across 6 curricular areas:
Language (Gaeilge + English), Mathematics, SESE (Science, History,
Geography), Arts Education, PE, SPHE. This adapter cognifies
the BAML-extracted ``PrimaryLearningOutcome`` rows into the
``oideachais_primary`` Cognee dataset with 5 edge types:

  * (:PrimaryLearningOutcome) -[:BELONGS_TO]-> (:CurricularArea)
  * (:PrimaryLearningOutcome) -[:DEVELOPS]-> (:KeyCompetency)
  * (:PrimaryLearningOutcome) -[:STAGE_OF]-> (:ClassStage)
  * (:PrimaryLearningOutcome) -[:STRAND_OF]-> (:Strand)
  * (:PrimaryLearningOutcome) -[:ASSESSED_VIA]-> (:AssessmentTask)

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


DATASET_PRIMARY = "oideachais_primary"


EDGE_TYPES = [
    "PrimaryLearningOutcome->BELONGS_TO->CurricularArea",
    "PrimaryLearningOutcome->DEVELOPS->KeyCompetency",
    "PrimaryLearningOutcome->STAGE_OF->ClassStage",
    "PrimaryLearningOutcome->STRAND_OF->Strand",
    "PrimaryLearningOutcome->ASSESSED_VIA->AssessmentTask",
]


STAGE_META = {
    "stage_id": "stage_2_primary",
    "stage_name": "Primary",
    "stage_name_ga": "Bunscoil",
    "age_range": "5-12",
    "node_count_estimate": 2400,  # ~300 LOs × 8 class stages
    "curricular_area_count": 6,
    "class_stages": [
        "Junior Infants",
        "Senior Infants",
        "1st Class",
        "2nd Class",
        "3rd Class",
        "4th Class",
        "5th Class",
        "6th Class",
    ],
}


async def cognify_primary_rows(
    rows: list[dict[str, Any]],
    *,
    locale: str = "en",
) -> dict[str, Any]:
    """Cognify a batch of BAML-extracted PrimaryLearningOutcome rows.

    Parameters
    ----------
    rows
        A list of dicts. Expected shape is the BAML-extracted
        ``PrimaryLearningOutcome`` row produced by
        ``cianfhoghlaim.dlt.british_isles.ireland.education.stages.primary``.
    locale
        ``"en"`` (English) or ``"ga"`` (Gaeilge). Defaults to ``"en"``.

    Returns
    -------
    dict[str, Any]
        ``{"dataset": str, "stage": str, "rows": int, "edges": int, "stub": bool}``.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "primary_cognify_skipped_stub_mode",
            dataset=DATASET_PRIMARY,
            rows=len(rows),
            locale=locale,
        )
        return {
            "dataset": DATASET_PRIMARY,
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
            dataset=DATASET_PRIMARY,
        )
        return {
            "dataset": DATASET_PRIMARY,
            "stage": STAGE_META["stage_id"],
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    for row in rows:
        enriched = {**row, "_stage": STAGE_META["stage_id"], "_locale": locale}
        payload = json.dumps(enriched, default=str)
        await cognee.add(payload, dataset_name=DATASET_PRIMARY)
    await cognee.cognify()
    return {
        "dataset": DATASET_PRIMARY,
        "stage": STAGE_META["stage_id"],
        "rows": len(rows),
        "edges": len(rows) * len(EDGE_TYPES),
        "stub": False,
    }


def primary_curricular_areas() -> list[str]:
    """Return the 6 canonical Primary curricular areas (EN)."""
    return [
        "Language",
        "Mathematics",
        "SESE (Science, History, Geography)",
        "Arts Education",
        "Physical Education",
        "SPHE",
    ]


def primary_curricular_areas_ga() -> list[str]:
    """Return the 6 canonical Primary curricular areas (GA / Gaeilge)."""
    return [
        "Teanga",
        "Matamaitic",
        "OSPS (Eolaíocht, Stair, Tíreolaíocht)",
        "Oideachas Ealaíne",
        "Corpoideachas",
        "OSPS",
    ]


__all__ = [
    "DATASET_PRIMARY",
    "EDGE_TYPES",
    "STAGE_META",
    "cognify_primary_rows",
    "primary_curricular_areas",
    "primary_curricular_areas_ga",
]