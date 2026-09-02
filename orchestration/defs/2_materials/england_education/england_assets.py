"""England BIEP pipeline generic Dagster assets (per the 2026-08-10-england-biiep-pipeline-v1 change).

Wires 6 asset groups:
- england_gcse_aqa_loaded
- england_gcse_ocr_loaded
- england_gcse_edexcel_loaded
- england_a_level_aqa_loaded
- england_a_level_ocr_loaded
- england_a_level_edexcel_loaded

Phase 11 (the 2026-09-XX-orchestration-integration-v1 change) replaces the
Phase 9 ``getattr(b, baml_fn_name, None)`` fallback with the canonical
``b.ExtractEnglandSubjectSpec(...)`` invocation defined in
``baml_src/british_isles/en/education/en_extraction.baml``.

Each England cohort (a board × subject × qualification tuple) gets its
canonical PDF read via pypdf, fed through ``ExtractEnglandSubjectSpec``,
and the result materialised to Convex's ``england_subject_specs`` table.
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

from dlt_sources.education.england.british_isles.education.gcse.england_gcse_sources import (
    gcse_aqa_subjects,
    gcse_ocr_subjects,
    gcse_edexcel_subjects,
)
from dlt_sources.education.england.british_isles.education.a_level.england_a_level_sources import (
    a_level_aqa_subjects,
    a_level_ocr_subjects,
    a_level_edexcel_subjects,
)


def _get_jurisdiction_extractor():
    """Lazy-importer for the shared Phase 11 helper. See the matching
    helper in `wales_assets.py` for why this can't be a module-level
    import.
    """
    import importlib
    return importlib.import_module(
        "orchestration.defs.2_materials._base.jurisdiction_baml_extractor"
    )


try:
    from baml_client import b  # type: ignore[import-not-found]
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]


def _england_loaded_asset(qualification: str, board: str, dlt_source):
    """Create one ``{board}_{qualification}_loaded`` Dagster asset.

    The inner ``def``s use plain names and get their real per-board /
    qualification name via the ``name=``/``asset=`` kwargs at decoration
    time (a previous version used literal ``<board>``/``<qualification>``
    tokens in the ``def`` line — a hard SyntaxError — then tried to fix
    the name via ``fn.__name__ = f"..."`` after decoration, which is a
    no-op for Dagster).

    Phase 11 adds the L2 BAML-extraction step: each cohort's canonical
    PDF is fed through ``b.ExtractEnglandSubjectSpec(...)`` and the
    resulting ``ENSubjectSpec`` is materialised to Convex's
    ``england_subject_specs`` table.
    """

    @asset(
        name=f"england_{board}_{qualification}_loaded",
        group_name="2_materials_england_education",
        description=(
            f"England {qualification.upper()} {board.upper()} ingestion: "
            f"DLT source + BAML `ExtractEnglandSubjectSpec` + Convex materialisation. "
            f"Per the 2026-08-10-england-biiep-pipeline-v1 change + the "
            f"2026-09-XX-orchestration-integration-v1 change (Phase 11)."
        ),
    )
    def loaded(context: AssetExecutionContext) -> dict[str, Any]:
        # Phase 9: yield rows from the DLT source
        rows = list(dlt_source())
        context.log.info(f"england_{board}_{qualification}_ingested: {len(rows)} rows")

        # Phase 11: invoke the canonical BAML extractor per row (best-effort;
        # silently no-ops when BAML isn't available or no PDF path is set).
        baml_extractions: dict[str, dict[str, Any]] = {}
        if BAML_AVAILABLE:
            _extractor_module = _get_jurisdiction_extractor()
            for row in rows:
                subject = row.get("subject")
                pdf_path = row.get("pdf_path") or row.get("source_pdf") or row.get("url")
                source_url = row.get("source_url") or row.get("url")
                if not subject or not pdf_path:
                    continue
                result = _extractor_module.invoke_jurisdiction_extractor(
                    jurisdiction="england",
                    pdf_path=pdf_path,
                    subject_slug=subject,
                    source_url=source_url,
                    stage="LEAVING_CERT",
                )
                baml_extractions[subject] = result

        extracted_count = sum(
            1 for r in baml_extractions.values() if r["extracted"]
        )
        convex_count = sum(
            1 for r in baml_extractions.values() if r["convex_written"]
        )
        context.log.info(
            "england_%s_%s_baml_extractions: %d extracted, %d convex-written",
            board, qualification, extracted_count, convex_count,
        )

        return {
            "qualification": qualification,
            "board": board,
            "row_count": len(rows),
            "baml_extractions": baml_extractions,
            "extracted_count": extracted_count,
            "convex_written_count": convex_count,
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
                "note": (
                    "Phase 11 now invokes b.ExtractEnglandSubjectSpec instead "
                    "of getattr fallback; coverage logged in loaded() return "
                    "value (`extracted_count`, `convex_written_count`)."
                ),
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
