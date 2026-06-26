"""
Education EN source: ocr_qualifications_source

Split from uk/england/national_curriculum.py in Phase 3D.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
import dlt
from ...common.firecrawl_source import crawl_website, scrape_page
from ...common.incremental import compute_content_hash

from ._national_curriculum_helpers import (
    _crawl_exam_board,
    _extract_exam_board_pdf_links,
)

def ocr_qualifications_source(
    qualification_level: str | None = None,
    include_pdf_links: bool = True,
    max_pages: int = 100,
):
    """
    DLT source for OCR qualifications.

    Args:
        qualification_level: "gcse" or "a_level"
        include_pdf_links: Extract PDF specification links
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with OCR pages and optionally PDF links
    """

    @dlt.resource(
        name="ocr_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def ocr_pages():
        """Crawled OCR qualification pages."""
        yield from _crawl_exam_board("ocr", qualification_level, max_pages)

    @dlt.resource(
        name="ocr_pdf_links",
        write_disposition="merge",
        primary_key=["url"],
    )
    def ocr_pdf_links():
        """OCR PDF specification links."""
        if include_pdf_links:
            for level in ["gcse", "a_level"]:
                if qualification_level is None or qualification_level == level:
                    yield from _extract_exam_board_pdf_links("ocr", level)

    return ocr_pages, ocr_pdf_links
