"""
Ireland CAO (Central Applications Office) DLT source — Tertiary 18+ stage.

Covers **CAO** — the Central Applications Office for undergraduate
Higher Education in the Republic of Ireland. CAO processes
~80,000 applications/year for ~1,400 courses across the 8
universities + 5 TUs + Colleges of Education + a small number of
private colleges.

CAO's role:
  - Round 1 (early August) — applicants receive offers
  - Round 2 (late August) — vacant places reallocated
  - Change-of-mind window — applications can be re-ordered

This source indexes the CAO **course catalog** (course code, HEI
mapping, NFQ level, points required for recent years) for downstream
joining with the 8 universities (`universities.py`) + 5 TUs (`tus.py`)
+ QQI awards (`qqi_awards.py`).

Honors `USE_LOCAL_SCRAPES=true` (default) to read from
`/stedding/ingest_queue/university/cao/`; live scraping is Phase 2
(JS-heavy CAO dropdowns — Skyvern/Stagehand preferred over plain HTTP).

Source URLs:
  - https://www.cao.ie
  - https://www.cao.ie/index.php?page=points
  - https://www.cao.ie/index.php?page=courses

Datasets produced (2 resources):
  tertiary_cao_courses       — one row per (cao_code, year)
  tertiary_cao_application_rounds — one row per (round_id, year)

BAML extraction (per `baml/education/university/university_extraction.baml`):
  b.ExtractCAOChoice(text, cao_code) -> CAOChoice
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

CAO_CACHE_DIR = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "university" / "cao"

# The 4 canonical CAO application rounds (per year).
# `round_date` is the ISO-8601 of the offer date; the dates shift year
# to year, so `round_id` is the canonical merge key (e.g. "R1_2025").
CAO_ROUNDS: tuple[dict[str, Any], ...] = (
    {
        "round_id": "R1",
        "round_label": "Round 1 Offers",
        "typical_window": "early August",
        "round_kind": "main_offer",
    },
    {
        "round_id": "R2",
        "round_label": "Round 2 Offers",
        "typical_window": "late August",
        "round_kind": "vacant_places",
    },
    {
        "round_id": "R3",
        "round_label": "Round 3 Offers",
        "typical_window": "early September",
        "round_kind": "vacant_places",
    },
    {
        "round_id": "R4",
        "round_label": "Round 4 Offers (final)",
        "typical_window": "mid September",
        "round_kind": "vacant_places",
    },
)
"""The 4 CAO application rounds. R1 is the main round (early August);
R2-R4 are vacant-places reallocation rounds."""


def _row_hash(*parts: str) -> str:
    """Deterministic SHA-256 for DLT merge keys (uniform across resources)."""
    sha = hashlib.sha256()
    sha.update("|".join(parts).encode("utf-8"))
    return sha.hexdigest()


@dlt.resource(
    name="tertiary_cao_courses",
    write_disposition="merge",
    primary_key=["cao_code", "year"],
)
def tertiary_cao_courses() -> Iterator[dict[str, Any]]:
    """One row per (cao_code, year) — the CAO course catalog.

    Phase 1 emits no rows from the registry (the live CAO catalog has
    ~1,400 entries; deferring to Phase 2 with BAML extraction). When
    the cache has BAML-extracted rows, layer them on top.
    """
    if CAO_CACHE_DIR.exists():
        courses = CAO_CACHE_DIR / "cao_courses"
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
                        row.setdefault("kind", "cao_course")
                        row.setdefault("stage", "tertiary")
                        row.setdefault("sector", "ie_cao")
                        row.setdefault("baml_extraction_status", "baml")
                        row.setdefault("extracted_at", datetime.now(UTC).isoformat())
                        yield row
                except (OSError, ValueError) as e:
                    logger.warning(
                        "cao_cache_read_failed",
                        path=str(json_file),
                        error=str(e),
                    )

    # Also yield any BAML-extracted `cao_choices.json` shards.
    if CAO_CACHE_DIR.exists():
        choices = CAO_CACHE_DIR / "cao_choices"
        if choices.exists():
            for json_file in sorted(choices.glob("**/*.json")):
                try:
                    import json as _json

                    rows = _json.loads(json_file.read_text())
                    if isinstance(rows, dict):
                        rows = [rows]
                    for row in rows:
                        if not isinstance(row, dict):
                            continue
                        # Normalize `cao_code` to primary key
                        if "cao_code" not in row and "course_code" in row:
                            row["cao_code"] = row["course_code"]
                        row.setdefault("year", datetime.now(UTC).year)
                        row.setdefault("kind", "cao_course")
                        row.setdefault("stage", "tertiary")
                        row.setdefault("sector", "ie_cao")
                        row.setdefault("baml_extraction_status", "baml")
                        row.setdefault("extracted_at", datetime.now(UTC).isoformat())
                        yield row
                except (OSError, ValueError) as e:
                    logger.warning(
                        "cao_choices_read_failed",
                        path=str(json_file),
                        error=str(e),
                    )


@dlt.resource(
    name="tertiary_cao_application_rounds",
    write_disposition="merge",
    primary_key=["round_id", "year"],
)
def tertiary_cao_application_rounds() -> Iterator[dict[str, Any]]:
    """One row per (round_id, year) — the CAO application rounds.

    The 4 rounds are static; we yield one row per (round_id, year)
    for the past 3 years + the current year to enable year-over-year
    timeline analytics.
    """
    current_year = datetime.now(UTC).year
    for year in (current_year - 2, current_year - 1, current_year):
        for round_info in CAO_ROUNDS:
            yield {
                "round_id": round_info["round_id"],
                "year": year,
                "round_label": round_info["round_label"],
                "typical_window": round_info["typical_window"],
                "round_kind": round_info["round_kind"],
                "row_hash": _row_hash(round_info["round_id"], str(year)),
                "kind": "cao_application_round",
                "stage": "tertiary",
                "sector": "ie_cao",
                "language": "en",
                "source_url": (
                    f"https://www.cao.ie/index.php?page=points"
                    f"&round={round_info['round_id'].lower()}&year={year}"
                ),
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="ireland_tertiary_cao")
def ireland_tertiary_cao_source(
    base_path: str | Path = CAO_CACHE_DIR,
) -> Iterator[Any]:
    """Ireland Tertiary (CAO) DLT source.

    Args:
        base_path: Local cache root (default
            `/stedding/ingest_queue/university/cao/`).
    """
    yield tertiary_cao_courses()
    yield tertiary_cao_application_rounds()


def create_ireland_tertiary_cao_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "ireland_tertiary_cao",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="ireland_tertiary_cao_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "CAO_CACHE_DIR",
    "CAO_ROUNDS",
    "create_ireland_tertiary_cao_pipeline",
    "ireland_tertiary_cao_source",
    "tertiary_cao_application_rounds",
    "tertiary_cao_courses",
]