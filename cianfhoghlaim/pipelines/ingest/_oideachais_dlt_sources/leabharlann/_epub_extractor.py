"""
EPUB text extractor.

Best-effort chapter-by-chapter text extraction via the `ebooklib` library.
Graceful degradation: if `ebooklib` isn't installed, the extractor returns
an empty list and the dlt row has `epub_chapters=[]` and a warning in
`epub_error`.

Reference: openspec/changes/leabharlann-cocoindex-v1/proposal.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


try:
    from ebooklib import epub  # type: ignore[import-not-found]

    EBOOKLIB_AVAILABLE = True
except ImportError:
    EBOOKLIB_AVAILABLE = False
    logger.warning("ebooklib_not_available_epub_extraction_disabled")


def extract_epub_chapters(path: Path, max_chars: int = 50_000) -> dict[str, Any]:
    """
    Extract chapters from an EPUB file.

    Returns a dict:
        - `status`: "success" | "error" | "skipped_no_library"
        - `epub_chapters`: list[dict] of `{title, text, order}`
        - `epub_total_chars`: int
        - `epub_error`: str | None
    """
    if not EBOOKLIB_AVAILABLE:
        return {
            "status": "skipped_no_library",
            "epub_chapters": [],
            "epub_total_chars": 0,
            "epub_error": (
                "ebooklib not installed. "
                "Install with `uv pip install 'oideachais[epub]'` (or ebooklib3 for Py3.13)."
            ),
        }

    if not path.exists():
        return {
            "status": "error",
            "epub_chapters": [],
            "epub_total_chars": 0,
            "epub_error": f"file not found: {path}",
        }

    try:
        book = epub.read_epub(str(path))
    except (OSError, ValueError, RuntimeError) as e:
        logger.warning("epub_read_failed", path=str(path), error=str(e))
        return {
            "status": "error",
            "epub_chapters": [],
            "epub_total_chars": 0,
            "epub_error": str(e),
        }

    chapters: list[dict[str, Any]] = []
    total_chars = 0
    order = 0
    try:
        items = list(book.get_items_of_type(epub.ITEM_DOCUMENT))
    except (AttributeError, RuntimeError) as e:
        return {
            "status": "error",
            "epub_chapters": [],
            "epub_total_chars": 0,
            "epub_error": f"get_items_of_type failed: {e}",
        }
    for item in items:
        try:
            content = item.get_content().decode("utf-8", errors="ignore")
        except (OSError, ValueError, AttributeError) as e:
            logger.debug("epub_item_decode_failed", error=str(e))
            continue
        # Strip simple HTML tags to get plain text.
        import re as _re

        text = _re.sub(r"<[^>]+>", " ", content)
        text = _re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        # Truncate individual chapters to avoid blowing up the row.
        if len(text) > max_chars:
            text = text[:max_chars]
        title = item.get_name() or f"chapter_{order}"
        chapters.append({"title": title, "text": text, "order": order})
        total_chars += len(text)
        order += 1
        if total_chars >= max_chars * 5:
            # Stop once we've collected a reasonable amount.
            break

    return {
        "status": "success",
        "epub_chapters": chapters,
        "epub_total_chars": total_chars,
        "epub_error": None,
    }


__all__ = ["EBOOKLIB_AVAILABLE", "extract_epub_chapters"]
