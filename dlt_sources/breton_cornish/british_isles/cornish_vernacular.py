"""cornish_vernacular_source — Cornish (Kernewek) DLT source.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Adds the
DLT ingestion layer for the Cornish vernacular (KW) sister-repo
lift pattern. Backs onto the official Cornwall Council + Golden
Tree Productions sources.

This is a sister-repo lift target — the full production source
will be developed in the ``ciancheiltis`` sister repo (Phase 8
sister-side mirrors). The Cianfhoghlaim side ships a working stub
that mirrors the structure of the other 6 vernacular sources.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterator

import dlt

import dlt_sources
from dlt_sources.common.firecrawl_source import crawl_website


CORNISH_VERNACULAR_URLS = {
    "cornwall_council_kernewek": "https://www.cornwall.gov.uk/education-and-learning/",
    "golden_tree": "https://goldentree.org.uk/",
    "kesson_lyther": "https://www.cornishdictionary.net/",
}


def _crawl_cornish_vernacular(max_pages: int = 100) -> Iterator[dict]:
    """Crawl Cornish-medium education pages."""
    for page in crawl_website(
        base_url=CORNISH_VERNACULAR_URLS["cornwall_council_kernewek"],
        include_paths=[
            "/education-and-learning/*",
            "/community-and-living/kernewek/*",
        ],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["language"] = "kw"
        page["jurisdiction"] = "cornwall"  # Cornwall
        page["vernacular"] = True
        page["nation"] = "england"
        page["source"] = "cornwall_council"
        page["curriculum_framework"] = "kernewek_medium"
        page["indexed_at"] = datetime.now(UTC).isoformat()
        yield page


@dlt.source(name="cornish_vernacular")
def cornish_vernacular_source(
    max_pages: int = 100,
    include_pdf_specs: bool = True,
):
    """DLT source for Cornish (Kernewek) education.

    Args:
        max_pages: Maximum number of pages to crawl.
        include_pdf_specs: Whether to emit PDF spec metadata.

    Returns:
        Two DLT resources: ``cornish_vernacular_pages`` +
        ``cornish_vernacular_specs`` (when ``include_pdf_specs``).
    """

    @dlt.resource(
        name="cornish_vernacular_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages() -> Iterator[dict]:
        """Crawled Cornish-medium education pages."""
        yield from _crawl_cornish_vernacular(max_pages)

    @dlt.resource(
        name="cornish_vernacular_specs",
        write_disposition="merge",
        primary_key=["source_url"],
    )
    def specs() -> Iterator[dict]:
        """Stub Cornish subject specification metadata."""
        if not include_pdf_specs:
            return
        yield {
            "source_url": "https://www.cornwall.gov.uk/education-and-learning/school-resources/kernewek/",
            "subject_slug": "mathematics",
            "stage": "gcse",
            "language": "kw",
            "jurisdiction": "cornwall",
            "year": 2026,
            "indexed_at": datetime.now(UTC).isoformat(),
        }

    return pages, specs


__all__ = ["CORNISH_VERNACULAR_URLS", "cornish_vernacular_source"]
