"""
Education IE source: oide_subject_source

Split from ireland/oide.py in Phase 3D.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
import dlt
from common.firecrawl_source import crawl_website, scrape_page
from common.incremental import compute_content_hash

from ._oide_helpers import (
    _crawl_oide_subject,
)

def oide_subject_source(
    subject_key: str,
    max_pages: int = 50,
):
    """
    DLT source for a specific Oide.ie subject.

    Args:
        subject_key: Subject key (e.g., "jc_mathematics", "lc_physics")
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with subject-specific CPD pages
    """

    @dlt.resource(
        name=f"oide_{subject_key}_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def subject_pages():
        """Subject-specific CPD resources."""
        yield from _crawl_oide_subject(subject_key, max_pages)

    return subject_pages
