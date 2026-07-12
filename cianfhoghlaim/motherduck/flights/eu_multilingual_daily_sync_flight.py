"""MotherDuck Flight: eu_multilingual_daily_sync_flight.

Daily BAML backfill for the EU multilingual alignment pipeline.
Added by 2026-07-15-eu-multilingual-irish-english-v1.
"""
from __future__ import annotations

from datetime import UTC, datetime

from motherduck.flights import run_flight


FLIGHT_NAME = "eu_multilingual_daily_sync_flight"
FLIGHT_CRON = "0 5 * * *"
FLIGHT_TIMEZONE = "UTC"


def build_eu_multilingual_daily_sync_flight() -> None:
    """Daily BAML backfill for the EU multilingual pipeline."""
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
    "build_eu_multilingual_daily_sync_flight",
]
