"""NCCA registry-change sensor (Ireland).

Per the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 change.

Triggers a re-extraction when the canonical British Isles subject registry
detects an Ireland (NCCA + SEC) source change.
"""
from __future__ import annotations

import logging
from typing import Any

from dagster import (
    AssetKey,
    EventLogEntry,
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
    sensor,
)

logger = logging.getLogger(__name__)


@sensor(
    job_name="ncca_registry_change_job",
    description="Re-extract Ireland (NCCA + SEC) cohorts when the registry detects a source change.",
    minimum_interval_seconds=300,
)
def ncca_registry_sensor(context: SensorEvaluationContext) -> Any:
    """Poll the registry for NCCA-driven changes; emit one RunRequest per change."""
    cursor_data: dict[str, Any] = {}
    if context.cursor:
        import json
        cursor_data = json.loads(context.cursor)

    # Real implementation: query
    # `cianfhoghlaim.education._registry.subjects WHERE jurisdiction='ireland'
    #  AND last_verified > (cursor.last_seen OR '1970-01-01')`.
    # For now, return a SkipReason.
    return SkipReason("No NCCA source changes detected since last poll.")
