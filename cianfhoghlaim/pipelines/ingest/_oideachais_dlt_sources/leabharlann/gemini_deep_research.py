"""
Gemini Deep Research filesystem DLT source.

Ingests every PDF in
`author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/gemini_deep_research/`
into the `author_archive_gemini_documents` DuckLake table.

Adds a `gemini_citations` column (list of `CitedUrl` dicts) extracted via
the shared `_citation_extractor` module.
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt
import structlog

from ._citation_extractor import extract_citations
from ._scanner import (
    PathGrammar,
    extract_content,
    scan_directory,
)

logger = structlog.get_logger(__name__)

DEFAULT_GEMINI_PATH = Path(
    os.environ.get(
        "AUTHOR_ARCHIVE_GEMINI_PATH",
        str(
            Path(__file__).resolve().parents[3]
            / "leabharlann"
            / "gemini_deep_research"
        ),
    )
)

# Top-level Gemini sub-directories map cleanly onto the `GeminiDomain` enum
# in `baml_src/author_archive.baml`.
GEMINI_DOMAINS: set[str] = {
    "culture",
    "law",
    "medical",
    "politics",
    "technology",
    "other",
    "identity",
}


def _gemini_grammar(base_path: Path) -> PathGrammar:
    """Build the Gemini-specific PathGrammar."""
    subject_paths: dict[str, Path] = {}
    if base_path.exists():
        for child in base_path.iterdir():
            if child.is_dir():
                subject_paths[child.name] = child
    return PathGrammar(
        subject_paths=subject_paths,
        # Gemini filenames are slugs, not course codes — disable.
        course_code_pattern=None,
    )


def _baml_extraction_row(
    file_info: dict[str, Any],
    baml_function: str = "ExtractGeminiReport",
) -> dict[str, Any]:
    """Memoised BAML extraction row, identical contract to the UoG helper."""
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
        if baml_function == "ExtractGeminiReport":
            result = b.ExtractGeminiReport(
                pdf_text=text[:50_000],
                file_name=file_info.get("file_name", ""),
            )
        else:
            row["status"] = "skipped_unknown_function"
            return row

        if hasattr(result, "model_dump"):
            row["result"] = result.model_dump()
        else:
            row["result"] = result
        row["status"] = "success"
    except Exception as e:  # noqa: BLE001
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


@dlt.source(name="author_archive_gemini")
def gemini_deep_research_source(
    base_path: str | Path = DEFAULT_GEMINI_PATH,
    max_files: int | None = None,
    include_extraction: bool = False,
    include_citations: bool = True,
    run_baml_extraction: bool = False,
):
    """
    DLT source for `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/gemini_deep_research/`.

    Args:
        base_path: Root directory to walk.
        max_files: Cap on rows yielded (testing).
        include_extraction: If True, extract text content with pymupdf.
        include_citations: If True, populate the `gemini_citations` column via
            PyMuPDF link annotations + first-page heading regex.
        run_baml_extraction: If True, invoke `b.ExtractGeminiReport` per row.
    """
    base_path = Path(base_path)
    grammar = _gemini_grammar(base_path)

    def _yield_with_citations(
        rows: Iterator[dict[str, Any]],
    ) -> Iterator[dict[str, Any]]:
        for row in rows:
            if include_citations and row.get("file_type") == "pdf":
                try:
                    citation = extract_citations(Path(row["file_path"]))
                    row["gemini_citations"] = [
                        {
                            "url": c.url,
                            "anchor_text": c.anchor_text,
                            "source": c.source,
                        }
                        for c in citation.get("cited_urls", [])
                    ]
                    row["gemini_citation_count"] = citation.get(
                        "citation_count", 0
                    )
                    row["gemini_first_page_heading"] = citation.get(
                        "first_page_heading", ""
                    )
                except (OSError, ValueError, RuntimeError) as e:
                    logger.debug(
                        "gemini_citation_extract_failed",
                        path=row.get("file_path"),
                        error=str(e),
                    )
                    row["gemini_citations"] = []
                    row["gemini_citation_count"] = 0
                    row["gemini_first_page_heading"] = ""
            else:
                row.setdefault("gemini_citations", [])
                row.setdefault("gemini_citation_count", 0)
                row.setdefault("gemini_first_page_heading", "")
            yield row

    @dlt.resource(
        name="all_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
        columns={
            "account": {"partition": True},
            "domain": {"partition": True},
        },
    )
    def all_documents() -> Iterator[dict[str, Any]]:
        """All discovered Gemini Deep Research PDFs with metadata + citations."""
        yield from _yield_with_citations(
            scan_directory(
                base_path=base_path,
                grammar=grammar,
                account="gemini_deep_research",
                max_files=max_files,
            )
        )

    @dlt.resource(
        name="pdf_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def pdf_documents() -> Iterator[dict[str, Any]]:
        """Gemini PDFs with text extraction + citations."""
        for row in _yield_with_citations(
            scan_directory(
                base_path=base_path,
                grammar=grammar,
                account="gemini_deep_research",
                file_types=["pdf"],
                max_files=max_files,
            )
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
        """Gemini DOCX files (rare — most are PDFs)."""
        for row in _yield_with_citations(
            scan_directory(
                base_path=base_path,
                grammar=grammar,
                account="gemini_deep_research",
                file_types=["word"],
                max_files=max_files,
            )
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
        """Gemini code files (almost always empty)."""
        yield from _yield_with_citations(
            scan_directory(
                base_path=base_path,
                grammar=grammar,
                account="gemini_deep_research",
                file_types=["code"],
                max_files=max_files,
            )
        )

    @dlt.resource(
        name="handwritten_pages",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def handwritten_pages() -> Iterator[dict[str, Any]]:
        """Gemini files that may need OCR (typically empty; Gemini output is born-digital)."""
        for row in scan_directory(
            base_path=base_path,
            grammar=grammar,
            account="gemini_deep_research",
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
        for row in _yield_with_citations(
            scan_directory(
                base_path=base_path,
                grammar=grammar,
                account="gemini_deep_research",
                file_types=["pdf"],
                max_files=max_files,
                include_extraction=True,
            )
        ):
            yield _baml_extraction_row(row, baml_function="ExtractGeminiReport")

    return (
        all_documents,
        pdf_documents,
        word_documents,
        code_documents,
        handwritten_pages,
        extraction_metadata,
    )


def create_gemini_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "author_archive_gemini",
) -> dlt.Pipeline:
    """Create a DLT pipeline for the Gemini Deep Research source (convenience helper)."""
    return dlt.pipeline(
        pipeline_name="author_archive_gemini_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


def run_gemini_ingestion(
    destination: str = "duckdb",
    max_files: int | None = None,
) -> Any:
    """Run a full Gemini Deep Research ingestion against the default destination."""
    pipeline = create_gemini_pipeline(destination=destination)
    load_info = pipeline.run(gemini_deep_research_source(max_files=max_files))
    logger.info(
        "gemini_ingestion_complete",
        load_info=str(load_info),
        destination=destination,
    )
    return load_info


__all__ = [
    "DEFAULT_GEMINI_PATH",
    "GEMINI_DOMAINS",
    "gemini_deep_research_source",
    "create_gemini_pipeline",
    "run_gemini_ingestion",
]
