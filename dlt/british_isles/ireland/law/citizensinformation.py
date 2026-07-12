"""
oideachais.cianfhoghlaim.dlt.british_isles.ireland.law.citizensinformation
— Citizens Information Board (CIB) of Ireland.

Source: `https://www.citizensinformation.ie/en/` — the plain-English
rights / entitlements / appeals articles that the public uses to navigate
Irish law. Covers categories:

- Justice (criminal, civil, family, immigration, asylum)
- Employment (rights at work, contracts, dismissals, equality)
- Social welfare (entitlements, appeals)
- Housing (tenancies, evictions, homelessness)
- Health (medical cards, hospital charges, complaints)
- Consumer (rights, returns, warranties)
- Money and tax (entitlements, PRSI, USC)

Covers 1 DLT resource:

- `articles` — CIB articles merged on `url`

Honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/citizensinformation.ie/`.
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

CIB_BASE = "https://www.citizensinformation.ie/en"

# The 7 canonical CIB categories (en/ paths only — Irish GA deferred to v2)
CIB_ARTICLE_PATHS = [
    "/justice/*",
    "/employment/*",
    "/social-welfare/*",
    "/housing/*",
    "/health/*",
    "/consumer/*",
    "/money-and-tax/*",
    "/births-deaths-marriages/*",
    "/moving-country/*",
    "/government-in-ireland/*",
    "/environmental-information/*",
]


def _crawl_citizensinfo_articles(max_pages: int = 400) -> Iterator[dict[str, Any]]:
    """Crawl CIB articles across all 7+ categories.

    Each article URL maps to one row with `nation`, `domain`,
    `entity`, `entity_type`, and the BAML fn `b.ExtractCitizensInfoArticle`
    extracts the structured fields in L2.
    """
    for page in _crawl_source(
        source_name="citizensinfo.articles",
        base_url=CIB_BASE,
        include_paths=CIB_ARTICLE_PATHS,
        max_pages=max_pages,
        max_depth=4,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "citizensinfo"
        page["entity_type"] = "article"
        yield page


@dlt.source(name="citizensinformation")
def citizensinformation_source(max_pages: int = 400):
    """DLT source for the Citizens Information Board (CIB).

    Returns 1 resource:

    - `articles` — CIB rights/entitlements/appeals articles
    """

    @dlt.resource(
        name="articles",
        write_disposition="merge",
        primary_key=["url"],
    )
    def articles():
        yield from _crawl_citizensinfo_articles(max_pages=max_pages)

    return articles
