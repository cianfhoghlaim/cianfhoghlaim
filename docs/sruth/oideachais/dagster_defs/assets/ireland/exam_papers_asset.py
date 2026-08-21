"""
SEC Exam Papers Dagster Asset with MultiPartition(subject, year).

Creates 2 Dagster assets (one per cycle) with MultiPartition(subject, year).
All assets write to DuckLake lakehouse (local or production via DLT_ENVIRONMENT).

Asset Structure:
    ireland/examinations/leaving_certificate ← MultiPartition(subject, year)
    ireland/examinations/junior_cycle       ← MultiPartition(subject, year)

Partition Keys: "mathematics|2024", "english|2024", etc.

Environment:
    DLT_ENVIRONMENT=local (default): Garage S3 + local PostgreSQL
    DLT_ENVIRONMENT=production: Cloudflare R2 + PlanetScale

Usage:
    from dagster_defs.assets.ireland import exam_papers_dlt_assets

    defs = Definitions(assets=exam_papers_dlt_assets)
"""

import os
from pathlib import Path

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

logger = __import__("structlog").get_logger(__name__)


# ============================================================================
# Configuration
# ============================================================================

# Leaving Certificate subjects (33 subjects from SEC)
LEAVING_CERT_SUBJECTS = [
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
]

# Junior Cycle subjects (18 subjects from SEC)
JUNIOR_CYCLE_SUBJECTS = [
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
]

# Available years for scraping (expandable)
YEARS_AVAILABLE = [str(y) for y in range(2020, 2025)]

# Unified DLT pipeline configuration
DLT_PIPELINE_NAME = "sec_examinations"
DLT_DATASET_NAME = "exam_materials"
DLT_PIPELINES_DIR = Path(__file__).parent.parent.parent.parent.parent / ".dlt"


# ============================================================================
# MultiPartition Definitions
# ============================================================================


def create_exam_partition(subjects: list[str]) -> MultiPartitionsDefinition:
    """
    Create a MultiPartition for exam materials: subject × year.

    Args:
        subjects: List of subject slugs

    Returns:
        MultiPartitionsDefinition with subject and year dimensions
    """
    return MultiPartitionsDefinition(
        {
            "subject": StaticPartitionsDefinition(subjects),
            "year": StaticPartitionsDefinition(YEARS_AVAILABLE),
        }
    )


# Pre-create partition definitions for each cycle
LC_PARTITIONS = create_exam_partition(LEAVING_CERT_SUBJECTS)
JC_PARTITIONS = create_exam_partition(JUNIOR_CYCLE_SUBJECTS)


# ============================================================================
# Asset Factory
# ============================================================================


