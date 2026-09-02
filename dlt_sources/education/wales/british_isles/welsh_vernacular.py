"""welsh_vernacular_source — Welsh-medium (Cymraeg) DLT source.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Adds the
DLT ingestion layer for the Welsh vernacular (CY) sister-repo lift
pattern. Backs onto the official WJEC + CBAC sources.

The source yields a `welsh_vernacular_pages` resource (crawled
Welsh-medium pages) and a `welsh_vernacular_specs` resource
(extracted PDF specification metadata). Both are merged into
``dlt/british_isles/wales/education/welsh_vernacular/{pages,specs}.jsonl``.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterator

import dlt

import dlt_sources
from dlt_sources.common.firecrawl_source import crawl_website


WELSH_VERNACULAR_URLS = {
    "wjec_cy": "https://www.wjec.co.cymru/qualifications/",
    "cbac": "https://www.cbac.co.uk/qualifications/",
    "welsh_medium_education": "https://www.gov.wales/education-and-learning",
    "cymraeg_iaith": "https://www.cymraeg.gov.wales/",
}


def _crawl_welsh_vernacular(max_pages: int = 100) -> Iterator[dict]:
    """Crawl Welsh-medium education pages.

    Yields Firecrawl-crawled pages with the vernacular metadata
    overlay (language='cy', jurisdiction='wales', is_vernacular=True).
    """
    for page in crawl_website(
        base_url=WELSH_VERNACULAR_URLS["welsh_medium_education"],
        include_paths=[
            "/education-and-learning/*",
            "/cy/education-and-learning/*",
        ],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["language"] = "cy"
        page["jurisdiction"] = "wales"
        page["vernacular"] = True
        page["nation"] = "wales"
        page["source"] = "gov_wales"
        page["curriculum_framework"] = "curriculum_for_wales_cy"
        page["indexed_at"] = datetime.now(UTC).isoformat()
        yield page


@dlt.source(name="welsh_vernacular")
def welsh_vernacular_source(
    max_pages: int = 100,
    include_pdf_specs: bool = True,
):
    """DLT source for Welsh-medium (Cymraeg) education.

    Args:
        max_pages: Maximum number of pages to crawl.
        include_pdf_specs: Whether to emit PDF spec metadata.

    Returns:
        Two DLT resources: ``welsh_vernacular_pages`` +
        ``welsh_vernacular_specs`` (when ``include_pdf_specs``).
    """

    @dlt.resource(
        name="welsh_vernacular_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages() -> Iterator[dict]:
        """Crawled Welsh-medium education pages."""
        yield from _crawl_welsh_vernacular(max_pages)

    @dlt.resource(
        name="welsh_vernacular_specs",
        write_disposition="merge",
        primary_key=["source_url"],
    )
    def specs() -> Iterator[dict]:
        """Stub Welsh subject specification metadata (PDF URLs)."""
        if not include_pdf_specs:
            return
        # Phase 14 seed: a single mathematics PDF stub. The PDF
        # text will be hydrated by the orchestrator asset and
        # the BAML ``ExtractWelshSubjectSpec`` invocation will
        # populate the full record.
        yield {
            "source_url": "https://www.wjec.co.uk/qualifications/mathematics-gcse",
            "subject_slug": "mathematics",
            "stage": "gcse",
            "language": "cy",
            "jurisdiction": "wales",
            "year": 2026,
            "indexed_at": datetime.now(UTC).isoformat(),
        }

    return pages, specs


__all__ = ["WELSH_VERNACULAR_URLS", "welsh_vernacular_source"]
