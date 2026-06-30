"""
oideachais.cianfhoghlaim.dlt.british_isles.isle_of_man.education.isle_of_man — Isle of Man education DLT source.

Moved from `dlt_sources/crown_dependencies/isle_of_man.py` in
Phase 3E (Round 11 oideachais audit). Single-source file — no helpers
to extract.
"""

from __future__ import annotations

from collections.abc import Iterator

import dlt
from cianfhoghlaim.dlt.common.firecrawl_source import crawl_website

IOM_URLS = {
    "education": "https://www.gov.im/categories/education-training-and-careers/",
    "schools": "https://www.gov.im/categories/education-training-and-careers/schools/",
}


def _crawl_iom_education(max_pages: int = 100) -> Iterator[dict]:
    """
    Crawl Isle of Man education pages.

    Args:
        max_pages: Maximum pages to crawl

    Yields:
        Crawled page data
    """
    for page in crawl_website(
        base_url=IOM_URLS["education"],
        include_paths=[
            "/categories/education-training-and-careers/*",
            "/about-the-government/departments/education-sport-and-culture/*",
        ],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "isle_of_man"
        page["source"] = "gov_im"
        yield page


@dlt.source(name="isle_of_man")
def isle_of_man_source(max_pages: int = 100):
    """
    DLT source for Isle of Man education data.

    Department of Education, Sport and Culture (DESC)
    provides education statistics and school information.

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with pages resource
    """

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages() -> Iterator[dict]:
        """Isle of Man education pages."""
        yield from _crawl_iom_education(max_pages)

    return pages


__all__ = ["IOM_URLS", "isle_of_man_source"]
