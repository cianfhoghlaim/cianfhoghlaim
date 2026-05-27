"""
Ireland Curriculum Pipeline - Centralized with MultiPartition.

Creates 4 Dagster assets (one per cycle) with MultiPartition(subject, language).
All assets write to a DuckLake lakehouse (local or production via DLT_ENVIRONMENT).

Asset Structure:
    ireland/curriculum/senior_cycle   ← MultiPartition(subject, language)
    ireland/curriculum/junior_cycle   ← MultiPartition(subject, language)
    ireland/curriculum/primary        ← MultiPartition(subject, language)
    ireland/curriculum/early_childhood ← MultiPartition(subject, language)

Partition Keys: "chemistry|en", "chemistry|ga", "biology|en", etc.

Environment:
    DLT_ENVIRONMENT=local (default): Garage S3 + local PostgreSQL
    DLT_ENVIRONMENT=production: Cloudflare R2 + PlanetScale

Usage:
    from dagster_defs.assets.ireland import curriculum_dlt_assets

    defs = Definitions(assets=curriculum_dlt_assets)
"""
import os
from pathlib import Path

import dagster as dg
import dlt
import structlog
from dagster import (
    MultiPartitionsDefinition,
    StaticPartitionsDefinition,
)

from data_platform.dlt_utils import (
    get_dlt_destination,
    get_duckdb_fallback_destination,
    safe_dlt_run,
)

logger = structlog.get_logger(__name__)


# ============================================================================
# Configuration
# ============================================================================

CYCLES = ["early_childhood", "primary", "junior_cycle", "senior_cycle"]

CYCLE_SUBJECTS = {
    "early_childhood": ["aistear", "siolta"],
    "primary": [
        "irish", "english", "mathematics", "gaeilge",
        "sese", "sphe", "arts", "pe",
    ],
    # Junior Cycle: 18 subjects from curriculum_index.json
    "junior_cycle": [
        "applied-technology",
        "business-studies",
        "classics",
        "engineering",
        "english",
        "gaeilge",
        "geography",
        "graphics",
        "history",
        "home-economics",
        "mathematics",
        "modern-foreign-languages",
        "music",
        "physical-education",
        "religious-education",
        "science",
        "visual-art",
        "wood-technology",
    ],
    # Senior Cycle: 33 subjects from curriculum_index.json
    "senior_cycle": [
        "accounting",
        "agricultural-science",
        "applied-mathematics",
        "arabic",
        "art",
        "biology",
        "business",
        "chemistry",
        "classical-studies",
        "computer-science",
        "construction-studies",
        "design-and-communication-graphics",
        "economics",
        "engineering",
        "english",
        "french",
        "gaeilge",
        "geography",
        "german",
        "history",
        "home-economics",
        "italian",
        "japanese",
        "latin",
        "mathematics",
        "music",
        "physical-education",
        "physics",
        "physics-and-chemistry",
        "politics-and-society",
        "religious-education",
        "spanish",
        "technology",
    ],
}

# Junior Cycle Short Courses: 8 courses from curriculum_index.json
SHORT_COURSES = [
    "artistic-performance",
    "chinese-language-and-culture",
    "coding",
    "cspe",
    "digital-media-literacy",
    "philosophy",
    "physical-education-sc",
    "sphe",
]

# Unified DLT pipeline configuration
DLT_PIPELINE_NAME = "curriculum_unified"
DLT_DATASET_NAME = "curriculum"
DLT_PIPELINES_DIR = Path(__file__).parent.parent.parent.parent / ".dlt"


# ============================================================================
# MultiPartition Definitions
# ============================================================================

def create_cycle_partition(cycle: str) -> MultiPartitionsDefinition:
    """
    Create a MultiPartition for a cycle: subject × language.

    Args:
        cycle: Education cycle (junior_cycle, senior_cycle, etc.)

    Returns:
        MultiPartitionsDefinition with subject and language dimensions
    """
    subjects = CYCLE_SUBJECTS.get(cycle, [])
    return MultiPartitionsDefinition({
        "subject": StaticPartitionsDefinition(subjects),
        "language": StaticPartitionsDefinition(["en", "ga"]),
    })


# Pre-create partition definitions for each cycle
CYCLE_PARTITIONS = {
    cycle: create_cycle_partition(cycle)
    for cycle in CYCLES
}

# Short course partition: course × language
SHORT_COURSE_PARTITION = MultiPartitionsDefinition({
    "course": StaticPartitionsDefinition(SHORT_COURSES),
    "language": StaticPartitionsDefinition(["en", "ga"]),
})


# ============================================================================
# Asset Factory
# ============================================================================

