"""
Ireland Technological Universities (TUs) DLT source — Tertiary 18+ stage.

Covers the **5 Technological Universities** of the Republic of Ireland,
created via the consolidation of the 11 Institutes of Technology (IoTs)
under the Technological Universities Act 2018:

  1. TU Dublin (TUD, formerly DIT + ITB + ITT)        — https://www.tudublin.ie
  2. Munster Technological University (MTU, formerly CIT + ITT) — https://www.mtu.ie
  3. Technological University of the Shannon (TUS, formerly AIT + LIT) — https://www.tus.ie
  4. Atlantic Technological University (ATU, formerly GMIT + IT Sligo + Letterkenny IT) — https://www.atu.ie
  5. South East Technological University (SETU, formerly WIT + IT Carlow) — https://www.setu.ie

Note: TU Ulster (proposed cross-border TU spanning both sides of the
border) is NOT in this registry; it would be tracked under
`dlt/british_isles/northern_ireland/tertiary/` if created.

Honors `USE_LOCAL_SCRAPES=true` (default) to read from
`/stedding/ingest_queue/university/tus/`; live scraping is Phase 2.

Source URLs:
  - https://www.tudublin.ie
  - https://www.mtu.ie
  - https://www.tus.ie
  - https://www.atu.ie
  - https://www.setu.ie

Datasets produced (2 resources):
  tertiary_tus              — one row per (tu_id, language)
  tertiary_tu_campuses      — one row per (tu_id, campus_slug)

BAML extraction (per `baml/education/university/university_extraction.baml`):
  b.ExtractTuInfo(text, tu_id) -> TU
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

TU_CACHE_DIR = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "university" / "tus"

# The 5 Technological Universities. `parent_iots` captures the
# predecessor Institutes of Technology (the 11 IoTs that merged).
# `nfq_min / nfq_max` is the same as the universities (NFQ 6-10).
TU_INSTITUTIONS: tuple[dict[str, Any], ...] = (
    {
        "tu_id": "ie-tu-dublin",
        "tu_name": "Technological University Dublin",
        "abbreviation": "TUD",
        "established": 2019,
        "home_url": "https://www.tudublin.ie",
        "language": "en",
        "parent_iots": ["DIT", "ITB", "ITT"],
        "campus_slugs": [
            "city",
            "blanchardstown",
            "tallaght",
            "aungier-street",
        ],
        "nfq_min": 6,
        "nfq_max": 10,
    },
    {
        "tu_id": "ie-tu-munster",
        "tu_name": "Munster Technological University",
        "abbreviation": "MTU",
        "established": 2021,
        "home_url": "https://www.mtu.ie",
        "language": "en",
        "parent_iots": ["CIT", "ITTralee"],
        "campus_slugs": [
            "cork",
            "bishopstown",
            "kerry",
            "tralee",
        ],
        "nfq_min": 6,
        "nfq_max": 10,
    },
    {
        "tu_id": "ie-tu-shannon",
        "tu_name": "Technological University of the Shannon",
        "abbreviation": "TUS",
        "established": 2021,
        "home_url": "https://www.tus.ie",
        "language": "en",
        "parent_iots": ["AIT", "LIT"],
        "campus_slugs": [
            "athlone",
            "moylish-limerick",
            "thurles",
            "clonmel",
        ],
        "nfq_min": 6,
        "nfq_max": 10,
    },
    {
        "tu_id": "ie-tu-atlantic",
        "tu_name": "Atlantic Technological University",
        "abbreviation": "ATU",
        "established": 2022,
        "home_url": "https://www.atu.ie",
        "language": "en",
        "parent_iots": ["GMIT", "ITSligo", "LYIT"],
        "campus_slugs": [
            "galway-city",
            "sligo",
            "letterkenny",
            "donegal",
            "mayo",
        ],
        "nfq_min": 6,
        "nfq_max": 10,
    },
    {
        "tu_id": "ie-tu-south-east",
        "tu_name": "South East Technological University",
        "abbreviation": "SETU",
        "established": 2022,
        "home_url": "https://www.setu.ie",
        "language": "en",
        "parent_iots": ["WIT", "ITCarlow"],
        "campus_slugs": [
            "waterford",
            "carlow",
            "wexford",
            "wicklow",
        ],
        "nfq_min": 6,
        "nfq_max": 10,
    },
)
"""The 5 Technological Universities per the Technological Universities Act 2018.

