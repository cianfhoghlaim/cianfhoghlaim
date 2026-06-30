"""
Education IE source: examinations_source

Split from ireland/examinations.py in Phase 3D.
"""

import dlt

from ._examinations_helpers import (
    _crawl_examinations,
    _map_examiner_reports,
)


def examinations_source(
    content_type: str | None = None,
    max_pages: int = 100,
    include_report_pdfs: bool = True,
):
    """
    DLT source for examinations.ie content (Firecrawl-based).

    Args:
        content_type: Optional filter (examiner_reports, exam_materials, statistics, circulars)
        max_pages: Maximum pages to crawl
        include_report_pdfs: Whether to include examiner report PDF discovery

    Returns:
        DLT source with examinations_pages and optionally report_pdfs resources
    """

    @dlt.resource(
        name="examinations_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def examinations_pages():
        """Crawled SEC pages."""
        yield from _crawl_examinations(content_type, max_pages)

    @dlt.resource(
        name="examiner_report_pdfs",
        write_disposition="merge",
        primary_key=["url"],
    )
    def examiner_report_pdfs():
        """Discovered examiner report PDF URLs."""
        if include_report_pdfs:
            yield from _map_examiner_reports()

    return examinations_pages, examiner_report_pdfs
