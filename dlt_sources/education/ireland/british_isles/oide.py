import dlt

"""
Education IE source: oide_source

Split from ireland/oide.py in Phase 3D.
"""

import dlt_sources

from ._oide_helpers import (
    OIDE_URLS,
    _crawl_oide_section,
    _extract_oide_resource_links,
)


def oide_source(
    section: str | None = None,
    include_resources: bool = True,
    max_pages: int = 150,
):
    """
    DLT source for Oide.ie CPD resources.

    Args:
        section: Specific section (primary, post_primary, stem, etc.)
        include_resources: Extract downloadable resource links
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with CPD pages and optionally resource links
    """

    @dlt.resource(
        name="oide_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def oide_pages():
        """Crawled Oide CPD pages."""
        yield from _crawl_oide_section(section, "en", max_pages)

    @dlt.resource(
        name="oide_resources",
        write_disposition="merge",
        primary_key=["url"],
    )
    def oide_resources():
        """Oide downloadable resource links."""
        if include_resources:
            for sec in OIDE_URLS:
                if section is None or section == sec:
                    yield from _extract_oide_resource_links(sec)

    return oide_pages, oide_resources
