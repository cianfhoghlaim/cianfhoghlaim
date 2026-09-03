"""NCCA registry-change sensor (Ireland) — BIEP v3 P0 critical-path fix.

Per the 2026-08-06-biep-v3-critical-path-fixes-v1 change.
"""
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
    job_name="ncca_registry_change_job",
    description="Re-extract Ireland (NCCA + SEC) cohorts when the registry detects a source change.",
    minimum_interval_seconds=300,
)
def ncca_registry_sensor(context: SensorEvaluationContext) -> Any:
    """Poll the registry for NCCA-driven changes; emit one RunRequest per change."""
    cursor_data: dict[str, Any] = {}
    if context.cursor:
        try:
            cursor_data = json.loads(context.cursor)
        except Exception:
            cursor_data = {}

    cursor_last_seen = cursor_data.get("last_seen", "1970-01-01T00:00:00+00:00")

    try:
        from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction
        rows = query_by_jurisdiction("ireland")
    except Exception as e:
        return SkipReason(f"NCCA registry unavailable: {e}")

    new_runs: list[RunRequest] = []
    for row in rows:
        last_verified = row.last_verified or "1970-01-01T00:00:00+00:00"
        if last_verified > cursor_last_seen:
            new_runs.append(RunRequest(
                run_key=f"ncca_{row.subject_slug}_{last_verified}",
                tags={
                    "jurisdiction": "ireland",
                    "subject": row.subject_slug,
                    "source": "ncca",
                },
            ))

    if new_runs:
        from datetime import UTC, datetime
        latest = max(
            (r.last_verified or "1970-01-01T00:00:00+00:00" for r in rows),
            default=cursor_last_seen,
        )
        context.update_cursor(json.dumps({"last_seen": latest}))
        return new_runs

    return SkipReason("No NCCA source changes detected since last poll.")
