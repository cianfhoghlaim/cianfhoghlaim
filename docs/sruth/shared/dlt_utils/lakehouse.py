"""
Shared DuckLake destination factory for all sruth projects.

Solves DuckDB concurrency issues by using DuckLake (S3 + PostgreSQL catalog).
Multiple Dagster partitions can write simultaneously because data is stored as
Parquet files in S3, with transaction coordination via PostgreSQL MVCC.

Usage:
    from sruth.shared.dlt_utils import get_lakehouse_destination, create_lakehouse_pipeline

    # Direct destination
    destination = get_lakehouse_destination("crypteolas")

    # Full pipeline
    pipeline = create_lakehouse_pipeline(
        namespace="oideachais",
        pipeline_name="curriculum",
        dataset_name="curriculum",
    )
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import dlt
from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials


@dataclass
class DuckLakeConfig:
    """Configuration for DuckLake destination."""

    namespace: str
    catalog_uri: str
    bucket_url: str
    endpoint_url: str | None = None
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "garage"
    use_ssl: bool = False

    def to_credentials(self) -> DuckLakeCredentials:
        """Convert to DLT DuckLakeCredentials format."""
        storage_config: dict[str, Any] = {
            "bucket_url": self.bucket_url,
        }

        if self.endpoint_url:
            storage_config["credentials"] = {
                "aws_access_key_id": self.aws_access_key_id,
                "aws_secret_access_key": self.aws_secret_access_key,
                "endpoint_url": self.endpoint_url,
            }

        return DuckLakeCredentials(
            ducklake_name=self.namespace,
            catalog=self.catalog_uri,
            storage=storage_config,
        )

    def to_global_config(self) -> dict[str, str]:
        """Get DuckDB S3 global config for Garage/MinIO compatibility."""
        if not self.endpoint_url:
            return {}

        # Extract host:port from endpoint URL
        # http://localhost:3900 -> localhost:3900
        s3_endpoint = self.endpoint_url.replace("http://", "").replace("https://", "")

        return {
            "s3_endpoint": s3_endpoint,
            "s3_use_ssl": "true" if self.use_ssl else "false",
            "s3_url_style": "path",
            "s3_access_key_id": self.aws_access_key_id,
            "s3_secret_access_key": self.aws_secret_access_key,
            "s3_region": self.aws_region,
        }


def _get_local_config(namespace: str) -> DuckLakeConfig:
    """Build local DuckLake config using Garage S3 + PostgreSQL."""
    postgres_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "localhost")
    postgres_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5433")
    postgres_db = os.environ.get("DUCKLAKE_POSTGRES_DB", f"ducklake_{namespace}")
    postgres_user = os.environ.get("DUCKLAKE_POSTGRES_USER", "lakekeeper")
    postgres_pass = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD", "devpassword")

    catalog_uri = f"postgresql://{postgres_user}:{postgres_pass}@{postgres_host}:{postgres_port}/{postgres_db}"

    endpoint_url = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:3900")
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    aws_region = os.environ.get("AWS_REGION", "garage")

    return DuckLakeConfig(
        namespace=namespace,
        catalog_uri=catalog_uri,
        bucket_url=f"s3://ducklake/{namespace}/",
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_region=aws_region,
        use_ssl=endpoint_url.startswith("https://"),
    )


def _get_production_config(namespace: str) -> DuckLakeConfig:
    """Build production DuckLake config using Cloudflare R2 + PostgreSQL."""
    pg_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "eu-west-3.pg.psdb.cloud")
    pg_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5432")
    pg_user = os.environ.get("DUCKLAKE_POSTGRES_USER", "")
    pg_pass = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD", "")
    pg_db = os.environ.get("DUCKLAKE_POSTGRES_DB", f"ducklake_{namespace}")

    catalog_uri = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}?sslmode=require"

    r2_bucket = os.environ.get("R2_DUCKLAKE_BUCKET", "ducklake")

    return DuckLakeConfig(
        namespace=namespace,
        catalog_uri=catalog_uri,
        bucket_url=f"s3://{r2_bucket}/{namespace}/",
        endpoint_url=os.environ.get("R2_ENDPOINT_URL"),
        aws_access_key_id=os.environ.get("R2_ACCESS_KEY_ID", ""),
        aws_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY", ""),
        aws_region="auto",
        use_ssl=True,
    )


def get_lakehouse_destination(
    namespace: str,
    use_ducklake: bool | None = None,
) -> dlt.destinations.Destination:
    """
    Get DLT destination for any sruth project.

    Environment Variables:
        DLT_ENVIRONMENT: "local" (default) or "production"
        USE_DUCKLAKE: "true" (default) or "false"

    Local:
        - Data: Garage S3 at s3://ducklake/{namespace}/
        - Metadata: PostgreSQL at localhost:5433

    Production:
        - Data: Cloudflare R2
        - Metadata: PostgreSQL (cloud)

    Args:
        namespace: Project namespace (oideachais, crypteolas, aleyum, tuath)
        use_ducklake: Override to force DuckLake or DuckDB fallback

    Returns:
        Configured destination for DLT pipeline
    """
    if use_ducklake is None:
        use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"

    if not use_ducklake:
        return get_duckdb_fallback(namespace)

    env = os.environ.get("DLT_ENVIRONMENT", "local").lower()

    if env == "production":
        config = _get_production_config(namespace)
    else:
        config = _get_local_config(namespace)

    return dlt.destinations.ducklake(
        credentials=config.to_credentials(),
        global_config=config.to_global_config(),
    )


def get_duckdb_fallback(
    namespace: str,
    base_path: str = "./data",
) -> dlt.destinations.Destination:
    """
    Get plain DuckDB destination as fallback.

    WARNING: This destination has single-writer lock - avoid parallel writes!

    Args:
        namespace: Project namespace for database file name
        base_path: Directory for DuckDB files

    Returns:
        DuckDB destination for DLT pipeline
    """
    db_path = os.path.join(base_path, f"{namespace}.duckdb")
    return dlt.destinations.duckdb(credentials=db_path)


def create_lakehouse_pipeline(
    namespace: str,
    pipeline_name: str,
    dataset_name: str,
    use_ducklake: bool | None = None,
    **kwargs: Any,
) -> dlt.Pipeline:
    """
    Create a DLT pipeline with DuckLake destination.

    Args:
        namespace: Project namespace (oideachais, crypteolas, aleyum, tuath)
        pipeline_name: Name of the pipeline (for state tracking)
        dataset_name: Dataset/schema name in destination
        use_ducklake: If True, use DuckLake; if False/None, use env default
        **kwargs: Additional arguments passed to dlt.pipeline()

    Returns:
        Configured DLT pipeline
    """
    destination = get_lakehouse_destination(namespace, use_ducklake=use_ducklake)

    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=destination,
        dataset_name=dataset_name,
        **kwargs,
    )
