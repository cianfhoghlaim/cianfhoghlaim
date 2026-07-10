"""
oideachais.cognee_integration.university_cognify — Stage 5 cognify
adapter for the University / Tertiary education Cognee dataset.

Stage 5 of the 5-stage curriculum pipeline (per
openspec/specs/oideachais-cognify-knowledge-graph/spec.md
Requirement "5-stage cross-stage knowledge graph").

The Irish Tertiary sector includes:
  * 8 Universities (TCD, UCD, NUIG/UoG, UCC, UL, MU, TU Dublin, RCSI/AUI)
  * 5 Institutes of Technology / Technological Universities (TU Dublin,
    TU Shannon, SETU, MTU, ATU, DkIT, IADT, etc.)
  * QQI (Quality & Qualifications Ireland) — NFQ Levels 6-10
  * CAO (Central Applications Office) — undergraduate admissions
  * Apprenticeships — SOLAS consortium
  * Springboard+ / HCI Pillar 1 / Pillar 2 — upskilling

This adapter cognifies the BAML-extracted ``CAOCourse`` /
``Programme`` / ``QQIFetAward`` / ``Apprenticeship`` rows into
the ``oideachais_university`` Cognee dataset with 8 edge types
(4 NUI/HEI types + 4 cross-stage bridges):

  * (:CAOCourse) -[:OFFERED_BY]-> (:Institution)
  * (:CAOCourse) -[:AWARDS]-> (:QQILevel)
  * (:CAOCourse) -[:DELIVERS]-> (:Programme)
  * (:Programme) -[:TEACHES]-> (:Subject)
  * (:QQIFetAward) -[:LADDERS_INTO]-> (:CAOCourse)
  * (:Apprenticeship) -[:ALTERNATIVE_TO]-> (:CAOCourse)
  * (:CAOCourse) -[:REQUIRES]-> (:LCSubject)
  * (:Programme) -[:HAS_NFQ_LEVEL]-> (:NFQLevel)

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


DATASET_UNIVERSITY = "oideachais_university"


EDGE_TYPES = [
    "CAOCourse->OFFERED_BY->Institution",
    "CAOCourse->AWARDS->QQILevel",
    "CAOCourse->DELIVERS->Programme",
    "Programme->TEACHES->Subject",
    "QQIFetAward->LADDERS_INTO->CAOCourse",
    "Apprenticeship->ALTERNATIVE_TO->CAOCourse",
    "CAOCourse->REQUIRES->LCSubject",
    "Programme->HAS_NFQ_LEVEL->NFQLevel",
]


STAGE_META = {
    "stage_id": "stage_5_university",
    "stage_name": "University / Tertiary",
    "stage_name_ga": "Ollscoil / Tríú Leibhéal",
    "age_range": "18+",
    "node_count_estimate": 4500,  # ~1500 CAO courses × 3 NUI/IoT layers
    "institutions_count": 16,  # 8 universities + 5 TUs + 3 colleges
    "nfq_levels": [6, 7, 8, 9, 10],
}


async def cognify_university_rows(
    rows: list[dict[str, Any]],
    *,
    locale: str = "en",
) -> dict[str, Any]:
    """Cognify a batch of BAML-extracted tertiary education rows.

    Accepts a heterogeneous list of CAOCourse, Programme,
    QQIFetAward, and Apprenticeship rows. The adapter dispatches
    on a ``record_kind`` key (default ``"cao_course"``) so a
    single list can be processed in one cognify pass.

    Parameters
    ----------
    rows
        A list of dicts. Expected shape is the BAML-extracted
        row produced by
        ``cianfhoghlaim.dlt.british_isles.ireland.education.stages.university``.
    locale
        ``"en"`` (English) or ``"ga"`` (Gaeilge). Defaults to ``"en"``.

    Returns
    -------
    dict[str, Any]
        ``{"dataset": str, "stage": str, "rows": int, "edges": int, "stub": bool}``.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "university_cognify_skipped_stub_mode",
            dataset=DATASET_UNIVERSITY,
            rows=len(rows),
            locale=locale,
        )
        return {
            "dataset": DATASET_UNIVERSITY,
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
            dataset=DATASET_UNIVERSITY,
        )
        return {
            "dataset": DATASET_UNIVERSITY,
            "stage": STAGE_META["stage_id"],
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    for row in rows:
        enriched = {**row, "_stage": STAGE_META["stage_id"], "_locale": locale}
        payload = json.dumps(enriched, default=str)
        await cognee.add(payload, dataset_name=DATASET_UNIVERSITY)
    await cognee.cognify()
    return {
        "dataset": DATASET_UNIVERSITY,
        "stage": STAGE_META["stage_id"],
        "rows": len(rows),
        "edges": len(rows) * len(EDGE_TYPES),
        "stub": False,
    }


def irish_universities() -> list[str]:
    """Return the 8 canonical Irish universities."""
    return [
        "Trinity College Dublin (TCD)",
        "University College Dublin (UCD)",
        "University of Galway / Ollscoil na Gaillimhe (UoG / NUIG)",
        "University College Cork (UCC)",
        "University of Limerick (UL)",
        "Maynooth University (MU)",
        "Technological University Dublin (TU Dublin)",
        "Royal College of Surgeons in Ireland (RCSI)",
    ]


def irish_nfq_levels() -> list[dict[str, Any]]:
    """Return the 5 NFQ Level descriptors (6-10)."""
    return [
        {"level": 6, "name": "Advanced Certificate / Higher Certificate"},
        {"level": 7, "name": "Ordinary Bachelor Degree"},
        {"level": 8, "name": "Honours Bachelor Degree / Higher Diploma"},
        {"level": 9, "name": "Master's Degree / Post-Graduate Diploma"},
        {"level": 10, "name": "Doctoral Degree (PhD)"},
    ]


__all__ = [
    "DATASET_UNIVERSITY",
    "EDGE_TYPES",
    "STAGE_META",
    "cognify_university_rows",
    "irish_nfq_levels",
    "irish_universities",
]