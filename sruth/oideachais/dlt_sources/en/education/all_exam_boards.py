"""
Education EN source: all_exam_boards_source

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

def all_exam_boards_source(
    qualification_level: str | None = None,
    include_pdf_links: bool = True,
    max_pages: int = 300,
):
    """
    DLT source combining all three major England exam boards.

    Args:
        qualification_level: "gcse" or "a_level"
        include_pdf_links: Extract PDF specification links
        max_pages: Maximum pages to crawl (divided among boards)

    Returns:
        DLT source with pages from AQA, Edexcel, and OCR
    """
    pages_per_board = max_pages // 3

    @dlt.resource(
        name="all_exam_board_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def all_exam_board_pages():
        """Crawled pages from all exam boards."""
        for board in ["aqa", "edexcel", "ocr"]:
            yield from _crawl_exam_board(board, qualification_level, pages_per_board)

    @dlt.resource(
        name="all_exam_board_pdf_links",
        write_disposition="merge",
        primary_key=["url"],
    )
    def all_exam_board_pdf_links():
        """PDF links from all exam boards."""
        if include_pdf_links:
            for board in ["aqa", "edexcel", "ocr"]:
                for level in ["gcse", "a_level"]:
                    if qualification_level is None or qualification_level == level:
                        yield from _extract_exam_board_pdf_links(board, level)

    return all_exam_board_pages, all_exam_board_pdf_links
