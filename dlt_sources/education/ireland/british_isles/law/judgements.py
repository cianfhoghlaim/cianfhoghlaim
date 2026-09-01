"""
cianfhoghlaim.dlt.british_isles.ireland.law.judgements — Judgements.ie.

Source: `https://www.courts.ie/judgements` (operated by the Courts
Service of Ireland) — ~30,000 published court decisions across the
District, Circuit, High, Supreme, and Court of Appeal courts.

Pick-8 scoping: this is a separate DLT source from `courts` (which
focuses on forms + fees). The `judgements` source has 1 resource:

- `judgements` — published decisions database (merge on `neutral_citation`)

Honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/judgements.ie/`.

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

JUDGEMENTS_BASE = "https://www.courts.ie"

# The Judgements.ie sub-tree lives at /judgements. Per the proposal
# we crawl the 5 court-level sub-trees.
JUDGEMENTS_PATHS = [
    "/judgements/*",
    "/supreme-court/judgements/*",
    "/court-of-appeal/judgements/*",
    "/high-court/judgements/*",
    "/circuit-court/judgements/*",
]


def _crawl_judgements(max_pages: int) -> Iterator[dict[str, Any]]:
    for page in _crawl_source(
        source_name="judgements.decisions",
        base_url=JUDGEMENTS_BASE,
        include_paths=JUDGEMENTS_PATHS,
        max_pages=max_pages,
        max_depth=4,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "judgements"
        page["entity_type"] = "judgement"
        yield page


@dlt.source(name="judgements")
def judgements_source(max_pages: int = 400):
    """DLT source for Judgements.ie (Courts Service of Ireland).

    Returns 1 resource:

    - `judgements` — published decisions (merge on `neutral_citation`
      when available, else on `url`)
    """

    @dlt.resource(
        name="judgements",
        write_disposition="merge",
        primary_key=["url"],
    )
    def judgements():
        yield from _crawl_judgements(max_pages=max_pages)

    return judgements
