"""Factory for per-subject JC DLT sources.

This module generates the 36 per-subject Junior Cycle DLT sources
(18 NCCA JC subjects × 2 languages EN + GA) at import time, sharing
the same code path through :func:`build_jc_subject_source`.

The 18 subjects (per `JC_SUBJECTS` in `dlt/british_isles/ireland/education/junior_cycle.py`):
    english, gaeilge, mathematics, irish_history, geography, science,
    business_studies, french, german, spanish, italian, home_economics,
    music, art, technology, engineering, graphics, wood_technology.

The 2 languages: en, ga.

For each (subject, language) tuple, a top-level function is generated:

    english_en_source(), english_ga_source(), ..., wood_technology_ga_source()

Each function returns a DLT source ready to be passed to `pipeline.run(...)`.

The destination DuckLake namespace is:
    cianfhoghlaim.education.british_isles.ireland.junior_cycle.<subject>.<lang>

per the cross-region-pipeline spec (canonical DuckLake namespace shape).

Reference: openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/
"""
from __future__ import annotations
import dlt


import hashlib
import os
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

from dlt_sources.british_isles.ireland.education._pdf_text import (
    extract_pdf_text,
)

logger = structlog.get_logger(__name__)

# The 18 NCCA JC subjects — kept in sync with `JC_SUBJECTS` at line 51 of the
# canonical `dlt/british_isles/ireland/education/junior_cycle.py`.
JC_SUBJECTS: tuple[str, ...] = (
    "english",
    "gaeilge",
    "mathematics",
    "irish_history",
    "geography",
    "science",
    "business_studies",
    "french",
    "german",
    "spanish",
    "italian",
    "home_economics",
    "music",
    "art",
    "technology",
    "engineering",
    "graphics",
    "wood_technology",
)

JC_LANGUAGES: tuple[str, ...] = ("en", "ga")

# The cache root (per `USE_LOCAL_SCRAPES=true` convention).
JC_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "junior_cycle"


def _file_hash(path: Path) -> str:
    """Compute the SHA-256 hash of a file (used as the canonical content hash)."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


# The shared `extract_pdf_text` helper handles both the real pymupdf extraction
# and the legacy stub fallback. See
# dlt_sources.british_isles.ireland.education._pdf_text


def build_jc_subject_source(
    subject: str,
    language: str,
    cache_dir: Path | None = None,
):
    """Build a DLT source for one (subject, language) pair.

    Parameters
    ----------
    subject : str
        One of the 18 NCCA JC subjects (`JC_SUBJECTS`).
    language : str
        One of `{"en", "ga"}`.
    cache_dir : Path | None
        Override the default `/stedding/ingest_queue/junior_cycle/<subject>/<lang>/`
        cache directory.

    Returns
    -------
    dlt.Source
        A DLT source with 2 resources:
        - `jc_<subject>_<lang>_specifications` — the per-subject specification
          (one row per PDF file in the cache)
        - `jc_<subject>_<lang>_metadata` — the per-subject metadata
          (one row per (subject, language) tuple, written once)
    """
    if subject not in JC_SUBJECTS:
        raise ValueError(
            f"Unknown JC subject '{subject}'. "
            f"Must be one of {JC_SUBJECTS}."
        )
    if language not in JC_LANGUAGES:
        raise ValueError(
            f"Unknown language '{language}'. Must be 'en' or 'ga'."
        )

    effective_cache_dir = (
        cache_dir
        if cache_dir is not None
        else JC_CACHE_ROOT / subject / language
    )
    source_id = f"british_isles.ireland.education.jc_{subject}_{language}"

    @dlt.resource(
        name=f"jc_{subject}_{language}_specifications",
        write_disposition="merge",
        primary_key=["content_hash"],
    )
    def jc_specifications():
        """Yield one row per cached specification PDF for this (subject, language)."""
        if not effective_cache_dir.exists():
            logger.warning(
                "jc_cache_dir_missing",
                subject=subject,
                language=language,
                path=str(effective_cache_dir),
            )
            return

        for pdf_path in sorted(effective_cache_dir.glob("*.pdf")):
            content_hash = _file_hash(pdf_path)
            yield {
                "source_id": source_id,
                "subject": subject,
                "language": language,
                "filename": pdf_path.name,
                "file_path": str(pdf_path),
                "file_size_bytes": pdf_path.stat().st_size,
                "content_hash": content_hash,
                "pdf_text": extract_pdf_text(pdf_path),
                "specification_year": _extract_year(pdf_path.name),
                "ingested_at": datetime.now(UTC).isoformat(),
                "country_code": "ireland",
                "jurisdiction": "ireland",
                "education_stage": "junior_cycle",
                "stage_year": "jc",
                "namespace": (
                    f"cianfhoghlaim.education.british_isles.ireland."
                    f"junior_cycle.{subject}.{language}"
                ),
            }

    @dlt.resource(
        name=f"jc_{subject}_{language}_metadata",
        write_disposition="merge",
        primary_key=["subject", "language"],
    )
    def jc_metadata():
        """Yield one row per (subject, language) — the per-resource metadata."""
        yield {
            "source_id": source_id,
            "subject": subject,
            "language": language,
            "country_code": "ireland",
            "jurisdiction": "ireland",
            "education_stage": "junior_cycle",
            "namespace": (
                f"cianfhoghlaim.education.british_isles.ireland."
                f"junior_cycle.{subject}.{language}"
            ),
            "uses_local_scrapes": os.getenv("USE_LOCAL_SCRAPES", "true").lower() == "true",
            "first_ingested_at": datetime.now(UTC).isoformat(),
        }

    return jc_specifications, jc_metadata


def _extract_year(filename: str) -> int | None:
    """Extract a 4-digit year from a filename (if present)."""
    m = re.search(r"(20\d{2}|19\d{2})", filename)
    return int(m.group(1)) if m else None


# Generate the 36 per-subject DLT source factories at import time.
__all__: list[str] = []
for _subject in JC_SUBJECTS:
    for _language in JC_LANGUAGES:
        _name = f"{_subject}_{_language}_source"

        def _make(subj: str = _subject, lang: str = _language):
            """Lazily return the built DLT source for a (subject, language) tuple."""
            return build_jc_subject_source(subj, lang)

        globals()[_name] = _make
        __all__.append(_name)
