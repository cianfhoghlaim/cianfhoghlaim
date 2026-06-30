"""
DLT source for Scottish Government education statistics.

Crawls and extracts data from:
https://www.gov.scot/collections/school-education-statistics/

Includes:
- Attainment and leaver destinations
- Teacher census
- School meals
- Pupil census
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt

from ...common.firecrawl_source import crawl_website, scrape_page

# Key statistics publications
SCOT_STATISTICS = {
    "attainment": {
        "url": "https://www.gov.scot/collections/school-education-statistics/#attainmentandqualifications",
        "description": "Attainment and qualifications",
    },
    "leaver_destinations": {
        "url": "https://www.gov.scot/collections/school-education-statistics/#leaverdestinations",
        "description": "School leaver destinations",
    },
    "teacher_census": {
        "url": "https://www.gov.scot/collections/school-education-statistics/#teachercensus",
        "description": "Teacher and support staff census",
    },
    "school_meals": {
        "url": "https://www.gov.scot/collections/school-education-statistics/#schoolmeals",
        "description": "School meals and free school meal registrations",
    },
    "pupil_census": {
        "url": "https://www.gov.scot/collections/school-education-statistics/#pupilcensus",
        "description": "Pupil census",
    },
    "school_contact": {
        "url": "https://www.gov.scot/collections/school-education-statistics/#schoolcontact",
        "description": "School contact details",
    },
}


def _crawl_gov_scot_statistics(
    category: str | None = None,
    max_pages: int = 200,
) -> Iterator[dict[str, Any]]:
    """
    Crawl Scottish Government education statistics.

    Args:
        category: Specific category to crawl (e.g., "attainment")
        max_pages: Maximum pages to crawl

    Yields:
        Crawled page data with metadata
    """
    base_url = "https://www.gov.scot/collections/school-education-statistics/"

    include_paths = [
        "/publications/*",
        "/binaries/*",
        "/collections/school-education-statistics/*",
    ]

    if category and category in SCOT_STATISTICS:
        # Start from specific category URL
        base_url = SCOT_STATISTICS[category]["url"]

    for page in crawl_website(
        base_url=base_url,
        include_paths=include_paths,
        exclude_paths=["/about/*", "/accessibility/*"],
        max_pages=max_pages,
        max_depth=4,
    ):
        # Add Scotland-specific metadata
        page["nation"] = "scotland"
        page["source"] = "gov_scot"
        page["category"] = category

        # Try to extract publication date from markdown
        markdown = page.get("markdown", "")
        if "Published" in markdown:
            import re

            date_match = re.search(r"Published:?\s*(\d{1,2}\s+\w+\s+\d{4})", markdown)
            if date_match:
                page["published_date"] = date_match.group(1)

        yield page


def _extract_excel_links(base_url: str) -> Iterator[dict[str, Any]]:
    """
    Extract Excel/ODS download links from gov.scot pages.

    Many Scottish statistics are published as Excel downloads.
    """
    page = scrape_page(base_url)
    links = page.get("links", [])

    for link in links:
        if not link:
            continue

        # Check for data file extensions
        lower_link = link.lower()
        if any(ext in lower_link for ext in [".xlsx", ".xls", ".ods", ".csv"]):
            file_type = "excel"
            if ".csv" in lower_link:
                file_type = "csv"
            elif ".ods" in lower_link:
                file_type = "ods"

            yield {
                "url": link if link.startswith("http") else f"https://www.gov.scot{link}",
                "file_type": file_type,
                "source_page": base_url,
                "nation": "scotland",
                "source": "gov_scot",
                "discovered_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="gov_scot_statistics")
def gov_scot_source(
    category: str | None = None,
    max_pages: int = 200,
    include_downloads: bool = True,
):
    """
    DLT source for Scottish Government education statistics.

    Args:
        category: Specific category to crawl (attainment, leaver_destinations, etc.)
        max_pages: Maximum pages to crawl
        include_downloads: Whether to extract download links

    Returns:
        DLT source with pages and optionally downloads resources
    """

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        """Crawled statistics pages."""
        yield from _crawl_gov_scot_statistics(category, max_pages)

    @dlt.resource(
        name="downloads",
        write_disposition="merge",
        primary_key=["url"],
    )
    def downloads():
        """Excel and CSV download links."""
        if include_downloads:
            for cat_info in SCOT_STATISTICS.values():
                yield from _extract_excel_links(cat_info["url"])

    return pages, downloads
