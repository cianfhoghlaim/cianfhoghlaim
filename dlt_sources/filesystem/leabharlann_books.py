"""
Leabharlann books dlt source.

Scans every supported file in `leabharlann/{gaeilge,aigne}/` and yields one
row per file. Subject partition key: `gaeilge` | `aigne` | `epub` | `md`.

Resources (5):
1. `all_documents` — discovered files (merge on `file_hash`).
2. `pdf_documents` — PDF with pymupdf extraction.
3. `word_documents` — DOCX with python-docx extraction.
4. `epub_documents` — EPUB with `ebooklib` chapter extraction.
5. `book_chunks` — pre-chunked markdown text (one row per chunk), useful
   for downstream CocoIndex flows that don't want to re-chunk.

The `preview_path` column is populated by `oideachais/dlt_sources/leabharlann/previews.py`.

Reference: openspec/changes/leabharlann-cocoindex-v1/specs/leabharlann-ingestion/spec.md
"""

from __future__ import annotations
import dlt


import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

from ._epub_extractor import extract_epub_chapters
from ._scanner import (
    PathGrammar,
    extract_content,
    scan_directory,
)
from .previews import find_preview_for

logger = structlog.get_logger(__name__)


DEFAULT_LEABHARLANN_ROOT = Path(
    os.environ.get(
        "LEABHARLANN_ROOT",
        str(
            Path(__file__).resolve().parents[3]
            / "leabharlann"
        ),
    )
)

BOOK_SUBJECTS = ("gaeilge", "aigne", "epub", "md")


def _leabharlann_grammar(subject_root: Path) -> PathGrammar:
    """
    Build a PathGrammar for a leabharlann subject directory.
    """
    subject_paths: dict[str, Path] = {}
    if subject_root.exists():
        for child in subject_root.iterdir():
            if child.is_dir():
                subject_paths[child.name] = child
    return PathGrammar(
        subject_paths=subject_paths,
        course_code_pattern=None,
        handwriting_extensions=set(),
        handwriting_subdirs=set(),
    )


def _subject_partition_value(relative_path: str) -> str:
    """
    Derive the subject partition from a relative path.

    e.g. "gaeilge/foo.pdf" → "gaeilge", "aigne/bar.pdf" → "aigne".
    Fallback: "md" (for files directly under the root, if any).
    """
    parts = relative_path.split("/", 1)
    if parts and parts[0] in BOOK_SUBJECTS:
        return parts[0]
    suffix = os.path.splitext(parts[-1] if parts else "")[1].lower()
    if suffix == ".epub":
        return "epub"
    if suffix in {".md", ".markdown"}:
        return "md"
    return "md"


def _book_row(
    file_info: dict[str, Any],
    previews_dir: Path,
) -> dict[str, Any]:
    """
    Annotate a scanner row with the `preview_path` column.
    """
    file_path = Path(file_info["file_path"])
    preview = find_preview_for(file_path, previews_dir)
    file_info["preview_path"] = preview
    return file_info


def _epub_row(file_info: dict[str, Any]) -> dict[str, Any]:
    """
    Augment a row with EPUB chapter extraction. Only meaningful for .epub files.
    """
    if not file_info["file_path"].endswith(".epub"):
        return file_info
    result = extract_epub_chapters(Path(file_info["file_path"]))
    file_info["epub_chapters"] = result.get("epub_chapters", [])
    file_info["epub_total_chars"] = result.get("epub_total_chars", 0)
    file_info["epub_status"] = result.get("status", "error")
    file_info["epub_error"] = result.get("epub_error")
    return file_info


# ============================================================================
# DLT source
# ============================================================================


