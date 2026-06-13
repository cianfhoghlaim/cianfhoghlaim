"""
DLT sources for Channel Islands education data.

Provides sources for:
- Jersey (Government of Jersey)
- Guernsey (States of Guernsey)
"""

from collections.abc import Iterator
from typing import Any

import dlt

from ...common.firecrawl_source import crawl_website

CHANNEL_ISLANDS_URLS = {
    "jersey": {
        "education": "https://www.gov.je/Education/",
        "schools": "https://www.gov.je/Education/Schools/",
    },
    "guernsey": {
        "education": "https://www.gov.gg/education",
        "schools": "https://www.gov.gg/schools",
    },
}


def _crawl_jersey_education(max_pages: int = 100) -> Iterator[dict[str, Any]]:
    """
    Crawl Jersey education pages.

    Args:
        max_pages: Maximum pages to crawl

    Yields:
        Crawled page data
    """
    for page in crawl_website(
        base_url=CHANNEL_ISLANDS_URLS["jersey"]["education"],
        include_paths=["/Education/*"],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "jersey"
        page["source"] = "gov_je"
        yield page


def _crawl_guernsey_education(max_pages: int = 100) -> Iterator[dict[str, Any]]:
    """
    Crawl Guernsey education pages.

    Args:
        max_pages: Maximum pages to crawl

    Yields:
        Crawled page data
    """
    for page in crawl_website(
        base_url=CHANNEL_ISLANDS_URLS["guernsey"]["education"],
        include_paths=["/education*", "/schools*"],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "guernsey"
        page["source"] = "gov_gg"
        yield page


@dlt.source(name="jersey_education")
def jersey_source(max_pages: int = 100):
    """
    DLT source for Jersey education data.

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
    def pages():
        """Jersey education pages."""
        yield from _crawl_jersey_education(max_pages)

    return pages


@dlt.source(name="guernsey_education")
def guernsey_source(max_pages: int = 100):
    """
    DLT source for Guernsey education data.

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
    def pages():
        """Guernsey education pages."""
        yield from _crawl_guernsey_education(max_pages)

    return pages
