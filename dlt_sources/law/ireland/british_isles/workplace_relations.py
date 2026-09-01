"""
cianfhoghlaim.cianfhoghlaim.dlt.british_isles.ireland.law.workplace_relations —
Workplace Relations Commission (WRC) of Ireland.

Source: `https://workplacerelations.ie/en/` — the ~6,000 published
Adjudication Decisions per year covering unfair dismissal, employment
equality, payment of wages, working time, redundancy, etc.

Covers 2 DLT resources:

- `pages`     — procedures, complaint-type pages, forms, news
- `decisions` — published WRC Adjudication Decisions (merged on `case_ref`)

Honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/workplacerelations.ie/`.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import structlog

import dlt_sources

logger = structlog.get_logger(__name__)

from dlt_sources.education.ireland.british_isles.education.curriculum import (  # type: ignore[import-not-found]
    _crawl_source,
)

WRC_BASE = "https://workplacerelations.ie/en"

# WRC decision database + complaint procedure sub-trees
WRC_PAGES_PATHS = [
    "/complaints-and-disputes/*",
    "/procedures/*",
    "/forms/*",
    "/news/*",
    "/publications/*",
    "/about-us/*",
]

WRC_DECISIONS_PATHS = [
    "/decisions/*",
    "/enforcement-decisions/*",
    "/adjudication-decisions/*",
]


def _crawl_wrc_pages(max_pages: int = 100) -> Iterator[dict[str, Any]]:
    """Crawl the WRC procedure pages (complaint types, forms, news)."""
    for page in _crawl_source(
        source_name="wrc.pages",
        base_url=WRC_BASE,
        include_paths=WRC_PAGES_PATHS,
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "wrc"
        page["entity_type"] = "page"
        yield page


def _crawl_wrc_decisions(max_pages: int = 300) -> Iterator[dict[str, Any]]:
    """Crawl the WRC published Adjudication Decisions database.

    Each decision page typically has a `case_ref` (e.g.
    `ADJ-00012345-2024`) in the URL or as a heading. The BAML fn
    `b.ExtractWRCDecision` will extract the structured fields in L2.
    """
    for page in _crawl_source(
        source_name="wrc.decisions",
        base_url=WRC_BASE,
        include_paths=WRC_DECISIONS_PATHS,
        max_pages=max_pages,
        max_depth=4,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "wrc"
        page["entity_type"] = "decision"
        yield page


@dlt.source(name="workplace_relations")
def workplace_relations_source(max_pages: int = 300):
    """DLT source for the Workplace Relations Commission (WRC).

    Returns 2 resources:

    - `pages`     — procedures, complaint-type pages, forms
    - `decisions` — published WRC Adjudication Decisions
    """

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        yield from _crawl_wrc_pages(max_pages=max_pages // 3)

    @dlt.resource(
        name="decisions",
        write_disposition="merge",
        primary_key=["url"],
    )
    def decisions():
        yield from _crawl_wrc_decisions(max_pages=max_pages)

    return pages, decisions
