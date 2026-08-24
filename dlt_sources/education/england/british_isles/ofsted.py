import dlt

"""
DLT source for Ofsted inspection reports.

Scrapes inspection reports from reports.ofsted.gov.uk
to extract inspection dates, judgements, and outcomes.
"""

import contextlib
from collections.abc import Iterator
from typing import Any

import dlt_sources

from dlt_sources.common.firecrawl_source import crawl_website, scrape_page


def _parse_inspection_from_page(page_data: dict[str, Any]) -> dict[str, Any]:
    """Extract structured inspection data from scraped page."""
    markdown = page_data.get("markdown", "")
    url = page_data.get("url", "")

    # Extract URN from URL (e.g., /provider/16/urn/123456)
    urn = None
    if "/urn/" in url:
        with contextlib.suppress(Exception):
            urn = url.split("/urn/")[-1].split("/")[0]

    # Parse inspection data from markdown
    # This is simplified - real implementation would use more robust parsing
    inspection_data = {
        "url": url,
        "urn": urn,
        "title": page_data.get("title"),
        "markdown": markdown,
        "links": page_data.get("links", []),
        "nation": "england",
        "source": "ofsted",
        "status": page_data.get("status"),
        "scraped_at": page_data.get("crawled_at") or page_data.get("scraped_at"),
    }

    # Try to extract key fields from markdown
    lines = markdown.split("\n") if markdown else []
    for line in lines:
        line_lower = line.lower()
        if "overall effectiveness" in line_lower:
            # Extract rating (Outstanding, Good, Requires Improvement, Inadequate)
            for rating in ["outstanding", "good", "requires improvement", "inadequate"]:
                if rating in line_lower:
                    inspection_data["overall_effectiveness"] = rating.title()
                    break
        elif "inspection date" in line_lower or "date of inspection" in line_lower:
            # Try to extract date
            import re

            date_match = re.search(r"\d{1,2}\s+\w+\s+\d{4}", line)
            if date_match:
                inspection_data["inspection_date"] = date_match.group()

    return inspection_data


def _crawl_ofsted_reports(
    provider_type: str | None = None,
    max_pages: int = 500,
) -> Iterator[dict[str, Any]]:
    """
    Crawl Ofsted inspection reports.

    Args:
        provider_type: Filter by provider type (schools, further-education, etc.)
        max_pages: Maximum pages to crawl

    Yields:
        Parsed inspection reports
    """
    base_url = "https://reports.ofsted.gov.uk"

    include_paths = ["/provider/*"]
    if provider_type:
        include_paths = [f"/provider/{provider_type}/*"]

    for page in crawl_website(
        base_url=base_url,
        include_paths=include_paths,
        exclude_paths=["/search", "/login", "/account"],
        max_pages=max_pages,
        max_depth=3,
    ):
        yield _parse_inspection_from_page(page)


def _scrape_ofsted_search(
    search_query: str,
    max_results: int = 100,
) -> Iterator[dict[str, Any]]:
    """
    Search Ofsted reports and scrape results.

    Args:
        search_query: Search query
        max_results: Maximum results to fetch

    Yields:
        Scraped inspection reports
    """
    base_url = f"https://reports.ofsted.gov.uk/search?q={search_query}"

    # First scrape search results page
    search_page = scrape_page(base_url)

    # Extract report URLs from links
    links = search_page.get("links", [])
    report_urls = [
        link for link in links if link and "/provider/" in link and "/urn/" in link
    ][:max_results]

    # Scrape each report
    for url in report_urls:
        if not url.startswith("http"):
            url = f"https://reports.ofsted.gov.uk{url}"
        page = scrape_page(url)
        yield _parse_inspection_from_page(page)


@dlt.source(name="ofsted")
def ofsted_source(
    provider_type: str | None = None,
    max_pages: int = 500,
    search_query: str | None = None,
):
    """
    DLT source for Ofsted inspection reports.

    Args:
        provider_type: Filter by provider type (e.g., "16" for schools)
        max_pages: Maximum pages to crawl
        search_query: Optional search query instead of crawling

    Returns:
        DLT source with inspection_reports resource
    """

    @dlt.resource(
        name="inspection_reports",
        write_disposition="merge",
        primary_key=["urn", "inspection_date"],
    )
    def inspection_reports():
        """Ofsted inspection reports."""
        if search_query:
            yield from _scrape_ofsted_search(search_query, max_results=max_pages)
        else:
            yield from _crawl_ofsted_reports(provider_type, max_pages)

    return inspection_reports
