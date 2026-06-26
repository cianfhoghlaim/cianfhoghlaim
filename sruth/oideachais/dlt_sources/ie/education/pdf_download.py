"""
Education IE source: pdf_download_source

Split from ireland/pdf_downloader.py in Phase 3D.
"""

import hashlib
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import dlt
import httpx
import structlog

from ._pdf_downloader_helpers import (
    DEFAULT_DOWNLOAD_DIR,
    MAX_FILE_SIZE_MB,
    RATE_LIMIT_DELAY,
    pdf_downloads,
)

def pdf_download_source(
    duckdb_path: str,
    download_dir: Path | str = DEFAULT_DOWNLOAD_DIR,
    cycle: str | None = None,
    subject: str | None = None,
    max_files: int = 100,
    max_size_mb: int = MAX_FILE_SIZE_MB,
    rate_limit_delay: float = RATE_LIMIT_DELAY,
):
    """
    DLT source for downloading curriculum PDFs.

    Resources:
    - pdf_downloads: All download records (success and failure)
    - pdf_download_errors: Failed downloads for retry

    Usage:
        pipeline = dlt.pipeline(...)
        pipeline.run(pdf_download_source(
            duckdb_path="./curriculum_unified.duckdb",
            download_dir="./downloads/pdfs",
            cycle="senior_cycle",
            subject="mathematics",
        ))
    """
    yield pdf_downloads(
        duckdb_path=duckdb_path,
        download_dir=download_dir,
        cycle=cycle,
        subject=subject,
        max_files=max_files,
        max_size_mb=max_size_mb,
        rate_limit_delay=rate_limit_delay,
    )
