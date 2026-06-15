"""
University of Galway filesystem DLT source.

Ingests every supported file in
`author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/university_of_galway/`
into the `author_archive_uog_documents` DuckLake table.

Yields 6 resources:
1. `all_documents` — discovered files (merge on `file_hash`).
2. `pdf_documents` — PDF only, with pymupdf extraction.
3. `word_documents` — DOCX only, with python-docx extraction.
4. `code_documents` — Python / notebook / JS / TS / Java (for the
   `software_development/` subdir).
5. `handwritten_pages` — files that need OCR (`.pages`, `.heic`, scanned PDF,
   or anything in `mata/` or `past/`).
6. `extraction_metadata` — memoised BAML extraction rows (one per `file_hash`).

Reference: openspec/changes/author-archive-gemini-and-uos-ingestion/specs/author-archive-filesystem/spec.md
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt
import structlog

from ._scanner import (
    PathGrammar,
    compute_file_hash,
    extract_content,
    get_document_metadata,
    scan_directory,
)

logger = structlog.get_logger(__name__)

# Default location of the UoG archive on the workstation.
# `oideachais/dlt_sources/author_archive/university_of_galway.py` is 3 levels
# deep from the repo root (`kings_college_galway/`). The author archive sits
# at the same level as `oideachais/` (i.e. the repo root), so:
DEFAULT_UOG_PATH = Path(
    os.environ.get(
        "AUTHOR_ARCHIVE_UOG_PATH",
        str(
            Path(__file__).resolve().parents[3]
            / "author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin"
            / "university_of_galway"
        ),
    )
)


def _uog_grammar(base_path: Path) -> PathGrammar:
    """
    Build the UoG-specific PathGrammar.

    Subject paths are derived from the UoG sub-directory names so that
    `detect_subject()` returns e.g. "education", "irish", "mata", "past",
    "software_development". These double as `domain` (via `detect_domain`).
    """
    subject_paths: dict[str, Path] = {}
    if base_path.exists():
        for child in base_path.iterdir():
            if child.is_dir():
                subject_paths[child.name] = child

    return PathGrammar(
        subject_paths=subject_paths,
        # `ed305_`, `ga101_`, `ct511_` — all three are present in this archive.
        course_code_pattern=__import__("re").compile(r"([A-Za-z]{2,3})(\d{3,4})"),
        # `.pages` (Apple) is handwriting-heavy; `.heic` is iOS photo scans.
        handwriting_extensions={".pages", ".heic"},
        # `mata/` and `past/` have scanned math / law PDFs.
        handwriting_subdirs={"mata", "past"},
    )


def _baml_extraction_row(
    file_info: dict[str, Any],
    baml_function: str = "ExtractUoGArtifact",
) -> dict[str, Any]:
    """
    Build a BAML extraction row, memoised by (file_hash, baml_function_name).

    If the BAML client is not generated, the row's `status` is set to
    `skipped_no_client` and the asset materialisation still succeeds.
    """
    file_hash = file_info.get("file_hash", "")
    row: dict[str, Any] = {
        "id": hashlib.sha256(
            f"{file_hash}:{baml_function}".encode("utf-8")
        ).hexdigest()[:16],
        "file_hash": file_hash,
        "file_path": file_info.get("file_path"),
        "baml_function": baml_function,
        "status": "pending",
        "extracted_at": None,
        "result": None,
        "extraction_text_chars": 0,
    }

    extraction = file_info.get("extraction") or {}
    text = extraction.get("full_text") or ""
    row["extraction_text_chars"] = len(text)

    try:
        from baml_client import b  # type: ignore[import-not-found]
    except ImportError:
        row["status"] = "skipped_no_client"
        return row

    if not text:
        row["status"] = "skipped_no_text"
        return row

    try:
        if baml_function == "ExtractUoGArtifact":
            result = b.ExtractUoGArtifact(
                pdf_text=text[:50_000],
                file_name=file_info.get("file_name", ""),
                file_type=file_info.get("file_type", "unknown"),
            )
        else:
            row["status"] = "skipped_unknown_function"
            return row

        # BAML objects are pydantic models; serialise via .model_dump().
        if hasattr(result, "model_dump"):
            row["result"] = result.model_dump()
        else:
            row["result"] = result
        row["status"] = "success"
    except Exception as e:  # noqa: BLE001 — BAML can raise LLM/parse errors
        logger.warning(
            "baml_extraction_failed",
            file_path=row["file_path"],
            function=baml_function,
            error=str(e),
        )
        row["status"] = "error"
        row["error"] = str(e)
    return row


# ============================================================================
# DLT source
# ============================================================================


@dlt.source(name="author_archive_uog")
def university_of_galway_source(
    base_path: str | Path = DEFAULT_UOG_PATH,
    max_files: int | None = None,
    include_extraction: bool = False,
    run_baml_extraction: bool = False,
):
    """
    DLT source for `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/university_of_galway/`.

    Args:
        base_path: Root directory to walk.
        max_files: Cap on rows yielded (testing).
        include_extraction: If True, extract text content with pymupdf/python-docx.
        run_baml_extraction: If True, invoke `b.ExtractUoGArtifact` for each row
            and emit an `extraction_metadata` resource.
    """
    base_path = Path(base_path)
    grammar = _uog_grammar(base_path)

    @dlt.resource(
        name="all_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
        columns={
            "account": {"partition": True},
            "domain": {"partition": True},
            "course_code": {"partition": True},
        },
    )
    def all_documents() -> Iterator[dict[str, Any]]:
        """All discovered UoG documents with metadata."""
        yield from scan_directory(
            base_path=base_path,
            grammar=grammar,
            account="university_of_galway",
            max_files=max_files,
        )

    @dlt.resource(
        name="pdf_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def pdf_documents() -> Iterator[dict[str, Any]]:
        """UoG PDFs with optional text extraction."""
        for row in scan_directory(
            base_path=base_path,
            grammar=grammar,
            account="university_of_galway",
            file_types=["pdf"],
            max_files=max_files,
        ):
            if include_extraction:
                row = extract_content(row, base_path, grammar)
            yield row

    @dlt.resource(
        name="word_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def word_documents() -> Iterator[dict[str, Any]]:
        """UoG DOCX files with optional text extraction."""
        for row in scan_directory(
            base_path=base_path,
            grammar=grammar,
            account="university_of_galway",
            file_types=["word"],
            max_files=max_files,
        ):
            if include_extraction:
                row = extract_content(row, base_path, grammar)
            yield row

    @dlt.resource(
        name="code_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def code_documents() -> Iterator[dict[str, Any]]:
        """UoG code files (Python / JS / TS / Java) for the software_development/ subdir."""
        yield from scan_directory(
            base_path=base_path,
            grammar=grammar,
            account="university_of_galway",
            file_types=["code"],
            max_files=max_files,
        )

    @dlt.resource(
        name="handwritten_pages",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def handwritten_pages() -> Iterator[dict[str, Any]]:
        """UoG files that need OCR (`.pages`, `.heic`, scanned PDF, `mata/`, `past/`)."""
        for row in scan_directory(
            base_path=base_path,
            grammar=grammar,
            account="university_of_galway",
            max_files=max_files,
        ):
            if row.get("requires_handwriting_ocr"):
                yield row

    @dlt.resource(
        name="extraction_metadata",
        write_disposition="merge",
        primary_key=["file_hash", "baml_function"],
    )
    def extraction_metadata() -> Iterator[dict[str, Any]]:
        """BAML extraction rows (one per file_hash × function)."""
        if not run_baml_extraction:
            return
        for row in scan_directory(
            base_path=base_path,
            grammar=grammar,
            account="university_of_galway",
            file_types=["pdf", "word"],
            max_files=max_files,
            include_extraction=True,
        ):
            yield _baml_extraction_row(row, baml_function="ExtractUoGArtifact")

    return (
        all_documents,
        pdf_documents,
        word_documents,
        code_documents,
        handwritten_pages,
        extraction_metadata,
    )


def create_uog_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "author_archive_uog",
) -> dlt.Pipeline:
    """Create a DLT pipeline for the UoG source (convenience helper)."""
    return dlt.pipeline(
        pipeline_name="author_archive_uog_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


def run_uog_ingestion(
    destination: str = "duckdb",
    max_files: int | None = None,
) -> Any:
    """Run a full UoG ingestion against the default destination."""
    pipeline = create_uog_pipeline(destination=destination)
    load_info = pipeline.run(university_of_galway_source(max_files=max_files))
    logger.info(
        "uog_ingestion_complete",
        load_info=str(load_info),
        destination=destination,
    )
    return load_info


__all__ = [
    "DEFAULT_UOG_PATH",
    "university_of_galway_source",
    "create_uog_pipeline",
    "run_uog_ingestion",
]
