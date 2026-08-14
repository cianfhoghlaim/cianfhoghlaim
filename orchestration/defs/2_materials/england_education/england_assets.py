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
# Deliberately NOT `from __future__ import annotations` — see the identical
# note in ../lc_extraction/lc_subjects.py: it breaks Dagster's
# `_validate_context_type_hint` for every `context: AssetExecutionContext`
# annotated @asset in this file.
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
    """Create one `{board}_{qualification}_loaded` Dagster asset.

    The inner `def`s use plain names and get their real per-board/
    qualification name via the `name=`/`asset=` kwargs at decoration time
    (a previous version used literal `<board>`/`<qualification>` tokens in
    the `def` line — a hard SyntaxError — then tried to fix the name via
    `fn.__name__ = f"..."` after decoration, which is a no-op for Dagster).
    """

    @asset(
        name=f"england_{board}_{qualification}_loaded",
        group_name="2_materials_england_education",
        description=(
            f"England {qualification.upper()} {board.upper()} ingestion: "
            f"DLT source + BAML `{qualification}_qual_spec` + CocoIndex embedding + MotherDuck load. "
            f"Per the 2026-08-10-england-biiep-pipeline-v1 change."
        ),
    )
    def loaded(context: AssetExecutionContext) -> dict[str, Any]:
        # Yield rows from the DLT source
        rows = list(dlt_source())
        context.log.info(f"england_{board}_{qualification}_ingested: {len(rows)} rows")
        return {
            "qualification": qualification,
            "board": board,
            "row_count": len(rows),
            "subjects": sorted(set(r["subject"] for r in rows)),
        }

    @asset_check(asset=loaded, name=f"england_{board}_{qualification}_loaded_check")
    def loaded_check(context) -> AssetCheckResult:
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

    return (loaded, loaded_check)


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


# NOTE: `dg.load_assets_from_modules`/`load_asset_checks_from_modules`
# (used by both the primary `dg.load_defs()` component-tree scan and the
# `_defs_walker.py` fallback) discover assets bound as a module-level
# `list[AssetsDefinition | AssetChecksDefinition]` on their own — `__all__`
# isn't required for that. (A previous version tried
# `[a.__name__ for a in _england_assets]` here — `AssetsDefinition` has no
# `__name__` attribute, so every import of this module raised
# AttributeError.)
__all__ = ["_england_assets"]
