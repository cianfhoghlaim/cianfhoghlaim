"""
Unified Celtic Education Platform - Dagster Definitions

Merged from:
- oideachas: Irish education curriculum platform (NCCA, SEC, curriculumonline.ie)
- teanga: Celtic language processing platform (6 Celtic languages, OCR, NLP)
- oideachas_oileáin: British Isles multilingual education (6 nations + Crown Dependencies)

Coverage:
- 6 nations: England, Scotland, Wales, Northern Ireland, Ireland, Crown Dependencies
- 6 Celtic languages: Irish (ga), Scottish Gaelic (gd), Welsh (cy), Manx (gv), Cornish (kw), Breton (br)
- 3 domains: Education curriculum, Language processing, Statistics & policy
- Geospatial: DuckDB Spatial + Met Office + GeoHive.ie + CSO Small Areas
- Auto-translation: Curriculum content translated to all Celtic languages on ingestion

Usage:
    cd /path/to/oideachais
    DAGSTER_HOME=. dagster dev -m dagster.definitions
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file (lakehouse credentials)
# This must happen before importing resources that use env vars
_locket_env = Path("/run/secrets/locket/secrets.env")
_env_file = Path(__file__).parent.parent / ".env"

if _locket_env.exists():
    load_dotenv(_locket_env)
    
if _env_file.exists():
    load_dotenv(_env_file, override=True)

import dagster as dg

# ============================================================================
# Job Definitions
# ============================================================================
from dagster import AssetKey, AssetSelection, define_asset_job

# ============================================================================
# Asset Check Imports
# ============================================================================
from .asset_checks import all_asset_checks

# ============================================================================
# Asset Imports
# ============================================================================
from .assets import all_assets

# Celtic Language Assets
# Geospatial Assets
# NOTE: Legacy assets removed during cleanup:
# - ie_education_assets (replaced by unified curriculum assets)
# - ncca_assets (replaced by unified curriculum assets)
# - curriculum_assets.py (replaced by @dlt_assets pattern)
# - subject_assets.py (replaced by @dlt_assets pattern)
# Ireland Curriculum Assets (@dlt_assets pattern - auto-parallelized)
from .assets.ireland import curriculum_dlt_assets

# PDF Processing Assets
from .assets.pdf_assets import pdf_processing_assets

# UK Education Assets
# ============================================================================
# Partition Imports
# ============================================================================
# NOTE: Deprecated NCCA/SEC partitions removed (208/780 partitions)
# Use partitions_v2.ireland_curriculum_partitions (4 partitions) instead
# New simplified partitions (4 cycles vs 208)
# Import all resources from the dedicated resources module (avoids circular imports)
from .resources import (
    all_resources,
)

# ============================================================================
# Sensor Imports
# ============================================================================
from .sensors import all_sensors

# NOTE: ireland_seed_job removed - asset was in deleted ie_education_assets.py

# Enriched assets pipeline (no partitions)
enriched_job = define_asset_job(
    name="enriched_pipeline",
    selection=AssetSelection.key_prefixes(["enriched"]),
    description="Run cross-domain enrichment assets",
)

# Search indexes pipeline (no partitions)
search_job = define_asset_job(
    name="search_pipeline",
    selection=AssetSelection.key_prefixes(["search"]),
    description="Build unified search indexes",
)

# NOTE: ncca_pipeline_job removed - use cycle-specific jobs instead

# Curriculum Pipeline Jobs (one per cycle due to different partition definitions)
# Each cycle has different subjects, so they need separate jobs
curriculum_early_childhood_job = define_asset_job(
    name="curriculum_early_childhood",
    selection=AssetSelection.assets(AssetKey(["ireland", "curriculum", "early_childhood"])),
    description="Ireland Early Childhood curriculum - Aistear and Siolta frameworks",
    tags={"pipeline": "ireland_curriculum", "cycle": "early_childhood"},
)

curriculum_primary_job = define_asset_job(
    name="curriculum_primary",
    selection=AssetSelection.assets(AssetKey(["ireland", "curriculum", "primary"])),
    description="Ireland Primary curriculum - 8 subjects",
    tags={"pipeline": "ireland_curriculum", "cycle": "primary"},
)

curriculum_junior_cycle_job = define_asset_job(
    name="curriculum_junior_cycle",
    selection=AssetSelection.assets(AssetKey(["ireland", "curriculum", "junior_cycle"])),
    description="Ireland Junior Cycle curriculum - 18 subjects",
    tags={"pipeline": "ireland_curriculum", "cycle": "junior_cycle"},
)

curriculum_senior_cycle_job = define_asset_job(
    name="curriculum_senior_cycle",
    selection=AssetSelection.assets(AssetKey(["ireland", "curriculum", "senior_cycle"])),
    description="Ireland Senior Cycle curriculum - 33 subjects",
    tags={"pipeline": "ireland_curriculum", "cycle": "senior_cycle"},
)

curriculum_short_courses_job = define_asset_job(
    name="curriculum_short_courses",
    selection=AssetSelection.assets(AssetKey(["ireland", "curriculum", "short_courses"])),
    description="Ireland Junior Cycle Short Courses - 8 courses",
    tags={"pipeline": "ireland_curriculum", "cycle": "junior_cycle", "type": "short_course"},
)

# PDF Processing Job
pdf_processing_job = define_asset_job(
    name="pdf_processing",
    selection=AssetSelection.assets(
        AssetKey(["ireland", "curriculum", "pdf_downloads"]),
        AssetKey(["ireland", "curriculum", "pdf_extracted_text"]),
    ),
    description="Download and extract text from curriculum PDFs",
    tags={"pipeline": "ireland_curriculum", "stage": "pdf_processing"},
)

# Note: Each cycle has MultiPartition(subject, language)
# Short courses have MultiPartition(course, language)
# Assets can be materialized individually or via backfill
# Firecrawl concurrency limited via op_tags

all_jobs = [
    enriched_job,
    search_job,
    curriculum_early_childhood_job,
    curriculum_primary_job,
    curriculum_junior_cycle_job,
    curriculum_senior_cycle_job,
    curriculum_short_courses_job,
    pdf_processing_job,
]


# ============================================================================
# Schedules
# ============================================================================

from .schedules import all_schedules

# ============================================================================
# Concurrency Limits
# ============================================================================

# Define concurrency limits for resource-constrained operations
# These work with op_tags={"dagster/concurrency_key": "key_name"} on assets
CONCURRENCY_LIMITS = {
    "duckdb": 1,      # DuckDB is single-threaded only - prevent segfaults
    "firecrawl": 3,   # Limit concurrent Firecrawl API calls
    "lancedb": 2,     # LanceDB is MVCC-safe but limit for performance
}


# ============================================================================
# Definitions
# ============================================================================

# Combine all asset lists
combined_assets = [
    *all_assets,
    *curriculum_dlt_assets,  # Ireland curriculum (@dlt_assets pattern, auto-parallelized)
    *pdf_processing_assets,  # PDF download and OCR extraction
]

defs = dg.Definitions(
    assets=combined_assets,
    asset_checks=all_asset_checks,
    jobs=all_jobs,
    sensors=all_sensors,
    schedules=all_schedules,
    resources=all_resources,
)
