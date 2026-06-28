"""
Education EN source: aqa_qualifications_source

Split from uk/england/national_curriculum.py in Phase 3D.
"""

import dlt

from ._national_curriculum_helpers import (
    _crawl_exam_board,
    _extract_exam_board_pdf_links,
)


def aqa_qualifications_source(
    qualification_level: str | None = None,
    include_pdf_links: bool = True,
    max_pages: int = 100,
):
    """
    DLT source for AQA qualifications.

    Args:
        qualification_level: "gcse" or "a_level"
        include_pdf_links: Extract PDF specification links
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with AQA pages and optionally PDF links
    """

    @dlt.resource(
        name="aqa_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def aqa_pages():
        """Crawled AQA qualification pages."""
        yield from _crawl_exam_board("aqa", qualification_level, max_pages)

    @dlt.resource(
        name="aqa_pdf_links",
        write_disposition="merge",
        primary_key=["url"],
    )
    def aqa_pdf_links():
        """AQA PDF specification links."""
        if include_pdf_links:
            for level in ["gcse", "a_level"]:
                if qualification_level is None or qualification_level == level:
                    yield from _extract_exam_board_pdf_links("aqa", level)

    return aqa_pages, aqa_pdf_links
