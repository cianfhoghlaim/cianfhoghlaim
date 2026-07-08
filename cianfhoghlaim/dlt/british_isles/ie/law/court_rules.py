"""
cianfhoghlaim.dlt.british_isles.ie.law.court_rules — Court Rules library.

Source: `https://www.courts.ie/rules` (operated by the Courts Service of
Ireland) — the Rules of Court PDF library (District Court Rules,
Circuit Court Rules, Rules of the Superior Courts, District Court Rules
of Procedure, etc.).

Pick-8 scoping: this is a separate DLT source from `courts` (which
focuses on forms + fees). The `court_rules` source has 1 resource:

- `rules` — Rules of Court (PDF library per jurisdiction)

Honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/courts.ie/rules/`.

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

COURT_RULES_BASE = "https://www.courts.ie"

COURT_RULES_PATHS = [
    "/rules/*",
    "/district-court-rules/*",
    "/circuit-court-rules/*",
    "/rules-of-the-superior-courts/*",
    "/district-court-rules-of-procedure/*",
]


def _crawl_court_rules(max_pages: int) -> Iterator[dict[str, Any]]:
    for page in _crawl_source(
        source_name="court_rules.rules",
        base_url=COURT_RULES_BASE,
        include_paths=COURT_RULES_PATHS,
        max_pages=max_pages,
        max_depth=2,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "court_rules"
        page["entity_type"] = "rule"
        yield page


@dlt.source(name="court_rules")
def court_rules_source(max_pages: int = 200):
    """DLT source for the Court Rules library (PDF catalogue).

    Returns 1 resource:

    - `rules` — Rules of Court (PDF library per jurisdiction)
    """

    @dlt.resource(
        name="rules",
        write_disposition="merge",
        primary_key=["url"],
    )
    def rules():
        yield from _crawl_court_rules(max_pages=max_pages)

    return rules
