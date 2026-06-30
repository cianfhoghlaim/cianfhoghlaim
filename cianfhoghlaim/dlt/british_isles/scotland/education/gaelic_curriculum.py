"""
Education SCT source: gaelic_curriculum_source

Split from uk/scotland/curriculum_for_excellence.py in Phase 3D.
"""

from datetime import UTC, datetime

import dlt

from cianfhoghlaim.dlt.common.firecrawl_source import crawl_website
from ._curriculum_for_excellence_helpers import (
    CFE_URLS,
)


def gaelic_curriculum_source(max_pages: int = 100):
    """
    DLT source specifically for Gaelic Medium Education resources.

    Focuses on:
    - Foghlam tron Ghàidhlig resources
    - Stòrlann materials
    - SQA Gàidhlig qualifications

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with Gaelic education resources
    """

    @dlt.resource(
        name="gaelic_cfe_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def gaelic_cfe_pages():
        """Gaelic Medium CfE resources."""
        for page in crawl_website(
            base_url=CFE_URLS["gaelic_medium"],
            max_pages=max_pages,
            max_depth=3,
        ):
            page["nation"] = "scotland"
            page["source"] = "education_gov_scot"
            page["language"] = "gd"
            page["curriculum_framework"] = "foghlam_tron_ghaidhlig"
            page["indexed_at"] = datetime.now(UTC).isoformat()
            yield page

    return gaelic_cfe_pages
