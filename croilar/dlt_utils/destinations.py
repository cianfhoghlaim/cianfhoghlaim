"""
Environment-aware DuckLake destination factory for croilar.

Solves DuckDB concurrency issues by using DuckLake (S3 + PostgreSQL catalog).
Multiple Dagster partitions can write simultaneously because data is stored as
Parquet files in S3, with transaction coordination via PostgreSQL MVCC.

Usage:
    from dlt_utils import get_dlt_destination, create_pipeline

    pipeline = create_pipeline(
        pipeline_name="spotify_croilar",
        dataset_name="spotify_data",
    )
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import dlt

NAMESPACE = "croilar"


@dataclass
class DuckLakeConfig:
    """Configuration for DuckLake destination."""

    data_dir: str
    catalog_uri: str
    staging_dir: str | None = None

    def to_credentials(self) -> dict[str, Any]:
        """Convert to DLT credentials format."""
        creds = {
            "data_dir": self.data_dir,
            "catalog_uri": self.catalog_uri,
        }
        if self.staging_dir:
            creds["staging_dir"] = self.staging_dir
        return creds


def _get_local_config() -> DuckLakeConfig:
    """Build local DuckLake config using Garage S3 + PostgreSQL."""
    postgres_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "localhost")
    postgres_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5432")
    postgres_db = os.environ.get("DUCKLAKE_POSTGRES_DB", f"ducklake_{NAMESPACE}")
    postgres_user = os.environ.get("DUCKLAKE_POSTGRES_USER", "lakekeeper")
    postgres_pass = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD", "devpassword")

    return DuckLakeConfig(
        data_dir=f"s3://ducklake/{NAMESPACE}/",
        catalog_uri=f"postgresql://{postgres_user}:{postgres_pass}@{postgres_host}:{postgres_port}/{postgres_db}",
    )


def _get_production_config() -> DuckLakeConfig:
    """Build production DuckLake config using Cloudflare R2 + PlanetScale PostgreSQL."""
    r2_bucket = os.environ.get("R2_DUCKLAKE_BUCKET", "ducklake")

    # PlanetScale PostgreSQL connection
    pg_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "eu-west-3.pg.psdb.cloud")
    pg_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5432")
    pg_user = os.environ.get("DUCKLAKE_POSTGRES_USER")
    pg_pass = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD")
    pg_db = os.environ.get("DUCKLAKE_POSTGRES_DB", f"ducklake_{NAMESPACE}")

    return DuckLakeConfig(
        data_dir=f"s3://{r2_bucket}/{NAMESPACE}/",
        catalog_uri=f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}?sslmode=require",
    )


def get_dlt_destination(
    use_ducklake: bool | None = None,
    local_only: bool = False,
) -> Any:
    """
    Get DLT destination for croilar pipelines.

    Environment Variables:
        DLT_ENVIRONMENT: "local" (default) or "production"
        USE_DUCKLAKE: "true" (default) or "false"

    Local:
        - Data: Garage S3 at s3://ducklake/croilar/
        - Metadata: PostgreSQL at localhost:5432

    Production:
        - Data: Cloudflare R2
        - Metadata: PlanetScale PostgreSQL

    Args:
        use_ducklake: Override to force DuckLake or DuckDB fallback
        local_only: If True, return a plain DuckDB destination under
            `./data/local/`. Never writes to R2. Used for `StreamSource`
            entries with `local_only=True` (e.g. the author CV folder).

    Returns:
        Configured destination for DLT pipeline
    """
    if local_only:
        return get_duckdb_fallback(base_path="./data/local", prefix="local")

    if use_ducklake is None:
        use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"

    if not use_ducklake:
        return get_duckdb_fallback()

    env = os.environ.get("DLT_ENVIRONMENT", "local").lower()

    if env == "production":
        config = _get_production_config()
    else:
        config = _get_local_config()

    return dlt.destinations.ducklake(credentials=config.to_credentials())


def get_duckdb_fallback(
    base_path: str = "./data",
    prefix: str = NAMESPACE,
) -> Any:
    """
    Get plain DuckDB destination as fallback.

    WARNING: This destination has single-writer lock - avoid parallel writes!

    Args:
        base_path: Directory for DuckDB files
        prefix: Filename prefix for the DuckDB file (e.g. "local" for
            local-only streams, "croilar" for the default).

    Returns:
        DuckDB destination for DLT pipeline
    """
    db_path = os.path.join(base_path, f"{prefix}.duckdb")
    return dlt.destinations.duckdb(credentials=db_path)


def create_pipeline(
    pipeline_name: str,
    dataset_name: str,
    use_ducklake: bool | None = None,
    **kwargs: Any,
) -> dlt.Pipeline:
    """
    Create a DLT pipeline with appropriate destination.

    Args:
        pipeline_name: Name of the pipeline (for state tracking)
        dataset_name: Dataset/schema name in destination
        use_ducklake: If True, use DuckLake; if False/None, use env default
        **kwargs: Additional arguments passed to dlt.pipeline()

    Returns:
        Configured DLT pipeline
    """
    destination = get_dlt_destination(use_ducklake=use_ducklake)

    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=destination,
        dataset_name=dataset_name,
        **kwargs,
    )
