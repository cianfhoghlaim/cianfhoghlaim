"""
cianfhoghlaim.dlt.british_isles.ireland.law.piab — Personal Injuries Assessment Board.

Source: `https://www.injuries.ie/eng/` — the front-door for every personal
injury claim in Ireland. The PIAB process (Application → Assessment →
Award / Section 14 Notice of Permission to Seek Judicial Review) gates
~90% of High Court personal-injury litigation.

Pick-8 scoped reimplementation of the absorbed `2026-07-06-ireland-legal-pipeline`
proposal — the `piab` source focuses on the 2 highest-value resources:

- `pages`  — crawled process / forms / news / about pages
- `forms`  — PIAB forms catalogue (Application form A/B, consent forms,
            medical report forms, etc.)

Honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/injuries.ie/`.

Reference: openspec/changes/archive/2026-07-07-finalize-v4-landing/
           absorbed/2026-07-06-ireland-legal-pipeline/proposal.md
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import structlog

import dlt

logger = structlog.get_logger(__name__)

from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum_source import (  # type: ignore[import-not-found]  # noqa: E402
    _crawl_source,
)

PIAB_BASE = "https://www.injuries.ie/eng"

# Public-facing routes. The PIAB site has 4 logical sub-trees we crawl.
PIAB_PAGE_PATHS = [
    "/the-personal-injuries-assessment-board/*",
    "/about-us/*",
    "/services/*",
    "/application-process/*",
    "/contact-us/*",
    "/news/*",
]

PIAB_FORM_PATHS = [
    "/forms/*",
    "/application-form/*",
]


def _crawl_piab_pages(max_pages: int = 80) -> Iterator[dict[str, Any]]:
    """Crawl the PIAB informational pages (process, about, news)."""
    for page in _crawl_source(
        source_name="piab.pages",
        base_url=PIAB_BASE,
        include_paths=PIAB_PAGE_PATHS,
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "piab"
        page["entity_type"] = "page"
        yield page


def _crawl_piab_forms(max_pages: int = 40) -> Iterator[dict[str, Any]]:
    """Crawl the PIAB forms catalogue (PDFs + form metadata pages)."""
    for page in _crawl_source(
        source_name="piab.forms",
        base_url=PIAB_BASE,
        include_paths=PIAB_FORM_PATHS,
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "piab"
        page["entity_type"] = "form"
        yield page


@dlt.source(name="piab")
def piab_source(max_pages: int = 80):
    """DLT source for the Personal Injuries Assessment Board (PIAB).

    Returns 2 resources:

    - `pages` — process / about / news pages
    - `forms` — PIAB forms catalogue
    """

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        yield from _crawl_piab_pages(max_pages=max_pages)

    @dlt.resource(
        name="forms",
        write_disposition="merge",
        primary_key=["url"],
    )
    def forms():
        yield from _crawl_piab_forms(max_pages=max_pages // 2)

    return pages, forms
