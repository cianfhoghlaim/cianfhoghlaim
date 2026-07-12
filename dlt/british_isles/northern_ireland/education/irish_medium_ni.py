"""
Education NI source: irish_medium_ni_source

Split from uk/northern_ireland/ccea_curriculum.py in Phase 3D.
"""

from datetime import UTC, datetime

import dlt

from cianfhoghlaim.dlt.common.firecrawl_source import crawl_website
from ._ccea_curriculum_helpers import (
    NI_CURRICULUM_URLS,
)


def irish_medium_ni_source(max_pages: int = 100):
    """
    DLT source specifically for Irish-medium education in Northern Ireland.

    Focuses on:
    - Gaelscoileanna (Irish-medium schools) resources
    - Irish language subject materials
    - Bilingual education resources

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with Irish-medium resources
    """

    @dlt.resource(
        name="irish_medium_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def irish_medium_pages():
        """Irish-medium curriculum resources."""
        for page in crawl_website(
            base_url=NI_CURRICULUM_URLS["irish_medium"],
            max_pages=max_pages,
            max_depth=3,
        ):
            page["nation"] = "northern_ireland"
            page["source"] = "ccea"
            page["language"] = "ga"
            page["curriculum_framework"] = "ni_curriculum"
            page["is_irish_medium"] = True
            page["indexed_at"] = datetime.now(UTC).isoformat()
            yield page

    return irish_medium_pages
