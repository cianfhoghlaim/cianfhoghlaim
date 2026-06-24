"""Wire 12 previously-unwired dlt sources as Dagster assets.

The 12 dlt sources in this module were defined but had no
corresponding Dagster asset wrapper, so they never materialised
into DuckLake. This module adds 12 plain `@asset` wrappers
following the `leaving_cert/dlt_assets.py` pattern.

UK (4):
- england_gias (GIAS — Get Information About Schools)
- scotland_insight (Insight National Benchmarking)
- scotland_simd (Scottish Index of Multiple Deprivation)
- wales_estyn (Estyn inspection reports)

Crown Dependencies (2):
- jersey_education (gov.je/Education/*)
- guernsey_education (gov.gg/education*)

Ireland (6):
- ireland_primary_dlt (12 NCCA primary curriculum specifications)
- ireland_junior_cycle_dlt (18 JC subjects + 16 short courses)
- ireland_tertiary_dlt (CAO + NUI/HEI + QQI-FET + Apprenticeships)
- ireland_local_documents_dlt (bunchloch local educational documents)
- ireland_parallel_corpus_dlt (Gaois/Tearma/Logainm/Duchas)

Reference: openspec/changes/wire-unwired-dlt-sources/
"""
import os
from typing import Any

from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    MaterializeResult,
    asset,
    asset_check,
)

from oideachais.dlt_utils.destinations import get_dlt_destination
from oideachais.dlt_utils.safety import safe_dlt_run


def _dlt_pipeline_name(name: str) -> str:
    return f"unwired_{name}"


def _dlt_dataset_name(name: str) -> str:
    return f"oideachais_unwired_{name}"


def _make_dlt_asset(asset_name: str, source_factory, group_name: str = "unwired_dlt"):
    """Factory for the 12 simple @asset wrappers.

    Each wrapper follows the same pattern:
    1. Build a dlt pipeline
    2. Run the source via safe_dlt_run
    3. Return MaterializeResult with row counts
    """

    @asset(
        name=asset_name,
        group_name=group_name,
        compute_kind="dlt",
        description=(
            f"DLT ingestion via the dlt source factory. See "
            f"openspec/changes/wire-unwired-dlt-sources/ for the wiring rationale."
        ),
    )
    def wrapper(context: AssetExecutionContext) -> MaterializeResult:
        os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")
        os.environ.setdefault("USE_LOCAL_SCRAPES", "true")

        destination = get_dlt_destination()
        pipeline = __import__("dlt").pipeline(
            pipeline_name=_dlt_pipeline_name(asset_name),
            destination=destination,
            dataset_name=_dlt_dataset_name(asset_name),
            dev_mode=False,
        )

        source = source_factory()
        load_info = safe_dlt_run(pipeline, source)

        rows_loaded: dict[str, int] = {}
        for pkg in load_info.load_packages:
            jobs_dict = getattr(pkg, "jobs", None)
            if not isinstance(jobs_dict, dict):
                continue
            for job in jobs_dict.get("completed_jobs", []) or []:
                count = getattr(job, "count", 0) or 0
                fp = getattr(job, "file_path", "") or ""
                table = "unknown"
                for candidate in ("page", "document", "record", "row", "entry", "result"):
                    if candidate in fp.lower():
                        table = candidate
                        break
                rows_loaded[table] = rows_loaded.get(table, 0) + count

        total = sum(rows_loaded.values())
        context.log.info(f"{asset_name} loaded {total} rows into DuckLake: {rows_loaded}")

        return MaterializeResult(
            metadata={
                "asset_name": asset_name,
                "pipeline_name": _dlt_pipeline_name(asset_name),
                "dataset_name": _dlt_dataset_name(asset_name),
                "rows_loaded_total": total,
                **{f"rows_{k}": v for k, v in rows_loaded.items()},
                "use_local_scrapes": os.environ.get("USE_LOCAL_SCRAPES", "true"),
            }
        )

    @asset_check(asset=wrapper)
    def row_count_check(context) -> AssetCheckResult:
        rows_total = (context.materialize_result.metadata or {}).get("rows_loaded_total") or 0
        return AssetCheckResult(
            passed=isinstance(rows_total, (int, float)) and rows_total >= 0,
            metadata={"rows_loaded_total": rows_total},
        )

    return wrapper, row_count_check


# ============================================================================
# UK assets (4)
# ============================================================================


def _gias_source_factory():
    from oideachais.dlt_sources.uk.england.school_info import gias_source
    return gias_source


def _insight_source_factory():
    from oideachais.dlt_sources.uk.scotland.insight_benchmarking import insight_source
    return insight_source


def _simd_source_factory():
    from oideachais.dlt_sources.uk.scotland.simd import simd_source
    return simd_source


def _estyn_source_factory():
    from oideachais.dlt_sources.uk.wales.estyn import estyn_source
    return estyn_source


