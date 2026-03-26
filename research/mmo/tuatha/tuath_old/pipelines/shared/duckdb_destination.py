"""
DuckDB destination utilities for crypto data pipelines.

Provides helpers for creating DLT destinations and getting
Ibis connections for analytics.
"""

import os
from pathlib import Path
from typing import Any, Optional

import dlt


def create_duckdb_destination(
    database_path: Optional[str] = None,
    dataset_name: Optional[str] = None,
) -> tuple[Any, str]:
    """
    Create a DLT DuckDB destination.

    Args:
        database_path: Path to DuckDB file. Defaults to ./data/crypto_analytics.duckdb
        dataset_name: Schema/dataset name. Defaults to crypto_raw

    Returns:
        Tuple of (dlt destination, database path)
    """
    if database_path is None:
        database_path = os.environ.get(
            "DUCKDB_DATABASE", "./data/crypto_analytics.duckdb"
        )

    if dataset_name is None:
        dataset_name = os.environ.get("DUCKDB_DATASET", "crypto_raw")

    # Ensure parent directory exists
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    destination = dlt.destinations.duckdb(database_path)

    return destination, database_path


def get_duckdb_connection(database_path: Optional[str] = None):
    """
    Get an Ibis DuckDB connection for analytics queries.

    Args:
        database_path: Path to DuckDB file

    Returns:
        Ibis DuckDB connection
    """
    import ibis

    if database_path is None:
        database_path = os.environ.get(
            "DUCKDB_DATABASE", "./data/crypto_analytics.duckdb"
        )

    return ibis.duckdb.connect(database_path)


def create_filesystem_destination(
    bucket_url: Optional[str] = None,
    layout: Optional[str] = None,
) -> Any:
    """
    Create a DLT filesystem destination for S3/R2/local storage.

    Args:
        bucket_url: Bucket URL (file:// or s3://)
        layout: File layout pattern

    Returns:
        DLT filesystem destination
    """
    if bucket_url is None:
        bucket_url = os.environ.get("FILESYSTEM_BUCKET_URL", "file://./data/raw")

    if layout is None:
        layout = "{table_name}/{load_id}.{file_id}.{ext}"

    # Get credentials from environment if S3
    credentials = None
    if bucket_url.startswith("s3://"):
        credentials = {
            "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
            "endpoint_url": os.environ.get("AWS_ENDPOINT_URL"),
            "region_name": os.environ.get("AWS_REGION", "auto"),
        }

    return dlt.destinations.filesystem(
        bucket_url=bucket_url,
        layout=layout,
        credentials=credentials,
    )


def create_motherduck_destination(
    database: Optional[str] = None,
    token: Optional[str] = None,
) -> Any:
    """
    Create a DLT MotherDuck destination.

    Args:
        database: MotherDuck database name
        token: MotherDuck service token

    Returns:
        DLT MotherDuck destination
    """
    if database is None:
        database = os.environ.get("MOTHERDUCK_DATABASE", "crypto_analytics")

    if token is None:
        token = os.environ.get("MOTHERDUCK_TOKEN")

    if not token:
        raise ValueError("MOTHERDUCK_TOKEN environment variable required")

    return dlt.destinations.motherduck(
        database=database,
        credentials={"password": token},
    )


def create_destination(destination_type: Optional[str] = None) -> tuple[Any, dict]:
    """
    Create a DLT destination based on type.

    The destination type can be set via DESTINATION_TYPE environment variable
    or passed directly.

    Args:
        destination_type: One of "duckdb", "filesystem", "motherduck"

    Returns:
        Tuple of (destination, metadata dict with paths/urls)
    """
    if destination_type is None:
        destination_type = os.environ.get("DESTINATION_TYPE", "duckdb")

    if destination_type == "duckdb":
        dest, path = create_duckdb_destination()
        return dest, {"type": "duckdb", "database_path": path}

    elif destination_type == "filesystem":
        bucket_url = os.environ.get("FILESYSTEM_BUCKET_URL", "file://./data/raw")
        dest = create_filesystem_destination(bucket_url)
        return dest, {"type": "filesystem", "bucket_url": bucket_url}

    elif destination_type == "motherduck":
        database = os.environ.get("MOTHERDUCK_DATABASE", "crypto_analytics")
        dest = create_motherduck_destination(database)
        return dest, {"type": "motherduck", "database": database}

    else:
        raise ValueError(f"Unknown destination type: {destination_type}")


def create_pipeline(
    pipeline_name: str,
    dataset_name: Optional[str] = None,
    destination_type: Optional[str] = None,
) -> tuple[dlt.Pipeline, dict]:
    """
    Create a DLT pipeline with the appropriate destination.

    Args:
        pipeline_name: Name of the pipeline
        dataset_name: Schema/dataset name
        destination_type: Destination type override

    Returns:
        Tuple of (dlt.Pipeline, destination metadata)
    """
    if dataset_name is None:
        dataset_name = os.environ.get("DUCKDB_DATASET", "crypto_raw")

    destination, metadata = create_destination(destination_type)

    pipeline = dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    return pipeline, metadata
