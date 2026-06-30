"""CCC Freshness Sensor — incremental re-index trigger.

Added in the `2026-06-30-agent-platform-cluster-hermes-cocoindex` change.

Polls `.cocoindex_code/cocoindex.db` mtime every 30 minutes. When
the mtime is > 24 hours old on the `main` branch (or > 7 days on
a release branch), the sensor fires a `RunRequest` to re-run the
3 CocoIndex v1 App materialisations:
- `codebase_index`
- `agent_registry_index`
- `agents_md_index`
"""
from __future__ import annotations

import os
import pathlib
import time
from datetime import datetime, timedelta, timezone

import structlog
from dagster import RunRequest, SensorEvaluationContext, SensorResult, sensor

logger = structlog.get_logger(__name__)


COCOINDEX_DB_PATH = pathlib.Path(
    os.getenv("COCOINDEX_DB_PATH", ".cocoindex_code/cocoindex.db")
)

FRESHNESS_THRESHOLDS = {
    "main": timedelta(hours=24),
    "release": timedelta(days=7),
}
DEFAULT_THRESHOLD = FRESHNESS_THRESHOLDS["main"]


@sensor(
    job_name="ccc_freshness_reindex_job",
    minimum_interval_seconds=1800,  # 30 min
    description="Re-runs codebase_index, agent_registry_index, agents_md_index when the CocoIndex DB is stale.",
)
def ccc_freshness_sensor(context: SensorEvaluationContext) -> SensorResult:
    """Poll .cocoindex_code/cocoindex.db mtime; trigger re-index if stale."""
    if not COCOINDEX_DB_PATH.exists():
        context.log.info(
            f"[ccc_freshness] index file does not exist at {COCOINDEX_DB_PATH}; "
            f"skipping (the index is created by `mise run ccc:init && mise run ccc:index`)"
        )
        return SensorResult(skip_message="no index file present")

    mtime = datetime.fromtimestamp(COCOINDEX_DB_PATH.stat().st_mtime, tz=timezone.utc)
    age = datetime.now(tz=timezone.utc) - mtime
    branch = os.getenv("DAGSTER_CURRENT_BRANCH", "main")
    threshold = FRESHNESS_THRESHOLDS.get(branch, DEFAULT_THRESHOLD)

    age_hours = age.total_seconds() / 3600
    threshold_hours = threshold.total_seconds() / 3600
    context.log.info(
        f"[ccc_freshness] last update: {age_hours:.1f}h ago; "
        f"threshold: {threshold_hours:.1f}h on {branch}"
    )

    if age < threshold:
        return SensorResult(
            skip_message=f"index is fresh ({age_hours:.1f}h < {threshold_hours:.1f}h)"
        )

    context.log.info(
        f"[ccc_freshness] index is stale ({age_hours:.1f}h > {threshold_hours:.1f}h threshold); firing re-index"
    )
    run_requests = [
        RunRequest(
            run_key=f"ccc-freshness-{job_name}-{int(time.time())}",
            job_name=job_name,
        )
        for job_name in (
            "codebase_index_job",
            "agent_registry_index_job",
            "agents_md_index_job",
        )
    ]
    return SensorResult(run_requests=run_requests)
