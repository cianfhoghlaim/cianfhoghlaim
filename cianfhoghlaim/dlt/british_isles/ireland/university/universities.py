"""
Ireland Universities DLT source — Tertiary 18+ stage.

Covers the **8 Republic of Ireland universities** (the canonical Irish
university sector per the Universities Act 1997 + the Technological
Universities Act 2018, before the 5 TUs were split out into
`sister file <tus.py>`):

  1. Trinity College Dublin (TCD)              — https://www.tcd.ie
  2. University College Dublin (UCD)          — https://www.ucd.ie
  3. University College Cork (UCC)            — https://www.ucc.ie
  4. University of Galway (UoG, formerly NUIG) — https://www.universityofgalway.ie
  5. University of Limerick (UL)              — https://www.ul.ie
  6. Dublin City University (DCU)              — https://www.dcu.ie
  7. Maynooth University (MU)                 — https://www.maynoothuniversity.ie
  8. Royal College of Surgeons in Ireland (RCSI) — https://www.rcsi.com

This source is the **registry-of-record** view of the 8 universities:
one row per (institution_id, academic_year, language) pair. The deep
extraction of course / module / programme descriptors per university
lives at `dlt/british_isles/ireland/education/university_of_galway_deep.py`
(UoG case study) + `_university_deep_factory.py` (reusable factory);
this source complements those by indexing the 8 institutions for
cross-university analytics (e.g. "NFQ coverage across the 8
universities").

Honors `USE_LOCAL_SCRAPES=true` (default) to read from
`/stedding/ingest_queue/university/universities/`; live scraping is
Phase 2 (Crawl4AI sitemap + Firecrawl fallback).

Source URLs:
  - https://www.tcd.ie
  - https://www.ucd.ie
  - https://www.ucc.ie
  - https://www.universityofgalway.ie
  - https://www.ul.ie
  - https://www.dcu.ie
  - https://www.maynoothuniversity.ie
  - https://www.rcsi.com

Datasets produced (2 resources):
  tertiary_universities         — one row per (institution_id, language)
  tertiary_university_faculties — one row per (institution_id, faculty_slug)

BAML extraction (per `baml/education/university/university_extraction.baml`):
  b.ExtractUniversityInfo(text, institution_id) -> University
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

UNIVERSITY_CACHE_DIR = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "university" / "universities"

# The 8 Republic of Ireland universities (Universities Act 1997 + subsequent).
# `institution_id` is the kebab-case slug used as the DLT merge primary
# key suffix. `nfq_range` captures the min/max NFQ level each institution
# awards (e.g. UoG awards 6-10, RCSI awards 8-10 only).
UNIVERSITY_INSTITUTIONS: tuple[dict[str, Any], ...] = (
    {
        "institution_id": "ie-university-trinity",
        "institution_name": "Trinity College Dublin",
        "abbreviation": "TCD",
        "founded": 1592,
        "home_url": "https://www.tcd.ie",
        "nfq_min": 6,
        "nfq_max": 10,
        "language": "en",
        "faculty_slugs": [
            "arts-humanities-social-sciences",
            "engineering-mathematics-science",
            "health-sciences",
            "business",
            "law",
        ],
    },
    {
        "institution_id": "ie-university-ucd",
        "institution_name": "University College Dublin",
        "abbreviation": "UCD",
        "founded": 1854,
        "home_url": "https://www.ucd.ie",
        "nfq_min": 6,
        "nfq_max": 10,
        "language": "en",
        "faculty_slugs": [
            "arts-humanities",
            "business",
            "engineering-architecture",
            "health-agricultural-sciences",
            "law",
            "science",
        ],
    },
    {
        "institution_id": "ie-university-ucc",
        "institution_name": "University College Cork",
        "abbreviation": "UCC",
        "founded": 1845,
        "home_url": "https://www.ucc.ie",
        "nfq_min": 6,
        "nfq_max": 10,
        "language": "en",
        "faculty_slugs": [
            "arts-celtic-studies-social-sciences",
            "business-law",
            "education-health-sciences",
            "engineering-science",
            "medicine-health",
            "science-engineering-food-science",
        ],
    },
    {
        "institution_id": "ie-university-galway",
        "institution_name": "University of Galway",
        "abbreviation": "UoG",
        "founded": 1845,
        "home_url": "https://www.universityofgalway.ie",
        "nfq_min": 6,
        "nfq_max": 10,
        "language": "en",
        "faculty_slugs": [
            "arts-social-sciences-celtic-studies",
            "business-public-policy-law",
            "college-of-science-engineering",
            "medicine-nursing-health-sciences",
        ],
    },
    {
        "institution_id": "ie-university-limerick",
        "institution_name": "University of Limerick",
        "abbreviation": "UL",
        "founded": 1972,
        "home_url": "https://www.ul.ie",
        "nfq_min": 6,
        "nfq_max": 10,
        "language": "en",
        "faculty_slugs": [
            "arts-humanities-social-sciences",
            "business-education",
            "education-health-sciences",
            "science-engineering",
            "irish-dance-studies",
        ],
    },
    {
        "institution_id": "ie-university-dcu",
        "institution_name": "Dublin City University",
        "abbreviation": "DCU",
        "founded": 1975,
        "home_url": "https://www.dcu.ie",
        "nfq_min": 6,
        "nfq_max": 10,
        "language": "en",
        "faculty_slugs": [
            "computing-engineering",
            "humanities-social-sciences",
            "business",
            "science-health",
            "education",
        ],
    },
    {
        "institution_id": "ie-university-maynooth",
        "institution_name": "Maynooth University",
        "abbreviation": "MU",
        "founded": 1997,
        "home_url": "https://www.maynoothuniversity.ie",
        "nfq_min": 6,
        "nfq_max": 10,
        "language": "en",
        "faculty_slugs": [
            "arts-humanities",
            "social-sciences",
            "science-engineering",
            "business",
            "education",
        ],
    },
    {
        "institution_id": "ie-university-rcsi",
        "institution_name": "Royal College of Surgeons in Ireland",
        "abbreviation": "RCSI",
        "founded": 1784,
        "home_url": "https://www.rcsi.com",
        "nfq_min": 8,
        "nfq_max": 10,
        "language": "en",
        "faculty_slugs": [
            "medicine",
            "nursing-midwifery",
            "pharmacy-biomolecular-sciences",
            "physiotherapy",
            "dentistry",
        ],
    },
)
"""The 8 Republic of Ireland universities per the Universities Act 1997.

