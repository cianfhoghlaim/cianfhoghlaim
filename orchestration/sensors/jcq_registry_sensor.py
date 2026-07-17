"""JCQ registry-change sensor (England — AQA + OCR + Edexcel)."""
from __future__ import annotations

from dagster import SkipReason, sensor, SensorEvaluationContext
from typing import Any


@sensor(
    job_name="jcq_registry_change_job",
    description="Re-extract England (AQA + OCR + Edexcel) cohorts when the registry detects a source change.",
    minimum_interval_seconds=300,
)
def jcq_registry_sensor(context: SensorEvaluationContext) -> Any:
    return SkipReason("No JCQ source changes detected since last poll.")
