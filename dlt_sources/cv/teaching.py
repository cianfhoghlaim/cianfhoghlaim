"""Teaching Placement DLT Pipeline.

Filesystem-source pipeline that reads teaching PDFs from the
author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/teaching/ directory.

Extracts placement reports, student feedback, and curriculum materials
for downstream BAML extraction.

Usage:
    import dlt_sources
    from pipelines.teaching import teaching_pdf_source

    pipeline = dlt.pipeline(
        pipeline_name="teaching_croilar",
        destination="duckdb",
        dataset_name="teaching_data",
    )
    load_info = pipeline.run(teaching_pdf_source())
"""

import os
from pathlib import Path
from typing import Any

import dlt_sources
from dlt_sources.common.paths import get_author_dir
from dlt_sources.cv.cv import cv_pdf_text_resource

AUTHOR_DIR = get_author_dir()
REPO_ROOT = AUTHOR_DIR.parent


def run_teaching_pipeline(
    destination: str | Any | None = None,
    dataset_name: str = "teaching_data",
) -> Any:
    """Run the teaching PDF ingestion pipeline.

    Reads PDFs from the author directory's teaching/ subdirectory
    and stores extracted text in DuckDB for BAML extraction.

    Args:
        destination: DLT destination
        dataset_name: Dataset name in the destination

    Returns:
        LoadInfo from the pipeline run
    """
    if destination is None:
        from dlt_utils import get_dlt_destination
        destination = get_dlt_destination()

    pipeline = dlt.pipeline(
        pipeline_name="teaching_croilar",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    teaching_dir = AUTHOR_DIR / "teaching"
    if not teaching_dir.exists():
        raise FileNotFoundError(f"Teaching directory not found: {teaching_dir}")

    return pipeline.run([
        cv_pdf_text_resource(base_dir=str(teaching_dir)),
    ])