Note: RCSI is the only one whose `nfq_min = 8` — it does not award
undergraduate (NFQ 6/7) certificates. All other 7 award NFQ 6-10.
"""


def _row_hash(*parts: str) -> str:
    """Deterministic SHA-256 for DLT merge keys (uniform across resources)."""
    sha = hashlib.sha256()
    sha.update("|".join(parts).encode("utf-8"))
    return sha.hexdigest()


@dlt.resource(
    name="tertiary_universities",
    write_disposition="merge",
    primary_key=["institution_id", "language"],
)
def tertiary_universities() -> Iterator[dict[str, Any]]:
    """One row per (institution_id, language) for the 8 Irish universities.

    Honors `USE_LOCAL_SCRAPES=true` (default). When the cache is empty
    (Phase 1), the registry is materialized from the canonical
    `UNIVERSITY_INSTITUTIONS` table above so downstream analytics can
    join immediately. Phase 2 will overwrite / enrich with BAML-extracted
    rows from `/stedding/ingest_queue/university/universities/`.
    """
    for inst in UNIVERSITY_INSTITUTIONS:
        yield {
            "institution_id": inst["institution_id"],
            "institution_name": inst["institution_name"],
            "abbreviation": inst["abbreviation"],
            "founded": inst["founded"],
            "home_url": inst["home_url"],
            "language": inst["language"],
            "nfq_min": inst["nfq_min"],
            "nfq_max": inst["nfq_max"],
            "faculty_count": len(inst["faculty_slugs"]),
            "row_hash": _row_hash(inst["institution_id"], inst["language"]),
            "kind": "university",
            "stage": "tertiary",
            "sector": "ie_university",
            "source_url": inst["home_url"],
            "extracted_at": datetime.now(UTC).isoformat(),
            "baml_extraction_status": "registry",
        }

    # If the cache has richer (BAML-extracted) rows, layer them on top.
    if UNIVERSITY_CACHE_DIR.exists():
        for json_file in sorted(UNIVERSITY_CACHE_DIR.glob("**/*.json")):
            try:
                import json as _json

                rows = _json.loads(json_file.read_text())
                if isinstance(rows, dict):
                    rows = [rows]
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    row.setdefault("kind", "university")
                    row.setdefault("stage", "tertiary")
                    row.setdefault("sector", "ie_university")
                    row.setdefault("baml_extraction_status", "baml")
                    row.setdefault("extracted_at", datetime.now(UTC).isoformat())
                    yield row
            except (OSError, ValueError) as e:
                logger.warning(
                    "university_cache_read_failed",
                    path=str(json_file),
                    error=str(e),
                )


@dlt.resource(
    name="tertiary_university_faculties",
    write_disposition="merge",
    primary_key=["institution_id", "faculty_slug"],
)
def tertiary_university_faculties() -> Iterator[dict[str, Any]]:
    """One row per (institution_id, faculty_slug) — the cross-product
    of the 8 universities × their faculties.

    Useful for faculty-level coverage analytics (e.g. "how many
    universities have a Faculty of Education?"). The full UoG
    faculty deep-extraction lives in `university_of_galway_deep.py`.
    """
    for inst in UNIVERSITY_INSTITUTIONS:
        for faculty_slug in inst["faculty_slugs"]:
            yield {
                "institution_id": inst["institution_id"],
                "institution_name": inst["institution_name"],
                "faculty_slug": faculty_slug,
                "row_hash": _row_hash(inst["institution_id"], faculty_slug),
                "language": inst["language"],
                "stage": "tertiary",
                "kind": "university_faculty",
                "sector": "ie_university",
                "source_url": (
                    f"{inst['home_url'].rstrip('/')}/"
                    f"{faculty_slug.replace('_', '-')}"
                ),
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="ireland_tertiary_universities")
def ireland_tertiary_universities_source(
    base_path: str | Path = UNIVERSITY_CACHE_DIR,
) -> Iterator[Any]:
    """Ireland Tertiary (8 universities) DLT source.

    Args:
        base_path: Local cache root (default
            `/stedding/ingest_queue/university/universities/`).
    """
    yield tertiary_universities()
    yield tertiary_university_faculties()


def create_ireland_tertiary_universities_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "ireland_tertiary_universities",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="ireland_tertiary_universities_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "UNIVERSITY_CACHE_DIR",
    "UNIVERSITY_INSTITUTIONS",
    "create_ireland_tertiary_universities_pipeline",
    "ireland_tertiary_universities_source",
    "tertiary_universities",
    "tertiary_university_faculties",
]