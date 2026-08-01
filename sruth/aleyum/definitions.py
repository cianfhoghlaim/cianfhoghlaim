"""Dagster Definitions for Aleyum Pipeline.

Main entry point for Dagster. Combines all assets, jobs,
schedules, and sensors.

Usage:
    # Start Dagster UI
    dagster dev -f definitions.py

    # Run a job
    dagster job execute -f definitions.py -j daily_ingestion_job

    # Materialize assets
    dagster asset materialize -f definitions.py --select spotify_ingestion
"""

import os

from dagster import (
    Definitions,
    EnvVar,
    load_assets_from_modules,
    load_assets_from_package_module,
)
from dagster_dlt import DagsterDltResource

# Import asset modules
from dagster_assets import dlt_assets, cocoindex_assets
from dagster_assets.schedules import (
    all_jobs,
    all_schedules,
    all_sensors,
)


# Load assets from modules
dlt_asset_defs = load_assets_from_modules([dlt_assets])
cocoindex_asset_defs = load_assets_from_modules([cocoindex_assets])

# Combine all assets
all_assets = [
    *dlt_asset_defs,
    *cocoindex_asset_defs,
]

# Resources
resources = {
    "dlt": DagsterDltResource(),
}

# Environment-based configuration
if os.environ.get("DAGSTER_ENV") == "production":
    # Production resources
    resources.update({
        # Add production-specific resources
    })

# Create definitions
defs = Definitions(
    assets=all_assets,
    jobs=all_jobs,
    schedules=all_schedules,
    sensors=all_sensors,
    resources=resources,
)


if __name__ == "__main__":
    # Quick test of definitions
    print("Assets:")
    for asset_def in all_assets:
        if hasattr(asset_def, "key"):
            print(f"  - {asset_def.key}")

    print("\nJobs:")
    for job in all_jobs:
        print(f"  - {job.name}")

    print("\nSchedules:")
    for schedule in all_schedules:
        print(f"  - {schedule.name}: {schedule.cron_schedule}")

    print("\nSensors:")
    for sensor in all_sensors:
        print(f"  - {sensor.name}")
