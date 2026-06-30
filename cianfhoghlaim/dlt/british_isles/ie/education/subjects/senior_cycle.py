"""
Senior Cycle Subject DLT Sources.

Provides per-subject DLT resources for all 34 Leaving Certificate subjects.
Each subject yields pages and PDF URLs from curriculumonline.ie and ncca.ie.

Usage:
    from cianfhoghlaim.dlt.british_isles.ie.education.subjects.senior_cycle import (
        senior_cycle_source,
    )

    # All subjects in English
    pipeline.run(senior_cycle_source(language="en"))

    # All subjects in Irish
    pipeline.run(senior_cycle_source(language="ga"))

    # Single subject
    pipeline.run(senior_cycle_source(language="en", subjects=["mathematics"]))
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

# All Senior Cycle subjects from curriculum_index.json
SENIOR_CYCLE_SUBJECTS = [
    "accounting",
    "agricultural-science",
    "applied-mathematics",
    "arabic",
    "art",
    "biology",
    "business",
    "chemistry",
    "classical-studies",
    "computer-science",
    "construction-studies",
    "design-and-communication-graphics",
    "economics",
    "engineering",
    "english",
    "french",
    "gaeilge",
    "geography",
    "german",
    "history",
    "home-economics",
    "italian",
    "japanese",
    "latin",
    "mathematics",
    "music",
    "physical-education",
    "physics",
    "physics-and-chemistry",
    "politics-and-society",
    "religious-education",
    "spanish",
    "technology",
]

# Subjects with NCCA pages (under redevelopment)
SUBJECTS_WITH_NCCA = [
    "accounting",
    "biology",
    "chemistry",
    "english",
    "gaeilge",
    "geography",
    "history",
    "physics",
]


@dlt.source(name="senior_cycle_subjects")
def senior_cycle_source(
    language: str = "en",
    subjects: list[str] | None = None,
    sources: list[str] | None = None,
    max_pages_per_subject: int = 30,
):
    """
    DLT source for Senior Cycle (Leaving Certificate) subjects.

    Args:
        language: Language code ("en" or "ga")
        subjects: Optional list of subjects (default: all 34 subjects)
        sources: Optional list of sources (default: curriculumonline, ncca)
        max_pages_per_subject: Max pages to crawl per subject

    Returns:
        DLT resources for pages and PDFs for each subject

    Examples:
        # All subjects in English
        pipeline.run(senior_cycle_source(language="en"))

        # Mathematics only
        pipeline.run(senior_cycle_source(subjects=["mathematics"]))

        # Multiple subjects in Irish
        pipeline.run(senior_cycle_source(
            language="ga",
            subjects=["mathematics", "gaeilge", "biology"]
        ))
    """
    if subjects is None:
        subjects = SENIOR_CYCLE_SUBJECTS

    if sources is None:
        sources = ["curriculumonline", "ncca"]

    logger.info(
        "senior_cycle_source_initialized",
        language=language,
        subject_count=len(subjects),
        sources=sources,
    )

    # Create unified pages resource for all subjects
    @dlt.resource(
        name="senior_cycle_pages",
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
    def senior_cycle_pages() -> Iterator[dict[str, Any]]:
        """All Senior Cycle subject pages."""
        for subject in subjects:
            # Determine which sources have data for this subject
            subject_sources = sources.copy()
            if subject not in SUBJECTS_WITH_NCCA and "ncca" in subject_sources:
                subject_sources = [s for s in subject_sources if s != "ncca"]

            for page in crawl_subject(
                subject=subject,
                cycle="senior_cycle",
                language=language,
                sources=subject_sources,
                max_pages=max_pages_per_subject,
            ):
                yield page.to_dict()

    @dlt.resource(
        name="senior_cycle_pdfs",
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
    def senior_cycle_pdfs() -> Iterator[dict[str, Any]]:
        """All Senior Cycle subject PDF URLs."""
        for subject in subjects:
            subject_sources = sources.copy()
            if subject not in SUBJECTS_WITH_NCCA and "ncca" in subject_sources:
                subject_sources = [s for s in subject_sources if s != "ncca"]

            for pdf in extract_pdfs_from_subject(
                subject=subject,
                cycle="senior_cycle",
                language=language,
                sources=subject_sources,
                max_pages=max_pages_per_subject,
            ):
                yield pdf.to_dict()

    return senior_cycle_pages, senior_cycle_pdfs


# Convenience functions for individual subjects


def mathematics_source(language: str = "en", max_pages: int = 50):
    """DLT source for Mathematics (Leaving Certificate)."""
    pages, pdfs = create_subject_source(
        subject="mathematics",
        cycle="senior_cycle",
        language=language,
        max_pages=max_pages,
    )
    return pages, pdfs


def gaeilge_source(language: str = "en", max_pages: int = 50):
    """DLT source for Gaeilge/Irish (Leaving Certificate)."""
    pages, pdfs = create_subject_source(
        subject="gaeilge",
        cycle="senior_cycle",
        language=language,
        sources=["curriculumonline", "ncca"],
        max_pages=max_pages,
    )
    return pages, pdfs


def english_source(language: str = "en", max_pages: int = 50):
    """DLT source for English (Leaving Certificate)."""
    pages, pdfs = create_subject_source(
        subject="english",
        cycle="senior_cycle",
        language=language,
        sources=["curriculumonline", "ncca"],
        max_pages=max_pages,
    )
    return pages, pdfs


def biology_source(language: str = "en", max_pages: int = 50):
    """DLT source for Biology (Leaving Certificate)."""
    pages, pdfs = create_subject_source(
        subject="biology",
        cycle="senior_cycle",
        language=language,
        sources=["curriculumonline", "ncca"],
        max_pages=max_pages,
    )
    return pages, pdfs


def chemistry_source(language: str = "en", max_pages: int = 50):
    """DLT source for Chemistry (Leaving Certificate)."""
    pages, pdfs = create_subject_source(
        subject="chemistry",
        cycle="senior_cycle",
        language=language,
        sources=["curriculumonline", "ncca"],
        max_pages=max_pages,
    )
    return pages, pdfs


def physics_source(language: str = "en", max_pages: int = 50):
    """DLT source for Physics (Leaving Certificate)."""
    pages, pdfs = create_subject_source(
        subject="physics",
        cycle="senior_cycle",
        language=language,
        sources=["curriculumonline", "ncca"],
        max_pages=max_pages,
    )
    return pages, pdfs


def geography_source(language: str = "en", max_pages: int = 50):
    """DLT source for Geography (Leaving Certificate)."""
    pages, pdfs = create_subject_source(
        subject="geography",
        cycle="senior_cycle",
        language=language,
        sources=["curriculumonline", "ncca"],
        max_pages=max_pages,
    )
    return pages, pdfs


def history_source(language: str = "en", max_pages: int = 50):
    """DLT source for History (Leaving Certificate)."""
    pages, pdfs = create_subject_source(
        subject="history",
        cycle="senior_cycle",
        language=language,
        sources=["curriculumonline", "ncca"],
        max_pages=max_pages,
    )
    return pages, pdfs


def computer_science_source(language: str = "en", max_pages: int = 50):
    """DLT source for Computer Science (Leaving Certificate)."""
    pages, pdfs = create_subject_source(
        subject="computer-science",
        cycle="senior_cycle",
        language=language,
        max_pages=max_pages,
    )
    return pages, pdfs


def business_source(language: str = "en", max_pages: int = 50):
    """DLT source for Business (Leaving Certificate)."""
    pages, pdfs = create_subject_source(
        subject="business",
        cycle="senior_cycle",
        language=language,
        max_pages=max_pages,
    )
    return pages, pdfs
