"""
Dagster Definitions for Aleyum.

Orchestrates music data ingestion, artwork processing, and embedding pipelines.
"""

from dagster import (
    Definitions,
    load_assets_from_modules,
)

from . import dlt_assets, cocoindex_assets
from .schedules import (
    all_jobs,
    all_schedules,
    all_sensors,
)

# Load all assets from modules
dlt_asset_list = load_assets_from_modules([dlt_assets])
cocoindex_asset_list = load_assets_from_modules([cocoindex_assets])

# Combine all definitions
defs = Definitions(
    assets=dlt_asset_list + cocoindex_asset_list,
    jobs=all_jobs,
    schedules=all_schedules,
    sensors=all_sensors,
)
