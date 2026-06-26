"""
Culture IE source: local_documents_by_subject_source

Split from ireland/local_documents.py in Phase 3D.
"""

import hashlib
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import dlt
import structlog
from dlt_sources.constants.local_sources import BUNCHLOCH_PATH, EXTRACTION_CONFIG, FILE_TYPE_EXTENSIONS, LOCAL_SUBJECT_PATHS, detect_language, get_document_metadata, get_file_type, should_process_file

from ._local_documents_helpers import (
    _extract_content,
    _scan_directory,
)

def local_documents_by_subject_source(
    subject: str,
    include_extraction: bool = True,
    max_files: int | None = None,
):
    """
    DLT source for documents from a specific subject.

    Args:
        subject: Subject to process (comp_science, gaeilge, mata, oideachas)
        include_extraction: Whether to extract text content
        max_files: Optional maximum number of files

    Returns:
        DLT source with subject-specific documents
    """
    if subject not in LOCAL_SUBJECT_PATHS:
        raise ValueError(f"Unknown subject: {subject}. Valid: {list(LOCAL_SUBJECT_PATHS.keys())}")

    @dlt.resource(
        name=f"{subject}_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def subject_documents() -> Iterator[dict[str, Any]]:
        """Documents from the specified subject."""
        for doc in _scan_directory(BUNCHLOCH_PATH, subject, None, max_files):
            if include_extraction:
                doc = _extract_content(doc)
            yield doc

    return subject_documents
