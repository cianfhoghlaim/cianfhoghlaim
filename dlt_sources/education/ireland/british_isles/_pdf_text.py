"""Shared PDF text extraction helper for the Ireland JC pipeline.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Replaces the `_pdf_text_stub` placeholder in:
- dlt_sources/british_isles/ireland/education/junior_cycle_subjects/_factory.py
- dlt_sources/british_isles/ireland/education/junior_cycle_cbas/_factory.py
- dlt_sources/british_isles/ireland/education/junior_cycle_short_courses/_factory.py

with a real `pymupdf` extractor that:
1. Opens the PDF
2. Extracts text per page (up to 50,000 chars by default)
3. Joins pages with `\n\n`
4. Falls back to the stub if pymupdf is unavailable

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def _pdf_text_stub(path: Path) -> str:
    """Fallback stub: return a placeholder string when pymupdf is unavailable.

    The legacy stub used by the BIEP v1 era — kept as the explicit
    fallback for the real `extract_pdf_text` function.
    """
    return f"[PDF_TEXT_STUB] file={path.name} size={path.stat().st_size}"


def extract_pdf_text(path: Path, max_chars: int = 50_000) -> str:
    """Extract the text content of a PDF file using pymupdf.

    Falls back to the legacy stub if pymupdf is unavailable or the
    file cannot be opened.

    Parameters
    ----------
    path : Path
        The absolute path to the PDF file.
    max_chars : int
        The maximum number of characters to extract (default 50,000).
        The BAML functions truncate to 30,000 chars downstream.

    Returns
    -------
    str
        The extracted text (joined with `\n\n` between pages), or the
        legacy stub if pymupdf is unavailable.
    """
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
        extracted = "\n\n".join(parts)
        if extracted:
            return extracted
        # Empty extraction — fall through to stub
        logger.warning("pymupdf_extracted_empty", path=str(path))
        return _pdf_text_stub(path)
    except (ImportError, OSError, ValueError, RuntimeError) as exc:  # noqa: BLE001
        logger.warning("pymupdf_extract_failed", path=str(path), error=str(exc))
        return _pdf_text_stub(path)


__all__ = ["extract_pdf_text", "_pdf_text_stub"]
