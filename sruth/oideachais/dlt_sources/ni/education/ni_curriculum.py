"""
Education NI source: ni_curriculum_source

Split from uk/northern_ireland/ccea_curriculum.py in Phase 3D.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
import dlt
from ...common.firecrawl_source import crawl_website, scrape_page
from ...common.incremental import compute_content_hash

from ._ccea_curriculum_helpers import (
    _crawl_ni_curriculum,
)

def ni_curriculum_source(
    key_stage: str | None = None,
    include_irish_medium: bool = True,
    max_pages: int = 200,
):
    """
    DLT source for Northern Ireland Curriculum.

    Args:
        key_stage: Specific key stage (foundation, key_stage_1, etc.)
        include_irish_medium: Include Irish-medium education resources
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with NI curriculum pages
    """

    @dlt.resource(
        name="ni_curriculum_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def ni_curriculum_pages():
        """Crawled Northern Ireland Curriculum pages."""
        yield from _crawl_ni_curriculum(key_stage, include_irish_medium, max_pages)

    return ni_curriculum_pages
