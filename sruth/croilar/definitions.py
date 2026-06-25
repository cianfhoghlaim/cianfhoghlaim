"""Dagster Definitions for Croílár Pipeline.

Main entry point for Dagster. Combines all assets, jobs,
schedules, and sensors for the croilar portfolio subproject.

Usage:
    dagster dev -f definitions.py       # Start Dagster UI
    dagster job execute -f definitions.py -j daily_music_job
    dagster asset materialize -f definitions.py --select cv_pdf_ingestion
"""

import os

from dagster import (
    Definitions,
    load_assets_from_modules,
)
from dagster_dlt import DagsterDltResource

from dagster_assets import cocoindex_assets, cv_assets, dlt_assets
from dagster_assets.schedules import (
    all_jobs,
    all_schedules,
    all_sensors,
)

dlt_asset_defs = load_assets_from_modules([dlt_assets])
cocoindex_asset_defs = load_assets_from_modules([cocoindex_assets])
cv_asset_defs = load_assets_from_modules([cv_assets])

all_assets = [*dlt_asset_defs, *cocoindex_asset_defs, *cv_asset_defs]

resources = {
    "dlt": DagsterDltResource(),
}

if os.environ.get("DAGSTER_ENV") == "production":
    resources.update({})

defs = Definitions(
    assets=all_assets,
    jobs=all_jobs,
    schedules=all_schedules,
    sensors=all_sensors,
    resources=resources,
)


if __name__ == "__main__":
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
