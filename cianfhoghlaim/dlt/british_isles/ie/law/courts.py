"""
cianfhoghlaim.dlt.british_isles.ie.law.courts — Courts Service of Ireland (forms + fees).

Source: `https://www.courts.ie/` — the catalogue of court forms
(District / Circuit / High / Supreme / Court of Appeal) + the Court Fees
schedules. Judgements are now a separate source (`judgements`) and Rules
are a separate source (`court_rules`) per the Pick-8 scoping.

Covers 2 DLT resources:

- `forms` — court forms catalogue (all court levels)
- `fees`  — Court Fees schedules per court level

Honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/courts.ie/`.

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

COURTS_BASE = "https://www.courts.ie"

# The Courts Service hosts distinct sub-trees for each resource.
COURTS_FORMS_PATHS = [
    "/forms/*",
    "/district-court/forms/*",
    "/circuit-court/forms/*",
    "/high-court/forms/*",
    "/supreme-court/forms/*",
    "/court-of-appeal/forms/*",
]

COURTS_FEES_PATHS = [
    "/fees/*",
    "/district-court/fees/*",
    "/circuit-court/fees/*",
    "/high-court/fees/*",
    "/supreme-court/fees/*",
    "/court-of-appeal/fees/*",
]


def _crawl_courts_forms(max_pages: int) -> Iterator[dict[str, Any]]:
    for page in _crawl_source(
        source_name="courts.forms",
        base_url=COURTS_BASE,
        include_paths=COURTS_FORMS_PATHS,
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "courts"
        page["entity_type"] = "form"
        yield page


def _crawl_court_fees(max_pages: int) -> Iterator[dict[str, Any]]:
    for page in _crawl_source(
        source_name="courts.fees",
        base_url=COURTS_BASE,
        include_paths=COURTS_FEES_PATHS,
        max_pages=max_pages,
        max_depth=2,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "courts"
        page["entity_type"] = "fee"
        yield page


@dlt.source(name="courts")
def courts_source(max_pages: int = 200):
    """DLT source for the Courts Service of Ireland (forms + fees).

    Returns 2 resources:

    - `forms` — court forms catalogue (all court levels)
    - `fees`  — Court Fees schedules

    (Pick-8 split: `judgements` and `court_rules` are separate sources.)
    """

    @dlt.resource(
        name="forms",
        write_disposition="merge",
        primary_key=["url"],
    )
    def forms():
        yield from _crawl_courts_forms(max_pages=max_pages)

    @dlt.resource(
        name="fees",
        write_disposition="merge",
        primary_key=["url"],
    )
    def fees():
        yield from _crawl_court_fees(max_pages=max_pages // 2)

    return forms, fees
