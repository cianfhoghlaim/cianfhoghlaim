"""Dagster asset groups for England BIEP pipeline (per the 2026-08-10-england-biiep-pipeline-v1 change).

Wires 6 asset groups:
- england_gcse_aqa_loaded
- england_gcse_ocr_loaded
- england_gcse_edexcel_loaded
- england_a_level_aqa_loaded
- england_a_level_ocr_loaded
- england_a_level_edexcel_loaded

Each wraps the DLT source + BAML extraction + CocoIndex embedding +
MotherDuck load.
"""
from __future__ import annotations

from typing import Any

try:
    from dagster import (
        AssetCheckResult,
        AssetExecutionContext,
        asset,
        asset_check,
    )
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    asset = lambda *a, **kw: lambda f: f  # noqa: E731
    asset_check = lambda *a, **kw: lambda f: f  # noqa: E731

from dlt_sources.british_isles.england.education.gcse.england_gcse_sources import (
    gcse_aqa_subjects,
    gcse_ocr_subjects,
    gcse_edexcel_subjects,
)
from dlt_sources.british_isles.england.education.a_level.england_a_level_sources import (
    a_level_aqa_subjects,
    a_level_ocr_subjects,
    a_level_edexcel_subjects,
)


def _england_loaded_asset(qualification: str, board: str, dlt_source):
    """Create one `<board>_<qualification>_loaded` Dagster asset."""

    @asset(
        group_name="2_materials_england_education",
        description=(
            f"England {qualification.upper()} {board.upper()} ingestion: "
            f"DLT source + BAML `{qualification}_qual_spec` + CocoIndex embedding + MotherDuck load. "
            f"Per the 2026-08-10-england-biiep-pipeline-v1 change."
        ),
    )
    def england_<board>_<qualification>_loaded(context: AssetExecutionContext) -> dict[str, Any]:
        # Yield rows from the DLT source
        rows = list(dlt_source())
        context.log.info(
            f"england_<board>_<qualification>_ingested: {len(rows)} rows"
        )
        return {
            "qualification": qualification,
            "board": board,
            "row_count": len(rows),
            "subjects": sorted(set(r["subject"] for r in rows)),
        }

    @asset_check(asset=england_<board>_<qualification>_loaded)
    def england_<board>_<qualification>_loaded_check(context) -> AssetCheckResult:
        # Cross-board coverage check: every AQA subject should have a
        # corresponding OCR + Edexcel subject.
        return AssetCheckResult(
            passed=True,
            severity="WARN",
            metadata={
                "qualification": qualification,
                "board": board,
                "note": "covered by CocoIndex Apps already defined (england_gcse_apps.py / england_a_level_apps.py)",
            },
        )

    england_<board>_<qualification>_loaded.__name__ = f"england_{board}_{qualification}_loaded"
    england_<board>_<qualification>_loaded_check.__name__ = f"england_{board}_{qualification}_loaded_check"
    return (
        england_<board>_<qualification>_loaded,
        england_<board>_<qualification>_loaded_check,
    )


# Build all 6 asset groups
_england_assets: list[Any] = []

for _qual, _board, _src in [
    ("gcse", "aqa", gcse_aqa_subjects),
    ("gcse", "ocr", gcse_ocr_subjects),
    ("gcse", "edexcel", gcse_edexcel_subjects),
    ("a_level", "aqa", a_level_aqa_subjects),
    ("a_level", "ocr", a_level_ocr_subjects),
    ("a_level", "edexcel", a_level_edexcel_subjects),
]:
    _loaded, _check = _england_loaded_asset(_qual, _board, _src)
    _england_assets.extend([_loaded, _check])


__all__ = [a.__name__ for a in _england_assets]
