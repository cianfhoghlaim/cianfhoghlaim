"""
Culture IE source: local_education_documents_source

Split from ireland/local_documents.py in Phase 3D.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt
from cianfhoghlaim.dlt.constants.local_sources import (
    BUNCHLOCH_PATH,
)

from ._local_documents_helpers import (
    _extract_content,
    _scan_directory,
)


def local_education_documents_source(
    base_path: str | Path = BUNCHLOCH_PATH,
    subject: str | None = None,
    file_types: list[str] | None = None,
    max_files: int | None = None,
    include_extraction: bool = False,
):
    """
    DLT source for local educational documents.

    Args:
        base_path: Base directory to scan (defaults to bunchloch)
        subject: Optional subject filter (comp_science, gaeilge, mata, oideachas)
        file_types: Optional list of file types (pdf, word, image, code, text)
        max_files: Optional maximum number of files to process
        include_extraction: Whether to extract text content

    Returns:
        DLT source with document resources
    """
    base_path = Path(base_path)

    @dlt.resource(
        name="local_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def local_documents() -> Iterator[dict[str, Any]]:
        """All discovered local documents with metadata."""
        yield from _scan_directory(base_path, subject, file_types, max_files)

    @dlt.resource(
        name="pdf_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def pdf_documents() -> Iterator[dict[str, Any]]:
        """PDF documents only."""
        for doc in _scan_directory(base_path, subject, ["pdf"], max_files):
            if include_extraction:
                doc = _extract_content(doc)
            yield doc

    @dlt.resource(
        name="word_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def word_documents() -> Iterator[dict[str, Any]]:
        """Word documents only."""
        for doc in _scan_directory(base_path, subject, ["word"], max_files):
            if include_extraction:
                doc = _extract_content(doc)
            yield doc

    @dlt.resource(
        name="code_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def code_documents() -> Iterator[dict[str, Any]]:
        """Code files only (Python, notebooks, etc.)."""
        for doc in _scan_directory(base_path, subject, ["code"], max_files):
            if include_extraction:
                doc = _extract_content(doc)
            yield doc

    @dlt.resource(
        name="image_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def image_documents() -> Iterator[dict[str, Any]]:
        """Image files only (requires OCR for text extraction)."""
        yield from _scan_directory(base_path, subject, ["image"], max_files)

    return local_documents, pdf_documents, word_documents, code_documents, image_documents
