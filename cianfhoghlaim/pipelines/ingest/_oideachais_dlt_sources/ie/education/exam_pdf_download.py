"""
Education IE source: exam_pdf_download_source

Split from ireland/pdf_downloader.py in Phase 3D.
"""

from pathlib import Path

from ._pdf_downloader_helpers import (
    EXAM_DOWNLOAD_DIR,
    MAX_FILE_SIZE_MB,
    RATE_LIMIT_DELAY,
    exam_pdf_downloads,
)


def exam_pdf_download_source(
    duckdb_path: str,
    download_dir: Path | str = EXAM_DOWNLOAD_DIR,
    level: str | None = None,
    subject: str | None = None,
    max_files: int = 500,
    max_size_mb: int = MAX_FILE_SIZE_MB,
    rate_limit_delay: float = RATE_LIMIT_DELAY,
):
    """
    DLT source for downloading exam material PDFs.

    Usage:
        pipeline = dlt.pipeline(...)
        pipeline.run(exam_pdf_download_source(
            duckdb_path="./curriculum_unified.duckdb",
            download_dir="./downloads/examinations",
            level="leaving_certificate",
        ))
    """
    yield exam_pdf_downloads(
        duckdb_path=duckdb_path,
        download_dir=download_dir,
        level=level,
        subject=subject,
        max_files=max_files,
        max_size_mb=max_size_mb,
        rate_limit_delay=rate_limit_delay,
    )
