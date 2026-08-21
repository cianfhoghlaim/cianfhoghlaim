"""
Scotland Curriculum Pipeline - Centralized with MultiPartition.

Creates Dagster assets (one per curriculum level) with MultiPartition(subject, language).
All assets write to a DuckLake lakehouse (local or production via DLT_ENVIRONMENT).

Asset Structure:
    scotland/curriculum/early    ← MultiPartition(subject, language)
    scotland/curriculum/first    ← MultiPartition(subject, language)
    scotland/curriculum/second   ← MultiPartition(subject, language)
    scotland/curriculum/third    ← MultiPartition(subject, language)
    scotland/curriculum/fourth   ← MultiPartition(subject, language)

Partition Keys: "mathematics|en", "gaelic_learners|gd", etc.

Environment:
    DLT_ENVIRONMENT=local (default): Garage S3 + local PostgreSQL
    DLT_ENVIRONMENT=production: Cloudflare R2 + PlanetScale

Usage:
    from dagster_defs.assets.scotland import curriculum_dlt_assets

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

CURRICULUM_LEVELS = ["early", "first", "second", "third", "fourth"]

LEVEL_SUBJECTS = {
    "early": [
        "gaelic_fluent",
        "health_wellbeing",
        "expressive_arts",
    ],
    "first": [
        "mathematics",
        "gaelic_learners",
        "gaelic_fluent",
        "english",
        "scots",
        "health_wellbeing",
        "expressive_arts",
        "technologies",
        "social_studies",
        "sciences",
    ],
    "second": [
        "mathematics",
        "gaelic_learners",
        "gaelic_fluent",
        "english",
        "scots",
        "biology",
        "chemistry",
        "physics",
        "history",
        "geography",
        "modern_studies",
        "religious_moral_education",
        "computing_science",
        "physical_education",
        "health_wellbeing",
        "expressive_arts",
        "technologies",
        "social_studies",
        "sciences",
        "languages",
        "art_and_design",
        "drama",
        "music",
        "business",
    ],
    "third": [
        "mathematics",
        "gaelic_learners",
        "gaelic_fluent",
        "english",
        "scots",
        "biology",
        "chemistry",
        "physics",
        "history",
        "geography",
        "modern_studies",
        "religious_moral_education",
        "computing_science",
        "physical_education",
        "health_wellbeing",
        "expressive_arts",
        "technologies",
        "social_studies",
        "sciences",
        "languages",
        "art_and_design",
        "drama",
        "music",
        "business",
    ],
    "fourth": [
        "mathematics",
        "gaelic_learners",
        "gaelic_fluent",
        "english",
        "biology",
        "chemistry",
        "physics",
        "history",
        "geography",
        "modern_studies",
        "computing_science",
        "physical_education",
        "art_and_design",
        "drama",
        "music",
        "business",
        "economics",
    ],
}

# Unified DLT pipeline configuration
DLT_PIPELINE_NAME = "scotland_curriculum_unified"
DLT_DATASET_NAME = "scotland_curriculum"
DLT_PIPELINES_DIR = Path(__file__).parent.parent.parent.parent / ".dlt"


# ============================================================================
# MultiPartition Definitions
# ============================================================================


def create_level_partition(level: str) -> MultiPartitionsDefinition:
    """
    Create a MultiPartition for a curriculum level: subject × language.

    Args:
        level: Curriculum level (early, first, second, third, fourth)

    Returns:
        MultiPartitionsDefinition with subject and language dimensions
    """
    subjects = LEVEL_SUBJECTS.get(level, [])
    return MultiPartitionsDefinition(
        {
            "subject": StaticPartitionsDefinition(subjects),
            "language": StaticPartitionsDefinition(["en", "gd"]),
        }
    )


# Pre-create partition definitions for each level
LEVEL_PARTITIONS = {level: create_level_partition(level) for level in CURRICULUM_LEVELS}


# ============================================================================
# Asset Factory
# ============================================================================


def create_level_asset(level: str):
    """
    Create a curriculum asset for a curriculum level with MultiPartition(subject, language).

    Asset key: scotland/curriculum/{level}
    Partition: subject|language (e.g., "mathematics|en")

    All assets write to the same unified DuckDB for centralized storage.
    """
    display_name = level.replace("_", " ").title()
    asset_key = ["scotland", "curriculum", level]

    @dg.asset(
        key=asset_key,
        group_name="scotland_curriculum",
        compute_kind="dlt",
        description=f"Scotland {display_name} Curriculum",
        partitions_def=LEVEL_PARTITIONS[level],
        retry_policy=dg.RetryPolicy(
            max_retries=3,
            delay=30,
            backoff=dg.Backoff.EXPONENTIAL,
        ),
        tags={
            "level": level,
            "nation": "scotland",
            "pipeline": "scotland_curriculum",
        },
        op_tags={"dagster/concurrency_key": f"scotland_curriculum_{level}"},
    )
    def _level_asset(context) -> dg.MaterializeResult:
        """Ingest curriculum data for this level's subject/language partition."""
        # Disable DLT plugin scanning to avoid metadata bug
        os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")

        from sruth.oideachais.dlt_sources.scotland.curriculum_source import (
            parallel_scrape_subject,
            build_subject_urls,
        )
        from sruth.oideachais.dlt_sources.scotland.curriculum_registry import SubjectRegistry

        # Extract partition keys
        partition_keys = context.partition_key.keys_by_dimension
        subject = partition_keys["subject"]
        language = partition_keys["language"]

        context.log.info(f"Ingesting: scotland/{level}/{subject}/{language}")

        # Initialize registry for URL building
        registry = SubjectRegistry.from_default()

        # Build and log URLs
        urls = build_subject_urls(level, subject, registry)
        for url_info in urls:
            context.log.info(f"  {url_info['source']}/{url_info['language']}: {url_info['url']}")

        # Parallel scrape all URLs
        pages = list(
            parallel_scrape_subject(
                level=level,
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

        context.log.info(f"Loaded {rows_loaded} rows for scotland/{level}/{subject}/{language}")

        return dg.MaterializeResult(
            metadata={
                "nation": "scotland",
                "level": level,
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

    return _level_asset


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
    """Create all Scottish curriculum assets (one per curriculum level)."""
    assets = []

    for level in CURRICULUM_LEVELS:
        try:
            asset = create_level_asset(level)
            assets.append(asset)
            _safe_log("debug", "created_level_asset", curriculum_level=level)
        except Exception as e:
            _safe_log(
                "warning", "failed_to_create_level_asset", curriculum_level=level, error=str(e)
            )

    _safe_log("info", "created_all_scotland_curriculum_assets", count=len(assets))
    return assets


# ============================================================================
# Default Export
# ============================================================================

curriculum_dlt_assets = create_all_curriculum_assets()

__all__ = [
    "curriculum_dlt_assets",
    "create_level_asset",
    "create_all_curriculum_assets",
    "LEVEL_PARTITIONS",
    "CURRICULUM_LEVELS",
    "LEVEL_SUBJECTS",
    "DLT_PIPELINE_NAME",
    "DLT_DATASET_NAME",
    "DLT_PIPELINES_DIR",
]
