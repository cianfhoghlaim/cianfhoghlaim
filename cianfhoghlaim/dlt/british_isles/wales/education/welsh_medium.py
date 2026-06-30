"""
Education WLS source: welsh_medium_source

Split from uk/wales/curriculum_for_wales.py in Phase 3D.
"""

from datetime import UTC, datetime

import dlt

from cianfhoghlaim.dlt.common.firecrawl_source import crawl_website
from ._curriculum_for_wales_helpers import (
    HWB_URLS,
)


def welsh_medium_source(max_pages: int = 100):
    """
    DLT source specifically for Welsh-medium education resources.

    Focuses on:
    - Cymraeg (Welsh language) as a subject
    - Resources through the medium of Welsh
    - Bilingual education materials

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with Welsh-medium resources
    """

    @dlt.resource(
        name="welsh_medium_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def welsh_medium_pages():
        """Welsh-medium curriculum resources."""
        # Crawl Welsh language section of Hwb
        for page in crawl_website(
            base_url=HWB_URLS["welsh_language"],
            max_pages=max_pages,
            max_depth=3,
        ):
            page["nation"] = "wales"
            page["source"] = "hwb"
            page["language"] = "cy"
            page["curriculum_framework"] = "curriculum_for_wales"
            page["is_welsh_medium"] = True
            page["indexed_at"] = datetime.now(UTC).isoformat()
            yield page

    return welsh_medium_pages
