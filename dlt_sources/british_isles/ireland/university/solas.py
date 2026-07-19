"""
Ireland SOLAS Further Education DLT source — Tertiary 18+ stage.

Covers **SOLAS** — An tSeirbhís Oideachais Leanúnaigh agus Scileanna,
the Further Education and Training Authority of Ireland (established
under the Further Education and Training Act 2013, operational from
2014).

SOLAS operates the **16 Education and Training Boards (ETBs)** which
together deliver:

  - Apprenticeships (the 25+ designated crafts, plus the 30+ new
    Generation Apprenticeship trades from 2016+)
  - Post-Leaving-Cert (PLC) courses (Level 5/6 QQI awards at the 16 ETBs)
  - Youthreach (early-school-leaver programmes)
  - Adult Literacy + numeracy
  - Vocational Training Opportunities Scheme (VTOS)

SOLAS's role at the Tertiary 18+ stage is **complementary** to the
8 universities + 5 TUs (which cover NFQ 6-10 academic awards) — SOLAS
covers the **vocational + apprenticeship + PLC** pathways that bridge
Leaving Cert (NFQ 4-6) to the Tertiary bracket.

Honors `USE_LOCAL_SCRAPES=true` (default) to read from
`/stedding/ingest_queue/university/solas/`; live scraping is Phase 2.

Source URLs:
  - https://www.solas.ie
  - https://www.apprenticeship.ie
  - https://www.fetchcourses.ie (the course-finder portal)

Datasets produced (2 resources):
  tertiary_solas_courses    — one row per (course_code, etb_slug)
  tertiary_solas_apprenticeships — one row per (apprenticeship_code)

BAML extraction (per `baml/education/university/university_extraction.baml`):
  b.ExtractSOLASCourse(text, course_code) -> SOLASCourse
"""

from __future__ import annotations
import dlt


import hashlib
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

logger = structlog.get_logger(__name__)

SOLAS_CACHE_DIR = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "university" / "solas"

# The 16 Education and Training Boards (ETBs) under SOLAS.
# (Replaced the 33 former VECs in 2013.)
SOLAS_ETBS: tuple[dict[str, Any], ...] = (
    {"etb_slug": "cavan-monaghan", "etb_name": "Cavan and Monaghan ETB"},
    {"etb_slug": "city-of-dublin", "etb_name": "City of Dublin ETB"},
    {"etb_slug": "donegal", "etb_name": "Donegal ETB"},
    {"etb_slug": "dublin-dun-laoghaire", "etb_name": "Dublin and Dún Laoghaire ETB"},
    {"etb_slug": "galway-roscommon", "etb_name": "Galway and Roscommon ETB"},
    {"etb_slug": "kerry", "etb_name": "Kerry ETB"},
    {"etb_slug": "kildare-wicklow", "etb_name": "Kildare and Wicklow ETB"},
    {"etb_slug": "kilkenny-carlow", "etb_name": "Kilkenny and Carlow ETB"},
    {"etb_slug": "laois-offaly", "etb_name": "Laois and Offaly ETB"},
    {"etb_slug": "limerick-clare", "etb_name": "Limerick and Clare ETB"},
    {"etb_slug": "longford-westmeath", "etb_name": "Longford and Westmeath ETB"},
    {"etb_slug": "louth-meath", "etb_name": "Louth and Meath ETB"},
    {"etb_slug": "mayo-sligo-leitrim", "etb_name": "Mayo, Sligo and Leitrim ETB"},
    {"etb_slug": "tipperary", "etb_name": "Tipperary ETB"},
    {"etb_slug": "waterford-wexford", "etb_name": "Waterford and Wexford ETB"},
    {"etb_slug": "cork", "etb_name": "Cork ETB"},
)
"""The 16 Education and Training Boards under SOLAS (per the 2013 FET Act).

Cross-references:
  - QQI awards at NFQ 5-7 (see `qqi_awards.py`) — the SOLAS PLC
    pathway awards QQI Level 5/6 certificates.
  - The 8 universities + 5 TUs (see `universities.py` + `tus.py`) —
    SOLAS PLC graduates can ladder into HEI degree programmes.
"""


def _row_hash(*parts: str) -> str:
    """Deterministic SHA-256 for DLT merge keys (uniform across resources)."""
    sha = hashlib.sha256()
    sha.update("|".join(parts).encode("utf-8"))
    return sha.hexdigest()


