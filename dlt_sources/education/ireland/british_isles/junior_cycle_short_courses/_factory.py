"""Factory for the 16 JC short-course DLT sources (BIEP v2).

The 16 NCCA JC short courses (per `JC_SHORT_COURSES` at line 73 of
`dlt/british_isles/ireland/education/junior_cycle.py`):
    coding, chinese, japanese, russian, polish, lithuanian, portuguese,
    arabic, hebrew, philosophy, film_studies, financial_literacy,
    media_literacy, personal_professional_development, digital_media,
    athletic_studies.

Each short-course DLT source is generated at import time via the
`build_jc_short_course_source` factory.

The destination DuckLake namespace is:
    cianfhoghlaim.education.british_isles.ireland.junior_cycle.short_courses.<course_slug>

Reference: openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/
"""
from __future__ import annotations
import dlt


import hashlib
import os
import re
from datetime import UTC, datetime
from pathlib import Path

import dlt_sources
import structlog

from dlt_sources.education.ireland.british_isles.education._pdf_text import (
    extract_pdf_text,
)

logger = structlog.get_logger(__name__)

JC_SHORT_COURSES: tuple[str, ...] = (
    "coding",
    "chinese",
    "japanese",
    "russian",
    "polish",
    "lithuanian",
    "portuguese",
    "arabic",
    "hebrew",
    "philosophy",
    "film_studies",
    "financial_literacy",
    "media_literacy",
    "personal_professional_development",
    "digital_media",
    "athletic_studies",
)

JC_SHORT_COURSE_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "junior_cycle" / "short_courses"


def _file_hash(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


# The shared `extract_pdf_text` helper handles both the real pymupdf extraction
# and the legacy stub fallback. See
# dlt_sources.education.ireland.british_isles.education._pdf_text


def build_jc_short_course_source(course_slug: str, cache_dir: Path | None = None):
    """Build a DLT source for one NCCA JC short course.

    Parameters
    ----------
    course_slug : str
        One of the 16 JC short courses (`JC_SHORT_COURSES`).
    cache_dir : Path | None
        Override the default cache dir.

    Returns
    -------
    dlt.Source
        A DLT source with 2 resources:
        - `jc_short_course_<slug>_specifications` — per-PDF specification rows
        - `jc_short_course_<slug>_metadata` — per-course metadata row
    """
    if course_slug not in JC_SHORT_COURSES:
        raise ValueError(
            f"Unknown JC short course '{course_slug}'. "
            f"Must be one of {JC_SHORT_COURSES}."
        )

    effective_cache_dir = (
        cache_dir
        if cache_dir is not None
        else JC_SHORT_COURSE_CACHE_ROOT / course_slug
    )
    source_id = (
        f"british_isles.ireland.education.jc_short_course_{course_slug}"
    )

    @dlt.resource(
        name=f"jc_short_course_{course_slug}_specifications",
        write_disposition="merge",
        primary_key=["content_hash"],
    )
    def jc_short_course_specifications():
        if not effective_cache_dir.exists():
            logger.warning(
                "jc_short_course_cache_dir_missing",
                course_slug=course_slug,
                path=str(effective_cache_dir),
            )
            return
        for pdf_path in sorted(effective_cache_dir.glob("*.pdf")):
            content_hash = _file_hash(pdf_path)
            m = re.search(r"(20\d{2}|19\d{2})", pdf_path.name)
            spec_year = int(m.group(1)) if m else None
            yield {
                "source_id": source_id,
                "course_slug": course_slug,
                "language": "en",
                "filename": pdf_path.name,
                "file_path": str(pdf_path),
                "file_size_bytes": pdf_path.stat().st_size,
                "content_hash": content_hash,
                "pdf_text": extract_pdf_text(pdf_path),
                "specification_year": spec_year,
                "ingested_at": datetime.now(UTC).isoformat(),
                "country_code": "ireland",
                "jurisdiction": "ireland",
                "education_stage": "junior_cycle_short_course",
                "namespace": (
                    "cianfhoghlaim.education.british_isles.ireland.junior_cycle."
                    f"short_courses.{course_slug}"
                ),
            }

    @dlt.resource(
        name=f"jc_short_course_{course_slug}_metadata",
        write_disposition="merge",
        primary_key=["course_slug"],
    )
    def jc_short_course_metadata():
        yield {
            "source_id": source_id,
            "course_slug": course_slug,
            "language": "en",
            "country_code": "ireland",
            "jurisdiction": "ireland",
            "education_stage": "junior_cycle_short_course",
            "namespace": (
                "cianfhoghlaim.education.british_isles.ireland.junior_cycle."
                f"short_courses.{course_slug}"
            ),
            "uses_local_scrapes": os.getenv("USE_LOCAL_SCRAPES", "true").lower() == "true",
            "first_ingested_at": datetime.now(UTC).isoformat(),
        }

    return jc_short_course_specifications, jc_short_course_metadata


# Generate the 16 per-short-course DLT source factories at import time.
__all__: list[str] = []
for _course_slug in JC_SHORT_COURSES:
    _name = f"{_course_slug}_source"

    def _make(slug: str = _course_slug):
        return build_jc_short_course_source(slug)

    globals()[_name] = _make
    __all__.append(_name)
