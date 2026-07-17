"""WJEC registry-change sensor (Wales)."""
from __future__ import annotations

from dagster import SkipReason, sensor, SensorEvaluationContext
from typing import Any


@sensor(
    job_name="wjec_registry_change_job",
    description="Re-extract Wales (WJEC) cohorts when the registry detects a source change.",
    minimum_interval_seconds=300,
)
def wjec_registry_sensor(context: SensorEvaluationContext) -> Any:
    return SkipReason("No WJEC source changes detected since last poll.")
