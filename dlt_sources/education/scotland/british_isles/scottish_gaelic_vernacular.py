"""scottish_gaelic_vernacular_source — Scottish Gaelic (Gàidhlig) DLT source.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Adds the
DLT ingestion layer for the Scottish Gaelic vernacular (GD)
sister-repo lift pattern. Backs onto the official SQA + Education
Scotland sources.

The source yields a ``scottish_gaelic_vernacular_pages`` resource
(crawled Gàidhlig-medium pages) and a
``scottish_gaelic_vernacular_specs`` resource (extracted PDF
specification metadata). Both are merged into
``dlt/british_isles/scotland/education/scottish_gaelic_vernacular/{pages,specs}.jsonl``.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterator

import dlt

import dlt_sources
from dlt_sources.common.firecrawl_source import crawl_website


SCOTTISH_GAELIC_VERNACULAR_URLS = {
    "sqa_gaelic": "https://www.sqa.org.uk/sqa/45620.html",
    "education_scotland_gaelic": "https://education.gov.scot/parentzone/learning-at-home/gaelic-medium-education/",
    "foghlam_tron_ghaidhlig": "https://www.gaidhlig.org/",
    "storlann": "https://www.storlann.co.uk/",
}


def _crawl_scottish_gaelic_vernacular(max_pages: int = 100) -> Iterator[dict]:
    """Crawl Scottish Gaelic medium-education pages."""
    for page in crawl_website(
        base_url=SCOTTISH_GAELIC_VERNACULAR_URLS["education_scotland_gaelic"],
        include_paths=[
            "/parentzone/*",
            "/learning-in-scotland/*",
        ],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["language"] = "gd"
        page["jurisdiction"] = "scotland"
        page["vernacular"] = True
        page["nation"] = "scotland"
        page["source"] = "education_gov_scot"
        page["curriculum_framework"] = "foghlam_tron_ghaidhlig"
        page["indexed_at"] = datetime.now(UTC).isoformat()
        yield page


@dlt.source(name="scottish_gaelic_vernacular")
def scottish_gaelic_vernacular_source(
    max_pages: int = 100,
    include_pdf_specs: bool = True,
):
    """DLT source for Scottish Gaelic (Gàidhlig) education.

    Args:
        max_pages: Maximum number of pages to crawl.
        include_pdf_specs: Whether to emit PDF spec metadata.

    Returns:
        Two DLT resources: ``scottish_gaelic_vernacular_pages`` +
        ``scottish_gaelic_vernacular_specs`` (when ``include_pdf_specs``).
    """

    @dlt.resource(
        name="scottish_gaelic_vernacular_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages() -> Iterator[dict]:
        """Crawled Gàidhlig-medium education pages."""
        yield from _crawl_scottish_gaelic_vernacular(max_pages)

    @dlt.resource(
        name="scottish_gaelic_vernacular_specs",
        write_disposition="merge",
        primary_key=["source_url"],
    )
    def specs() -> Iterator[dict]:
        """Stub Scottish Gaelic subject specification metadata."""
        if not include_pdf_specs:
            return
        yield {
            "source_url": "https://www.sqa.org.uk/sqa/56992.html",
            "subject_slug": "mathematics",
            "stage": "higher",
            "language": "gd",
            "jurisdiction": "scotland",
            "year": 2026,
            "indexed_at": datetime.now(UTC).isoformat(),
        }

    return pages, specs


__all__ = ["SCOTTISH_GAELIC_VERNACULAR_URLS", "scottish_gaelic_vernacular_source"]
