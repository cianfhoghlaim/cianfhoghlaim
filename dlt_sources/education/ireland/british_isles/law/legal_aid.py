"""
cianfhoghlaim.dlt.british_isles.ireland.law.legal_aid — Legal Aid Board.

Source: `https://www.legalaidboard.ie/` — the Legal Aid Board (formerly
the Free Legal Advice Centres / FLAC overlap). Provides civil legal aid
and family mediation services to qualifying applicants.

Pick-8 scoping: the 5th new operational-law source. The `legal_aid`
source has 2 resources:

- `pages` — informational pages (services, eligibility, application process)
- `forms` — Legal Aid Board forms catalogue (application forms,
            financial eligibility forms, etc.)

Honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/legalaidboard.ie/`.

Reference: openspec/changes/archive/2026-07-07-finalize-v4-landing/
           absorbed/2026-07-06-ireland-legal-pipeline/proposal.md
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import structlog

import dlt_sources

logger = structlog.get_logger(__name__)

from dlt_sources.education.ireland.british_isles.education.curriculum import (  # type: ignore[import-not-found]  # noqa: E402
    _crawl_source,
)

LEGAL_AID_BASE = "https://www.legalaidboard.ie"

# Public-facing routes. The Legal Aid Board site has 3 logical
# sub-trees: services / apply / about.
LEGAL_AID_PAGE_PATHS = [
    "/en/*",
    "/services/*",
    "/apply-for-legal-aid/*",
    "/about-us/*",
    "/contact-us/*",
    "/news/*",
    "/publications/*",
]

LEGAL_AID_FORM_PATHS = [
    "/forms/*",
    "/application-form/*",
]


def _crawl_legal_aid_pages(max_pages: int = 60) -> Iterator[dict[str, Any]]:
    """Crawl the Legal Aid Board informational pages."""
    for page in _crawl_source(
        source_name="legal_aid.pages",
        base_url=LEGAL_AID_BASE,
        include_paths=LEGAL_AID_PAGE_PATHS,
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "legal_aid"
        page["entity_type"] = "page"
        yield page


def _crawl_legal_aid_forms(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    """Crawl the Legal Aid Board forms catalogue."""
    for page in _crawl_source(
        source_name="legal_aid.forms",
        base_url=LEGAL_AID_BASE,
        include_paths=LEGAL_AID_FORM_PATHS,
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "legal_aid"
        page["entity_type"] = "form"
        yield page


@dlt.source(name="legal_aid")
def legal_aid_source(max_pages: int = 60):
    """DLT source for the Legal Aid Board of Ireland.

    Returns 2 resources:

    - `pages` — services / apply / about / news pages
    - `forms` — Legal Aid Board forms catalogue
    """

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        yield from _crawl_legal_aid_pages(max_pages=max_pages)

    @dlt.resource(
        name="forms",
        write_disposition="merge",
        primary_key=["url"],
    )
    def forms():
        yield from _crawl_legal_aid_forms(max_pages=max_pages // 2)

    return pages, forms
