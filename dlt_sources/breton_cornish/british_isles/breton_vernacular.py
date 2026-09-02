"""breton_vernacular_source — Breton (Brezhoneg) DLT source.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Adds the
DLT ingestion layer for the Breton vernacular (BR) sister-repo
lift pattern. Backs onto the official Rennes 2 + Ofis ar Brezhoneg
sources.

This is a sister-repo lift target — the full production source will
be developed in the ``ciancheiltis`` sister repo (Phase 8 sister-side
mirrors). The Cianfhoghlaim side ships a working stub that mirrors
the structure of the other 6 vernacular sources.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterator

import dlt

import dlt_sources
from dlt_sources.common.firecrawl_source import crawl_website


BRETON_VERNACULAR_URLS = {
    "ofis_ar_brezhoneg": "https://www.ofis-bzh.org/",
    "rennes_2_brezhoneg": "https://www.univ-rennes2.fr/brezhoneg",
    "ens_brezhoneg": "https://www.ens-rennes.fr/brezhoneg",
}


def _crawl_breton_vernacular(max_pages: int = 100) -> Iterator[dict]:
    """Crawl Breton-medium education pages."""
    for page in crawl_website(
        base_url=BRETON_VERNACULAR_URLS["ofis_ar_brezhoneg"],
        include_paths=["/*"],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["language"] = "br"
        page["jurisdiction"] = "breizh"  # Brittany
        page["vernacular"] = True
        page["nation"] = "france"
        page["source"] = "ofis_ar_brezhoneg"
        page["curriculum_framework"] = "brezhoneg_medium"
        page["indexed_at"] = datetime.now(UTC).isoformat()
        yield page


@dlt.source(name="breton_vernacular")
def breton_vernacular_source(
    max_pages: int = 100,
    include_pdf_specs: bool = True,
):
    """DLT source for Breton (Brezhoneg) education.

    Args:
        max_pages: Maximum number of pages to crawl.
        include_pdf_specs: Whether to emit PDF spec metadata.

    Returns:
        Two DLT resources: ``breton_vernacular_pages`` +
        ``breton_vernacular_specs`` (when ``include_pdf_specs``).
    """

    @dlt.resource(
        name="breton_vernacular_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages() -> Iterator[dict]:
        """Crawled Breton-medium education pages."""
        yield from _crawl_breton_vernacular(max_pages)

    @dlt.resource(
        name="breton_vernacular_specs",
        write_disposition="merge",
        primary_key=["source_url"],
    )
    def specs() -> Iterator[dict]:
        """Stub Breton subject specification metadata."""
        if not include_pdf_specs:
            return
        yield {
            "source_url": "https://www.ofis-bzh.org/fr/ressources-pedagogiques",
            "subject_slug": "mathematics",
            "stage": "lycee",
            "language": "br",
            "jurisdiction": "breizh",
            "year": 2026,
            "indexed_at": datetime.now(UTC).isoformat(),
        }

    return pages, specs


__all__ = ["BRETON_VERNACULAR_URLS", "breton_vernacular_source"]
