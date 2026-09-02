"""jersey_french_vernacular_source — Jersey French (Jèrriais) DLT source.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Adds the
DLT ingestion layer for the Jersey French vernacular (FR_JE)
sister-repo lift pattern. Backs onto the official States of Jersey
+ L'Office du Jèrriais sources.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterator

import dlt

import dlt_sources
from dlt_sources.common.firecrawl_source import crawl_website


JERSEY_FRENCH_VERNACULAR_URLS = {
    "states_of_jersey": "https://www.gov.je/education/Pages/default.aspx",
    "office_du_jerriais": "https://www.officedujerriais.org.je/",
}


def _crawl_jersey_french_vernacular(max_pages: int = 100) -> Iterator[dict]:
    """Crawl Jersey French (Jèrriais) education pages."""
    for page in crawl_website(
        base_url=JERSEY_FRENCH_VERNACULAR_URLS["states_of_jersey"],
        include_paths=[
            "/education/*",
            "/Leisure/Events/*",
        ],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["language"] = "fr-je"
        page["jurisdiction"] = "jersey"
        page["vernacular"] = True
        page["nation"] = "jersey"
        page["source"] = "gov_je"
        page["curriculum_framework"] = "jerriais_medium"
        page["indexed_at"] = datetime.now(UTC).isoformat()
        yield page


@dlt.source(name="jersey_french_vernacular")
def jersey_french_vernacular_source(
    max_pages: int = 100,
    include_pdf_specs: bool = True,
):
    """DLT source for Jersey French (Jèrriais) education.

    Args:
        max_pages: Maximum number of pages to crawl.
        include_pdf_specs: Whether to emit PDF spec metadata.

    Returns:
        Two DLT resources: ``jersey_french_vernacular_pages`` +
        ``jersey_french_vernacular_specs`` (when ``include_pdf_specs``).
    """

    @dlt.resource(
        name="jersey_french_vernacular_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages() -> Iterator[dict]:
        """Crawled Jersey French-medium education pages."""
        yield from _crawl_jersey_french_vernacular(max_pages)

    @dlt.resource(
        name="jersey_french_vernacular_specs",
        write_disposition="merge",
        primary_key=["source_url"],
    )
    def specs() -> Iterator[dict]:
        """Stub Jersey French subject specification metadata."""
        if not include_pdf_specs:
            return
        yield {
            "source_url": "https://www.gov.je/education/primarycurriculum/pages/default.aspx",
            "subject_slug": "mathematics",
            "stage": "gcse",
            "language": "fr-je",
            "jurisdiction": "jersey",
            "year": 2026,
            "indexed_at": datetime.now(UTC).isoformat(),
        }

    return pages, specs


__all__ = ["JERSEY_FRENCH_VERNACULAR_URLS", "jersey_french_vernacular_source"]
