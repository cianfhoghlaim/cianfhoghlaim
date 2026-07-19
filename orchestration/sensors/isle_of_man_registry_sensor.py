"""Isle of Man registry-change sensor — BIEP v3 P1 hardening."""
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
    job_name="isle_of_man_registry_change_job",
    description="Re-extract Isle of Man cohorts when the registry detects a source change.",
    minimum_interval_seconds=300,
)
def isle_of_man_registry_sensor(context: SensorEvaluationContext) -> Any:
    cursor_data: dict[str, Any] = {}
    if context.cursor:
        try:
            cursor_data = json.loads(context.cursor)
        except Exception:
            cursor_data = {}
    cursor_last_seen = cursor_data.get("last_seen", "1970-01-01T00:00:00+00:00")

    try:
        from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction
        rows = query_by_jurisdiction("isle_of_man")
    except Exception as e:
        return SkipReason(f"IoM registry unavailable: {e}")

    new_runs = []
    for row in rows:
        last_verified = row.last_verified or "1970-01-01T00:00:00+00:00"
        if last_verified > cursor_last_seen:
            new_runs.append(RunRequest(
                run_key=f"iom_{row.subject_slug}_{last_verified}",
                tags={"jurisdiction": "isle_of_man", "subject": row.subject_slug, "source": "iom"},
            ))

    if new_runs:
        latest = max(
            (r.last_verified or "1970-01-01T00:00:00+00:00" for r in rows),
            default=cursor_last_seen,
        )
        context.update_cursor(json.dumps({"last_seen": latest}))
        return new_runs

    return SkipReason("No IoM source changes detected since last poll.")
