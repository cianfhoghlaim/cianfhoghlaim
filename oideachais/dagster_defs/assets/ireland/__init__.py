"""
oideachais.dagster_defs.assets.ireland — LEGACY re-export shim.

Phase 5 of the openspec change moves the Ireland assets to the
domain-first address `oideachais.dagster_defs.assets.ie.education`.
This shim preserves the legacy import path for one release cycle.
"""
from __future__ import annotations

from oideachais.dagster_defs.assets.ie import education as _new

# Forward every name from the new package, with the legacy "ireland" alias.
curriculum_dlt_assets = _new.curriculum_dlt_assets
exam_materials_assets = _new.exam_materials_assets
scraped_curriculum_pages = _new.scraped_curriculum_pages
FirecrawlConfig = _new.FirecrawlConfig
create_cycle_asset = _new.create_cycle_asset

__all__ = [
    "curriculum_dlt_assets",
    "exam_materials_assets",
    "scraped_curriculum_pages",
    "FirecrawlConfig",
    "create_cycle_asset",
]
