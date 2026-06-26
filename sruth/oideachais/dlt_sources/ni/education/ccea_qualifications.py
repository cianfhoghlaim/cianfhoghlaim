"""
Education NI source: ccea_qualifications_source

Split from uk/northern_ireland/ccea_curriculum.py in Phase 3D.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
import dlt
from ...common.firecrawl_source import crawl_website, scrape_page
from ...common.incremental import compute_content_hash

from ._ccea_curriculum_helpers import (
    _crawl_ccea_qualifications,
    _extract_ccea_pdf_links,
)

def ccea_qualifications_source(
    qualification_level: str | None = None,
    include_pdf_links: bool = True,
    max_pages: int = 150,
):
    """
    DLT source for CCEA qualifications.

    Args:
        qualification_level: "gcse", "a_level", or "as_level"
        include_pdf_links: Extract PDF specification links
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with CCEA pages and optionally PDF links
    """

    @dlt.resource(
        name="ccea_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def ccea_pages():
        """Crawled CCEA qualification pages."""
        yield from _crawl_ccea_qualifications(qualification_level, max_pages)

    @dlt.resource(
        name="ccea_pdf_links",
        write_disposition="merge",
        primary_key=["url"],
    )
    def ccea_pdf_links():
        """CCEA PDF specification links."""
        if include_pdf_links:
            for level in ["gcse", "a_level", "as_level"]:
                if qualification_level is None or qualification_level == level:
                    yield from _extract_ccea_pdf_links(level)

    return ccea_pages, ccea_pdf_links
