"""
Zotero dlt source.

Scans every PDF in `leabharlann/zotero/` (real Zotero storage format) and
yields one row per non-empty PDF. Empty `_.pdf` placeholders are skipped.
Zotero duplicate markers (`__dup0`, `_(N)`) are preserved on the row but
the SHA-256 primary key ensures we only load each unique file once.

Filename-derived columns:
- `arxiv_id` (e.g. "2504.02890" or "2402" for pre-DOI arXiv IDs)
- `arxiv_version` (e.g. "v2")
- `duplicate_marker` (e.g. "__dup0", "_(1)", or None)
- `title_guess` (heuristic: strip the author/year prefix)

Reference: openspec/changes/leabharlann-cocoindex-v1/specs/leabharlann-ingestion/spec.md
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt
import structlog

from ._scanner import (
    PathGrammar,
    extract_content,
    scan_directory,
)

logger = structlog.get_logger(__name__)


DEFAULT_ZOTERO_ROOT = Path(
    os.environ.get(
        "LEABHARLANN_ZOTERO_ROOT",
        str(
            Path(__file__).resolve().parents[3]
            / "leabharlann"
            / "zotero"
        ),
    )
)

# Patterns.
_ARXIV_DOT_RE = re.compile(r"(\d{4}\.\d{4,5})(v(\d+))?")
_ARXIV_LEGACY_RE = re.compile(r"^(\d{4})__dup\d")
_DUP_MARKER_RE = re.compile(r"(__dup\d+|\(\d+\))")
_TITLE_STRIP_RE = re.compile(
    r"^(?P<authors>[A-Z][a-z]+(?: et al\.)?(?:,?\s+[A-Z][a-z]+)*\s*-\s*)?"
    r"(\d{4}\s*-\s*)?"
    r"(?P<rest>.+?)(?P<ext>\.pdf)?$"
)


def _extract_arxiv_id(file_name: str) -> tuple[str | None, str | None]:
    """Reuse the same logic as the CocoIndex v1 App."""
    m = _ARXIV_DOT_RE.search(file_name)
    if m:
        return m.group(1), f"v{m.group(3)}" if m.group(3) else None
    m2 = _ARXIV_LEGACY_RE.match(file_name)
    if m2:
        return m2.group(1), None
    return None, None


def _extract_duplicate_marker(file_name: str) -> str | None:
    m = _DUP_MARKER_RE.search(file_name)
    return m.group(1) if m else None


def _extract_title_guess(file_name: str) -> str:
    m = _TITLE_STRIP_RE.match(file_name.replace("__dup0", ""))
    if not m:
        return file_name.replace(".pdf", "")
    rest = m.group("rest").strip()
    return rest


def _zotero_grammar(base_path: Path) -> PathGrammar:
    return PathGrammar(
        subject_paths={},
        course_code_pattern=None,
        handwriting_extensions=set(),
        handwriting_subdirs=set(),
    )


# ============================================================================
# DLT source
# ============================================================================


@dlt.source(name="leabharlann_zotero")
def zotero_source(
    base_path: str | Path = DEFAULT_ZOTERO_ROOT,
    max_files: int | None = None,
    include_extraction: bool = True,
):
    """
    DLT source for `leabharlann/zotero/`.

    Skips the `_.pdf` empty placeholder that Zotero uses as a directory
    marker. The empty placeholder would otherwise be loaded as a
    0-byte PDF row.
    """
    base_path = Path(base_path)
    grammar = _zotero_grammar(base_path)
    account = "leabharlann_zotero"

    @dlt.resource(
        name="all_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
        columns={
            "account": {"partition": True},
        },
    )
    def all_documents() -> Iterator[dict[str, Any]]:
        """All Zotero PDFs with arxiv_id + duplicate marker + title guess."""
        for row in scan_directory(
            base_path=base_path,
            grammar=grammar,
            account=account,
            file_types=["pdf"],
            max_files=max_files,
        ):
            # Skip the empty `_.pdf` placeholder.
            if row["file_name"] == "_.pdf" or row["file_size"] == 0:
                continue
            arxiv_id, arxiv_version = _extract_arxiv_id(row["file_name"])
            row["arxiv_id"] = arxiv_id
            row["arxiv_version"] = arxiv_version
            row["duplicate_marker"] = _extract_duplicate_marker(row["file_name"])
            row["title_guess"] = _extract_title_guess(row["file_name"])
            yield row

    @dlt.resource(
        name="pdf_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def pdf_documents() -> Iterator[dict[str, Any]]:
        """Zotero PDFs with pymupdf text extraction."""
        for row in all_documents():
            if include_extraction:
                row = extract_content(row, base_path, grammar)
            yield row

    @dlt.resource(
        name="arxiv_papers",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def arxiv_papers() -> Iterator[dict[str, Any]]:
        """Subset of `all_documents` where the filename matches an arXiv ID pattern."""
        for row in all_documents():
            if row.get("arxiv_id") is not None:
                yield row

    return all_documents, pdf_documents, arxiv_papers


def _extract_text_from_pdf(path: Path, max_chars: int = 50_000) -> str:
    """Best-effort text extraction via pymupdf (graceful if missing)."""
    try:
        import pymupdf  # type: ignore[import-not-found]

        doc = pymupdf.open(str(path))
        parts: list[str] = []
        total = 0
        for page in doc:
            text = page.get_text() or ""
            if not text:
                continue
            if total + len(text) > max_chars:
                text = text[: max_chars - total]
            parts.append(text)
            total += len(text)
            if total >= max_chars:
                break
        doc.close()
        return "\n\n".join(parts)
    except (ImportError, OSError, ValueError, RuntimeError) as e:
        logger.debug("pymupdf_zotero_extract_failed", path=str(path), error=str(e))
        return ""


def _baml_extract_zotero(
    pdf_text: str,
    file_name: str,
    arxiv_id: str | None,
) -> dict[str, Any]:
    """Invoke `b.ExtractZoteroMetadata` and serialise the result. Graceful if missing."""
    try:
        from baml_client import b  # type: ignore[import-not-found]
    except ImportError:
        return {"status": "skipped_no_client", "result": None}

    try:
        result = b.ExtractZoteroMetadata(
            pdf_text=pdf_text[:30_000],
            file_name=file_name,
            arxiv_id=arxiv_id,
        )
        if hasattr(result, "model_dump"):
            return {"status": "success", "result": result.model_dump()}
        return {"status": "success", "result": result}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "zotero_baml_extraction_failed",
            file_name=file_name,
            arxiv_id=arxiv_id,
            error=str(e),
        )
        return {"status": "error", "error": str(e)}


@dlt.resource(
    name="arxiv_papers_baml",
    write_disposition="merge",
    primary_key=["file_hash", "baml_function"],
)
def arxiv_papers_baml() -> Any:
    """BAML-extracted `ZoteroPaper` rows (one per arXiv paper)."""
    if not DEFAULT_ZOTERO_ROOT.exists():
        return
    for row in all_documents():
        arxiv_id = row.get("arxiv_id")
        if not arxiv_id:
            continue
        file_path = Path(row["file_path"])
        text = _extract_text_from_pdf(file_path)
        if not text:
            continue
        result = _baml_extract_zotero(text, file_path.name, arxiv_id)
        if result["status"] != "success" or not result["result"]:
            continue
        zotero_paper = result["result"]
        if hasattr(zotero_paper, "model_dump"):
            zotero_paper = zotero_paper.model_dump()
        if not isinstance(zotero_paper, dict):
            continue
        # Extract author names as a flat list (BAML returns Author[]).
        authors = zotero_paper.get("authors", [])
        if not isinstance(authors, list):
            authors = []
        author_names = [
            a.get("name", "") if isinstance(a, dict) else str(a)
            for a in authors
        ]
        yield {
            "file_hash": row["file_hash"],
            "filename": row["file_name"],
            "baml_function": "ExtractZoteroMetadata",
            "paper_kind": zotero_paper.get("paper_kind", "OTHER"),
            "arxiv_id": zotero_paper.get("arxiv_id", arxiv_id),
            "doi": zotero_paper.get("doi"),
            "title": zotero_paper.get("title", ""),
            "authors": author_names,
            "year": zotero_paper.get("year"),
            "abstract": zotero_paper.get("abstract"),
            "venue": zotero_paper.get("venue"),
            "irish_relevant": zotero_paper.get("irish_relevant", False),
            "htr_relevant": zotero_paper.get("htr_relevant", False),
            "confidence": zotero_paper.get("confidence", 0.0),
            "extracted_at": datetime.now(UTC).isoformat(),
        }


def create_zotero_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "leabharlann_zotero",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="leabharlann_zotero_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "DEFAULT_ZOTERO_ROOT",
    "zotero_source",
    "create_zotero_pipeline",
    "arxiv_papers_baml",
    "_extract_arxiv_id",
    "_extract_duplicate_marker",
    "_extract_title_guess",
]
