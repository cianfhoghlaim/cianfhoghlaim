"""
Bunchloch CROSS source: bunchloch_source

Split from bunchloch/filesystem_source.py in Phase 3D.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt

from ._filesystem_source_helpers import (
    BUNCHLOCH_PATH,
    scan_directory,
)


def bunchloch_source(
    base_path: str | Path = BUNCHLOCH_PATH,
    subject: str | None = None,
    max_files: int | None = None,
):
    """
    DLT source for bunchloch research documents.

    Args:
        base_path: Base directory (default: taighde/bunchloch)
        subject: Optional subject filter (comp_science, gaeilge, mata, oideachas)
        max_files: Optional limit on files to process

    Returns:
        DLT resources for each document type
    """
    base_path = Path(base_path)

    @dlt.resource(
        name="documents",
        write_disposition="merge",
        primary_key=["file_hash"],
        columns={
            "subject": {"partition": True},  # Partition by subject for DuckLake
        },
    )
    def all_documents() -> Iterator[dict[str, Any]]:
        """All discovered documents with metadata."""
        yield from scan_directory(base_path, subject, None, max_files)

    @dlt.resource(
        name="pdf_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def pdf_documents() -> Iterator[dict[str, Any]]:
        """PDF documents only (843 files)."""
        yield from scan_directory(base_path, subject, ["pdf"], max_files)

    @dlt.resource(
        name="word_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def word_documents() -> Iterator[dict[str, Any]]:
        """Word documents only (407 files)."""
        yield from scan_directory(base_path, subject, ["word"], max_files)

    @dlt.resource(
        name="code_files",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def code_files() -> Iterator[dict[str, Any]]:
        """Code files only (42 Java files)."""
        yield from scan_directory(base_path, subject, ["code"], max_files)

    @dlt.resource(
        name="presentations",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def presentations() -> Iterator[dict[str, Any]]:
        """Presentation files (Keynote, PowerPoint)."""
        yield from scan_directory(base_path, subject, ["presentation"], max_files)

    return all_documents, pdf_documents, word_documents, code_files, presentations
