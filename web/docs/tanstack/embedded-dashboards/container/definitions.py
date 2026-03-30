"""Example Dagster definitions for the embedded dashboards demo."""

from dagster import (
    asset,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    AssetSelection,
)
import pandas as pd
from datetime import datetime


@asset(description="Sample data for demonstration")
def sample_data() -> pd.DataFrame:
    """Generate sample data for the dashboard."""
    return pd.DataFrame({
        "id": range(1, 101),
        "value": [i * 2 for i in range(1, 101)],
        "category": ["A", "B", "C", "D"] * 25,
        "timestamp": [datetime.now() for _ in range(100)],
    })


@asset(description="Aggregated statistics from sample data")
def aggregated_stats(sample_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate statistics from sample data."""
    return sample_data.groupby("category").agg({
        "value": ["mean", "sum", "count"],
        "id": "count"
    }).reset_index()


@asset(description="Time series analysis")
def time_series_analysis(sample_data: pd.DataFrame) -> pd.DataFrame:
    """Perform time series analysis."""
    return sample_data.assign(
        running_total=sample_data["value"].cumsum(),
        moving_avg=sample_data["value"].rolling(window=5, min_periods=1).mean()
    )


# Define a job that materializes all assets
analytics_job = define_asset_job(
    name="analytics_job",
    selection=AssetSelection.all(),
    description="Materialize all analytics assets"
)

# Define a schedule for the job
analytics_schedule = ScheduleDefinition(
    job=analytics_job,
    cron_schedule="0 * * * *",  # Every hour
    description="Hourly analytics refresh"
)


defs = Definitions(
    assets=[sample_data, aggregated_stats, time_series_analysis],
    jobs=[analytics_job],
    schedules=[analytics_schedule],
)
