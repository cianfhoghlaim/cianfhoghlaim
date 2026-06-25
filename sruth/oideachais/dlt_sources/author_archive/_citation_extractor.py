"""
Citation extractor for Gemini Deep Research PDFs.

Gemini's deep-research output includes:
1. Markdown headings (`# Topic`, `## Subtopic`).
2. Inline URL references in `Source: <url>` or `[label](url)` form.
3. PyMuPDF link annotations on the underlying PDF (when exported as PDF).

This module extracts (a) the heading hierarchy of the first page and
(b) the union of URLs from all three sources.

Tolerant of PDFs without citations (returns an empty list, never raises).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Data classes
# ============================================================================


@dataclass(frozen=True)
class CitedUrl:
    """One citation extracted from a Gemini PDF."""

    url: str
    anchor_text: str = ""
    source: str = ""  # "pymupdf_link" | "markdown_inline" | "first_page_header"


# ============================================================================
# Patterns
# ============================================================================


# `[anchor](url)` form, tolerant of newlines and parens in the URL.
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
# Bare URLs.
_BARE_URL_RE = re.compile(r"(?<![\(\[])(https?://[^\s\)\]]+)")
# `Source: <url>` lines (very common in Gemini output).
_SOURCE_LINE_RE = re.compile(r"(?:^|\n)\s*Source:\s*(https?://\S+)", re.IGNORECASE)
# `### Heading` / `## Heading` / `# Heading`.
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


# ============================================================================
# Extraction
# ============================================================================


def _extract_pymupdf_links(path: Path) -> list[CitedUrl]:
    """Use PyMuPDF link annotations to extract URLs."""
    try:
        import pymupdf  # type: ignore[import-untyped]
    except ImportError:
        return []

    out: list[CitedUrl] = []
    try:
        doc = pymupdf.open(str(path))
        for page in doc:
            for link in page.get_links():
                uri = link.get("uri")
                if not uri:
                    continue
                if not (uri.startswith("http://") or uri.startswith("https://")):
                    continue
                anchor = link.get("from") or ""
                if hasattr(anchor, "get"):
                    anchor = anchor.get("text", "") or ""
                out.append(
                    CitedUrl(
                        url=uri,
                        anchor_text=str(anchor) if anchor else "",
                        source="pymupdf_link",
                    )
                )
        doc.close()
    except (OSError, ValueError, RuntimeError) as e:
        logger.debug("pymupdf_link_extract_failed", path=str(path), error=str(e))
    return out


def _extract_markdown_citations(text: str) -> list[CitedUrl]:
    """Extract URLs from markdown link and `Source:` patterns."""
    out: list[CitedUrl] = []
    seen: set[str] = set()
    for match in _MD_LINK_RE.finditer(text):
        url = match.group(2)
        if url in seen:
            continue
        seen.add(url)
        out.append(
            CitedUrl(
                url=url,
                anchor_text=match.group(1),
                source="markdown_inline",
            )
        )
    for match in _SOURCE_LINE_RE.finditer(text):
        url = match.group(1)
        if url in seen:
            continue
        seen.add(url)
        out.append(CitedUrl(url=url, anchor_text="", source="markdown_inline"))
    for match in _BARE_URL_RE.finditer(text):
        url = match.group(1)
        if url in seen:
            continue
        seen.add(url)
        out.append(CitedUrl(url=url, anchor_text="", source="markdown_inline"))
    return out


def _extract_first_page_heading(path: Path) -> tuple[str, list[CitedUrl]]:
    """
    Extract the first markdown heading from the first page.

    Returns (heading_text, []). Citations are returned separately
    by `extract_citations` — kept separate for future tests / caller reuse.
    """
    try:
        import pymupdf  # type: ignore[import-untyped]
    except ImportError:
        return "", []

    try:
        doc = pymupdf.open(str(path))
        if len(doc) == 0:
            doc.close()
            return "", []
        first_page_text = doc[0].get_text() or ""
        doc.close()
    except (OSError, ValueError, RuntimeError):
        return "", []

    match = _HEADING_RE.search(first_page_text)
    if match:
        return match.group(2).strip(), []
    return "", []


def extract_citations(path: Path) -> dict[str, Any]:
    """
    Extract citations + the first-page heading from a Gemini PDF.

    Returns a dict with:
        - `first_page_heading: str`
        - `cited_urls: list[CitedUrl]`
        - `citation_count: int`
        - `status: "success" | "error"`
    """
    if not path.exists():
        return {
            "first_page_heading": "",
            "cited_urls": [],
            "citation_count": 0,
            "status": "error",
            "error": f"file not found: {path}",
        }

    heading, _ = _extract_first_page_heading(path)
    pymupdf_links = _extract_pymupdf_links(path)
    markdown_citations: list[CitedUrl] = []

    # Extract text from the first 5 pages and look for markdown citations.
    try:
        import pymupdf  # type: ignore[import-untyped]

        doc = pymupdf.open(str(path))
        snippet_parts: list[str] = []
        max_pages = min(len(doc), 5)
        for i in range(max_pages):
            snippet_parts.append(doc[i].get_text() or "")
        doc.close()
        snippet = "\n".join(snippet_parts)
        markdown_citations = _extract_markdown_citations(snippet)
    except (ImportError, OSError, ValueError, RuntimeError) as e:
        logger.debug("citation_text_extract_failed", path=str(path), error=str(e))

    # De-duplicate by URL, preferring pymupdf_link source.
    merged: dict[str, CitedUrl] = {}
    for c in markdown_citations:
        merged.setdefault(c.url, c)
    for c in pymupdf_links:
        if c.url not in merged:
            merged[c.url] = c
        else:
            # pymupdf wins on conflict (more authoritative)
            merged[c.url] = c

    return {
        "first_page_heading": heading,
        "cited_urls": list(merged.values()),
        "citation_count": len(merged),
        "status": "success",
    }


__all__ = [
    "CitedUrl",
    "extract_citations",
]
