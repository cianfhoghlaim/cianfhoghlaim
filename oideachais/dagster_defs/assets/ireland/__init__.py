"""
Ireland Education Assets with MultiPartition.

This package contains Dagster assets for Ireland education curriculum data,
organized by cycle with MultiPartition(subject, language).

Asset Structure:
    ireland/curriculum/senior_cycle   ← MultiPartition(subject, language)
    ireland/curriculum/junior_cycle   ← MultiPartition(subject, language)
    ireland/curriculum/primary        ← MultiPartition(subject, language)
    ireland/curriculum/early_childhood ← MultiPartition(subject, language)

Partition keys: "chemistry|en", "chemistry|ga", "biology|en", etc.

All assets write to a single unified DuckDB: .dlt/curriculum_unified/curriculum.duckdb

Usage:
    from dagster_defs.assets.ireland import curriculum_dlt_assets

    defs = Definitions(assets=curriculum_dlt_assets)
"""
from __future__ import annotations

from .curriculum_dlt_assets import (
    CYCLE_PARTITIONS,
    CYCLE_SUBJECTS,
    CYCLES,
    DLT_DATASET_NAME,
    DLT_PIPELINE_NAME,
    DLT_PIPELINES_DIR,
    create_all_curriculum_assets,
    create_cycle_asset,
    curriculum_dlt_assets,
)
from .firecrawl_assets import scraped_curriculum_pages

__all__ = [
    "curriculum_dlt_assets",
    "scraped_curriculum_pages",
    "create_cycle_asset",
    "create_all_curriculum_assets",
    "CYCLE_PARTITIONS",
    "CYCLES",
    "CYCLE_SUBJECTS",
    "DLT_PIPELINE_NAME",
    "DLT_DATASET_NAME",
    "DLT_PIPELINES_DIR",
]
