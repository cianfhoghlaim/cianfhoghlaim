"""
DLT source for Estyn inspection reports.

Estyn is the education and training inspectorate for Wales.
https://www.estyn.gov.wales/

Supports both English and Welsh language content.
"""

from collections.abc import Iterator
from typing import Any

import dlt

from cianfhoghlaim.dlt.common.firecrawl_source import crawl_website

ESTYN_URLS = {
    "main": "https://www.estyn.gov.wales",
    "inspection_reports": "https://www.estyn.gov.wales/inspection-reports",
    "welsh": "https://www.estyn.llyw.cymru",  # Welsh language site
}


def _parse_estyn_inspection(page_data: dict[str, Any]) -> dict[str, Any]:
    """Extract structured inspection data from scraped page."""
    markdown = page_data.get("markdown", "")
    url = page_data.get("url", "")

    inspection_data = {
        "url": url,
        "title": page_data.get("title"),
        "markdown": markdown,
        "links": page_data.get("links", []),
        "nation": "wales",
        "source": "estyn",
        "status": page_data.get("status"),
        "scraped_at": page_data.get("crawled_at") or page_data.get("scraped_at"),
    }

    # Detect language from URL
    inspection_data["language"] = "cy" if "llyw.cymru" in url else "en"

    # Parse key fields from markdown
    lines = markdown.split("\n") if markdown else []

    for line in lines:
        line_lower = line.lower()

        # Welsh medium indicator
        if "cyfrwng cymraeg" in line_lower or "welsh medium" in line_lower:
            inspection_data["welsh_medium"] = True

        # Inspection date
        if "inspection date" in line_lower or "dyddiad arolygiad" in line_lower:
            import re

            date_match = re.search(r"\d{1,2}\s+\w+\s+\d{4}", line)
            if date_match:
                inspection_data["inspection_date"] = date_match.group()

        # Overall judgement
        for judgement in ["excellent", "good", "adequate", "unsatisfactory"]:
            welsh_judgements = {
                "excellent": "rhagorol",
                "good": "da",
                "adequate": "digonol",
                "unsatisfactory": "anfoddhaol",
            }
            if judgement in line_lower or welsh_judgements[judgement] in line_lower:
                inspection_data["overall_effectiveness"] = judgement.title()
                break

    return inspection_data


def _crawl_estyn_inspections(
    language: str = "en",
    max_pages: int = 300,
) -> Iterator[dict[str, Any]]:
    """
    Crawl Estyn inspection reports.

    Args:
        language: Language (en or cy for Welsh)
        max_pages: Maximum pages to crawl

    Yields:
        Parsed inspection reports
    """
    base_url = ESTYN_URLS["welsh"] if language == "cy" else ESTYN_URLS["inspection_reports"]

    for page in crawl_website(
        base_url=base_url,
        include_paths=["/inspection-reports/*", "/adroddiadau-arolygu/*"],
        exclude_paths=["/search", "/login", "/account"],
        max_pages=max_pages,
        max_depth=3,
    ):
        yield _parse_estyn_inspection(page)


@dlt.source(name="estyn")
def estyn_source(
    language: str = "en",
    max_pages: int = 300,
    include_welsh: bool = True,
):
    """
    DLT source for Estyn inspection reports.

    Args:
        language: Primary language (en or cy)
        max_pages: Maximum pages to crawl
        include_welsh: Whether to also crawl Welsh language site

    Returns:
        DLT source with inspection_reports resource
    """

    @dlt.resource(
        name="inspection_reports",
        write_disposition="merge",
        primary_key=["url"],
    )
    def inspection_reports():
        """Estyn inspection reports."""
        # Crawl primary language
        yield from _crawl_estyn_inspections(language, max_pages)

        # Optionally crawl Welsh language site
        if include_welsh and language != "cy":
            yield from _crawl_estyn_inspections("cy", max_pages // 2)

    return inspection_reports
