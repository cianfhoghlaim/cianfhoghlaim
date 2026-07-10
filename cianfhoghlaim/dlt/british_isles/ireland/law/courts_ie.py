"""
oideachais.cianfhoghlaim.dlt.british_isles.ireland.law.courts_ie — Courts
Service of Ireland.

Source: `https://www.courts.ie/` — the catalogue of court forms, the
published Judgements.ie database, the Court Fees schedules, and the
Rules of Court (PDF library).

Covers 4 DLT resources:

- `forms`     — District / Circuit / High / Supreme / Court of Appeal forms
- `judgements` — Judgements.ie published decisions database
- `fees`      — Court Fees schedules per court level
- `rules`     — Rules of Court (PDF library per jurisdiction)

Honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/courts.ie/`.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import structlog

import dlt

logger = structlog.get_logger(__name__)

from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import (  # type: ignore[import-not-found]
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

COURTS_JUDGEMENTS_PATHS = [
    "/judgements/*",
    "/supreme-court/judgements/*",
    "/court-of-appeal/judgements/*",
    "/high-court/judgements/*",
    "/circuit-court/judgements/*",
]

COURTS_FEES_PATHS = [
    "/fees/*",
    "/district-court/fees/*",
    "/circuit-court/fees/*",
    "/high-court/fees/*",
    "/supreme-court/fees/*",
    "/court-of-appeal/fees/*",
]

COURTS_RULES_PATHS = [
    "/rules/*",
    "/district-court-rules/*",
    "/circuit-court-rules/*",
    "/rules-of-the-superior-courts/*",
    "/district-court-rules-of-procedure/*",
]


def _crawl_courts_forms(max_pages: int) -> Iterator[dict[str, Any]]:
    for page in _crawl_source(
        source_name="courts_ie.forms",
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


def _crawl_courts_judgements(max_pages: int) -> Iterator[dict[str, Any]]:
    for page in _crawl_source(
        source_name="courts_ie.judgements",
        base_url=COURTS_BASE,
        include_paths=COURTS_JUDGEMENTS_PATHS,
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "courts"
        page["entity_type"] = "judgement"
        yield page


def _crawl_court_fees(max_pages: int) -> Iterator[dict[str, Any]]:
    for page in _crawl_source(
        source_name="courts_ie.fees",
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


def _crawl_court_rules(max_pages: int) -> Iterator[dict[str, Any]]:
    for page in _crawl_source(
        source_name="courts_ie.rules",
        base_url=COURTS_BASE,
        include_paths=COURTS_RULES_PATHS,
        max_pages=max_pages,
        max_depth=2,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "courts"
        page["entity_type"] = "rule"
        yield page


@dlt.source(name="courts_ie")
def courts_ie_source(max_pages: int = 200):
    """DLT source for the Courts Service of Ireland.

    Returns 4 resources:

    - `forms`     — court forms catalogue (all court levels)
    - `judgements` — Judgements.ie published decisions database
    - `fees`      — Court Fees schedules
    - `rules`     — Rules of Court
    """

    @dlt.resource(
        name="forms",
        write_disposition="merge",
        primary_key=["url"],
    )
    def forms():
        yield from _crawl_courts_forms(max_pages=max_pages)

    @dlt.resource(
        name="judgements",
        write_disposition="merge",
        primary_key=["url"],
    )
    def judgements():
        yield from _crawl_courts_judgements(max_pages=max_pages)

    @dlt.resource(
        name="fees",
        write_disposition="merge",
        primary_key=["url"],
    )
    def fees():
        yield from _crawl_court_fees(max_pages=max_pages // 2)

    @dlt.resource(
        name="rules",
        write_disposition="merge",
        primary_key=["url"],
    )
    def rules():
        yield from _crawl_court_rules(max_pages=max_pages // 2)

    return forms, judgements, fees, rules
