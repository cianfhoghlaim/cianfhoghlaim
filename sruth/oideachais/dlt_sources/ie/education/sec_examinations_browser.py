"""
Education IE source: sec_examinations_browser_source

Split from ireland/examinations.py in Phase 3D.
"""

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from logging import basicConfig, getLogger
from typing import Any
import dlt
import logfire

from ._examinations_helpers import (
    ALL_JC_SUBJECTS,
    ALL_LCA_SUBJECTS,
    ALL_LC_SUBJECTS,
    _get_exam_materials_browser,
)

def sec_examinations_browser_source(
    subjects: list[str] | None = None,
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
    material_types: list[str] | None = None,
):
    """
    DLT source for SEC exam materials using browser automation.

    Uses Stagehand browser automation to interact with dropdowns on examinations.ie
    and discover exam papers, marking schemes, and examiner reports.

    The exam archive page uses a cascading JavaScript form:
    1. Accept terms checkbox
    2. Choose Type dropdown (Exam Papers, Marking Schemes, etc.)
    3. Level dropdown → Subject dropdown → Year dropdown → Submit

    A single Stagehand session is reused across all subjects for efficiency.

    Args:
        subjects: List of subject slugs (default: all LC/JC subjects for level)
        years: List of years (default: 2020-2024, full archive: 1999-2025)
        level: Exam level (leaving_certificate, junior_cycle, leaving_certificate_applied)
        language: Language code (en, ga). Both languages' papers are downloaded.
        material_types: List of types to scrape (default: both exam_papers and marking_schemes)
            Options: "exam_papers", "marking_schemes"

    Returns:
        DLT resources: exam_papers, marking_schemes, all_exam_materials

    Examples:
        # All Leaving Certificate subjects, recent 5 years
        pipeline.run(sec_examinations_browser_source(years=[2023, 2024]))

        # Mathematics exam papers only, full archive
        pipeline.run(sec_examinations_browser_source(
            subjects=["mathematics"],
            years=list(range(1999, 2026)),
            material_types=["exam_papers"],
        ))

        # All marking schemes for Junior Cycle
        pipeline.run(sec_examinations_browser_source(
            level="junior_cycle",
            material_types=["marking_schemes"],
        ))
    """
    _LEVEL_SUBJECTS = {
        "leaving_certificate": ALL_LC_SUBJECTS,
        "junior_cycle": ALL_JC_SUBJECTS,
        "leaving_certificate_applied": ALL_LCA_SUBJECTS,
    }
    if subjects is None:
        subjects = _LEVEL_SUBJECTS.get(level, ALL_LC_SUBJECTS)

    if years is None:
        years = list(range(2020, 2025))

    if material_types is None:
        material_types = ["exam_papers", "marking_schemes"]

    logger.info(
        f"sec_examinations_browser_source_initialized: "
        f"subject_count={len(subjects)}, year_count={len(years)}, "
        f"level={level}, language={language}, material_types={material_types}"
    )

    @dlt.resource(
        name="exam_papers",
        write_disposition="merge",
        primary_key=["pdf_url"],
        columns={
            "subject": {"data_type": "text"},
            "year": {"data_type": "bigint"},
            "level": {"data_type": "text"},
            "material_type": {"data_type": "text"},
            "pdf_url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "paper_number": {"data_type": "bigint"},
            "exam_level": {"data_type": "text"},
            "language": {"data_type": "text"},
            "content_hash": {"data_type": "text"},
            "scraped_at": {"data_type": "timestamp"},
            "status": {"data_type": "text"},
        },
    )
    def exam_papers() -> Iterator[dict[str, Any]]:
        """Past examination papers."""
        for material in _get_exam_materials_browser(subjects, years, level, language, material_types):
            if material.get("material_type") == "paper":
                yield material

    @dlt.resource(
        name="marking_schemes",
        write_disposition="merge",
        primary_key=["pdf_url"],
        columns={
            "subject": {"data_type": "text"},
            "year": {"data_type": "bigint"},
            "level": {"data_type": "text"},
            "material_type": {"data_type": "text"},
            "pdf_url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "paper_number": {"data_type": "bigint"},
            "exam_level": {"data_type": "text"},
            "language": {"data_type": "text"},
            "content_hash": {"data_type": "text"},
            "scraped_at": {"data_type": "timestamp"},
            "status": {"data_type": "text"},
        },
    )
    def marking_schemes() -> Iterator[dict[str, Any]]:
        """Marking schemes for examination papers."""
        for material in _get_exam_materials_browser(subjects, years, level, language, material_types):
            if material.get("material_type") == "marking_scheme":
                yield material

    @dlt.resource(
        name="all_exam_materials",
        write_disposition="merge",
        primary_key=["pdf_url"],
        columns={
            "subject": {"data_type": "text"},
            "year": {"data_type": "bigint"},
            "level": {"data_type": "text"},
            "material_type": {"data_type": "text"},
            "pdf_url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "paper_number": {"data_type": "bigint"},
            "exam_level": {"data_type": "text"},
            "language": {"data_type": "text"},
            "content_hash": {"data_type": "text"},
            "scraped_at": {"data_type": "timestamp"},
            "status": {"data_type": "text"},
        },
    )
    def all_exam_materials() -> Iterator[dict[str, Any]]:
        """All exam materials (papers, schemes, reports)."""
        yield from _get_exam_materials_browser(subjects, years, level, language, material_types)

    return exam_papers, marking_schemes, all_exam_materials
