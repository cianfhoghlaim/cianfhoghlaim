"""
Environment-aware DuckLake destination factory for oideachais.

Solves DuckDB concurrency issues by using DuckLake (S3 + PostgreSQL catalog).
Multiple Dagster partitions can write simultaneously because data is stored as
Parquet files in S3, with transaction coordination via PostgreSQL MVCC.

Usage:
    from dlt_utils import get_dlt_destination, create_pipeline

    pipeline = create_pipeline(
        pipeline_name="curriculum",
        dataset_name="curriculum",
    )
"""

from __future__ import annotations

import os
from typing import Any

import dlt
from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials

NAMESPACE = "oideachais"


def _get_local_ducklake_destination() -> Any:
    """Build local DuckLake destination using Garage S3 + PostgreSQL."""
    # PostgreSQL catalog config
    postgres_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "localhost")
    postgres_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5433")
    postgres_db = os.environ.get("DUCKLAKE_POSTGRES_DB", f"ducklake_{NAMESPACE}")
    postgres_user = os.environ.get("DUCKLAKE_POSTGRES_USER", "lakekeeper")
    postgres_pass = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD", "devpassword")

    catalog_uri = f"postgresql://{postgres_user}:{postgres_pass}@{postgres_host}:{postgres_port}/{postgres_db}"

    # S3/Garage storage config
    bucket_url = f"s3://ducklake/{NAMESPACE}/"
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:3900")
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

    # Build storage credentials dict for filesystem-style config
    storage_config = {
        "bucket_url": bucket_url,
        "credentials": {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "endpoint_url": endpoint_url,
        },
        # Force path-style URLs for S3-compatible storage (Garage, MinIO)
        # s3fs uses virtual-host style by default which requires DNS for bucket subdomains
        # config_kwargs is a top-level field in FilesystemDestinationClientConfiguration
        # that gets passed to botocore.Config
        "config_kwargs": {"s3": {"addressing_style": "path"}},
    }

    # Use DuckLakeCredentials with proper catalog + storage config
    credentials = DuckLakeCredentials(
        ducklake_name=NAMESPACE,
        catalog=catalog_uri,
        storage=storage_config,
    )

    # Extract host:port from endpoint URL for DuckDB S3 settings
    # http://localhost:3900 -> localhost:3900
    s3_endpoint = endpoint_url.replace("http://", "").replace("https://", "")

    # DuckDB S3 configuration for Garage/MinIO (path-style URLs)
    global_config = {
        "s3_endpoint": s3_endpoint,
        "s3_use_ssl": "false",
        "s3_url_style": "path",
        "s3_access_key_id": aws_access_key_id,
        "s3_secret_access_key": aws_secret_access_key,
        "s3_region": os.environ.get("AWS_REGION", "garage"),
    }

    return dlt.destinations.ducklake(credentials=credentials, global_config=global_config)


def _get_production_ducklake_destination() -> Any:
    """Build production DuckLake destination using Cloudflare R2 + PostgreSQL."""
    # PostgreSQL catalog config
    pg_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "eu-west-3.pg.psdb.cloud")
    pg_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5432")
    pg_user = os.environ.get("DUCKLAKE_POSTGRES_USER")
    pg_pass = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD")
    pg_db = os.environ.get("DUCKLAKE_POSTGRES_DB", f"ducklake_{NAMESPACE}")

    catalog_uri = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}?sslmode=require"

    # R2 storage config
    r2_bucket = os.environ.get("R2_DUCKLAKE_BUCKET", "ducklake")
    bucket_url = f"s3://{r2_bucket}/{NAMESPACE}/"

    storage_config = {
        "bucket_url": bucket_url,
        "credentials": {
            "aws_access_key_id": os.environ.get("R2_ACCESS_KEY_ID", ""),
            "aws_secret_access_key": os.environ.get("R2_SECRET_ACCESS_KEY", ""),
            "endpoint_url": os.environ.get("R2_ENDPOINT_URL", ""),
        },
    }

    credentials = DuckLakeCredentials(
        ducklake_name=NAMESPACE,
        catalog=catalog_uri,
        storage=storage_config,
    )

    return dlt.destinations.ducklake(credentials=credentials)


def get_dlt_destination(
    use_ducklake: bool | None = None,
) -> Any:
    """
    Get DLT destination for oideachais pipelines.

    Environment Variables:
        DLT_ENVIRONMENT: "local" (default) or "production"
        USE_DUCKLAKE: "true" (default) or "false"

    Local:
        - Data: Garage S3 at s3://ducklake/oideachais/
        - Metadata: PostgreSQL at localhost:5433

    Production:
        - Data: Cloudflare R2
        - Metadata: PlanetScale PostgreSQL

    Args:
        use_ducklake: Override to force DuckLake or DuckDB fallback

    Returns:
        Configured destination for DLT pipeline
    """
    if use_ducklake is None:
        use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"

    if not use_ducklake:
        return get_duckdb_fallback_destination()

    env = os.environ.get("DLT_ENVIRONMENT", "local").lower()

    if env == "production":
        return _get_production_ducklake_destination()
    else:
        return _get_local_ducklake_destination()


def get_duckdb_fallback_destination(
    database_path: str = "./data/oideachais.duckdb",
) -> Any:
    """
    Get plain DuckDB destination as fallback when DuckLake is not available.

    Use this for quick testing or when the lakehouse infrastructure isn't running.

    Args:
        database_path: Path to local DuckDB file

    Returns:
        DuckDB destination for DLT pipeline
    """
    return dlt.destinations.duckdb(credentials=database_path)


def create_pipeline(
    pipeline_name: str = "curriculum",
    dataset_name: str = "curriculum",
    use_ducklake: bool = True,
    **kwargs: Any,
) -> dlt.Pipeline:
    """
    Create a DLT pipeline with appropriate destination.

    Args:
        pipeline_name: Name of the pipeline (for state tracking)
        dataset_name: Dataset/schema name in destination
        use_ducklake: If True, use DuckLake; if False, use plain DuckDB
        **kwargs: Additional arguments passed to dlt.pipeline()

    Returns:
        Configured DLT pipeline
    """
    destination = get_dlt_destination() if use_ducklake else get_duckdb_fallback_destination()

    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=destination,
        dataset_name=dataset_name,
        **kwargs,
    )