england_gias, england_gias_check = _make_dlt_asset(
    "england_gias", _gias_source_factory, group_name="uk_education"
)
scotland_insight, scotland_insight_check = _make_dlt_asset(
    "scotland_insight", _insight_source_factory, group_name="uk_education"
)
scotland_simd, scotland_simd_check = _make_dlt_asset(
    "scotland_simd", _simd_source_factory, group_name="uk_education"
)
wales_estyn, wales_estyn_check = _make_dlt_asset(
    "wales_estyn", _estyn_source_factory, group_name="uk_education"
)


# ============================================================================
# Crown Dependencies assets (2)
# ============================================================================


def _jersey_source_factory():
    from oideachais.dlt_sources.crown_dependencies.channel_islands import jersey_source
    return jersey_source


def _guernsey_source_factory():
    from oideachais.dlt_sources.crown_dependencies.channel_islands import guernsey_source
    return guernsey_source


jersey_education, jersey_education_check = _make_dlt_asset(
    "jersey_education", _jersey_source_factory, group_name="crown_dependencies_education"
)
guernsey_education, guernsey_education_check = _make_dlt_asset(
    "guernsey_education", _guernsey_source_factory, group_name="crown_dependencies_education"
)


# ============================================================================
# Ireland assets (6)
# ============================================================================


def _ireland_primary_source_factory():
    from oideachais.dlt_sources.ireland.primary import ireland_primary_source
    return ireland_primary_source


def _ireland_junior_cycle_source_factory():
    from oideachais.dlt_sources.ireland.junior_cycle import ireland_junior_cycle_source
    return ireland_junior_cycle_source


def _ireland_tertiary_source_factory():
    from oideachais.dlt_sources.ireland.tertiary import tertiary_courses
    return tertiary_courses


def _ireland_local_documents_source_factory():
    from oideachais.dlt_sources.ireland.local_documents import local_education_documents_source
    return local_education_documents_source


def _ireland_parallel_corpus_source_factory():
    from oideachais.dlt_sources.ireland.parallel_corpus import parallel_corpus_source
    return parallel_corpus_source


ireland_primary_dlt, ireland_primary_dlt_check = _make_dlt_asset(
    "ireland_primary_dlt", _ireland_primary_source_factory, group_name="ie_education"
)
ireland_junior_cycle_dlt, ireland_junior_cycle_dlt_check = _make_dlt_asset(
    "ireland_junior_cycle_dlt", _ireland_junior_cycle_source_factory, group_name="ie_education"
)
ireland_tertiary_dlt, ireland_tertiary_dlt_check = _make_dlt_asset(
    "ireland_tertiary_dlt", _ireland_tertiary_source_factory, group_name="ie_education"
)
ireland_local_documents_dlt, ireland_local_documents_dlt_check = _make_dlt_asset(
    "ireland_local_documents_dlt", _ireland_local_documents_source_factory, group_name="ie_education"
)
ireland_parallel_corpus_dlt, ireland_parallel_corpus_dlt_check = _make_dlt_asset(
    "ireland_parallel_corpus_dlt", _ireland_parallel_corpus_source_factory, group_name="ie_education"
)


# ============================================================================
# Exports
# ============================================================================


WIRE_UNWIRED_DLT_ASSETS: list[Any] = [
    # UK (4)
    england_gias,
    scotland_insight,
    scotland_simd,
    wales_estyn,
    # Crown Dependencies (2)
    jersey_education,
    guernsey_education,
    # Ireland (6)
    ireland_primary_dlt,
    ireland_junior_cycle_dlt,
    ireland_tertiary_dlt,
    ireland_local_documents_dlt,
    ireland_parallel_corpus_dlt,
]


WIRE_UNWIRED_DLT_CHECKS: list[Any] = [
    # UK (4)
    england_gias_check,
    scotland_insight_check,
    scotland_simd_check,
    wales_estyn_check,
    # Crown Dependencies (2)
    jersey_education_check,
    guernsey_education_check,
    # Ireland (6)
    ireland_primary_dlt_check,
    ireland_junior_cycle_dlt_check,
    ireland_tertiary_dlt_check,
    ireland_local_documents_dlt_check,
    ireland_parallel_corpus_dlt_check,
]


__all__ = [
    "WIRE_UNWIRED_DLT_ASSETS",
    "WIRE_UNWIRED_DLT_CHECKS",
    # UK
    "england_gias",
    "scotland_insight",
    "scotland_simd",
    "wales_estyn",
    # Crown Dependencies
    "jersey_education",
    "guernsey_education",
    # Ireland
    "ireland_primary_dlt",
    "ireland_junior_cycle_dlt",
    "ireland_tertiary_dlt",
    "ireland_local_documents_dlt",
    "ireland_parallel_corpus_dlt",
]
