"""
DLT source for Scotland Insight National Benchmarking data.

Insight is the senior phase benchmarking tool used in Scotland
to measure school performance and attainment.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt

from ...common.firecrawl_source import crawl_website, scrape_page

INSIGHT_URLS = {
    "main": "https://www.gov.scot/policies/schools/school-performance/",
    "measures": "https://insight-guides.scotxed.net/support/InsightNationalBenchmarkingMeasures.htm",
}


def _crawl_insight_pages(max_pages: int = 50) -> Iterator[dict[str, Any]]:
    """
    Crawl Insight-related pages from gov.scot.

    Args:
        max_pages: Maximum pages to crawl

    Yields:
        Crawled page data
    """
    for page in crawl_website(
        base_url=INSIGHT_URLS["main"],
        include_paths=["/policies/schools/*", "/publications/*"],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "scotland"
        page["source"] = "insight"
        yield page


def _scrape_insight_measures() -> Iterator[dict[str, Any]]:
    """
    Scrape Insight benchmark measures documentation.

    Yields:
        Insight measure definitions
    """
    page = scrape_page(INSIGHT_URLS["measures"])

    if page.get("status") != "success":
        yield {
            "url": INSIGHT_URLS["measures"],
            "status": page.get("status"),
            "error": page.get("error"),
            "nation": "scotland",
            "source": "insight",
            "scraped_at": datetime.now(UTC).isoformat(),
        }
        return

    # Parse measures from content
    markdown = page.get("markdown", "")
    title = page.get("title", "Insight Measures")

    yield {
        "url": INSIGHT_URLS["measures"],
        "title": title,
        "content": markdown,
        "content_type": "measures_documentation",
        "nation": "scotland",
        "source": "insight",
        "status": "success",
        "scraped_at": datetime.now(UTC).isoformat(),
    }


@dlt.source(name="insight_benchmarking")
def insight_source(max_pages: int = 50):
    """
    DLT source for Insight National Benchmarking data.

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with pages and measures resources
    """

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        """Insight-related pages."""
        yield from _crawl_insight_pages(max_pages)

    @dlt.resource(
        name="measures",
        write_disposition="replace",
        primary_key=["url"],
    )
    def measures():
        """Insight benchmark measure definitions."""
        yield from _scrape_insight_measures()

    return pages, measures
