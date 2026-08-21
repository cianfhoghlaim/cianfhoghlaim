"""
Northern Ireland Curriculum Pipeline - Centralized with MultiPartition.

Creates Dagster assets (one per key stage) with MultiPartition(subject, language).
All assets write to a DuckLake lakehouse (local or production via DLT_ENVIRONMENT).

Asset Structure:
    northern_ireland/curriculum/foundation ← MultiPartition(subject, language)
    northern_ireland/curriculum/ks1       ← MultiPartition(subject, language)
    northern_ireland/curriculum/ks2       ← MultiPartition(subject, language)
    northern_ireland/curriculum/ks3       ← MultiPartition(subject, language)
    northern_ireland/curriculum/ks4       ← MultiPartition(subject, language)

Partition Keys: "mathematics|en", "irish|ga", etc.

Environment:
    DLT_ENVIRONMENT=local (default): Garage S3 + local PostgreSQL
    DLT_ENVIRONMENT=production: Cloudflare R2 + PlanetScale

Usage:
    from dagster_defs.assets.northern_ireland import curriculum_dlt_assets

    defs = Definitions(assets=curriculum_dlt_assets)
"""

import os
from pathlib import Path

import structlog
import dlt
import dagster as dg
from dagster import (
    MultiPartitionsDefinition,
    StaticPartitionsDefinition,
)

from sruth.oideachais.dlt_utils import (
    get_dlt_destination,
    get_duckdb_fallback_destination,
    safe_dlt_run,
)

logger = structlog.get_logger(__name__)


# ============================================================================
# Configuration
# ============================================================================

KEY_STAGES = ["foundation", "ks1", "ks2", "ks3", "ks4"]

KEY_STAGE_SUBJECTS = {
    "foundation": [
        "mathematics",
        "english",
        "irish",
        "science",
        "art_and_design",
        "music",
        "physical_education",
    ],
    "ks1": [
        "mathematics",
        "english",
        "irish",
        "science",
        "art_and_design",
        "music",
        "physical_education",
        "religious_studies",
    ],
    "ks2": [
        "mathematics",
        "english",
        "irish",
        "science",
        "history",
        "geography",
        "religious_studies",
        "computing",
        "art_and_design",
        "music",
        "physical_education",
    ],
    "ks3": [
        "mathematics",
        "english",
        "irish",
        "science",
        "history",
        "geography",
        "religious_studies",
        "digital_technology",
        "computing",
        "art_and_design",
        "music",
        "drama",
        "physical_education",
        "business_studies",
        "home_economics",
        "technology_and_design",
        "modern_languages",
        "learning_for_life_and_work",
    ],
    "ks4": [
        "mathematics",
        "english",
        "irish",
        "science",
        "biology",
        "chemistry",
        "physics",
        "double_award_science",
        "history",
        "geography",
        "religious_studies",
        "digital_technology",
        "art_and_design",
        "music",
        "drama",
        "business_studies",
        "media_studies",
        "modern_languages",
        "learning_for_life_and_work",
        "home_economics",
        "technology_and_design",
    ],
}

# Unified DLT pipeline configuration
DLT_PIPELINE_NAME = "northern_ireland_curriculum_unified"
DLT_DATASET_NAME = "northern_ireland_curriculum"
DLT_PIPELINES_DIR = Path(__file__).parent.parent.parent.parent / ".dlt"


# ============================================================================
# MultiPartition Definitions
# ============================================================================


def create_key_stage_partition(key_stage: str) -> MultiPartitionsDefinition:
    """
    Create a MultiPartition for a key stage: subject × language.

    Args:
        key_stage: Education key stage (ks1, ks2, ks3, ks4)

    Returns:
        MultiPartitionsDefinition with subject and language dimensions
    """
    subjects = KEY_STAGE_SUBJECTS.get(key_stage, [])
    return MultiPartitionsDefinition(
        {
            "subject": StaticPartitionsDefinition(subjects),
            "language": StaticPartitionsDefinition(["en", "ga"]),
        }
    )


# Pre-create partition definitions for each key stage
KEY_STAGE_PARTITIONS = {
    key_stage: create_key_stage_partition(key_stage) for key_stage in KEY_STAGES
}


# ============================================================================
# Asset Factory
# ============================================================================


