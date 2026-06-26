"""
Education EN source: national_curriculum_source

Split from uk/england/national_curriculum.py in Phase 3D.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
import dlt
from ...common.firecrawl_source import crawl_website, scrape_page
from ...common.incremental import compute_content_hash

from ._national_curriculum_helpers import (
    _crawl_gov_uk_curriculum,
)

def national_curriculum_source(
    key_stage: str | None = None,
    max_pages: int = 200,
):
    """
    DLT source for England's National Curriculum.

    Args:
        key_stage: Specific key stage (key_stage_1, key_stage_2, etc.)
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with National Curriculum pages
    """

    @dlt.resource(
        name="national_curriculum_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def national_curriculum_pages():
        """Crawled National Curriculum pages."""
        yield from _crawl_gov_uk_curriculum(key_stage, max_pages)

    return national_curriculum_pages
