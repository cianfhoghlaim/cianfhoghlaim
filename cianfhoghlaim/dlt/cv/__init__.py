"""CV / Author PDF Ingestion Pipeline.

Filesystem-source pipeline that reads scanned PDFs from the
author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/ directory and
extracts text via pdfplumber for downstream BAML extraction.

Usage:
    import dlt
    from pipelines.cv import cv_pdf_text_resource, run_cv_pipeline

    pipeline = dlt.pipeline(
        pipeline_name="cv_pdf_croilar",
        destination="duckdb",
        dataset_name="cv_data",
    )
    load_info = pipeline.run([cv_pdf_text_resource()])
"""

from pipelines.cv.source import (
    AUTHOR_DIR,
    REPO_ROOT,
    author_pdf_resource,
    cv_pdf_text_resource,
    find_author_pdfs,
    run_cv_pipeline,
)

__all__ = [
    "AUTHOR_DIR",
    "REPO_ROOT",
    "author_pdf_resource",
    "cv_pdf_text_resource",
    "find_author_pdfs",
    "run_cv_pipeline",
]
