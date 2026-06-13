"""
DLT source for Scottish Index of Multiple Deprivation (SIMD).

SIMD is the Scottish Government's official tool for identifying
areas of deprivation, used for educational attainment analysis.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt

from ...common.firecrawl_source import crawl_website, scrape_page

SIMD_URLS = {
    "main": "https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/",
    "data": "https://www.gov.scot/publications/scottish-index-of-multiple-deprivation-2020v2-data-zone-look-up/",
    "interactive": "https://simd.scot/",
}


def _crawl_simd_pages(max_pages: int = 50) -> Iterator[dict[str, Any]]:
    """
    Crawl SIMD documentation and data pages.

    Args:
        max_pages: Maximum pages to crawl

    Yields:
        Crawled page data
    """
    for page in crawl_website(
        base_url=SIMD_URLS["main"],
        include_paths=[
            "/collections/scottish-index-of-multiple-deprivation*",
            "/publications/scottish-index-of-multiple-deprivation*",
        ],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "scotland"
        page["source"] = "simd"
        yield page


def _extract_simd_download_links() -> Iterator[dict[str, Any]]:
    """
    Extract SIMD data download links.

    Yields:
        Download URLs for SIMD data files
    """
    page = scrape_page(SIMD_URLS["data"])
    links = page.get("links", [])

    for link in links:
        if not link:
            continue

        lower_link = link.lower()
        if any(ext in lower_link for ext in [".xlsx", ".csv", ".zip"]):
            file_type = "excel"
            if ".csv" in lower_link:
                file_type = "csv"
            elif ".zip" in lower_link:
                file_type = "zip"

            yield {
                "url": link if link.startswith("http") else f"https://www.gov.scot{link}",
                "file_type": file_type,
                "dataset": "simd_2020",
                "source_page": SIMD_URLS["data"],
                "nation": "scotland",
                "source": "simd",
                "discovered_at": datetime.now(UTC).isoformat(),
            }


def _scrape_simd_interactive() -> Iterator[dict[str, Any]]:
    """
    Scrape information from SIMD interactive site.

    The simd.scot site provides an interactive map and data explorer.
    """
    page = scrape_page(SIMD_URLS["interactive"])

    yield {
        "url": SIMD_URLS["interactive"],
        "title": page.get("title", "SIMD Interactive"),
        "description": page.get("description"),
        "markdown": page.get("markdown"),
        "content_type": "interactive_tool",
        "nation": "scotland",
        "source": "simd",
        "status": page.get("status"),
        "scraped_at": datetime.now(UTC).isoformat(),
    }


@dlt.source(name="simd")
def simd_source(max_pages: int = 50):
    """
    DLT source for Scottish Index of Multiple Deprivation.

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with pages, downloads, and interactive resources
    """

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        """SIMD documentation pages."""
        yield from _crawl_simd_pages(max_pages)

    @dlt.resource(
        name="downloads",
        write_disposition="merge",
        primary_key=["url"],
    )
    def downloads():
        """SIMD data download links."""
        yield from _extract_simd_download_links()

    @dlt.resource(
        name="interactive",
        write_disposition="replace",
        primary_key=["url"],
    )
    def interactive():
        """SIMD interactive tool information."""
        yield from _scrape_simd_interactive()

    return pages, downloads, interactive
