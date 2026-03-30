"""
Schedule definitions for crypto data pipeline.

Defines cron-based schedules for automated job execution.
"""

from dagster import (
    DefaultScheduleStatus,
    Definitions,
    ScheduleDefinition,
)

from crypteolas.defs.jobs import api_ingestion_job, document_job


# Hourly API updates
hourly_api_schedule = ScheduleDefinition(
    job=api_ingestion_job,
    cron_schedule="0 * * * *",  # Every hour
    default_status=DefaultScheduleStatus.STOPPED,
    description="Hourly API data refresh",
)

# Weekly documentation refresh
weekly_docs_schedule = ScheduleDefinition(
    job=document_job,
    cron_schedule="0 3 * * 0",  # 3 AM Sunday
    default_status=DefaultScheduleStatus.STOPPED,
    description="Weekly documentation refresh",
)


# Export definitions for load_from_defs_folder
defs = Definitions(
    schedules=[
        hourly_api_schedule,
        weekly_docs_schedule,
    ],
)
