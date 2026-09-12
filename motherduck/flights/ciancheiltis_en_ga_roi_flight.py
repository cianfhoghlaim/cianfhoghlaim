"""MotherDuck Flight: ciancheiltis_en_ga_roi_flight.

Daily BAML backfill for the en-ga-roi (Republic of Ireland) phase of
the ciancheiltis umbrella. Runs the L1 ingestion + L2 BAML extraction
+ L3 CocoIndex mount for the 8 Phase 2 themes, then surfaces the
bilingual-pair coverage to the Phase 2 RAGAS gate (≥ 0.70 + ≥ 500
pairs seeded).

Phase 2 is the Republic of Ireland (en-ga) — the only ciancheiltis
jurisdiction that ALREADY ships rich bilingual content cached in
`stedding/` (2,388 EN + 2,010 GA cached pages from `ncca.ie` and
1,398 EN + 1,000 GA from `curriculumonline.ie`). The canonical
bilingual example is
`https://www.irishstatutebook.ie/eli/1937/act/0019/enacted/ga/html`
(Bunreacht na hÉireann / Constitution of Ireland 1937).

This Flight is the canonical entry-point for the
`ciancheiltis_en_ga_roi_bilingual_pairs` MotherDuck Dive and is
paired with the marimo notebook `notebooks/ciancheiltis_en_ga_roi.py`.
"""
from __future__ import annotations

from datetime import UTC, datetime

from motherduck.flights import run_flight


FLIGHT_NAME = "ciancheiltis_en_ga_roi_flight"
FLIGHT_CRON = "0 4 * * *"
FLIGHT_TIMEZONE = "UTC"
FLIGHT_TAGS = (
    "ciancheiltis",
    "en_ga_roi",
    "ireland",
    "bilingual",
    "phase_2",
    "daily_sync",
)


def build_ciancheiltis_en_ga_roi_flight() -> None:
    """Daily BAML backfill + RAGAS gate for the en-ga-roi (Republic) phase."""
    run_flight(
        name=FLIGHT_NAME,
        cron=FLIGHT_CRON,
        timezone=FLIGHT_TIMEZONE,
        schedule_kind="daily",
        started_at=datetime.now(UTC).isoformat(),
        tags=list(FLIGHT_TAGS),
    )


__all__ = [
    "FLIGHT_NAME",
    "FLIGHT_CRON",
    "FLIGHT_TIMEZONE",
    "FLIGHT_TAGS",
    "build_ciancheiltis_en_ga_roi_flight",
]