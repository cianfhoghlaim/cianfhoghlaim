"""
Junior Cycle Subject DLT Sources.

Provides per-subject DLT resources for all 18 Junior Cycle subjects.
Each subject yields pages and PDF URLs from curriculumonline.ie.

Usage:
    from cianfhoghlaim.dlt.british_isles.ireland.subjects.junior_cycle import (
        junior_cycle_source,
    )

    # All subjects in English
    pipeline.run(junior_cycle_source(language="en"))

    # All subjects in Irish
    pipeline.run(junior_cycle_source(language="ga"))

    # Single subject
    pipeline.run(junior_cycle_source(language="en", subjects=["mathematics"]))
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog

from .base import (
    crawl_subject,
    create_subject_source,
    extract_pdfs_from_subject,
)

logger = structlog.get_logger(__name__)

# All Junior Cycle subjects from curriculum_index.json
JUNIOR_CYCLE_SUBJECTS = [
    "applied-technology",
    "business-studies",
    "classics",
    "engineering",
    "english",
    "gaeilge",
    "geography",
    "graphics",
    "history",
    "home-economics",
    "mathematics",
    "modern-foreign-languages",
    "music",
    "physical-education",
    "religious-education",
    "science",
    "visual-art",
    "wood-technology",
]

# Junior Cycle short courses
JUNIOR_CYCLE_SHORT_COURSES = [
    "coding",
    "cspe",
    "digital-media-literacy",
    "philosophy",
    "physical-education-sc",
    "sphe",
    "chinese-language-and-culture",
    "artistic-performance",
]


@dlt.source(name="junior_cycle_subjects")
def junior_cycle_source(
    language: str = "en",
    subjects: list[str] | None = None,
    include_short_courses: bool = False,
    sources: list[str] | None = None,
    max_pages_per_subject: int = 30,
):
    """
    DLT source for Junior Cycle subjects.

    Args:
        language: Language code ("en" or "ga")
        subjects: Optional list of subjects (default: all 18 subjects)
        include_short_courses: Whether to include short courses (default: False)
        sources: Optional list of sources (default: curriculumonline)
        max_pages_per_subject: Max pages to crawl per subject

    Returns:
        DLT resources for pages and PDFs for each subject

    Examples:
        # All subjects in English
        pipeline.run(junior_cycle_source(language="en"))

        # Include short courses
        pipeline.run(junior_cycle_source(include_short_courses=True))

        # Specific subjects in Irish
        pipeline.run(junior_cycle_source(
            language="ga",
            subjects=["mathematics", "gaeilge", "science"]
        ))
    """
    if subjects is None:
        subjects = JUNIOR_CYCLE_SUBJECTS.copy()
        if include_short_courses:
            subjects.extend(JUNIOR_CYCLE_SHORT_COURSES)

    if sources is None:
        sources = ["curriculumonline"]

    logger.info(
        "junior_cycle_source_initialized",
        language=language,
        subject_count=len(subjects),
        include_short_courses=include_short_courses,
        sources=sources,
    )

    @dlt.resource(
        name="junior_cycle_pages",
        write_disposition="merge",
        primary_key=["url"],
        columns={
            "url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "content": {"data_type": "text"},
            "content_hash": {"data_type": "text"},
            "cycle": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "language": {"data_type": "text"},
            "source": {"data_type": "text"},
            "document_type": {"data_type": "text"},
            "crawled_at": {"data_type": "timestamp"},
            "metadata": {"data_type": "complex"},
            "status": {"data_type": "text"},
            "error": {"data_type": "text"},
        },
    )
    def junior_cycle_pages() -> Iterator[dict[str, Any]]:
        """All Junior Cycle subject pages."""
        for subject in subjects:
            for page in crawl_subject(
                subject=subject,
                cycle="junior_cycle",
                language=language,
                sources=sources,
                max_pages=max_pages_per_subject,
            ):
                yield page.to_dict()

    @dlt.resource(
        name="junior_cycle_pdfs",
        write_disposition="merge",
        primary_key=["url"],
        columns={
            "url": {"data_type": "text"},
            "cycle": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "language": {"data_type": "text"},
            "source": {"data_type": "text"},
            "document_type": {"data_type": "text"},
            "discovered_at": {"data_type": "timestamp"},
            "source_page_url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "year": {"data_type": "bigint"},
        },
    )
    def junior_cycle_pdfs() -> Iterator[dict[str, Any]]:
        """All Junior Cycle subject PDF URLs."""
        for subject in subjects:
            for pdf in extract_pdfs_from_subject(
                subject=subject,
                cycle="junior_cycle",
                language=language,
                sources=sources,
                max_pages=max_pages_per_subject,
            ):
                yield pdf.to_dict()

    return junior_cycle_pages, junior_cycle_pdfs


@dlt.source(name="junior_cycle_short_courses")
def short_courses_source(
    language: str = "en",
    courses: list[str] | None = None,
    max_pages_per_course: int = 20,
):
    """
    DLT source for Junior Cycle short courses.

    Args:
        language: Language code ("en" or "ga")
        courses: Optional list of short courses (default: all 8)
        max_pages_per_course: Max pages per course

    Returns:
        DLT resources for short course pages and PDFs
    """
    if courses is None:
        courses = JUNIOR_CYCLE_SHORT_COURSES

    logger.info(
        "short_courses_source_initialized",
        language=language,
        course_count=len(courses),
    )

    @dlt.resource(
        name="short_course_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def short_course_pages() -> Iterator[dict[str, Any]]:
        """All Junior Cycle short course pages."""
        for course in courses:
            for page in crawl_subject(
                subject=course,
                cycle="junior_cycle",
                language=language,
                sources=["curriculumonline"],
                max_pages=max_pages_per_course,
            ):
                yield page.to_dict()

    @dlt.resource(
        name="short_course_pdfs",
        write_disposition="merge",
        primary_key=["url"],
    )
    def short_course_pdfs() -> Iterator[dict[str, Any]]:
        """All Junior Cycle short course PDF URLs."""
        for course in courses:
            for pdf in extract_pdfs_from_subject(
                subject=course,
                cycle="junior_cycle",
                language=language,
                sources=["curriculumonline"],
                max_pages=max_pages_per_course,
            ):
                yield pdf.to_dict()

    return short_course_pages, short_course_pdfs


# Convenience functions for individual subjects


def mathematics_jc_source(language: str = "en", max_pages: int = 50):
    """DLT source for Mathematics (Junior Cycle)."""
    pages, pdfs = create_subject_source(
        subject="mathematics",
        cycle="junior_cycle",
        language=language,
        max_pages=max_pages,
    )
    return pages, pdfs


def gaeilge_jc_source(language: str = "en", max_pages: int = 50):
    """DLT source for Gaeilge/Irish (Junior Cycle)."""
    pages, pdfs = create_subject_source(
        subject="gaeilge",
        cycle="junior_cycle",
        language=language,
        max_pages=max_pages,
    )
    return pages, pdfs


def english_jc_source(language: str = "en", max_pages: int = 50):
    """DLT source for English (Junior Cycle)."""
    pages, pdfs = create_subject_source(
        subject="english",
        cycle="junior_cycle",
        language=language,
        max_pages=max_pages,
    )
    return pages, pdfs


def science_source(language: str = "en", max_pages: int = 50):
    """DLT source for Science (Junior Cycle)."""
    pages, pdfs = create_subject_source(
        subject="science",
        cycle="junior_cycle",
        language=language,
        max_pages=max_pages,
    )
    return pages, pdfs


def history_jc_source(language: str = "en", max_pages: int = 50):
    """DLT source for History (Junior Cycle)."""
    pages, pdfs = create_subject_source(
        subject="history",
        cycle="junior_cycle",
        language=language,
        max_pages=max_pages,
    )
    return pages, pdfs


def geography_jc_source(language: str = "en", max_pages: int = 50):
    """DLT source for Geography (Junior Cycle)."""
    pages, pdfs = create_subject_source(
        subject="geography",
        cycle="junior_cycle",
        language=language,
        max_pages=max_pages,
    )
    return pages, pdfs
