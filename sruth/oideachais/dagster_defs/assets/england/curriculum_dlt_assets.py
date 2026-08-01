"""
England Curriculum Pipeline - Centralized with MultiPartition.

Creates Dagster assets (one per key stage) with MultiPartition(subject).
All assets write to a DuckLake lakehouse (local or production via DLT_ENVIRONMENT).

Asset Structure:
    england/curriculum/ks1 ← MultiPartition(subject)
    england/curriculum/ks2 ← MultiPartition(subject)
    england/curriculum/ks3 ← MultiPartition(subject)
    england/curriculum/ks4 ← MultiPartition(subject)
    england/curriculum/ks5 ← MultiPartition(subject)

Partition Keys: "mathematics", "english", etc. (English only - no language dimension)

Environment:
    DLT_ENVIRONMENT=local (default): Garage S3 + local PostgreSQL
    DLT_ENVIRONMENT=production: Cloudflare R2 + PlanetScale

Usage:
    from dagster_defs.assets.england import curriculum_dlt_assets

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

KEY_STAGES = ["ks1", "ks2", "ks3", "ks4", "ks5"]

KEY_STAGE_SUBJECTS = {
    "ks1": [
        "mathematics",
        "english_language",
        "science",
        "history",
        "geography",
        "religious_studies",
        "physical_education",
        "computing",
        "art_and_design",
        "music",
    ],
    "ks2": [
        "mathematics",
        "english_language",
        "english_literature",
        "science",
        "history",
        "geography",
        "religious_studies",
        "computing",
        "physical_education",
        "art_and_design",
        "music",
        "design_technology",
        "modern_foreign_languages",
    ],
    "ks3": [
        "mathematics",
        "english_language",
        "english_literature",
        "science",
        "history",
        "geography",
        "religious_studies",
        "computer_science",
        "physical_education",
        "art_and_design",
        "music",
        "drama",
        "design_technology",
        "modern_foreign_languages",
        "statistics",
        "citizenship",
    ],
    "ks4": [
        "mathematics",
        "english_language",
        "english_literature",
        "science",
        "biology",
        "chemistry",
        "physics",
        "history",
        "geography",
        "religious_studies",
        "computer_science",
        "physical_education_sport",
        "art_and_design",
        "music",
        "drama",
        "design_technology",
        "business_studies",
        "economics",
        "modern_foreign_languages",
        "statistics",
        "psychology",
        "sociology",
        "politics",
        "media_studies",
    ],
    "ks5": [
        "mathematics",
        "english_language",
        "english_literature",
        "biology",
        "chemistry",
        "physics",
        "history",
        "geography",
        "computer_science",
        "business_studies",
        "economics",
        "modern_foreign_languages",
        "statistics",
        "psychology",
        "sociology",
        "politics",
        "media_studies",
        "art_and_design",
        "music",
        "drama",
        "physical_education_sport",
    ],
}

# Unified DLT pipeline configuration
DLT_PIPELINE_NAME = "england_curriculum_unified"
DLT_DATASET_NAME = "england_curriculum"
DLT_PIPELINES_DIR = Path(__file__).parent.parent.parent.parent / ".dlt"


# ============================================================================
# Partition Definitions
# ============================================================================

# England is English only - no language dimension
def create_key_stage_partitions(key_stage: str) -> StaticPartitionsDefinition:
    """
    Create StaticPartitions for a key stage (subjects only, no language dimension).

    Args:
        key_stage: Education key stage (ks1, ks2, ks3, ks4, ks5)

    Returns:
        StaticPartitionsDefinition with subjects
    """
    subjects = KEY_STAGE_SUBJECTS.get(key_stage, [])
    return StaticPartitionsDefinition(subjects)


# Pre-create partition definitions for each key stage
KEY_STAGE_PARTITIONS = {
    key_stage: create_key_stage_partitions(key_stage)
    for key_stage in KEY_STAGES
}


# ============================================================================
# Asset Factory
# ============================================================================

def create_key_stage_asset(key_stage: str):
    """
    Create a curriculum asset for a key stage with StaticPartition(subject).

    Asset key: england/curriculum/{key_stage}
    Partition: subject (e.g., "mathematics")

    All assets write to the same unified DuckDB for centralized storage.
    """
    display_name = key_stage.replace("ks", "Key Stage ").upper()
    asset_key = ["england", "curriculum", key_stage]

    @dg.asset(
        key=asset_key,
        group_name="england_curriculum",
        compute_kind="dlt",
        description=f"England {display_name} Curriculum",
        partitions_def=KEY_STAGE_PARTITIONS[key_stage],
        retry_policy=dg.RetryPolicy(
            max_retries=3,
            delay=30,
            backoff=dg.Backoff.EXPONENTIAL,
        ),
        tags={
            "key_stage": key_stage,
            "nation": "england",
            "pipeline": "england_curriculum",
        },
        op_tags={"dagster/concurrency_key": f"england_curriculum_{key_stage}"},
    )
    def _key_stage_asset(context) -> dg.MaterializeResult:
        """Ingest curriculum data for this key stage's subject partition."""
        # Disable DLT plugin scanning to avoid metadata bug
        os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")

        from sruth.oideachais.dlt_sources.england.curriculum_source import (
            parallel_scrape_subject,
            build_subject_urls,
        )
        from sruth.oideachais.dlt_sources.england.curriculum_registry import SubjectRegistry

        # Extract partition key (subject only - no language dimension for England)
        subject = context.partition_key
        language = "en"  # England is English only

        context.log.info(
            f"Ingesting: england/{key_stage}/{subject}"
        )

        # Initialize registry for URL building
        registry = SubjectRegistry.from_default()

        # Build and log URLs
        urls = build_subject_urls(key_stage, subject, registry)
        for url_info in urls:
            context.log.info(f"  {url_info['source']}: {url_info['url']}")

        # Parallel scrape all URLs
        pages = list(parallel_scrape_subject(
            key_stage=key_stage,
            subject=subject,
            registry=registry,
            max_workers=4,
            max_pages_per_url=50,
            max_depth=3,
        ))

        context.log.info(f"Scraped {len(pages)} pages from {len(urls)} URLs")

        # Choose destination based on environment
        use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"

        if use_ducklake:
            destination = get_dlt_destination()
            context.log.info(f"Using DuckLake destination (DLT_ENVIRONMENT={os.environ.get('DLT_ENVIRONMENT', 'local')})")
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
            if hasattr(pkg, 'jobs'):
                for job in pkg.jobs.values() if isinstance(pkg.jobs, dict) else pkg.jobs:
                    if hasattr(job, 'metrics') and job.metrics:
                        rows_loaded += getattr(job.metrics, 'rows_count', 0) or 0

        context.log.info(f"Loaded {rows_loaded} rows for england/{key_stage}/{subject}")

        return dg.MaterializeResult(
            metadata={
                "nation": "england",
                "key_stage": key_stage,
                "subject": subject,
                "language": language,
                "urls_scraped": len(urls),
                "pages_found": len(pages),
                "rows_loaded": rows_loaded,
                "load_id": str(load_info.loads_ids[0]) if load_info.loads_ids else "unknown",
                "duckdb_path": str(DLT_PIPELINES_DIR / DLT_PIPELINE_NAME / f"{DLT_DATASET_NAME}.duckdb"),
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
    """Create all English curriculum assets (one per key stage)."""
    assets = []

    for key_stage in KEY_STAGES:
        try:
            asset = create_key_stage_asset(key_stage)
            assets.append(asset)
            _safe_log("debug", "created_key_stage_asset", key_stage=key_stage)
        except Exception as e:
            _safe_log("warning", "failed_to_create_key_stage_asset", key_stage=key_stage, error=str(e))

    _safe_log("info", "created_all_england_curriculum_assets", count=len(assets))
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
