"""manx_vernacular_source — Manx (Gaelg) DLT source.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Adds the
DLT ingestion layer for the Manx vernacular (GV) sister-repo lift
pattern. Backs onto the official Isle of Man Government + Mooinjer
Vaggey + Manx National Heritage sources.

Manx has only ~2,000 speakers but is one of the 3 vernaculars with
actual PDF corpora (per the Phase 14 spec).
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterator

import dlt

import dlt_sources
from dlt_sources.common.firecrawl_source import crawl_website


MANX_VERNACULAR_URLS = {
    "iom_gov_im": "https://www.gov.im/education-training-and-careers/",
    "mooinjer_vaggey": "https://www.manxnationalheritage.im/",
    "culture_venn": "https://www.iomculture.im/",
}


def _crawl_manx_vernacular(max_pages: int = 100) -> Iterator[dict]:
    """Crawl Manx-medium education pages."""
    for page in crawl_website(
        base_url=MANX_VERNACULAR_URLS["iom_gov_im"],
        include_paths=[
            "/education-training-and-careers/*",
            "/about-the-government/departments/education-sport-and-culture/*",
        ],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["language"] = "gv"
        page["jurisdiction"] = "isle_of_man"
        page["vernacular"] = True
        page["nation"] = "isle_of_man"
        page["source"] = "gov_im"
        page["curriculum_framework"] = "gaelg_medium"
        page["indexed_at"] = datetime.now(UTC).isoformat()
        yield page


@dlt.source(name="manx_vernacular")
def manx_vernacular_source(
    max_pages: int = 100,
    include_pdf_specs: bool = True,
):
    """DLT source for Manx (Gaelg) education.

    Args:
        max_pages: Maximum number of pages to crawl.
        include_pdf_specs: Whether to emit PDF spec metadata.

    Returns:
        Two DLT resources: ``manx_vernacular_pages`` +
        ``manx_vernacular_specs`` (when ``include_pdf_specs``).
    """

    @dlt.resource(
        name="manx_vernacular_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages() -> Iterator[dict]:
        """Crawled Manx-medium education pages."""
        yield from _crawl_manx_vernacular(max_pages)

    @dlt.resource(
        name="manx_vernacular_specs",
        write_disposition="merge",
        primary_key=["source_url"],
    )
    def specs() -> Iterator[dict]:
        """Stub Manx subject specification metadata.

        Per the Phase 14 spec, GV is one of 3 vernaculars with
        actual PDF corpora.
        """
        if not include_pdf_specs:
            return
        yield {
            "source_url": "https://www.gov.im/education-training-and-careers/gaelg-medium-education",
            "subject_slug": "mathematics",
            "stage": "gcse",
            "language": "gv",
            "jurisdiction": "isle_of_man",
            "year": 2026,
            "indexed_at": datetime.now(UTC).isoformat(),
        }

    return pages, specs


__all__ = ["MANX_VERNACULAR_URLS", "manx_vernacular_source"]