def create_exam_asset(
    cycle: str,
    subjects: list[str],
    partitions_def: MultiPartitionsDefinition,
):
    """
    Create an exam materials asset for a cycle with MultiPartition(subject, year).

    Asset key: ireland/examinations/{cycle}
    Partition: subject|year (e.g., "mathematics|2024")

    All assets write to DuckLake for centralized storage.

    Args:
        cycle: Education cycle (leaving_certificate, junior_cycle)
        subjects: List of subject slugs for this cycle
        partitions_def: MultiPartition definition for this cycle
    """
    display_name = cycle.replace("_", " ").title()
    asset_key = ["ireland", "examinations", cycle]

    @dg.asset(
        key=asset_key,
        group_name="examinations",
        compute_kind="browser",
        description=f"SEC {display_name} Exam Materials",
        partitions_def=partitions_def,
        retry_policy=dg.RetryPolicy(
            max_retries=3,
            delay=30,
            backoff=dg.Backoff.EXPONENTIAL,
        ),
        tags={
            "cycle": cycle,
            "pipeline": "sec_examinations",
            "scrape_target": "examinations.ie",
        },
        # Allow parallel execution across partitions but limit concurrent scrapes
        op_tags={"dagster/concurrency_key": f"sec_examinations_{cycle}"},
    )
    def _exam_asset(context) -> dg.MaterializeResult:
        """Ingest SEC exam materials for this partition's subject/year combination."""
        # Disable DLT plugin scanning to avoid metadata bug
        os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")

        # Extract partition keys
        partition_keys = context.partition_key.keys_by_dimension
        subject = partition_keys["subject"]
        year = int(partition_keys["year"])

        context.log.info(f"Scraping SEC exam materials: {cycle}/{subject}/{year}")

        # Import scraper - supports both Stagehand and CDP based on config
        scraper_method = os.getenv("SEC_SCRAPER_METHOD", "stagehand").lower()

        if scraper_method == "cdp":
            from sruth.browser.sruth_browser.tools.examinations_cdp import (
                scrape_exam_materials_cdp_sync,
            )

            scrape_func = scrape_exam_materials_cdp_sync
            context.log.info(f"Using CDP scraper (CSS selectors)")
        else:
            from sruth.browser.sruth_browser.tools.examinations_scraper import (
                scrape_exam_materials_sync,
            )

            scrape_func = scrape_exam_materials_sync
            context.log.info(f"Using Stagehand scraper (AI)")

        # Scrape exam materials
        materials = scrape_func(
            subject=subject,
            years=[year],
            level=cycle,
            language="en",  # TODO: Add language to partition
        )

        context.log.info(f"Found {len(materials)} materials")

        # Convert to dicts with metadata
        from datetime import datetime

        def generate_materials():
            for material in materials:
                data = {
                    "subject": material.subject,
                    "year": material.year,
                    "level": material.level,
                    "material_type": material.material_type,
                    "exam_level": material.exam_level,
                    "paper_number": material.paper_number,
                    "language": material.language,
                    "title": material.title,
                    "pdf_url": material.pdf_url,
                    "content_hash": material.content_hash,
                    "scraped_at": datetime.utcnow().isoformat(),
                    "scraper_method": scraper_method,
                    "source_url": "https://www.examinations.ie/exammaterialarchive/",
                }
                yield data

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

        # Create unified DLT pipeline with appropriate destination
        dlt_pipeline = (
            dg.build_op_context().instance if hasattr(dg.build_op_context(), "instance") else None
        )

        import dlt

        dlt_pipeline = dlt.pipeline(
            pipeline_name=DLT_PIPELINE_NAME,
            destination=destination,
            dataset_name=DLT_DATASET_NAME,
            pipelines_dir=str(DLT_PIPELINES_DIR),
        )

        # Run DLT pipeline through serial executor for DuckDB safety
        load_info = safe_dlt_run(
            dlt_pipeline,
            generate_materials(),
            table_name="exam_materials",
            write_disposition="merge",
            primary_key=["pdf_url"],  # Dedupe by PDF URL
        )

        # Calculate rows loaded
        rows_loaded = 0
        for pkg in load_info.load_packages:
            if hasattr(pkg, "jobs"):
                for job in pkg.jobs.values() if isinstance(pkg.jobs, dict) else pkg.jobs:
                    if hasattr(job, "metrics") and job.metrics:
                        rows_loaded += getattr(job.metrics, "rows_count", 0) or 0

        context.log.info(f"Loaded {rows_loaded} rows for {cycle}/{subject}/{year}")

        return dg.MaterializeResult(
            metadata={
                "cycle": cycle,
                "subject": subject,
                "year": year,
                "materials_found": len(materials),
                "rows_loaded": rows_loaded,
                "scraper_method": scraper_method,
                "load_id": str(load_info.loads_ids[0]) if load_info.loads_ids else "unknown",
                "duckdb_path": str(
                    DLT_PIPELINES_DIR / DLT_PIPELINE_NAME / f"{DLT_DATASET_NAME}.duckdb"
                ),
            }
        )

    return _exam_asset


# ============================================================================
# Asset Generation
# ============================================================================


def _safe_log(level: str, event: str, **kwargs) -> None:
    """Safely log without raising BrokenPipeError in Dagster daemon context."""
    try:
        getattr(logger, level)(event, **kwargs)
    except (BrokenPipeError, OSError):
        pass


def create_all_exam_assets() -> list:
    """Create all SEC exam assets (one per cycle)."""
    assets = []

    # Create Leaving Certificate asset
    try:
        lc_asset = create_exam_asset(
            cycle="leaving_certificate",
            subjects=LEAVING_CERT_SUBJECTS,
            partitions_def=LC_PARTITIONS,
        )
        assets.append(lc_asset)
        _safe_log("debug", "created_lc_exam_asset")
    except Exception as e:
        _safe_log("warning", "failed_to_create_lc_exam_asset", error=str(e))

    # Create Junior Cycle asset
    try:
        jc_asset = create_exam_asset(
            cycle="junior_cycle",
            subjects=JUNIOR_CYCLE_SUBJECTS,
            partitions_def=JC_PARTITIONS,
        )
        assets.append(jc_asset)
        _safe_log("debug", "created_jc_exam_asset")
    except Exception as e:
        _safe_log("warning", "failed_to_create_jc_exam_asset", error=str(e))

    _safe_log("info", "created_all_exam_assets", count=len(assets))
    return assets


# ============================================================================
# Default Export
# ============================================================================

exam_papers_dlt_assets = create_all_exam_assets()

__all__ = [
    "exam_papers_dlt_assets",
    "create_exam_asset",
    "create_all_exam_assets",
    "LC_PARTITIONS",
    "JC_PARTITIONS",
    "LEAVING_CERT_SUBJECTS",
    "JUNIOR_CYCLE_SUBJECTS",
    "YEARS_AVAILABLE",
    "DLT_PIPELINE_NAME",
    "DLT_DATASET_NAME",
    "DLT_PIPELINES_DIR",
]
