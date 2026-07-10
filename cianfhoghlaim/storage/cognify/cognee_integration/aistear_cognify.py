"""
oideachais.cognee_integration.aistear_cognify — Stage 1 cognify
adapter for the Aistear (early-childhood) Cognee dataset.

Stage 1 of the 5-stage curriculum pipeline
(per openspec/specs/oideachais-cognify-knowledge-graph/spec.md
Requirement "5-stage cross-stage knowledge graph").

The Aistear framework has 4 themes (Well-being, Identity &
Belonging, Communicating, Exploring & Thinking) and 12 guiding
principles. This adapter cognifies the BAML-extracted
AistearPrinciple rows into the ``oideachais_aistear`` Cognee
dataset with 4 edge types:

  * (:AistearPrinciple) -[:BELONGS_TO]-> (:AistearTheme)
  * (:AistearPrinciple) -[:ALIGNS_WITH]-> (:KeyCompetency)
  * (:AistearPrinciple) -[:SUPPORTED_BY]-> (:LearningExperience)
  * (:LearningExperience) -[:TARGETS]-> (:ChildOutcome)

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


DATASET_AISTEAR = "oideachais_aistear"


EDGE_TYPES = [
    "AistearPrinciple->BELONGS_TO->AistearTheme",
    "AistearPrinciple->ALIGNS_WITH->KeyCompetency",
    "AistearPrinciple->SUPPORTED_BY->LearningExperience",
    "LearningExperience->TARGETS->ChildOutcome",
]


STAGE_META = {
    "stage_id": "stage_1_aistear",
    "stage_name": "Aistear",
    "stage_name_ga": "Aistear (Luath-Óige)",
    "age_range": "0-6",
    "node_count_estimate": 12,  # 12 guiding principles
    "theme_count": 4,  # well-being / identity / communicating / exploring
}


async def cognify_aistear_rows(
    rows: list[dict[str, Any]],
    *,
    locale: str = "en",
) -> dict[str, Any]:
    """Cognify a batch of BAML-extracted AistearPrinciple rows.

    Parameters
    ----------
    rows
        A list of dicts. Expected shape is the BAML-extracted
        ``AistearPrinciple`` row produced by
        ``cianfhoghlaim.dlt.british_isles.ireland.education.stages.aistear``.
    locale
        ``"en"`` (English) or ``"ga"`` (Gaeilge). Defaults to ``"en"``.

    Returns
    -------
    dict[str, Any]
        ``{"dataset": str, "stage": str, "rows": int, "edges": int, "stub": bool}``.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "aistear_cognify_skipped_stub_mode",
            dataset=DATASET_AISTEAR,
            rows=len(rows),
            locale=locale,
        )
        return {
            "dataset": DATASET_AISTEAR,
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
            dataset=DATASET_AISTEAR,
        )
        return {
            "dataset": DATASET_AISTEAR,
            "stage": STAGE_META["stage_id"],
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    for row in rows:
        # Annotate with stage metadata + locale before cognify pass.
        enriched = {**row, "_stage": STAGE_META["stage_id"], "_locale": locale}
        payload = json.dumps(enriched, default=str)
        await cognee.add(payload, dataset_name=DATASET_AISTEAR)
    await cognee.cognify()
    return {
        "dataset": DATASET_AISTEAR,
        "stage": STAGE_META["stage_id"],
        "rows": len(rows),
        "edges": len(rows) * len(EDGE_TYPES),
        "stub": False,
    }


def aistear_theme_labels() -> list[str]:
    """Return the 4 canonical Aistear theme labels (EN)."""
    return [
        "Well-being",
        "Identity & Belonging",
        "Communicating",
        "Exploring & Thinking",
    ]


def aistear_theme_labels_ga() -> list[str]:
    """Return the 4 canonical Aistear theme labels (GA / Gaeilge)."""
    return [
        "Biú Folláine",
        "Céannacht agus Muintearas",
        "Cumarsáid",
        "Taiscéalaíocht agus Smaointeoireacht",
    ]


__all__ = [
    "DATASET_AISTEAR",
    "EDGE_TYPES",
    "STAGE_META",
    "aistear_theme_labels",
    "aistear_theme_labels_ga",
    "cognify_aistear_rows",
]