def create_key_stage_asset(key_stage: str):
    """
    Create a curriculum asset for a key stage with MultiPartition(subject, language).

    Asset key: northern_ireland/curriculum/{key_stage}
    Partition: subject|language (e.g., "mathematics|en")

    All assets write to the same unified DuckDB for centralized storage.
    """
    display_name = key_stage.replace("_", " ").replace("ks", "Key Stage ").upper()
    asset_key = ["northern_ireland", "curriculum", key_stage]

    @dg.asset(
        key=asset_key,
        group_name="northern_ireland_curriculum",
        compute_kind="dlt",
        description=f"Northern Ireland {display_name} Curriculum",
        partitions_def=KEY_STAGE_PARTITIONS[key_stage],
        retry_policy=dg.RetryPolicy(
            max_retries=3,
            delay=30,
            backoff=dg.Backoff.EXPONENTIAL,
        ),
        tags={
            "key_stage": key_stage,
            "nation": "northern_ireland",
            "pipeline": "northern_ireland_curriculum",
        },
        op_tags={"dagster/concurrency_key": f"northern_ireland_curriculum_{key_stage}"},
    )
    def _key_stage_asset(context) -> dg.MaterializeResult:
        """Ingest curriculum data for this key stage's subject/language partition."""
        # Disable DLT plugin scanning to avoid metadata bug
        os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")

        from sruth.oideachais.dlt_sources.northern_ireland.curriculum_source import (
            parallel_scrape_subject,
            build_subject_urls,
        )
        from sruth.oideachais.dlt_sources.northern_ireland.curriculum_registry import (
            SubjectRegistry,
        )

        # Extract partition keys
        partition_keys = context.partition_key.keys_by_dimension
        subject = partition_keys["subject"]
        language = partition_keys["language"]

        context.log.info(f"Ingesting: northern_ireland/{key_stage}/{subject}/{language}")

        # Initialize registry for URL building
        registry = SubjectRegistry.from_default()

        # Build and log URLs
        urls = build_subject_urls(key_stage, subject, registry)
        for url_info in urls:
            context.log.info(f"  {url_info['source']}/{url_info['language']}: {url_info['url']}")

        # Parallel scrape all URLs
        pages = list(
            parallel_scrape_subject(
                key_stage=key_stage,
                subject=subject,
                registry=registry,
                max_workers=4,
                max_pages_per_url=50,
                max_depth=3,
            )
        )

        context.log.info(f"Scraped {len(pages)} pages from {len(urls)} URLs")

        # Choose destination based on environment
        use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"

        if use_ducklake:
            destination = get_dlt_destination()
            context.log.info(
                f"Using DuckLake destination (DLT_ENVIRONMENT={os.environ.get('DLT_ENVIRONMENT', 'local')})"
            )
        else:
            destination = get_duckdb_fallback_destination(
                str(DLT_PIPELINES_DIR / DLT_PIPELINE_NAME / f"{DLT_DATASET_NAME}.duckdb")
            )
            context.log.info("Using DuckDB fallback destination")

        # Create unified DLT pipeline
        dlt_pipeline = dlt.pipeline(
            pipeline_name=DLT_PIPELINE_NAME,
            destination=destination,
            dataset_name=DLT_DATASET_NAME,
            pipelines_dir=str(DLT_PIPELINES_DIR),
        )

        def generate_pages():
            for page in pages:
                if page.get("status") not in ("error", "no_api_key", "firecrawl_not_installed"):
                    yield page

        # Run DLT pipeline through serial executor for DuckDB safety
        load_info = safe_dlt_run(
            dlt_pipeline,
            generate_pages(),
            table_name="curriculum_pages",
            write_disposition="merge",
            primary_key=["url"],
        )

        # Calculate rows loaded
        rows_loaded = 0
        for pkg in load_info.load_packages:
            if hasattr(pkg, "jobs"):
                for job in pkg.jobs.values() if isinstance(pkg.jobs, dict) else pkg.jobs:
                    if hasattr(job, "metrics") and job.metrics:
                        rows_loaded += getattr(job.metrics, "rows_count", 0) or 0

        context.log.info(
            f"Loaded {rows_loaded} rows for northern_ireland/{key_stage}/{subject}/{language}"
        )

        return dg.MaterializeResult(
            metadata={
                "nation": "northern_ireland",
                "key_stage": key_stage,
                "subject": subject,
                "language": language,
                "urls_scraped": len(urls),
                "pages_found": len(pages),
                "rows_loaded": rows_loaded,
                "load_id": str(load_info.loads_ids[0]) if load_info.loads_ids else "unknown",
                "duckdb_path": str(
                    DLT_PIPELINES_DIR / DLT_PIPELINE_NAME / f"{DLT_DATASET_NAME}.duckdb"
                ),
            }
        )

    return _key_stage_asset


# ============================================================================
# Asset Generation
# ============================================================================


def _safe_log(level: str, event: str, **kwargs) -> None:
    """Safely log without raising BrokenPipeError in Dagster daemon context."""
    try:
        getattr(logger, level)(event, **kwargs)
    except (BrokenPipeError, OSError):
        pass


def create_all_curriculum_assets() -> list:
    """Create all Northern Irish curriculum assets (one per key stage)."""
    assets = []

    for key_stage in KEY_STAGES:
        try:
            asset = create_key_stage_asset(key_stage)
            assets.append(asset)
            _safe_log("debug", "created_key_stage_asset", key_stage=key_stage)
        except Exception as e:
            _safe_log(
                "warning", "failed_to_create_key_stage_asset", key_stage=key_stage, error=str(e)
            )

    _safe_log("info", "created_all_northern_ireland_curriculum_assets", count=len(assets))
    return assets


# ============================================================================
# Default Export
# ============================================================================

curriculum_dlt_assets = create_all_curriculum_assets()

__all__ = [
    "curriculum_dlt_assets",
    "create_key_stage_asset",
    "create_all_curriculum_assets",
    "KEY_STAGE_PARTITIONS",
    "KEY_STAGES",
    "KEY_STAGE_SUBJECTS",
    "DLT_PIPELINE_NAME",
    "DLT_DATASET_NAME",
    "DLT_PIPELINES_DIR",
]
