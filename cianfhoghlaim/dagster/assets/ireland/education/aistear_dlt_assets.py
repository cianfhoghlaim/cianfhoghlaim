"""Aistear (Early Childhood) DLT-backed assets.

For each of the Aistear (early childhood) framework PDFs in the
cache, this module runs the DLT `aistear_curriculum` source and
materialises 3 resource tables (documents, principles, learning
goals) into DuckLake (Garage S3 + Lakekeeper Postgres catalog).

Follows the same pattern as `assets/leaving_cert/dlt_assets.py`:
plain `@asset` + `dlt.pipeline(...)` + `safe_dlt_run(pipeline, source)`.

When the BAML client (`baml_client`) is not yet generated, the
documents table is still materialised (with placeholder fields);
the principles and learning_goals tables are skipped gracefully.
"""
import os
from typing import Any

from dagster import AssetCheckResult, MaterializeResult, asset, asset_check, define_asset_job

from cianfhoghlaim.dlt.british_isles.ireland.education.aistear import aistear_curriculum
from cianfhoghlaim.dlt.destinations import get_dlt_destination
from cianfhoghlaim.dlt.safety import safe_dlt_run


AISTEAR_PIPELINE_NAME = "aistear_curriculum"
AISTEAR_DATASET_NAME = "aistear_curriculum"


@asset(
    name="aistear_documents_ducklake",
    group_name="aistear_dlt",
    compute_kind="dlt",
    description=(
        "DLT ingestion of cached Aistear (early childhood) framework PDFs into "
        "DuckLake. Reads from `/stedding/ingest_queue/aistear/` and writes 1 row "
        "per PDF to the `aistear_documents` table in the `aistear_curriculum` "
        "dataset. Invokes the BAML `ExtractAistearFramework` function to extract "
        "the 4 themes, 12 principles, and all learning goals; when the BAML "
        "client is not yet generated, the row is yielded with placeholder fields."
    ),
)
def aistear_documents_ducklake(context) -> MaterializeResult:
    os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")
    os.environ.setdefault("USE_LOCAL_SCRAPES", "true")
    os.environ.setdefault("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")

    destination = get_dlt_destination()
    pipeline = __import__("dlt").pipeline(
        pipeline_name=AISTEAR_PIPELINE_NAME,
        destination=destination,
        dataset_name=AISTEAR_DATASET_NAME,
        dev_mode=False,
    )

    source = aistear_curriculum()
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
            for candidate in (
                "aistear_documents",
                "aistear_principles",
                "aistear_learning_goals",
                "naionra_listings",
            ):
                if candidate in fp:
                    table = candidate
                    break
            rows_loaded[table] = rows_loaded.get(table, 0) + count

    total = sum(rows_loaded.values())
    context.log.info(f"aistear loaded {total} rows into DuckLake: {rows_loaded}")

    return MaterializeResult(
        metadata={
            "pipeline_name": AISTEAR_PIPELINE_NAME,
            "dataset_name": AISTEAR_DATASET_NAME,
            "rows_loaded_total": total,
            **{f"rows_{k}": v for k, v in rows_loaded.items()},
            "use_local_scrapes": os.environ.get("USE_LOCAL_SCRAPES", "true"),
            "load_ids": str(load_info.loads_ids[0]) if load_info.loads_ids else "",
        }
    )


@asset_check(asset=aistear_documents_ducklake)
def aistear_documents_row_count_check(context) -> AssetCheckResult:
    """Assert at least 1 aistear document was loaded (cache is non-empty)."""
    rows_total = (context.materialize_result.metadata or {}).get("rows_loaded_total")
    passed = isinstance(rows_total, (int, float)) and rows_total > 0
    return AssetCheckResult(
        passed=passed,
        metadata={"rows_loaded_total": rows_total or 0},
    )


AISTEAR_ASSETS = [aistear_documents_ducklake]
AISTEAR_CHECKS = [aistear_documents_row_count_check]

AISTEAR_FULL_JOB = define_asset_job(
    name="aistear_full",
    selection=__import__("dagster").AssetSelection.groups("aistear_dlt"),
    description=(
        "Aistear (early childhood) curriculum DLT ingestion into DuckLake. "
        "Runs the aistear_documents_ducklake asset which materialises "
        "aistear_documents, aistear_principles, aistear_learning_goals, "
        "and naionra_listings into the aistear_curriculum dataset."
    ),
)


__all__ = [
    "aistear_documents_ducklake",
    "aistear_documents_row_count_check",
    "AISTEAR_ASSETS",
    "AISTEAR_CHECKS",
    "AISTEAR_FULL_JOB",
]
