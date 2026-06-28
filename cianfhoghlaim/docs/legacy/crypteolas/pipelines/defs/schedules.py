"""
Schedule definitions for indexing and knowledge graph pipelines.
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


# Daily vector index refresh
daily_vector_index = ScheduleDefinition(
    job_name="vector_index_only",
    cron_schedule="0 5 * * *",  # 5 AM daily (after API ingestion)
    execution_timezone="UTC",
    name="daily_vector_index",
)

# Weekly full knowledge graph rebuild
weekly_knowledge_graph = ScheduleDefinition(
    job_name="complete_indexing_pipeline",
    cron_schedule="0 6 * * 0",  # 6 AM Sunday
    execution_timezone="UTC",
    name="weekly_knowledge_graph",
)


# List of all schedules
indexing_schedules = [
    daily_vector_index,
    weekly_knowledge_graph,
]
