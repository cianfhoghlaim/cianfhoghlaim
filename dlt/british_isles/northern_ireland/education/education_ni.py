"""
DLT source for education-ni.gov.uk.

Department of Education Northern Ireland website
provides school statistics, policies, and publications.
"""

from collections.abc import Iterator
from typing import Any

import dlt

from cianfhoghlaim.dlt.common.firecrawl_source import crawl_website

EDUCATION_NI_URLS = {
    "main": "https://www.education-ni.gov.uk",
    "statistics": "https://www.education-ni.gov.uk/topics/statistics-and-research",
    "publications": "https://www.education-ni.gov.uk/publications",
}


def _crawl_education_ni(
    section: str | None = None,
    max_pages: int = 200,
) -> Iterator[dict[str, Any]]:
    """
    Crawl education-ni.gov.uk pages.

    Args:
        section: Specific section to crawl (statistics, publications)
        max_pages: Maximum pages to crawl

    Yields:
        Crawled page data
    """
    if section and section in EDUCATION_NI_URLS:
        base_url = EDUCATION_NI_URLS[section]
    else:
        base_url = EDUCATION_NI_URLS["main"]

    include_paths = [
        "/topics/statistics*",
        "/publications/*",
        "/articles/*",
    ]

    for page in crawl_website(
        base_url=base_url,
        include_paths=include_paths,
        exclude_paths=["/search", "/contact-us"],
        max_pages=max_pages,
        max_depth=4,
    ):
        page["nation"] = "northern_ireland"
        page["source"] = "education_ni"
        page["section"] = section

        # Extract publication type if present
        url = page.get("url", "")
        if "/publications/" in url:
            page["content_type"] = "publication"
        elif "/statistics" in url:
            page["content_type"] = "statistics"

        yield page


@dlt.source(name="education_ni")
def education_ni_source(
    section: str | None = None,
    max_pages: int = 200,
):
    """
    DLT source for Department of Education NI.

    Args:
        section: Section to crawl (statistics, publications, or None for all)
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
        """Education NI website pages."""
        yield from _crawl_education_ni(section, max_pages)

    return pages
