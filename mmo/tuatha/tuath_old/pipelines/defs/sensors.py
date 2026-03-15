"""
Sensor definitions for crypto data pipeline.

Defines sensors that monitor for conditions and trigger runs.
"""

from datetime import datetime, timedelta

from dagster import (
    Definitions,
    RunRequest,
    sensor,
    SkipReason,
)


def make_api_sensor(asset_key: str, interval_seconds: int = 3600):
    """
    Factory for API update sensors.

    Args:
        asset_key: Asset to monitor
        interval_seconds: Check interval

    Returns:
        Sensor definition
    """

    @sensor(
        name=f"{asset_key}_update_sensor",
        minimum_interval_seconds=interval_seconds,
    )
    def api_update_sensor(context):
        # Check if enough time has passed since last run
        last_run = context.cursor or "1970-01-01T00:00:00"
        last_dt = datetime.fromisoformat(last_run)

        if datetime.utcnow() - last_dt < timedelta(seconds=interval_seconds):
            return SkipReason(f"Not enough time since last run ({last_run})")

        # Trigger run
        context.update_cursor(datetime.utcnow().isoformat())
        return RunRequest(
            run_key=f"{asset_key}_{datetime.utcnow().isoformat()}",
            tags={"triggered_by": "sensor"},
        )

    return api_update_sensor


# Create sensors for API sources
coingecko_sensor = make_api_sensor("coingecko_assets", interval_seconds=3600)
defillama_sensor = make_api_sensor("defillama_assets", interval_seconds=21600)


# Export definitions for load_from_defs_folder
defs = Definitions(
    sensors=[
        coingecko_sensor,
        defillama_sensor,
    ],
)
