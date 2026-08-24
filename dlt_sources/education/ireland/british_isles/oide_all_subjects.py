import dlt

"""
Education IE source: oide_all_subjects_source

Split from ireland/oide.py in Phase 3D.
"""

import dlt_sources

from ._oide_helpers import (
    OIDE_SUBJECTS,
    _crawl_oide_subject,
)


def oide_all_subjects_source(
    levels: list[str] | None = None,
    max_pages_per_subject: int = 30,
):
    """
    DLT source crawling all subjects from Oide.ie.

    Args:
        levels: Filter by level(s) ["primary", "jc", "lc"], defaults to all
        max_pages_per_subject: Max pages per subject

    Returns:
        DLT source with all subject CPD pages
    """
    levels = levels or ["primary", "jc", "lc"]

    @dlt.resource(
        name="all_subject_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def all_subject_pages():
        """All subject CPD resources."""
        for subject_key in OIDE_SUBJECTS:
            # Filter by level prefix
            if any(subject_key.startswith(level) for level in levels):
                yield from _crawl_oide_subject(subject_key, max_pages_per_subject)

    return all_subject_pages
