"""
Dagster Schedules for Tuath.

Defines automated scheduling for Celtic education data pipelines.
"""

from dagster import (
    DefaultScheduleStatus,
    RunRequest,
    ScheduleDefinition,
    ScheduleEvaluationContext,
    schedule,
)


@schedule(
    cron_schedule="0 6 * * *",
    job_name="curriculum_sync_job",
    default_status=DefaultScheduleStatus.RUNNING,
    description="Sync Celtic curriculum data daily at 6 AM UTC",
)
def daily_curriculum_schedule(context: ScheduleEvaluationContext):
    """Run curriculum sync job daily.

    Fetches updates from:
    - NCCA (Ireland)
    - WJEC (Wales)
    - SQA (Scotland)
    - Other Celtic education bodies
    """
    return RunRequest(
        run_key=f"curriculum_sync_{context.scheduled_execution_time.date().isoformat()}",
        tags={
            "schedule": "daily_curriculum",
            "pipeline": "tuath",
        },
    )


@schedule(
    cron_schedule="0 0 * * 0",
    job_name="mythology_sync_job",
    default_status=DefaultScheduleStatus.RUNNING,
    description="Sync mythology data weekly on Sunday midnight UTC",
)
def weekly_mythology_schedule(context: ScheduleEvaluationContext):
    """Run mythology sync job weekly.

    Mythology content changes infrequently, so weekly sync is sufficient.
    Includes characters, stories, and locations from all Celtic traditions.
    """
    return RunRequest(
        run_key=f"mythology_sync_{context.scheduled_execution_time.date().isoformat()}",
        tags={
            "schedule": "weekly_mythology",
            "pipeline": "tuath",
        },
    )


@schedule(
    cron_schedule="0 8 * * *",
    job_name="embedding_pipeline_job",
    default_status=DefaultScheduleStatus.RUNNING,
    description="Generate embeddings daily at 8 AM UTC (after data refresh)",
)
def daily_embedding_schedule(context: ScheduleEvaluationContext):
    """Run embedding pipeline daily after data is refreshed.

    Uses BGE-M3 for multilingual embeddings supporting:
    - Irish, Welsh, Scottish Gaelic
    - English translations and summaries
    """
    return RunRequest(
        run_key=f"embeddings_{context.scheduled_execution_time.date().isoformat()}",
        tags={
            "schedule": "daily_embeddings",
            "pipeline": "tuath",
            "model": "BAAI/bge-m3",
        },
    )


@schedule(
    cron_schedule="0 4 * * 1",
    job_name="exam_papers_job",
    default_status=DefaultScheduleStatus.STOPPED,
    description="Fetch new exam papers weekly on Monday 4 AM UTC",
)
def weekly_exam_papers_schedule(context: ScheduleEvaluationContext):
    """Fetch historical exam papers from national bodies.

    Only runs during exam season (May-September) by default.
    Can be manually triggered for historical data backfill.
    """
    import datetime

    # Only run during exam season
    month = context.scheduled_execution_time.month
    if month not in [5, 6, 7, 8, 9]:
        context.instance.report_schedule_skip(
            schedule_name="weekly_exam_papers_schedule",
            reason="Outside exam season (May-September)",
        )
        return None

    return RunRequest(
        run_key=f"exam_papers_{context.scheduled_execution_time.date().isoformat()}",
        tags={
            "schedule": "weekly_exam_papers",
            "pipeline": "tuath",
        },
    )


# Static schedule definitions for jobs that don't need dynamic logic
full_pipeline_schedule = ScheduleDefinition(
    job_name="full_pipeline_job",
    cron_schedule="0 2 * * 0",
    default_status=DefaultScheduleStatus.STOPPED,
    description="Run full Tuath pipeline weekly (Sunday 2 AM UTC)",
)


index_rebuild_schedule = ScheduleDefinition(
    job_name="rebuild_indexes_job",
    cron_schedule="0 3 * * 0",
    default_status=DefaultScheduleStatus.STOPPED,
    description="Rebuild vector indexes weekly (Sunday 3 AM UTC)",
)


@schedule(
    cron_schedule="0 */6 * * *",
    job_name="game_content_refresh_job",
    default_status=DefaultScheduleStatus.RUNNING,
    description="Refresh game content cache every 6 hours",
)
def game_content_schedule(context: ScheduleEvaluationContext):
    """Refresh game content caches.

    Updates:
    - NPC dialogue caches
    - Quest availability
    - Location descriptions
    - Player leaderboards
    """
    return RunRequest(
        run_key=f"game_content_{context.scheduled_execution_time.isoformat()}",
        tags={
            "schedule": "game_content_refresh",
            "pipeline": "tuath",
        },
    )
