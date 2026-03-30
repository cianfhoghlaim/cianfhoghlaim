"""Schedule definitions for the ingestion pipeline.

Schedules define when jobs should run automatically.
Configuration is loaded from config/dagster.yaml.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from dagster import ScheduleDefinition


def load_dagster_config() -> dict:
    """Load Dagster configuration from dagster.yaml."""
    config_path = Path(__file__).parent.parent / "config" / "dagster.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


def build_schedules() -> list[ScheduleDefinition]:
    """Build schedule definitions from configuration.

    Returns:
        List of schedule definitions
    """
    config = load_dagster_config()
    schedule_config = config.get("schedules", {})

    schedules = []

    # GitHub API daily schedule
    api_config = schedule_config.get("api_daily", {})
    if api_config.get("enabled", True):
        schedules.append(
            ScheduleDefinition(
                job_name="github_api_job",
                cron_schedule=api_config.get("cron", "0 2 * * *"),
                name="github_api_daily",
                execution_timezone="UTC",
            )
        )

    return schedules


# Build schedules at module load time
ingestion_schedules = build_schedules()
