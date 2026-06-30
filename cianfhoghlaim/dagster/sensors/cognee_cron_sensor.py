"""
Cognee + FalkorDB cron sensor.

Daily cron that fires the 4 leabharlann cognify + cross-archive assets.
Runs at 02:00 UTC every day by default (Cognee is expensive, so we
batch it overnight).

Reference: openspec/changes/leabharlann-cognify-and-cross-archive-edges/
"""

import os
from datetime import datetime, timezone
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# Cron expression: every day at 02:00 UTC.
DEFAULT_CRON = "0 2 * * *"
DEFAULT_TIMEZONE = "UTC"


def _cognify_assets() -> list[Any]:
    """Lazy import to avoid loading the cognify assets at sensor-import time."""
    from cianfhoghlaim.dagster.assets.leabharlann_cognify_assets import (
        LEABHARLANN_COGNIFY_ASSETS,
    )

    return LEABHARLANN_COGNIFY_ASSETS


def evaluate_cognee_cron(
    context: dg.SensorEvaluationContext,
) -> dg.SensorResult:
    """Sensor callback that fires the 4 cognify + cross-archive assets on the cron tick."""
    now = datetime.now(timezone.utc)
    logger.info("cognee_cron_sensor_evaluating", now=now.isoformat())

    run_requests = []
    for asset_def in _cognify_assets():
        run_requests.append(
            dg.RunRequest(
                run_key=f"cognee-cron-{now.strftime('%Y%m%d')}-{asset_def.key.to_user_string()}",
                asset_selection=[asset_def.key],
            )
        )

    cursor = (context.cursor or "0")
    try:
        cursor_int = int(cursor)
    except (TypeError, ValueError):
        cursor_int = 0
    next_cursor = str(cursor_int + 1)

    return dg.SensorResult(
        run_requests=run_requests,
        cursor=next_cursor,
    )


# Sensor instance for the dagster_defs.sensors.__init__.
cognee_cron_sensor = dg.SensorDefinition(
    name="cognee_cron_sensor",
    evaluation_fn=evaluate_cognee_cron,
    minimum_interval_seconds=24 * 60 * 60,  # 1 day
    description=(
        "Daily cron sensor that fires the 4 leabharlann Cognee + FalkorDB "
        "cross-archive assets (3 cognify + 1 cross-archive edges). Runs at "
        "02:00 UTC every day. Cognee is expensive, so we batch it overnight."
    ),
    default_status=dg.DefaultSensorStatus.STOPPED,
)


__all__ = ["cognee_cron_sensor", "evaluate_cognee_cron"]
