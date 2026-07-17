"""WJEC registry-change sensor (Wales) — BIEP v3 P0 critical-path fix."""
from __future__ import annotations

import json
import logging
from typing import Any

from dagster import (
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
    sensor,
)

logger = logging.getLogger(__name__)


@sensor(
    job_name="wjec_registry_change_job",
    description="Re-extract Wales (WJEC) cohorts when the registry detects a source change.",
    minimum_interval_seconds=300,
)
def wjec_registry_sensor(context: SensorEvaluationContext) -> Any:
    cursor_data: dict[str, Any] = {}
    if context.cursor:
        try:
            cursor_data = json.loads(context.cursor)
        except Exception:
            cursor_data = {}
    cursor_last_seen = cursor_data.get("last_seen", "1970-01-01T00:00:00+00:00")

    try:
        from dlt.british_isles._cross.registry_api import query_by_jurisdiction
        rows = query_by_jurisdiction("wales")
    except Exception as e:
        return SkipReason(f"WJEC registry unavailable: {e}")

    new_runs = []
    for row in rows:
        last_verified = row.last_verified or "1970-01-01T00:00:00+00:00"
        if last_verified > cursor_last_seen:
            new_runs.append(RunRequest(
                run_key=f"wjec_{row.subject_slug}_{last_verified}",
                tags={"jurisdiction": "wales", "subject": row.subject_slug, "source": "wjec"},
            ))

    if new_runs:
        latest = max(
            (r.last_verified or "1970-01-01T00:00:00+00:00" for r in rows),
            default=cursor_last_seen,
        )
        context.update_cursor(json.dumps({"last_seen": latest}))
        return new_runs

    return SkipReason("No WJEC source changes detected since last poll.")
