"""
Bunchloch CROSS source: bunchloch_by_subject_source

Split from bunchloch/filesystem_source.py in Phase 3D.
"""

import hashlib
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import dlt
import structlog

from ._filesystem_source_helpers import (
    BUNCHLOCH_PATH,
    SUBJECT_PATHS,
    scan_directory,
)

def bunchloch_by_subject_source(
    subject: str,
    max_files: int | None = None,
):
    """
    DLT source for documents from a specific subject.

    Args:
        subject: Subject to process (comp_science, gaeilge, mata, oideachas)
        max_files: Optional maximum number of files

    Returns:
        DLT resource with subject-specific documents
    """
    if subject not in SUBJECT_PATHS:
        raise ValueError(f"Unknown subject: {subject}. Valid: {list(SUBJECT_PATHS.keys())}")

    @dlt.resource(
        name=f"{subject}_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def subject_documents() -> Iterator[dict[str, Any]]:
        """Documents from the specified subject."""
        yield from scan_directory(BUNCHLOCH_PATH, subject, None, max_files)

    return subject_documents
