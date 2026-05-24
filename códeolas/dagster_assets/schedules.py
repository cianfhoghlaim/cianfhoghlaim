"""
Dagster schedules for Códeolas code analysis flow.

Schedules:
- hourly_code_indexing: Re-index code every hour
- daily_architecture_docs: Generate .arch.md daily
"""

from dagster import (
    ScheduleDefinition,
    DefaultScheduleStatus,
)


# =============================================================================
# Schedule Definitions
# =============================================================================

# Hourly code indexing schedule
# Runs at the start of every hour
hourly_code_indexing_schedule = ScheduleDefinition(
    name="hourly_code_indexing",
    job_name="codeolas_indexing_job",
    cron_schedule="0 * * * *",  # Every hour at :00
    default_status=DefaultScheduleStatus.RUNNING,
    description="Re-index repository code chunks every hour",
)

# Daily architecture documentation schedule
# Runs at 6 AM daily
daily_architecture_docs_schedule = ScheduleDefinition(
    name="daily_architecture_docs",
    job_name="codeolas_full_pipeline_job",
    cron_schedule="0 6 * * *",  # 6 AM daily
    default_status=DefaultScheduleStatus.RUNNING,
    description="Generate architecture documentation daily",
)

# Weekly full rebuild schedule
# Runs at 3 AM every Sunday for complete graph rebuild
weekly_full_rebuild_schedule = ScheduleDefinition(
    name="weekly_full_rebuild",
    job_name="codeolas_full_pipeline_job",
    cron_schedule="0 3 * * 0",  # 3 AM every Sunday
    default_status=DefaultScheduleStatus.RUNNING,
    description="Full rebuild of code index and graph weekly",
)


# Export all schedules
codeolas_schedules = [
    hourly_code_indexing_schedule,
    daily_architecture_docs_schedule,
    weekly_full_rebuild_schedule,
]
