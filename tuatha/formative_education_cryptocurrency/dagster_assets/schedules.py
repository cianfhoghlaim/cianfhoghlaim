"""
Dagster Schedules for Crypteolas.

Defines automated scheduling for data pipelines.
"""

from dagster import (
    DefaultScheduleStatus,
    RunRequest,
    ScheduleDefinition,
    ScheduleEvaluationContext,
    schedule,
)


@schedule(
    cron_schedule="0 * * * *",
    job_name="github_sync_job",
    default_status=DefaultScheduleStatus.RUNNING,
    description="Sync GitHub data hourly",
)
def hourly_github_schedule(context: ScheduleEvaluationContext):
    """Run GitHub sync job every hour."""
    return RunRequest(
        run_key=f"github_sync_{context.scheduled_execution_time.isoformat()}",
        tags={"schedule": "hourly_github"},
    )


@schedule(
    cron_schedule="0 6 * * *",
    job_name="defi_metrics_job",
    default_status=DefaultScheduleStatus.RUNNING,
    description="Fetch DeFi metrics daily at 6 AM UTC",
)
def daily_defi_schedule(context: ScheduleEvaluationContext):
    """Run DeFi metrics job daily."""
    return RunRequest(
        run_key=f"defi_metrics_{context.scheduled_execution_time.date().isoformat()}",
        tags={"schedule": "daily_defi"},
    )


@schedule(
    cron_schedule="0 8 * * *",
    job_name="embedding_stats_job",
    default_status=DefaultScheduleStatus.RUNNING,
    description="Compute embedding stats daily at 8 AM UTC",
)
def daily_embedding_schedule(context: ScheduleEvaluationContext):
    """Run embedding stats job daily after data is refreshed."""
    return RunRequest(
        run_key=f"embeddings_{context.scheduled_execution_time.date().isoformat()}",
        tags={"schedule": "daily_embeddings"},
    )
