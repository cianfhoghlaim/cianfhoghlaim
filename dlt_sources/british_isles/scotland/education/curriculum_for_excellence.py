import dlt

"""
Education SCT source: curriculum_for_excellence_source

Split from uk/scotland/curriculum_for_excellence.py in Phase 3D.
"""

import dlt_sources

from ._curriculum_for_excellence_helpers import (
    _crawl_education_gov_scot,
)


def curriculum_for_excellence_source(
    section: str | None = None,
    include_gaelic: bool = True,
    max_pages: int = 300,
):
    """
    DLT source for Scotland's Curriculum for Excellence.

    Args:
        section: Specific CfE section (benchmarks, experiences_outcomes, etc.)
        include_gaelic: Include Gaelic Medium Education resources
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with CfE pages resource
    """

    @dlt.resource(
        name="cfe_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def cfe_pages():
        """Crawled Curriculum for Excellence pages."""
        yield from _crawl_education_gov_scot(section, include_gaelic, max_pages)

    return cfe_pages