def create_cycle_asset(cycle: str):
    """
    Create a curriculum asset for a cycle with MultiPartition(subject, language).

    Asset key: ireland/curriculum/{cycle}
    Partition: subject|language (e.g., "chemistry|en")

    All assets write to the same unified DuckDB for centralized storage.
    """
    display_name = cycle.replace("_", " ").title()
    asset_key = ["ireland", "curriculum", cycle]

    @dg.asset(
        key=asset_key,
        group_name="curriculum",
        compute_kind="dlt",
        description=f"Ireland {display_name} Curriculum",
        partitions_def=CYCLE_PARTITIONS[cycle],
        retry_policy=dg.RetryPolicy(
            max_retries=3,
            delay=30,
            backoff=dg.Backoff.EXPONENTIAL,
        ),
        tags={
            "cycle": cycle,
            "pipeline": "ireland_curriculum",
        },
        # Allow parallel execution across cycles but limit within cycle
        op_tags={"dagster/concurrency_key": f"curriculum_{cycle}"},
    )
    def _cycle_asset(context) -> dg.MaterializeResult:
        """Ingest curriculum data for this cycle's subject/language partition."""
        import os
        import sys
        # Disable DLT plugin scanning to avoid metadata bug
        os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

        
        from oideachais.data_platform.dlt_sources.ireland.curriculum_registry import SubjectRegistry
        from oideachais.data_platform.dlt_sources.ireland.curriculum_source import (
            build_subject_urls,
            parallel_scrape_subject,
        )

        # Extract partition keys
        partition_keys = context.partition_key.keys_by_dimension
        subject = partition_keys["subject"]
        language = partition_keys["language"]

        context.log.info(
            f"Ingesting: {cycle}/{subject}/{language}"
        )

        # Initialize registry for URL building
        registry = SubjectRegistry.from_default()

        # Build and log URLs
        urls = build_subject_urls(cycle, subject, registry, language=language)
        for url_info in urls:
            context.log.info(f"  {url_info['site']}/{url_info['language']}: {url_info['url']}")

        # Parallel scrape filtered URLs
        pages = list(parallel_scrape_subject(
            cycle=cycle,
            subject=subject,
            registry=registry,
            language=language,
            max_workers=2,
            max_pages_per_url=50,
            max_depth=3,
        ))

        context.log.info(f"Scraped {len(pages)} pages from {len(urls)} URLs")

        # Ensure we have valid pages before passing to DLT pipeline
        valid_pages = [p for p in pages if p.get("status") not in ("error", "no_api_key", "firecrawl_not_installed")]
        if not valid_pages:
            raise RuntimeError(
                f"Firecrawl failed to scrape any valid pages for {cycle}/{subject}/{language}. "
                f"Check API limits or error logs. URLs attempted: {[u['url'] for u in urls]}"
            )

        # Choose destination based on environment
        # Set USE_DUCKLAKE=false to use plain DuckDB (when lakehouse not running)
        use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"

        if use_ducklake:
            destination = get_dlt_destination()
            context.log.info(f"Using DuckLake destination (DLT_ENVIRONMENT={os.environ.get('DLT_ENVIRONMENT', 'local')})")
        else:
            destination = get_duckdb_fallback_destination(
                str(DLT_PIPELINES_DIR / DLT_PIPELINE_NAME / f"{DLT_DATASET_NAME}.duckdb")
            )
            context.log.info("Using DuckDB fallback destination")

        # Create unified DLT pipeline with appropriate destination
        dlt_pipeline = dlt.pipeline(
            pipeline_name=DLT_PIPELINE_NAME,
            destination=destination,
            dataset_name=DLT_DATASET_NAME,
            pipelines_dir=str(DLT_PIPELINES_DIR),
        )

        # Prepare data for loading
        def generate_pages():
            for page in pages:
                # Skip error pages
                if page.get("status") in ("error", "no_api_key", "firecrawl_not_installed"):
                    continue
                yield page

        # Run DLT pipeline through serial executor for DuckDB safety
        load_info = safe_dlt_run(
            dlt_pipeline,
            generate_pages(),
            table_name="curriculum_pages",
            write_disposition="merge",
            primary_key=["content_hash"],  # Dedupe by content_hash
        )

        # Calculate rows loaded
        rows_loaded = 0
        for pkg in load_info.load_packages:
            if hasattr(pkg, 'jobs'):
                for job in pkg.jobs.values() if isinstance(pkg.jobs, dict) else pkg.jobs:
                    if hasattr(job, 'metrics') and job.metrics:
                        rows_loaded += getattr(job.metrics, 'rows_count', 0) or 0

        context.log.info(f"Loaded {rows_loaded} rows for {cycle}/{subject}/{language}")

        return dg.MaterializeResult(
            metadata={
                "cycle": cycle,
                "subject": subject,
                "language": language,
                "urls_scraped": len(urls),
                "pages_found": len(pages),
                "rows_loaded": rows_loaded,
                "load_id": str(load_info.loads_ids[0]) if load_info.loads_ids else "unknown",
                "duckdb_path": str(DLT_PIPELINES_DIR / DLT_PIPELINE_NAME / f"{DLT_DATASET_NAME}.duckdb"),
            }
        )

    return _cycle_asset


