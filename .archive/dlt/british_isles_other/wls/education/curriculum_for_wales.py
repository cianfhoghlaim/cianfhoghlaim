"""
Education WLS source: curriculum_for_wales_source

Split from uk/wales/curriculum_for_wales.py in Phase 3D.
"""

import dlt

from ._curriculum_for_wales_helpers import (
    _crawl_hwb_curriculum,
)


def curriculum_for_wales_source(
    aole: str | None = None,
    languages: list[str] | None = None,
    max_pages: int = 200,
):
    """
    DLT source for Wales' Curriculum for Wales.

    Args:
        aole: Specific Area of Learning and Experience
        languages: Languages to crawl ["en", "cy"], defaults to both
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with Hwb curriculum pages
    """
    languages = languages or ["en", "cy"]

    @dlt.resource(
        name="curriculum_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def curriculum_pages():
        """Crawled Curriculum for Wales pages."""
        for lang in languages:
            yield from _crawl_hwb_curriculum(aole, lang, max_pages // len(languages))

    return curriculum_pages