@dlt.resource(
    name="tertiary_solas_courses",
    write_disposition="merge",
    primary_key=["course_code", "etb_slug"],
)
def tertiary_solas_courses() -> Iterator[dict[str, Any]]:
    """One row per (course_code, etb_slug) for SOLAS courses.

    Phase 1 emits no rows from the registry (the live SOLAS catalog
    has thousands of courses across the 16 ETBs; deferring to Phase 2
    with BAML extraction). When the cache has BAML-extracted rows,
    layer them on top.
    """
    if SOLAS_CACHE_DIR.exists():
        courses = SOLAS_CACHE_DIR / "solas_courses"
        if courses.exists():
            for json_file in sorted(courses.glob("**/*.json")):
                try:
                    import json as _json

                    rows = _json.loads(json_file.read_text())
                    if isinstance(rows, dict):
                        rows = [rows]
                    for row in rows:
                        if not isinstance(row, dict):
                            continue
                        row.setdefault("kind", "solas_course")
                        row.setdefault("stage", "tertiary")
                        row.setdefault("sector", "ie_solas")
                        row.setdefault("baml_extraction_status", "baml")
                        row.setdefault("extracted_at", datetime.now(UTC).isoformat())
                        yield row
                except (OSError, ValueError) as e:
                    logger.warning(
                        "solas_cache_read_failed",
                        path=str(json_file),
                        error=str(e),
                    )


@dlt.resource(
    name="tertiary_solas_apprenticeships",
    write_disposition="merge",
    primary_key=["apprenticeship_code"],
)
def tertiary_solas_apprenticeships() -> Iterator[dict[str, Any]]:
    """One row per apprenticeship_code — the SOLAS apprenticeship catalog.

    Phase 1 emits the 16 ETBs as the canonical scaffolding (the
    apprenticeship codes themselves are BAML-extracted in Phase 2).
    """
    for etb in SOLAS_ETBS:
        yield {
            "apprenticeship_code": f"SOLAS-ETB-{etb['etb_slug']}",
            "etb_slug": etb["etb_slug"],
            "etb_name": etb["etb_name"],
            "row_hash": _row_hash(etb["etb_slug"]),
            "kind": "solas_apprenticeship",
            "stage": "tertiary",
            "sector": "ie_solas",
            "language": "en",
            "source_url": (
                f"https://www.fetchcourses.ie/etb/"
                f"{etb['etb_slug']}"
            ),
            "extracted_at": datetime.now(UTC).isoformat(),
            "baml_extraction_status": "registry",
        }

    if SOLAS_CACHE_DIR.exists():
        apps = SOLAS_CACHE_DIR / "apprenticeships"
        if apps.exists():
            for json_file in sorted(apps.glob("**/*.json")):
                try:
                    import json as _json

                    rows = _json.loads(json_file.read_text())
                    if isinstance(rows, dict):
                        rows = [rows]
                    for row in rows:
                        if not isinstance(row, dict):
                            continue
                        row.setdefault("kind", "solas_apprenticeship")
                        row.setdefault("stage", "tertiary")
                        row.setdefault("sector", "ie_solas")
                        row.setdefault("baml_extraction_status", "baml")
                        row.setdefault("extracted_at", datetime.now(UTC).isoformat())
                        yield row
                except (OSError, ValueError) as e:
                    logger.warning(
                        "solas_apprenticeships_read_failed",
                        path=str(json_file),
                        error=str(e),
                    )


@dlt.source(name="ireland_tertiary_solas")
def ireland_tertiary_solas_source(
    base_path: str | Path = SOLAS_CACHE_DIR,
) -> Iterator[Any]:
    """Ireland Tertiary (SOLAS Further Education) DLT source.

    Args:
        base_path: Local cache root (default
            `/stedding/ingest_queue/university/solas/`).
    """
    yield tertiary_solas_courses()
    yield tertiary_solas_apprenticeships()


def create_ireland_tertiary_solas_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "ireland_tertiary_solas",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="ireland_tertiary_solas_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "SOLAS_CACHE_DIR",
    "SOLAS_ETBS",
    "create_ireland_tertiary_solas_pipeline",
    "ireland_tertiary_solas_source",
    "tertiary_solas_apprenticeships",
    "tertiary_solas_courses",
]