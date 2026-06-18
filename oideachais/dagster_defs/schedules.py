"""
Schedules for Celtic Education Platform.

Automated execution schedules for data pipelines.
All schedules are disabled by default - enable in Dagster UI as needed.

Schedule Types:
- Daily: Curriculum updates, enrichment
- Weekly: Full corpus updates, translations
- Monthly: Geospatial updates, statistics refresh

Usage:
    Schedules can be enabled/disabled in the Dagster UI.
    Use sensors for event-driven triggering instead of fixed schedules.
"""
from dagster import (
    AssetSelection,
    DefaultScheduleStatus,
    ScheduleDefinition,
    define_asset_job,
)

# ============================================================================
# Job Definitions for Schedules
# ============================================================================

# NOTE: ireland_refresh_job removed - asset was in deleted ie_education_assets.py
# Use unified_curriculum_pipeline from definitions.py instead

# UK education refresh (daily)
uk_refresh_job = define_asset_job(
    name="uk_refresh_job",
    selection=AssetSelection.key_prefixes(["uk"]),
    description="Daily refresh of UK education assets",
)

# Celtic corpus refresh (weekly)
# NOTE: Disabled - celtic assets have different partition definitions (county, language, dialect)
# Split into separate jobs per partition type if needed
# celtic_refresh_job = define_asset_job(
#     name="celtic_refresh_job",
#     selection=AssetSelection.key_prefixes(["celtic"]),
#     description="Weekly refresh of Celtic language corpus",
# )

# Enriched assets (daily)
enriched_refresh_job = define_asset_job(
    name="enriched_refresh_job",
    selection=AssetSelection.key_prefixes(["enriched"]),
    description="Daily enrichment pass",
)

# Search indexes (daily)
search_refresh_job = define_asset_job(
    name="search_refresh_job",
    selection=AssetSelection.key_prefixes(["search"]),
    description="Daily search index rebuild",
)


# ============================================================================
# Daily Schedules
# ============================================================================

# NOTE: ireland_daily_schedule removed - job referenced deleted asset
# Use unified_curriculum_pipeline with schedules in sensors/curriculum_freshness.py

uk_daily_schedule = ScheduleDefinition(
    name="uk_daily_schedule",
    job=uk_refresh_job,
    cron_schedule="0 7 * * *",  # 7 AM daily
    default_status=DefaultScheduleStatus.STOPPED,
    description="Daily refresh of UK education data at 7 AM",
)

enriched_daily_schedule = ScheduleDefinition(
    name="enriched_daily_schedule",
    job=enriched_refresh_job,
    cron_schedule="0 8 * * *",  # 8 AM daily (after source updates)
    default_status=DefaultScheduleStatus.STOPPED,
    description="Daily enrichment pass at 8 AM",
)

search_daily_schedule = ScheduleDefinition(
    name="search_daily_schedule",
    job=search_refresh_job,
    cron_schedule="0 9 * * *",  # 9 AM daily (after enrichment)
    default_status=DefaultScheduleStatus.STOPPED,
    description="Daily search index rebuild at 9 AM",
)


# ============================================================================
# Weekly Schedules
# ============================================================================

# NOTE: Disabled - celtic assets have different partition definitions
# celtic_weekly_schedule = ScheduleDefinition(
#     name="celtic_weekly_schedule",
#     job=celtic_refresh_job,
#     cron_schedule="0 2 * * 0",  # 2 AM Sunday
#     default_status=DefaultScheduleStatus.STOPPED,
#     description="Weekly Celtic corpus refresh on Sunday at 2 AM",
# )


# ============================================================================
# Custom Schedule with Partition Selection
# ============================================================================

# NOTE: ireland_weekday_schedule removed - job referenced deleted asset


# ============================================================================
# Export All Schedules
# ============================================================================

all_schedules = [
    uk_daily_schedule,
    enriched_daily_schedule,
    search_daily_schedule,
]


# ============================================================================
# Official Media — monthly refresh (1st of month, 05:00 Europe/Dublin)
# ============================================================================
# Phase 5 of the official-media-pipeline change. The official-media
# group refreshes monthly: the 4 intelligence agencies get crawled
# (sources.yaml), the 4-lookup resolver fans out (Wikipedia + Companies
# House / CRO + Mastodon + Bluesky), the embed + cognify assets re-run,
# and the HMGCC co-creation sentinel records the trailing 12-week
# project call count.
official_media_refresh_job = define_asset_job(
    name="official_media_refresh_job",
    selection=AssetSelection.groups("official_media"),
    description="Monthly refresh of the official-media pipeline (DLT extract + 4-lookup resolver + embed + cognify + HMGCC co-creation sentinel).",
)

official_media_monthly_schedule = ScheduleDefinition(
    name="official_media_monthly_schedule",
    job=official_media_refresh_job,
    cron_schedule="0 5 1 * *",  # 1st of month, 05:00 UTC
    default_status=DefaultScheduleStatus.STOPPED,
    execution_timezone="Europe/Dublin",
    description="Monthly refresh of the official-media pipeline.",
)

all_schedules.append(official_media_monthly_schedule)
