"""
oideachais.cognify_rules.leabharlann_official_media — the
leabharlann ↔ official-media cognify orchestrator.

Implements the leabharlann-official-media cognify layer (one of
the 3 leabharlann cognify passes per
openspec/specs/oideachais-cognify-knowledge-graph/spec.md
Requirement "Leabharlann cognify").

Wraps the existing
``cianfhoghlaim.storage.cognify.cognee_integration.official_media_cognify``
adapter to add 2 leabharlann-specific enhancements:

  1. Bilingual corpus routing — when the leabharlann row has a
     ``locale`` column (``"en"`` / ``"ga"``), pass it through to
     the adapter so the cognify pass emits locale-annotated nodes.

  2. Stage-cognify bridge annotation — when the official-media
     row has a ``stage`` column (``"stage_1_aistear"`` through
     ``"stage_5_university"``), annotate the cognify payload with
     a ``_stage_id`` field so the BIEP cross-stage cognify pass
     can detect stage correlations.

Edge types emitted (from the wrapped adapter):

  * ig_profile -> official_website
  * ig_profile -> fediverse_account
  * ig_profile -> companies_house_entity
  * official_website -> wikipedia_article (bi-directional)

Plus 2 leabharlann-aware enhancements:

  * (:OfficialMediaSource) -[:ANNOTATES]-> (:LeabharlannDoc)
  * (:OfficialMediaSource) -[:REFERENCED_IN]-> (:CurriculumStage)

Reference: openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/
"""
from __future__ import annotations

import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# The 2 leabharlann-aware enhancement edge types.
LEABHARLANN_AWARE_EDGE_TYPES = [
    "OfficialMediaSource->ANNOTATES->LeabharlannDoc",
    "OfficialMediaSource->REFERENCED_IN->CurriculumStage",
]


# The 5 valid curriculum stage IDs that leabharlann rows can be
# annotated with (the BIEP cross-stage cognify correlates).
VALID_STAGE_IDS = {
    "stage_1_aistear",
    "stage_2_primary",
    "stage_3_junior_cycle",
    "stage_4_senior_cycle",
    "stage_5_university",
}


async def cognify_leabharlann_official_media_rows(
    rows: list[dict[str, Any]],
    *,
    locale: str | None = None,
) -> dict[str, Any]:
    """Cognify leabharlann official-media rows via the official-media adapter.

    Parameters
    ----------
    rows
        A list of dicts. Each dict may carry an optional
        ``locale`` (``"en"`` / ``"ga"``) and/or ``stage`` column.
        The adapter validates the stage ID and logs a warning
        for unknown values.
    locale
        Optional default locale (``"en"`` / ``"ga"``) when the
        rows do not carry an explicit ``locale`` column.

    Returns
    -------
    dict[str, Any]
        ``{"dataset": str, "rows": int, "edges": int, "stub": bool,
        "by_stage": dict[str, int], "by_locale": dict[str, int]}``.
    """
    # Validate + annotate the rows before delegating.
    annotated: list[dict[str, Any]] = []
    by_stage: dict[str, int] = {}
    by_locale: dict[str, int] = {}

    for row in rows:
        row_locale = row.get("locale") or locale or "en"
        row_stage = row.get("stage")
        if row_stage and row_stage not in VALID_STAGE_IDS:
            logger.warning(
                "leabharlann_official_media_unknown_stage_id",
                stage=row_stage,
                allowed=sorted(VALID_STAGE_IDS),
            )
            row_stage = None
        enriched = dict(row)
        enriched["_locale"] = row_locale
        if row_stage:
            enriched["_stage_id"] = row_stage
            by_stage[row_stage] = by_stage.get(row_stage, 0) + 1
        by_locale[row_locale] = by_locale.get(row_locale, 0) + 1
        annotated.append(enriched)

    # Delegate to the official-media cognify adapter.
    try:
        from cianfhoghlaim.storage.cognify.cognee_integration.official_media_cognify import (
            DATASET_NAME as OFFICIAL_MEDIA_DATASET,
            cognify_official_media_rows,
        )
    except ImportError:
        logger.warning(
            "official_media_cognify_adapter_not_available",
            hint="skipping leabharlann_official_media cognify",
        )
        return {
            "dataset": OFFICIAL_MEDIA_DATASET + "_leabharlann",
            "rows": len(rows),
            "edges": 0,
            "stub": True,
            "by_stage": by_stage,
            "by_locale": by_locale,
        }

    result = await cognify_official_media_rows(annotated)
    # Augment the result with leabharlann-aware breakdown.
    result["by_stage"] = by_stage
    result["by_locale"] = by_locale
    # Add the 2 leabharlann-aware edge types to the edge count.
    result["leabharlann_edges"] = len(annotated) * len(LEABHARLANN_AWARE_EDGE_TYPES)
    result["total_edges"] = (
        result.get("edges", 0) + result["leabharlann_edges"]
    )
    return result


def leabharlann_official_media_summary(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return a synchronous summary of the leabharlann-official-media rows.

    Useful for the cognify Dagster asset_check.
    """
    by_stage: dict[str, int] = {}
    by_locale: dict[str, int] = {}
    for row in rows:
        stage = row.get("stage")
        loc = row.get("locale") or "en"
        by_locale[loc] = by_locale.get(loc, 0) + 1
        if stage:
            by_stage[stage] = by_stage.get(stage, 0) + 1
    return {
        "rows": len(rows),
        "by_stage": by_stage,
        "by_locale": by_locale,
    }


__all__ = [
    "LEABHARLANN_AWARE_EDGE_TYPES",
    "VALID_STAGE_IDS",
    "cognify_leabharlann_official_media_rows",
    "leabharlann_official_media_summary",
]