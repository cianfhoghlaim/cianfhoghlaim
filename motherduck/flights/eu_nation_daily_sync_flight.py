"""MotherDuck Flight: eu_nation_daily_sync_flight.

Daily BAML backfill for the EU nations + Ukraine pipeline. Reads any
updated per-nation source rows and runs the canonical
``b.Extract{UKR,FRA,DEU,POL,ESP,ITA}{Education,Law,Medicine}Document``
extractor to refresh the typed DuckLake tables.
"""
from __future__ import annotations

from datetime import UTC, datetime

from motherduck.flights import run_flight


FLIGHT_NAME = "eu_nation_daily_sync_flight"
FLIGHT_CRON = "0 6 * * *"
FLIGHT_TIMEZONE = "UTC"


def build_eu_nation_daily_sync_flight() -> None:
    """Daily BAML backfill for the EU nations + Ukraine pipeline."""
    run_flight(
        name=FLIGHT_NAME,
        cron=FLIGHT_CRON,
        timezone=FLIGHT_TIMEZONE,
        schedule_kind="daily",
        started_at=datetime.now(UTC).isoformat(),
    )


__all__ = [
    "FLIGHT_CRON",
    "FLIGHT_NAME",
    "FLIGHT_TIMEZONE",
    "build_eu_nation_daily_sync_flight",
]
