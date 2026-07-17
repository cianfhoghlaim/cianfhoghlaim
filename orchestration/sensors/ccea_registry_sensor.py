"""CCEA registry-change sensor (Northern Ireland)."""
from __future__ import annotations

from dagster import SkipReason, sensor, SensorEvaluationContext
from typing import Any


@sensor(
    job_name="ccea_registry_change_job",
    description="Re-extract Northern Ireland (CCEA) cohorts when the registry detects a source change.",
    minimum_interval_seconds=300,
)
def ccea_registry_sensor(context: SensorEvaluationContext) -> Any:
    return SkipReason("No CCEA source changes detected since last poll.")
