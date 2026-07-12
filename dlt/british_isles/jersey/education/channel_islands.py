"""
oideachais.cianfhoghlaim.dlt.british_isles.jersey.education.channel_islands — Jersey education DLT source.

Split from `dlt_sources/crown_dependencies/channel_islands.py` in
Phase 3E (Round 11 oideachais audit). The Jersey source (`jersey_source`)
lives at the canonical country-first path; the shared `CHANNEL_ISLANDS_URLS`
constant + crawl helper live in the sibling `_channel_islands_helpers.py`.
"""

from __future__ import annotations

from collections.abc import Iterator

import dlt

from ._channel_islands_helpers import CHANNEL_ISLANDS_URLS, _crawl_jersey_education


@dlt.source(name="jersey_education")
def jersey_source(max_pages: int = 100):
    """
    DLT source for Jersey education data.

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
        """Jersey education pages."""
        yield from _crawl_jersey_education(max_pages)

    return pages


__all__ = ["CHANNEL_ISLANDS_URLS", "jersey_source"]
