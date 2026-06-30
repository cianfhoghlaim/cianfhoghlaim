"""
Ireland Exam Materials Pipeline - MultiPartition assets for SEC examinations.

Creates 3 Dagster assets (one per exam cycle) with
MultiPartition(subject, material_type). Years are a Config parameter,
NOT a partition dimension, to avoid ~1664+ empty partitions.

Asset Structure:
    ireland/exam_materials/leaving_certificate        <- MultiPartition(subject, material_type)
    ireland/exam_materials/junior_cycle                <- MultiPartition(subject, material_type)
    ireland/exam_materials/leaving_certificate_applied <- MultiPartition(subject, material_type)

Partition Keys: "mathematics|exam_papers", "biology|marking_schemes", etc.

Environment:
    DLT_ENVIRONMENT=local (default): Garage S3 + local PostgreSQL
    DLT_ENVIRONMENT=production: Cloudflare R2 + PlanetScale
    USE_LOCAL_SCRAPES=true: Skip browser automation (testing/offline)

Usage:
    from .import exam_materials_assets

    defs = Definitions(assets=exam_materials_assets)
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

from cianfhoghlaim.dlt.british_isles.ireland.education._examinations_helpers import (
    ALL_JC_SUBJECTS,
    ALL_LCA_SUBJECTS,
    ALL_LC_SUBJECTS,
)
from dlt_utils import (
    get_dlt_destination,
    get_duckdb_fallback_destination,
    safe_dlt_run,
)

logger = structlog.get_logger(__name__)


# ============================================================================
# Configuration
# ============================================================================

EXAM_CYCLES = ["leaving_certificate", "junior_cycle", "leaving_certificate_applied"]

EXAM_SUBJECTS = {
    "leaving_certificate": ALL_LC_SUBJECTS,
    "junior_cycle": ALL_JC_SUBJECTS,
    "leaving_certificate_applied": ALL_LCA_SUBJECTS,
}

MATERIAL_TYPES = ["exam_papers", "marking_schemes"]

DLT_PIPELINE_NAME = "exam_materials"
DLT_DATASET_NAME = "examinations"
DLT_SCHEMA_NAME = "ireland_examinations"
DLT_PIPELINES_DIR = Path(__file__).parent.parent.parent.parent / ".dlt"


# ============================================================================
# MultiPartition Definitions
# ============================================================================

def create_exam_partition(cycle: str) -> MultiPartitionsDefinition:
    """
    Create a MultiPartition for an exam cycle: subject x material_type.

    Args:
        cycle: Exam cycle (leaving_certificate, junior_cycle, leaving_certificate_applied)

    Returns:
        MultiPartitionsDefinition with subject and material_type dimensions
    """
    subjects = EXAM_SUBJECTS.get(cycle, ALL_LC_SUBJECTS)
    return MultiPartitionsDefinition({
        "subject": StaticPartitionsDefinition(subjects),
        "material_type": StaticPartitionsDefinition(MATERIAL_TYPES),
    })


EXAM_PARTITIONS = {
    cycle: create_exam_partition(cycle)
    for cycle in EXAM_CYCLES
}


# ============================================================================
# Asset Factory
# ============================================================================

class ExamMaterialsConfig(dg.Config):
    """Configuration for exam materials asset materialization.

    Years are a run config parameter, NOT a partition dimension,
    to avoid creating ~1664+ sparsely-populated partition keys.
    """
    years: list[int] = [2020, 2021, 2022, 2023, 2024]


def create_exam_asset(cycle: str):
    """
    Create an exam materials asset for a cycle with
    MultiPartition(subject, material_type).

    Asset key: ireland/exam_materials/{cycle}
    Partition: subject|material_type (e.g., "mathematics|exam_papers")

    All assets write to DuckLake for centralized storage.
    """
    display_name = cycle.replace("_", " ").title()
    asset_key = ["ireland", "exam_materials", cycle]

    @dg.asset(
        key=asset_key,
        group_name="exam_materials",
        compute_kind="dlt",
        description=f"Ireland {display_name} Exam Materials",
        partitions_def=EXAM_PARTITIONS[cycle],
        retry_policy=dg.RetryPolicy(
            max_retries=3,
            delay=30,
            backoff=dg.Backoff.EXPONENTIAL,
        ),
        tags={
            "cycle": cycle,
            "pipeline": "ireland_examinations",
        },
        op_tags={"dagster/concurrency_key": f"examinations_{cycle}"},
    )
    def _exam_asset(context: dg.AssetExecutionContext, config: ExamMaterialsConfig) -> dg.MaterializeResult:
        """Ingest exam materials for this cycle's subject/material_type partition."""
        os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")

        sys_path_insert = str(Path(__file__).parent.parent.parent.parent.parent)
        import sys
        if sys_path_insert not in sys.path:
            sys.path.insert(0, sys_path_insert)

        from cianfhoghlaim.dlt.british_isles.ireland.education.sec_examinations_browser import sec_examinations_browser_source

        # Extract partition keys
        partition_key_str = context.partition_key
        parts = partition_key_str.split("|")
        material_type = parts[0]
        subject = parts[1] if len(parts) > 1 else ""

        context.log.info(
            f"Ingesting: {cycle}/{subject}/{material_type} for years {config.years}"
        )

        # Map Dagster material_type partition to SEC dropdown values
        sec_material_types = [material_type]

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

        # Create DLT pipeline
        dlt_pipeline = dlt.pipeline(
            pipeline_name=DLT_PIPELINE_NAME,
            destination=destination,
            dataset_name=DLT_DATASET_NAME,
            pipelines_dir=str(DLT_PIPELINES_DIR),
        )

        source = sec_examinations_browser_source(
            subjects=[subject],
            years=config.years,
            level=cycle,
            language="en",
            material_types=sec_material_types,
        )

        load_info = safe_dlt_run(
            dlt_pipeline,
            source,
        )

        # Calculate rows loaded
        rows_loaded = 0
        for pkg in load_info.load_packages:
            if hasattr(pkg, 'jobs'):
                for job in pkg.jobs.values() if isinstance(pkg.jobs, dict) else pkg.jobs:
                    if hasattr(job, 'metrics') and job.metrics:
                        rows_loaded += getattr(job.metrics, 'rows_count', 0) or 0

        context.log.info(f"Loaded {rows_loaded} rows for {cycle}/{subject}/{material_type}")

        return dg.MaterializeResult(
            metadata={
                "cycle": cycle,
                "subject": subject,
                "material_type": material_type,
                "years": config.years,
                "rows_loaded": rows_loaded,
                "load_id": str(load_info.loads_ids[0]) if load_info.loads_ids else "unknown",
            }
        )

    return _exam_asset


# ============================================================================
# Asset Generation
# ============================================================================

def create_all_exam_materials_assets() -> list:
    """Create all exam materials assets (one per cycle)."""
    assets = []

    for cycle in EXAM_CYCLES:
        try:
            asset = create_exam_asset(cycle)
            assets.append(asset)
            logger.debug("created_exam_asset", cycle=cycle)
        except Exception as e:
            logger.warning("failed_to_create_exam_asset", cycle=cycle, error=str(e))

    logger.info("created_all_exam_materials_assets", count=len(assets))
    return assets


# ============================================================================
# Default Export
# ============================================================================

exam_materials_assets = create_all_exam_materials_assets()

__all__ = [
    "exam_materials_assets",
    "create_exam_asset",
    "create_all_exam_materials_assets",
    "EXAM_PARTITIONS",
    "EXAM_SUBJECTS",
    "EXAM_CYCLES",
    "MATERIAL_TYPES",
    "ExamMaterialsConfig",
    "DLT_PIPELINE_NAME",
    "DLT_DATASET_NAME",
    "DLT_SCHEMA_NAME",
    "DLT_PIPELINES_DIR",
]