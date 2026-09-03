"""sync_schedules.py — the cron that materialises the sync_health asset.

Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change
(see openspec/changes/2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1/specs/knowledge-sync-loop/spec.md)
+ the 2026-07-30-drift-remediation-everything-bagel-v1 change (which
restored the deleted sync_health + dagster_sync_health jobs after commit
91b85c1c1 accidentally truncated them).

Attaches the `0 */4 * * *` cron that the `sync_health` asset docstring in
`orchestration/defs/sync_assets.py:64` already promises. Without this
schedule, the asset is only materialised by the `sync_report_sensor`
(which fires on every new `stedding/sync-reports/all-*.md` file) —
that's reactive-only. The cron adds the proactive 4-hourly check.
"""
from __future__ import annotations

from dagster import RunRequest, schedule

from orchestration.defs.sync_assets import (
    sync_health_job,
    dagster_sync_health_job,
    baml_sync_health_job,
)


@schedule(
    cron_schedule="0 */4 * * *",
    job=sync_health_job,
    execution_timezone="UTC",
    description=(
        "Materialises the sync_health asset every 4 hours. Emits "
        "paths_sync_time, ccc_chunk_count, cognee_cluster_count, "
        "skill_pass_rate, mcp_server_count_healthy, dagster_asset_count "
        "metadata each tick. Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 "
        "change (the `knowledge-sync-loop` spec's Daily sync_health cron "
        "requirement)."
    ),
)
def sync_health_every_4h(context) -> RunRequest:
    """Cron entry-point that triggers the sync_health job every 4 hours."""
    return RunRequest(run_key=f"sync_health_cron_{context.scheduled_execution_time.isoformat()}")


@schedule(
    cron_schedule="15 */4 * * *",  # offset by 15 min from sync_health
    job=dagster_sync_health_job,
    execution_timezone="UTC",
    description=(
        "Materialises the dagster_sync_health asset every 4 hours "
        "(offset by 15 min from sync_health so the all-report is "
        "available by the time this asset reads it). Layer 6 of the "
        "knowledge-sync-loop."
    ),
)
def dagster_sync_health_every_4h(context) -> RunRequest:
    """Cron entry-point that triggers the dagster_sync_health job."""
    return RunRequest(run_key=f"dagster_sync_health_cron_{context.scheduled_execution_time.isoformat()}")


@schedule(
    cron_schedule="30 */4 * * *",  # offset by 30 min from sync_health
    job=baml_sync_health_job,
    execution_timezone="UTC",
    description=(
        "Materialises the baml_sync_health asset every 4 hours "
        "(offset by 30 min from sync_health + 15 min from dagster_sync_health "
        "so the all-report is available by the time this asset reads it). "
        "Layer 7 of the knowledge-sync-loop (per the 2026-08-15-baml-sync-loop-v1 change)."
    ),
)
def baml_sync_health_every_4h(context) -> RunRequest:
    """Cron entry-point that triggers the baml_sync_health job."""
    return RunRequest(run_key=f"baml_sync_health_cron_{context.scheduled_execution_time.isoformat()}")


# Explicit schedule registry so `dagster dev` + `dagster-daemon` can
# discover all 3 crons without scanning `automation/`.
sync_schedules = [
    sync_health_every_4h,
    dagster_sync_health_every_4h,
    baml_sync_health_every_4h,
]


__all__ = [
    "sync_schedules",
    "sync_health_every_4h",
    "dagster_sync_health_every_4h",
    "baml_sync_health_every_4h",
]
