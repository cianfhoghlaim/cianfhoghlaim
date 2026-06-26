"""
Education IE source: oide_gaeilge_source

Split from ireland/oide.py in Phase 3D.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
import dlt
from common.firecrawl_source import crawl_website, scrape_page
from common.incremental import compute_content_hash

from ._oide_helpers import (
    _crawl_oide_section,
)

def oide_gaeilge_source(max_pages: int = 100):
    """
    DLT source specifically for Irish-medium CPD resources.

    Focuses on Gaeilge teaching and Irish-medium education support.

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with Irish-medium CPD resources
    """

    @dlt.resource(
        name="oide_gaeilge_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def oide_gaeilge_pages():
        """Irish-medium CPD resources."""
        yield from _crawl_oide_section("irish", "ga", max_pages)

    return oide_gaeilge_pages
