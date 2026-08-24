"""
cianfhoghlaim.cianfhoghlaim.dlt.british_isles.guernsey.education.channel_islands — Guernsey education DLT source.

Split from `dlt_sources/crown_dependencies/channel_islands.py` in
Phase 3E (Round 11 oideachais audit). The Guernsey source (`guernsey_source`)
lives at the canonical country-first path; the shared `CHANNEL_ISLANDS_URLS`
constant + crawl helper live in the sibling `_channel_islands_helpers.py`
(imported from `jey.education._channel_islands_helpers` to keep one
canonical home for the shared data).
"""

from __future__ import annotations
import dlt


from collections.abc import Iterator

import dlt_sources
from dlt_sources.british_isles.jersey.education._channel_islands_helpers import (
    CHANNEL_ISLANDS_URLS,
    _crawl_guernsey_education,
)


@dlt.source(name="guernsey_education")
def guernsey_source(max_pages: int = 100):
    """
    DLT source for Guernsey education data.

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with pages resource
    """

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages() -> Iterator[dict]:
        """Guernsey education pages."""
        yield from _crawl_guernsey_education(max_pages)

    return pages


__all__ = ["CHANNEL_ISLANDS_URLS", "guernsey_source"]