@dlt.source(name="leabharlann_books")
def leabharlann_books_source(
    base_path: str | Path = DEFAULT_LEABHARLANN_ROOT,
    max_files: int | None = None,
    include_extraction: bool = True,
):
    """
    DLT source for `leabharlann/{gaeilge,aigne}/`.

    Args:
        base_path: Root `leabharlann/` directory.
        max_files: Optional cap (testing).
        include_extraction: If True, extract text content (pymupdf / python-docx / ebooklib).
    """
    base_path = Path(base_path)
    account = "leabharlann"

    @dlt.resource(
        name="all_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
        columns={
            "account": {"partition": True},
            "subject": {"partition": True},
        },
    )
    def all_documents() -> Iterator[dict[str, Any]]:
        """All discovered leabharlann book files with metadata + preview."""
        for subject_dir_name in BOOK_SUBJECTS:
            subject_dir = base_path / subject_dir_name
            if not subject_dir.exists():
                continue
            grammar = _leabharlann_grammar(subject_dir)
            for row in scan_directory(
                base_path=subject_dir,
                grammar=grammar,
                account=account,
                max_files=max_files,
            ):
                row["subject"] = subject_dir_name
                row["preview_path"] = find_preview_for(
                    Path(row["file_path"]), subject_dir / "previews"
                )
                yield row

    @dlt.resource(
        name="pdf_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def pdf_documents() -> Iterator[dict[str, Any]]:
        """Leabharlann PDFs with text extraction."""
        for subject_dir_name in ("gaeilge", "aigne"):
            subject_dir = base_path / subject_dir_name
            if not subject_dir.exists():
                continue
            grammar = _leabharlann_grammar(subject_dir)
            for row in scan_directory(
                base_path=subject_dir,
                grammar=grammar,
                account=account,
                file_types=["pdf"],
                max_files=max_files,
            ):
                row["subject"] = subject_dir_name
                row["preview_path"] = find_preview_for(
                    Path(row["file_path"]), subject_dir / "previews"
                )
                if include_extraction:
                    row = extract_content(row, subject_dir, grammar)
                yield row

    @dlt.resource(
        name="word_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def word_documents() -> Iterator[dict[str, Any]]:
        """Leabharlann DOCX with text extraction."""
        for subject_dir_name in ("gaeilge", "aigne"):
            subject_dir = base_path / subject_dir_name
            if not subject_dir.exists():
                continue
            grammar = _leabharlann_grammar(subject_dir)
            for row in scan_directory(
                base_path=subject_dir,
                grammar=grammar,
                account=account,
                file_types=["word"],
                max_files=max_files,
            ):
                row["subject"] = subject_dir_name
                row["preview_path"] = find_preview_for(
                    Path(row["file_path"]), subject_dir / "previews"
                )
                if include_extraction:
                    row = extract_content(row, subject_dir, grammar)
                yield row

    @dlt.resource(
        name="epub_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def epub_documents() -> Iterator[dict[str, Any]]:
        """Leabharlann EPUBs with chapter extraction (graceful if ebooklib missing)."""
        # Scan recursively for any .epub file (location-independent).
        grammar = _leabharlann_grammar(base_path)
        for row in scan_directory(
            base_path=base_path,
            grammar=grammar,
            account=account,
            file_types=["epub"],
            max_files=max_files,
        ):
            row["subject"] = _subject_partition_value(row["relative_path"])
            row = _epub_row(row)
            yield row

    @dlt.resource(
        name="md_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def md_documents() -> Iterator[dict[str, Any]]:
        """Leabharlann MD/TXT files."""
        grammar = _leabharlann_grammar(base_path)
        for row in scan_directory(
            base_path=base_path,
            grammar=grammar,
            account=account,
            file_types=["text"],
            max_files=max_files,
        ):
            row["subject"] = _subject_partition_value(row["relative_path"])
            if include_extraction:
                row = extract_content(row, base_path, grammar)
            yield row

    return all_documents, pdf_documents, word_documents, epub_documents, md_documents


def create_leabharlann_books_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "leabharlann_books",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="leabharlann_books_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "DEFAULT_LEABHARLANN_ROOT",
    "BOOK_SUBJECTS",
    "leabharlann_books_source",
    "create_leabharlann_books_pipeline",
]
