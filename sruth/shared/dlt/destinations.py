"""DLT destination factories for unified data loading.

This module provides destination configuration for:
- DuckDB (local development)
- DuckLake/Iceberg (production lakehouse)
- PostgreSQL (metadata catalog)
- LanceDB (vector storage)

Usage:
    from sruth.shared.dlt.destinations import get_dlt_destination

    # Automatically selects destination based on environment
    pipeline = dlt.pipeline(
        pipeline_name="my_pipeline",
        destination=get_dlt_destination(),
    )
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal

import dlt

# Destination types
DestinationType = Literal[
    "duckdb",
    "ducklake",
    "iceberg",
    "postgres",
    "lancedb",
    "bigquery",
    "snowflake",
    "motherduck",
]


@dataclass
class DuckLakeConfig:
    """Configuration for DuckLake/Iceberg destination."""

    namespace: str = "default"
    catalog_uri: str = "sqlite:///data/catalog.db"
    warehouse: str = "s3://garage/warehouse"
    table_properties: dict[str, str] | None = None

    # S3/Garage configuration
    endpoint_url: str | None = "http://garage:3900"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "garage"
    use_ssl: bool = False

    def to_credentials(self) -> dict[str, Any]:
        """Convert to DLT credentials format."""
        storage_config: dict[str, Any] = {
            "bucket_url": self.warehouse,
        }

        if self.endpoint_url:
            storage_config["credentials"] = {
                "aws_access_key_id": self.aws_access_key_id,
                "aws_secret_access_key": self.aws_secret_access_key,
                "endpoint_url": self.endpoint_url,
                "region_name": self.aws_region,
            }
            # CRITICAL: Add path-style URL config for Garage/MinIO
            storage_config["config_kwargs"] = {"s3": {"addressing_style": "path"}}

        return {
            "ducklake_name": self.namespace,
            "catalog": self.catalog_uri,
            "storage": storage_config,
        }

    def to_global_config(self) -> dict[str, Any]:
        """Build DuckDB global_config for S3-compatible storage.

        Required for Garage/MinIO that need path-style URLs.
        """
        if not self.endpoint_url:
            return {}

        # Parse endpoint to get host:port without protocol
        endpoint = self.endpoint_url.replace("http://", "").replace("https://", "")

        return {
            "s3_endpoint": endpoint,
            "s3_url_style": "path",  # CRITICAL for Garage/MinIO
            "s3_use_ssl": str(self.use_ssl).lower(),
            "s3_region": self.aws_region,
            "s3_access_key_id": self.aws_access_key_id,
            "s3_secret_access_key": self.aws_secret_access_key,
        }


def get_dlt_destination(
    destination_type: DestinationType | None = None,
    config: DuckLakeConfig | None = None,
) -> Any:
    """Get DLT destination based on environment or type.

    Args:
        destination_type: Explicit destination type (auto-detect if None)
        config: DuckLake configuration (for iceberg/ducklake)

    Returns:
        DLT destination object

    Auto-detection order:
    1. MOTHERDUCK_TOKEN -> MotherDuck (cloud analytics)
    2. LAKEKEEPER_CATALOG_URI -> DuckLake/Iceberg (lakehouse)
    3. POSTGRES_URL -> PostgreSQL (transactional)
    4. BIGQUERY_PROJECT_ID -> BigQuery
    5. SNOWFLAKE_ACCOUNT -> Snowflake
    6. Default -> DuckDB (./data.duckdb)
    """
    if destination_type:
        return _create_destination(destination_type, config)

    # Auto-detect from environment
    if os.getenv("MOTHERDUCK_TOKEN"):
        return get_motherduck_destination()
    if os.getenv("LAKEKEEPER_CATALOG_URI"):
        return get_iceberg_destination(config or DuckLakeConfig())
    if os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL"):
        return get_postgres_destination()
    if os.getenv("BIGQUERY_PROJECT_ID"):
        return get_bigquery_destination()
    if os.getenv("SNOWFLAKE_ACCOUNT"):
        return get_snowflake_destination()

    # Default to DuckDB for local development
    return get_duckdb_destination()


def get_duckdb_destination(
    path: str = "./data.duckdb",
    schema: str = "main",
) -> dlt.destinations.duckdb:
    """Get DuckDB destination for local development.

    Args:
        path: Path to DuckDB database file
        schema: Schema name (default: main)

    Returns:
        DLT DuckDB destination
    """
    return dlt.destinations.duckdb(
        path=path,
        schema=schema,
    )


def get_iceberg_destination(
    config: DuckLakeConfig | None = None,
) -> Any:
    """Get Iceberg/DuckLake destination with Lakekeeper catalog.

    Args:
        config: DuckLake configuration

    Returns:
        DLT Iceberg destination
    """
    if config is None:
        config = DuckLakeConfig(
            catalog_uri=os.getenv("LAKEKEEPER_CATALOG_URI", "sqlite:///data/catalog.db"),
            warehouse=os.getenv(
                "ICEBERG_WAREHOUSE",
                "s3://garage/warehouse",
            ),
            endpoint_url=os.getenv("GARAGE_ENDPOINT_URL", "http://garage:3900"),
            aws_access_key_id=os.getenv("GARAGE_ACCESS_KEY", "garage_key"),
            aws_secret_access_key=os.getenv("GARAGE_SECRET_KEY", "garage_secret"),
        )

    # Check if dlt.ducklake is available
    try:
        return dlt.destinations.ducklake(
            credentials=config.to_credentials(),
            global_config=config.to_global_config(),
        )
    except (ImportError, AttributeError):
        # Fall back to duckdb with Iceberg extension
        import duckdb

        duckdb.sql("INSTALL iceberg FROM community; LOAD iceberg;")
        return dlt.destinations.duckdb(
            path="./lakehouse.duckdb",
        )


def get_postgres_destination(
    host: str | None = None,
    port: int | None = None,
    database: str | None = None,
    username: str | None = None,
    password: str | None = None,
) -> dlt.destinations.postgres:
    """Get PostgreSQL destination.

    Args:
        host: Database host (default: from POSTGRES_URL or localhost)
        port: Database port (default: from POSTGRES_URL or 5432)
        database: Database name (default: from POSTGRES_URL or postgres)
        username: Database user (default: from POSTGRES_URL or postgres)
        password: Database password (default: from POSTGRES_URL or None)

    Returns:
        DLT PostgreSQL destination
    """
    # Parse POSTGRES_URL if available
    postgres_url = os.getenv("POSTGRES_URL")
    if postgres_url:
        return dlt.destinations.postgres(credentials=postgres_url)

    return dlt.destinations.postgres(
        host=host or os.getenv("POSTGRES_HOST", "localhost"),
        port=port or int(os.getenv("POSTGRES_PORT", "5432")),
        database=database or os.getenv("POSTGRES_DATABASE", "postgres"),
        username=username or os.getenv("POSTGRES_USER", "postgres"),
        password=password or os.getenv("POSTGRES_PASSWORD", ""),
    )


def get_bigquery_destination(
    project_id: str | None = None,
        dataset: str | None = None,
    location: str = "US",
) -> dlt.destinations.bigquery:
    """Get BigQuery destination.

    Args:
        project_id: GCP project ID (default: from GOOGLE_CLOUD_PROJECT)
        dataset: Dataset name
        location: Dataset location

    Returns:
        DLT BigQuery destination
    """
    return dlt.destinations.bigquery(
        project_id=project_id or os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=location,
    )


def get_snowflake_destination(
    account: str | None = None,
    warehouse: str | None = None,
) -> dlt.destinations.snowflake:
    """Get Snowflake destination.

    Args:
        account: Snowflake account (default: from SNOWFLAKE_ACCOUNT)
        warehouse: Warehouse name

    Returns:
        DLT Snowflake destination
    """
    snowflake_url = f"snowflake://{account or os.getenv('SNOWFLAKE_ACCOUNT')}"
    return dlt.destinations.snowflake(credentials=snowflake_url)


def get_motherduck_destination(
    token: str | None = None,
    database: str = "sruth",
) -> dlt.destinations.duckdb:
    """Get MotherDuck destination for cloud data warehouse.

    MotherDuck is a serverless DuckDB cloud service that provides:
    - Fast analytical queries on large datasets
    - Hybrid OLTP/OLAP with PlanetScale via pg_duckdb
    - Direct integration with S3 for external data

    Args:
        token: MotherDuck service token (default: from MOTHERDUCK_TOKEN)
        database: Database name (default: sruth)

    Returns:
        DLT DuckDB destination configured for MotherDuck

    Example:
        # In DLT pipeline
        pipeline = dlt.pipeline(
            pipeline_name="my_pipeline",
            destination=get_motherduck_destination(),
        )
    """
    token = token or os.getenv("MOTHERDUCK_TOKEN")
    if not token:
        raise ValueError(
            "MotherDuck token required. Set MOTHERDUCK_TOKEN environment "
            "variable or pass token parameter."
        )

    # MotherDuck uses DuckDB destination with special connection string
    conn_str = f"md:?motherduck_token={token}&database={database}"

    return dlt.destinations.duckdb(
        connection_string=conn_str,
    )


def _create_destination(
    destination_type: DestinationType,
    config: DuckLakeConfig | None = None,
) -> Any:
    """Create a specific destination type."""
    if destination_type == "duckdb":
        return get_duckdb_destination()
    if destination_type == "ducklake" or destination_type == "iceberg":
        return get_iceberg_destination(config)
    if destination_type == "postgres":
        return get_postgres_destination()
    if destination_type == "bigquery":
        return get_bigquery_destination()
    if destination_type == "snowflake":
        return get_snowflake_destination()
    if destination_type == "motherduck":
        return get_motherduck_destination()

    raise ValueError(f"Unknown destination type: {destination_type}")
