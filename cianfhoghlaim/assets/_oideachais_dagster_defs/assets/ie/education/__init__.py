"""
oideachais.dagster_defs.assets.ie.education — Ireland education Dagster assets.

Phase 5 of the openspec change. Previously at
`oideachais.dagster_defs.assets.ireland`; renamed to the new
domain-first path. The legacy address is preserved as a re-export
shim in `oideachais.dagster_defs.assets.ireland.__init__`.
"""
from .aistear_dlt_assets import (
    AISTEAR_ASSETS,
    AISTEAR_CHECKS,
    AISTEAR_FULL_JOB,
    aistear_documents_ducklake,
    aistear_documents_row_count_check,
)
from .curriculum_dlt_assets import (
    create_cycle_asset,
    curriculum_dlt_assets,
)
from .exam_materials_assets import (
    exam_materials_assets,
)
from .firecrawl_assets import (
    FirecrawlConfig,
    scraped_curriculum_pages,
)

__all__ = [
    "create_cycle_asset",
    "curriculum_dlt_assets",
    "exam_materials_assets",
    "scraped_curriculum_pages",
    "FirecrawlConfig",
    "aistear_documents_ducklake",
    "aistear_documents_row_count_check",
    "AISTEAR_ASSETS",
    "AISTEAR_CHECKS",
    "AISTEAR_FULL_JOB",
]
