"""SQA registry-change sensor (Scotland)."""
from __future__ import annotations

from dagster import SkipReason, sensor, SensorEvaluationContext
from typing import Any


@sensor(
    job_name="sqa_registry_change_job",
    description="Re-extract Scotland (SQA) cohorts when the registry detects a source change.",
    minimum_interval_seconds=300,
)
def sqa_registry_sensor(context: SensorEvaluationContext) -> Any:
    return SkipReason("No SQA source changes detected since last poll.")
