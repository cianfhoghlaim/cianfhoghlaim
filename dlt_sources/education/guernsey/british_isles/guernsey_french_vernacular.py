"""guernsey_french_vernacular_source — Guernsey French (Guernésiais) DLT source.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Adds the
DLT ingestion layer for the Guernsey French vernacular (FR_GG)
sister-repo lift pattern. Backs onto the official States of Guernsey
+ L'Office du Guernesiais sources.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterator

import dlt

import dlt_sources
from dlt_sources.common.firecrawl_source import crawl_website


GUERNSEY_FRENCH_VERNACULAR_URLS = {
    "states_of_guernsey": "https://www.gov.gg/education/Pages/default.aspx",
    "guernesiaise_society": "https://www.guernseysociety.org.gg/",
    "les_piaiches": "https://www.lespiaiches.org.gg/",
}


def _crawl_guernsey_french_vernacular(max_pages: int = 100) -> Iterator[dict]:
    """Crawl Guernsey French (Guernésiais) education pages."""
    for page in crawl_website(
        base_url=GUERNSEY_FRENCH_VERNACULAR_URLS["states_of_guernsey"],
        include_paths=[
            "/education/*",
        ],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["language"] = "fr-gg"
        page["jurisdiction"] = "guernsey"
        page["vernacular"] = True
        page["nation"] = "guernsey"
        page["source"] = "gov_gg"
        page["curriculum_framework"] = "guernesiaise_medium"
        page["indexed_at"] = datetime.now(UTC).isoformat()
        yield page


@dlt.source(name="guernsey_french_vernacular")
def guernsey_french_vernacular_source(
    max_pages: int = 100,
    include_pdf_specs: bool = True,
):
    """DLT source for Guernsey French (Guernésiais) education.

    Args:
        max_pages: Maximum number of pages to crawl.
        include_pdf_specs: Whether to emit PDF spec metadata.

    Returns:
        Two DLT resources: ``guernsey_french_vernacular_pages`` +
        ``guernsey_french_vernacular_specs`` (when ``include_pdf_specs``).
    """

    @dlt.resource(
        name="guernsey_french_vernacular_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages() -> Iterator[dict]:
        """Crawled Guernsey French-medium education pages."""
        yield from _crawl_guernsey_french_vernacular(max_pages)

    @dlt.resource(
        name="guernsey_french_vernacular_specs",
        write_disposition="merge",
        primary_key=["source_url"],
    )
    def specs() -> Iterator[dict]:
        """Stub Guernsey French subject specification metadata."""
        if not include_pdf_specs:
            return
        yield {
            "source_url": "https://www.gov.gg/education/curriculum/primary",
            "subject_slug": "mathematics",
            "stage": "gcse",
            "language": "fr-gg",
            "jurisdiction": "guernsey",
            "year": 2026,
            "indexed_at": datetime.now(UTC).isoformat(),
        }

    return pages, specs


__all__ = ["GUERNSEY_FRENCH_VERNACULAR_URLS", "guernsey_french_vernacular_source"]
