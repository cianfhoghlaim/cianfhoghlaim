import dlt

"""
Education WLS source: wjec_qualifications_source

Split from uk/wales/curriculum_for_wales.py in Phase 3D.
"""

import dlt_sources

from ._curriculum_for_wales_helpers import (
    _crawl_wjec_qualifications,
    _extract_wjec_pdf_links,
)


def wjec_qualifications_source(
    qualification_level: str | None = None,
    languages: list[str] | None = None,
    include_pdf_links: bool = True,
    max_pages: int = 150,
):
    """
    DLT source for WJEC/CBAC qualifications.

    Args:
        qualification_level: "gcse" or "a_level"
        languages: ["en"] for WJEC, ["cy"] for CBAC, or both
        include_pdf_links: Extract PDF specification links
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with WJEC pages and optionally PDF links
    """
    languages = languages or ["en", "cy"]

    @dlt.resource(
        name="wjec_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def wjec_pages():
        """Crawled WJEC/CBAC qualification pages."""
        for lang in languages:
            yield from _crawl_wjec_qualifications(qualification_level, lang, max_pages // len(languages))

    @dlt.resource(
        name="wjec_pdf_links",
        write_disposition="merge",
        primary_key=["url"],
    )
    def wjec_pdf_links():
        """WJEC/CBAC PDF specification links."""
        if include_pdf_links:
            for level in ["gcse", "a_level"]:
                if qualification_level is None or qualification_level == level:
                    for lang in languages:
                        yield from _extract_wjec_pdf_links(level, lang)

    return wjec_pages, wjec_pdf_links