def create_short_course_asset():
    """
    Create a curriculum asset for Junior Cycle short courses.

    Asset key: ireland/curriculum/short_courses
    Partition: course|language (e.g., "coding|en")

    Short courses are only available on curriculumonline.ie (not NCCA).
    """

    @dg.asset(
        key=["ireland", "curriculum", "short_courses"],
        group_name="curriculum",
        compute_kind="dlt",
        description="Ireland Junior Cycle Short Courses",
        partitions_def=SHORT_COURSE_PARTITION,
        retry_policy=dg.RetryPolicy(
            max_retries=3,
            delay=30,
            backoff=dg.Backoff.EXPONENTIAL,
        ),
        tags={
            "cycle": "junior_cycle",
            "type": "short_course",
            "pipeline": "ireland_curriculum",
        },
        op_tags={"dagster/concurrency_key": "curriculum_short_courses"},
    )
    def _short_course_asset(context) -> dg.MaterializeResult:
        """Ingest short course curriculum data."""
        os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")

        from oideachais.data_platform.dlt_sources.ireland.curriculum_source import (
            _scrape_single_url,
        )

        # Extract partition keys
        partition_keys = context.partition_key.keys_by_dimension
        course = partition_keys["course"]
        language = partition_keys["language"]

        context.log.info(f"Ingesting short course: {course}/{language}")

        # Build short course URLs (curriculumonline only)
        # Short courses are at /junior-cycle/short-courses/{slug}/
        lang_prefix = "/ga-ie" if language == "ga" else ""
        urls = [
            {
                "site": "curriculumonline",
                "language": language,
                "url": f"https://www.curriculumonline.ie{lang_prefix}/junior-cycle/short-courses/{course}/",
            }
        ]

        for url_info in urls:
            context.log.info(f"  {url_info['site']}/{url_info['language']}: {url_info['url']}")

        # Scrape short course pages
        pages = []
        for url_info in urls:
            try:
                result = _scrape_single_url(
                    url_config=url_info,
                    cycle="junior_cycle",
                    subject=course,  # Use course as subject for short courses
                    max_pages=50,
                    max_depth=3,
                )
                if result:
                    for page in result:
                        page["is_short_course"] = True
                        page["course"] = course
                        pages.append(page)
            except Exception as e:
                context.log.warning(f"Failed to scrape {url_info['url']}: {e}")

        context.log.info(f"Scraped {len(pages)} pages for short course {course}")

        # Choose destination
        use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"

        if use_ducklake:
            destination = get_dlt_destination()
        else:
            destination = get_duckdb_fallback_destination(
                str(DLT_PIPELINES_DIR / DLT_PIPELINE_NAME / f"{DLT_DATASET_NAME}.duckdb")
            )

        # Create DLT pipeline
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

        # Run DLT pipeline
        load_info = safe_dlt_run(
            dlt_pipeline,
            generate_pages(),
            table_name="curriculum_pages",
            write_disposition="merge",
            primary_key=["content_hash"],
        )

        # Calculate rows loaded
        rows_loaded = 0
        for pkg in load_info.load_packages:
            if hasattr(pkg, 'jobs'):
                for job in pkg.jobs.values() if isinstance(pkg.jobs, dict) else pkg.jobs:
                    if hasattr(job, 'metrics') and job.metrics:
                        rows_loaded += getattr(job.metrics, 'rows_count', 0) or 0

        context.log.info(f"Loaded {rows_loaded} rows for short course {course}/{language}")

        return dg.MaterializeResult(
            metadata={
                "cycle": "junior_cycle",
                "course": course,
                "language": language,
                "is_short_course": True,
                "urls_scraped": len(urls),
                "pages_found": len(pages),
                "rows_loaded": rows_loaded,
                "load_id": str(load_info.loads_ids[0]) if load_info.loads_ids else "unknown",
            }
        )

    return _short_course_asset


# ============================================================================
# Asset Generation
# ============================================================================

def create_all_curriculum_assets() -> list:
    """Create all curriculum assets (one per cycle + short courses)."""
    assets = []

    # Create cycle assets
    for cycle in CYCLES:
        try:
            asset = create_cycle_asset(cycle)
            assets.append(asset)
            logger.debug("created_cycle_asset", cycle=cycle)
        except Exception as e:
            logger.warning("failed_to_create_cycle_asset", cycle=cycle, error=str(e))

    # Create short course asset
    try:
        short_course_asset = create_short_course_asset()
        assets.append(short_course_asset)
        logger.debug("created_short_course_asset")
    except Exception as e:
        logger.warning("failed_to_create_short_course_asset", error=str(e))

    logger.info("created_all_curriculum_assets", count=len(assets))
    return assets


# ============================================================================
# Default Export
# ============================================================================

curriculum_dlt_assets = create_all_curriculum_assets()

__all__ = [
    "curriculum_dlt_assets",
    "create_cycle_asset",
    "create_short_course_asset",
    "create_all_curriculum_assets",
    "CYCLE_PARTITIONS",
    "SHORT_COURSE_PARTITION",
    "CYCLES",
    "CYCLE_SUBJECTS",
    "SHORT_COURSES",
    "DLT_PIPELINE_NAME",
    "DLT_DATASET_NAME",
    "DLT_PIPELINES_DIR",
]
