"""DLT Destination Configurations.

Factory functions for creating DLT destinations including DuckDB and DuckLake.

The legacy `aleyum_*` pipeline names + the `aleyum.duckdb` /
`aleyum_catalog.duckdb` / `aleyum-data` defaults have been
renamed to `croilar_*` / `croilar.duckdb` /
`croilar_catalog.duckdb` / `croilar-data` per round 11 of the
multi-quadrant refactor plan (the `croilar-aleyum-to-streams-cleanup-v1`
openspec change).

The canonical Stream-registry-driven configuration is at
`croilar/_shared/streams.py` + `croilar/_shared/config/settings.py`
(where the `STREAMS_` env prefix replaces the legacy `ALEYUM_`).
"""

import os

import dlt


def create_duckdb_destination(
    database_path: str = "./data/croilar.duckdb",
    dataset_name: str = "portfolio_data",
) -> tuple[dlt.Pipeline, str]:
    """Create a DuckDB destination for local development.

    Args:
        database_path: Path to DuckDB database file
        dataset_name: Name of the dataset in the database

    Returns:
        Tuple of (pipeline, dataset_name)
    """
    pipeline = dlt.pipeline(
        pipeline_name="croilar_local",
        destination="duckdb",
        credentials=database_path,
        dataset_name=dataset_name,
        progress="log",
    )

    return pipeline, dataset_name


def create_ducklake_destination(
    catalog_uri: str | None = None,
    r2_bucket: str = "croilar-data",
    dataset_name: str = "portfolio_data",
) -> tuple[dlt.Pipeline, str]:
    """Create a DuckLake destination backed by Cloudflare R2.

    DuckLake provides a lakehouse architecture with:
    - SQL catalog (DuckDB or PostgreSQL)
    - Object storage backend (R2)
    - Parquet file format

    Args:
        catalog_uri: DuckLake catalog connection string
        r2_bucket: R2 bucket for data storage
        dataset_name: Name of the dataset

    Returns:
        Tuple of (pipeline, dataset_name)
    """
    r2_account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    r2_access_key = os.environ.get("R2_ACCESS_KEY_ID", "")
    r2_secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", "")

    if catalog_uri is None:
        catalog_uri = "./data/croilar_catalog.duckdb"

    pipeline = dlt.pipeline(
        pipeline_name="croilar_ducklake",
        destination=dlt.destinations.filesystem(
            bucket_url=f"s3://{r2_bucket}",
            credentials={
                "aws_access_key_id": r2_access_key,
                "aws_secret_access_key": r2_secret_key,
                "endpoint_url": f"https://{r2_account_id}.r2.cloudflarestorage.com",
            },
        ),
        dataset_name=dataset_name,
        progress="log",
    )

    return pipeline, dataset_name


def create_lancedb_destination(
    uri: str = "./data/croilar.lancedb",
    dataset_name: str = "portfolio_vectors",
) -> tuple[dlt.Pipeline, str]:
    """Create a LanceDB destination for vector search.

    Args:
        uri: Path to LanceDB database
        dataset_name: Name of the dataset

    Returns:
        Tuple of (pipeline, dataset_name)
    """
    pipeline = dlt.pipeline(
        pipeline_name="croilar_vectors",
        destination="lancedb",
        credentials={"uri": uri},
        dataset_name=dataset_name,
        progress="log",
    )

    return pipeline, dataset_name


def get_destination_for_env() -> tuple[dlt.Pipeline, str]:
    """Get the appropriate destination based on environment.

    Returns DuckDB for local development, DuckLake for production.

    Returns:
        Tuple of (pipeline, dataset_name)
    """
    env = os.environ.get("CROILAR_ENV", "development")

    if env == "production":
        return create_ducklake_destination()
    return create_duckdb_destination()
