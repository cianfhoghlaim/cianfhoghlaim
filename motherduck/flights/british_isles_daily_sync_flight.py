"""MotherDuck Flight: british_isles_daily_sync_flight.

Daily BAML backfill for the British Isles parity layer
(Scotland / Wales / England / Northern Ireland + 3 Crown Dependencies).
"""
from __future__ import annotations

from datetime import UTC, datetime

from motherduck.flights import run_flight


FLIGHT_NAME = "british_isles_daily_sync_flight"
FLIGHT_CRON = "0 5 * * *"
FLIGHT_TIMEZONE = "UTC"


def build_british_isles_daily_sync_flight() -> None:
    """Daily BAML backfill for the BIEP parity layer."""
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
    "build_british_isles_daily_sync_flight",
]
