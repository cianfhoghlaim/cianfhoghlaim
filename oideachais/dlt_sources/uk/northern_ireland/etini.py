"""
DLT source for ETI (Education and Training Inspectorate) NI.

ETI provides inspection reports for schools in Northern Ireland.
https://www.etini.gov.uk/
"""

from collections.abc import Iterator
from typing import Any

import dlt

from ..common.firecrawl_source import crawl_website


def _crawl_eti_inspections(max_pages: int = 200) -> Iterator[dict[str, Any]]:
    """
    Crawl ETI inspection reports.

    Args:
        max_pages: Maximum pages to crawl

    Yields:
        Inspection report data
    """
    for page in crawl_website(
        base_url="https://www.etini.gov.uk",
        include_paths=["/publications/*", "/inspection-reports/*"],
        exclude_paths=["/search", "/contact"],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "northern_ireland"
        page["source"] = "etini"

        # Parse inspection data from content
        markdown = page.get("markdown", "")

        # Extract performance levels (Outstanding, Very Good, Good, etc.)
        for level in ["outstanding", "very good", "good", "satisfactory", "inadequate"]:
            if level in markdown.lower():
                page["performance_level"] = level.title()
                break

        yield page


@dlt.source(name="etini")
def etini_source(max_pages: int = 200):
    """
    DLT source for ETI inspection reports.

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with inspection_reports resource
    """

    @dlt.resource(
        name="inspection_reports",
        write_disposition="merge",
        primary_key=["url"],
    )
    def inspection_reports():
        """ETI inspection reports."""
        yield from _crawl_eti_inspections(max_pages)

    return inspection_reports
