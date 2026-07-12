"""MotherDuck Flight: canada_daily_sync_flight.

Daily BAML backfill for the Canada provincial + Quebec/Montreal
deep cluster pipeline.
"""
from __future__ import annotations

from datetime import UTC, datetime

from motherduck.flights import run_flight


FLIGHT_NAME = "canada_daily_sync_flight"
FLIGHT_CRON = "0 6 * * *"
FLIGHT_TIMEZONE = "UTC"


def build_canada_daily_sync_flight() -> None:
    """Daily BAML backfill for the Canada provincial pipeline."""
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
    "build_canada_daily_sync_flight",
]
