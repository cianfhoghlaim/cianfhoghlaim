"""MotherDuck Flight: ciancheiltis_en_cy_flight.

Daily BAML backfill for the en-cy (Wales) phase of the ciancheiltis
umbrella. Runs the L1 ingestion + L2 BAML extraction + L3 CocoIndex
mount for the 8 Phase 1 themes, then surfaces the bilingual-pair
coverage to the Phase 1 RAGAS gate (≥ 0.70 + ≥ 500 pairs seeded).

This Flight is the canonical entry-point for the
`ciancheiltis_en_cy_bilingual_pairs` MotherDuck Dive and is paired
with the marimo notebook `notebooks/ciancheiltis_en_cy.py`.
"""
from __future__ import annotations

from datetime import UTC, datetime

from motherduck.flights import run_flight


FLIGHT_NAME = "ciancheiltis_en_cy_flight"
FLIGHT_CRON = "0 4 * * *"
FLIGHT_TIMEZONE = "UTC"
FLIGHT_TAGS = (
    "ciancheiltis",
    "en_cy",
    "wales",
    "bilingual",
    "phase_1",
    "daily_sync",
)


def build_ciancheiltis_en_cy_flight() -> None:
    """Daily BAML backfill + RAGAS gate for the en-cy (Wales) phase."""
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
    "build_ciancheiltis_en_cy_flight",
]
