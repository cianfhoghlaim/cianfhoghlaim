"""
Education SCT source: sqa_qualifications_source

Split from uk/scotland/curriculum_for_excellence.py in Phase 3D.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
import dlt
from ...common.firecrawl_source import crawl_website, scrape_page
from ...common.incremental import compute_content_hash

from ._curriculum_for_excellence_helpers import (
    _crawl_sqa_qualifications,
    _extract_sqa_pdf_links,
)

def sqa_qualifications_source(
    qualification_level: str | None = None,
    include_pdf_links: bool = True,
    max_pages: int = 200,
):
    """
    DLT source for SQA National Qualifications.

    Args:
        qualification_level: national_5, higher, or advanced_higher
        include_pdf_links: Extract PDF specification links
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with SQA pages and optionally PDF links
    """

    @dlt.resource(
        name="sqa_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def sqa_pages():
        """Crawled SQA qualification pages."""
        yield from _crawl_sqa_qualifications(qualification_level, None, max_pages)

    @dlt.resource(
        name="sqa_pdf_links",
        write_disposition="merge",
        primary_key=["url"],
    )
    def sqa_pdf_links():
        """SQA PDF specification links."""
        if include_pdf_links:
            for level in ["national_5", "higher", "advanced_higher"]:
                if qualification_level is None or qualification_level == level:
                    yield from _extract_sqa_pdf_links(level)

    return sqa_pages, sqa_pdf_links