Cross-references:
  - Universities Act 1997 (the 7 universities, see `universities.py`)
  - Qualifications and Quality Assurance (Education and Training) Act 2012
    (QQI, see `qqi_awards.py`)
"""


def _row_hash(*parts: str) -> str:
    """Deterministic SHA-256 for DLT merge keys (uniform across resources)."""
    sha = hashlib.sha256()
    sha.update("|".join(parts).encode("utf-8"))
    return sha.hexdigest()


@dlt.resource(
    name="tertiary_tus",
    write_disposition="merge",
    primary_key=["tu_id", "language"],
)
def tertiary_tus() -> Iterator[dict[str, Any]]:
    """One row per (tu_id, language) for the 5 Irish TUs."""
    for tu in TU_INSTITUTIONS:
        yield {
            "tu_id": tu["tu_id"],
            "tu_name": tu["tu_name"],
            "abbreviation": tu["abbreviation"],
            "established": tu["established"],
            "home_url": tu["home_url"],
            "language": tu["language"],
            "parent_iots": tu["parent_iots"],
            "campus_count": len(tu["campus_slugs"]),
            "nfq_min": tu["nfq_min"],
            "nfq_max": tu["nfq_max"],
            "row_hash": _row_hash(tu["tu_id"], tu["language"]),
            "kind": "technological_university",
            "stage": "tertiary",
            "sector": "ie_tu",
            "source_url": tu["home_url"],
            "extracted_at": datetime.now(UTC).isoformat(),
            "baml_extraction_status": "registry",
        }

    # If the cache has richer (BAML-extracted) rows, layer them on top.
    if TU_CACHE_DIR.exists():
        for json_file in sorted(TU_CACHE_DIR.glob("**/*.json")):
            try:
                import json as _json

                rows = _json.loads(json_file.read_text())
                if isinstance(rows, dict):
                    rows = [rows]
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    row.setdefault("kind", "technological_university")
                    row.setdefault("stage", "tertiary")
                    row.setdefault("sector", "ie_tu")
                    row.setdefault("baml_extraction_status", "baml")
                    row.setdefault("extracted_at", datetime.now(UTC).isoformat())
                    yield row
            except (OSError, ValueError) as e:
                logger.warning(
                    "tu_cache_read_failed",
                    path=str(json_file),
                    error=str(e),
                )


@dlt.resource(
    name="tertiary_tu_campuses",
    write_disposition="merge",
    primary_key=["tu_id", "campus_slug"],
)
def tertiary_tu_campuses() -> Iterator[dict[str, Any]]:
    """One row per (tu_id, campus_slug) — the cross-product of the 5 TUs
    × their campuses.
    """
    for tu in TU_INSTITUTIONS:
        for campus_slug in tu["campus_slugs"]:
            yield {
                "tu_id": tu["tu_id"],
                "tu_name": tu["tu_name"],
                "campus_slug": campus_slug,
                "row_hash": _row_hash(tu["tu_id"], campus_slug),
                "language": tu["language"],
                "stage": "tertiary",
                "kind": "tu_campus",
                "sector": "ie_tu",
                "source_url": (
                    f"{tu['home_url'].rstrip('/')}/"
                    f"{campus_slug.replace('_', '-')}"
                ),
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="ireland_tertiary_tus")
def ireland_tertiary_tus_source(
    base_path: str | Path = TU_CACHE_DIR,
) -> Iterator[Any]:
    """Ireland Tertiary (5 Technological Universities) DLT source.

    Args:
        base_path: Local cache root (default
            `/stedding/ingest_queue/university/tus/`).
    """
    yield tertiary_tus()
    yield tertiary_tu_campuses()


def create_ireland_tertiary_tus_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "ireland_tertiary_tus",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="ireland_tertiary_tus_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "TU_CACHE_DIR",
    "TU_INSTITUTIONS",
    "create_ireland_tertiary_tus_pipeline",
    "ireland_tertiary_tus_source",
    "tertiary_tu_campuses",
    "tertiary_tus",
]