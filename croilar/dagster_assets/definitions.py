"""
Dagster Definitions for Croílár.

Orchestrates music data ingestion, CV/teaching PDF extraction,
artwork processing, embedding pipelines, and cross-linking.
"""

from dagster import (
    Definitions,
    load_assets_from_modules,
)

from . import dlt_assets, cocoindex_assets, cv_assets
from .schedules import (
    all_jobs,
    all_schedules,
    all_sensors,
)

dlt_asset_list = load_assets_from_modules([dlt_assets])
cocoindex_asset_list = load_assets_from_modules([cocoindex_assets])
cv_asset_list = load_assets_from_modules([cv_assets])

defs = Definitions(
    assets=dlt_asset_list + cocoindex_asset_list + cv_asset_list,
    jobs=all_jobs,
    schedules=all_schedules,
    sensors=all_sensors,
)
