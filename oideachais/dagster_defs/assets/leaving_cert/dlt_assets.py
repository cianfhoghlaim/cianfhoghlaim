"""Leaving Certificate 2026 — DLT-backed assets.

For each of the 7 priority subjects, this module registers a `@asset` that
runs the DLT `leaving_cert_source` and materialises the four resource
tables (syllabus, past_papers, marking_schemes, examiner_reports) into
DuckLake (Garage S3 + Lakekeeper Postgres catalog).

The DLT source lives in `oideachais.dlt_sources.ireland.leaving_cert`
and reads cached PDFs from `stedding/ingest_queue/`.

This follows the pattern used by `ireland/curriculum_dlt_assets.py`:
plain `@asset` + `dlt.pipeline(...)` + `safe_dlt_run(pipeline, source)`.
The `dagster_dlt.dlt_assets` decorator has more constraints (no
`compute_kind` kwarg, requires `@dlt_assets(name=...)` to be applied at
the AssetsDefinition level, not the function body), so the plain
`@asset` pattern is simpler and more idiomatic for this codebase.
"""
from __future__ import annotations

import os
from typing import Any

from dagster import AssetSelection, MaterializeResult, define_asset_job, asset

from oideachais.dlt_sources.ireland.leaving_cert import (
    SUBJECTS,
    leaving_cert_source,
)
from oideachais.dlt_utils.destinations import get_dlt_destination
from oideachais.dlt_utils.safety import safe_dlt_run


def _dlt_pipeline_name(subject: str) -> str:
    return f"leaving_cert_{subject.replace('-', '_')}"


def _dlt_dataset_name(subject: str) -> str:
    """DuckLake dataset for the LC tables, **per subject** to avoid
    concurrent transaction conflicts on the shared `leaving_cert` dataset.

    Each subject gets its own `leaving_cert_{subject_slug}` dataset in
    DuckLake. The API and the asset readers filter by `subject` column
    in the joined view, so the per-subject split is transparent to
    consumers.
    """
    return f"leaving_cert_{subject.replace('-', '_')}"


def make_subject_assets(subject: str) -> list:
    """Build the asset for one subject. Returns a list of one asset.

    Each asset runs the DLT source through a per-subject dlt pipeline
    (named `leaving_cert_{subject_slug}`) and materialises 4 resource
    tables into the per-subject `leaving_cert_{subject_slug}` dataset.
    The source is filtered by `subjects=[subject]` so the dataset
    only contains rows for this subject.
    """

    @asset(
        name=f"leaving_cert_{subject.replace('-', '_')}_ducklake",
        group_name="leaving_cert_dlt",
        compute_kind="dlt",
        description=(
            f"DLT ingestion of cached Leaving Cert PDFs for {subject} into "
            "DuckLake (Garage S3 + Lakekeeper Postgres catalog). Reads from "
            "`stedding/ingest_queue/{examinations,ncca,curriculumonline}.ie/` "
            f"and writes 4 tables to the `leaving_cert_{subject.replace('-', '_')}` "
            f"dataset (per-subject to avoid concurrent DuckLake transaction "
            f"conflicts when 7 subjects pipeline in parallel)."
        ),
    )
    def leaving_cert_ducklake(context) -> MaterializeResult:
        os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")
        os.environ.setdefault("USE_LOCAL_SCRAPES", "true")
        os.environ.setdefault("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")

        destination = get_dlt_destination()
        pipeline = __import__("dlt").pipeline(
            pipeline_name=_dlt_pipeline_name(subject),
            destination=destination,
            dataset_name=_dlt_dataset_name(subject),
            dev_mode=False,
        )
        # Filter the DLT source by this asset's subject so the
        # `leaving_cert_{subject}` dataset only contains rows for this subject.
        source = leaving_cert_source(use_local_scrapes=True, subjects=[subject])
        load_info = safe_dlt_run(pipeline, source)

        # Calculate rows loaded per resource. The DLT load_info structure is:
        # load_info.load_packages -> [LoadPackageInfo]
        #   LoadPackageInfo.jobs -> {"completed_jobs": [LoadJobInfo], ...}
        #     LoadJobInfo.count (rows), .file_path (e.g. "syllabus.abc.0.parquet")
        rows_loaded: dict[str, int] = {}
        for pkg in load_info.load_packages:
            jobs_dict = getattr(pkg, "jobs", None)
            if not isinstance(jobs_dict, dict):
                continue
            for job in jobs_dict.get("completed_jobs", []) or []:
                count = getattr(job, "count", 0) or 0
                # Extract table name from file_path (e.g. "syllabus.abc.0.parquet")
                fp = getattr(job, "file_path", "") or ""
                table = "unknown"
                for candidate in ("syllabus", "past_papers", "marking_schemes", "examiner_reports"):
                    if candidate in fp:
                        table = candidate
                        break
                rows_loaded[table] = rows_loaded.get(table, 0) + count

        total = sum(rows_loaded.values())
        context.log.info(
            f"leaving_cert[{subject}] loaded {total} rows into DuckLake: {rows_loaded}"
        )

        return MaterializeResult(
            metadata={
                "subject": subject,
                "pipeline_name": _dlt_pipeline_name(subject),
                "dataset_name": _dlt_dataset_name(subject),
                "rows_loaded_total": total,
                **{f"rows_{k}": v for k, v in rows_loaded.items()},
                "use_local_scrapes": os.environ.get("USE_LOCAL_SCRAPES", "true"),
                "load_ids": str(load_info.loads_ids[0]) if load_info.loads_ids else "",
            }
        )

    return [leaving_cert_ducklake]


# Build the 7 subject assets.
LEAVING_CERT_DLT_ASSETS: list[Any] = []
for subject in SUBJECTS:
    LEAVING_CERT_DLT_ASSETS.extend(make_subject_assets(subject))


# Dagster job that materialises all 7 subject DLT assets in parallel.
# This is the canonical "run me in CI / on a cron" entry point for the
# DLT ingestion layer. The downstream 70 stub @assets (BAML / LLM /
# MotherDuck stages) are NOT included — those are the LEAVING_CERT_ASSETS
# in __init__.py and run in their own per-subject jobs.
LEAVING_CERT_DLT_JOB = define_asset_job(
    name="leaving_cert_dlt_full",
    selection=AssetSelection.groups("leaving_cert_dlt"),
    description=(
        "DLT ingestion of cached Leaving Cert PDFs for all 7 priority "
        "subjects into DuckLake. Runs the 7 leaving_cert_{subject}_ducklake "
        "assets in parallel. Each runs the DLT leaving_cert_source and "
        "materialises 4 resource tables (syllabus, past_papers, "
        "marking_schemes, examiner_reports) into the leaving_cert dataset."
    ),
)
