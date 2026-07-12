"""
oideachais.cianfhoghlaim.dlt.british_isles.jersey.education._channel_islands_helpers — shared helpers
for Jersey + Guernsey education sources.

Split from `dlt_sources/crown_dependencies/channel_islands.py` in Phase 3E.
Contains the shared `CHANNEL_ISLANDS_URLS` constants + the per-nation
crawl helpers `_crawl_jersey_education` (used by `channel_islands.py`)
and `_crawl_guernsey_education` (used by `ggy/education/channel_islands.py`).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cianfhoghlaim.dlt.common.firecrawl_source import crawl_website

CHANNEL_ISLANDS_URLS = {
    "jersey": {
        "education": "https://www.gov.je/Education/",
        "schools": "https://www.gov.je/Education/Schools/",
    },
    "guernsey": {
        "education": "https://www.gov.gg/education",
        "schools": "https://www.gov.gg/schools",
    },
}


def _crawl_jersey_education(max_pages: int = 100) -> Iterator[dict[str, Any]]:
    """
    Crawl Jersey education pages.

    Args:
        max_pages: Maximum pages to crawl

    Yields:
        Crawled page data
    """
    for page in crawl_website(
        base_url=CHANNEL_ISLANDS_URLS["jersey"]["education"],
        include_paths=["/Education/*"],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "jersey"
        page["source"] = "gov_je"
        yield page


def _crawl_guernsey_education(max_pages: int = 100) -> Iterator[dict[str, Any]]:
    """
    Crawl Guernsey education pages.

    Args:
        max_pages: Maximum pages to crawl

    Yields:
        Crawled page data
    """
    for page in crawl_website(
        base_url=CHANNEL_ISLANDS_URLS["guernsey"]["education"],
        include_paths=["/education*", "/schools*"],
        max_pages=max_pages,
        max_depth=3,
    ):
        page["nation"] = "guernsey"
        page["source"] = "gov_gg"
        yield page


__all__ = [
    "CHANNEL_ISLANDS_URLS",
    "_crawl_guernsey_education",
    "_crawl_jersey_education",
]
