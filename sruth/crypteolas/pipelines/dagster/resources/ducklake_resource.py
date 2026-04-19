"""DuckLake destination resource for production.

DuckLake uses PostgreSQL for metadata and S3/R2 for data storage,
providing a lakehouse architecture with DuckDB query capabilities.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

import dagster as dg
import duckdb
from pydantic import Field

if TYPE_CHECKING:
    from duckdb import DuckDBPyConnection


class DuckLakeResource(dg.ConfigurableResource):
    """DuckLake resource for production destination with S3/R2 storage.

    Configures DuckDB to use DuckLake extension with:
    - PostgreSQL as metadata backend
    - S3/R2 as data storage backend

    Environment variables:
        DUCKLAKE_PG_HOST: PostgreSQL host
        DUCKLAKE_PG_PORT: PostgreSQL port (default: 5432)
        DUCKLAKE_PG_DATABASE: Database name
        DUCKLAKE_PG_USER: Database user
        DUCKLAKE_PG_PASSWORD: Database password
        S3_ENDPOINT: S3-compatible endpoint URL
        S3_BUCKET: Bucket name
        S3_ACCESS_KEY_ID: Access key
        S3_SECRET_ACCESS_KEY: Secret key
        S3_REGION: Region (default: auto)

    Example:
        ```python
        @asset(required_resource_keys={"destination"})
        def my_asset(context):
            with context.resources.destination.connect() as conn:
                conn.execute("SELECT * FROM ducklake.my_table")
        ```
    """

    # Metadata backend (PostgreSQL)
    pg_host: str = Field(
        default_factory=lambda: os.getenv("DUCKLAKE_PG_HOST", "localhost"),
        description="PostgreSQL host"
    )
    pg_port: int = Field(
        default=5432,
        description="PostgreSQL port"
    )
    pg_database: str = Field(
        default_factory=lambda: os.getenv("DUCKLAKE_PG_DATABASE", "ducklake"),
        description="PostgreSQL database name"
    )
    pg_user: str = Field(
        default_factory=lambda: os.getenv("DUCKLAKE_PG_USER", ""),
        description="PostgreSQL user"
    )
    pg_password: str = Field(
        default_factory=lambda: os.getenv("DUCKLAKE_PG_PASSWORD", ""),
        description="PostgreSQL password"
    )

    # Storage backend (S3/R2)
    s3_endpoint: str = Field(
        default_factory=lambda: os.getenv("S3_ENDPOINT", ""),
        description="S3-compatible endpoint URL"
    )
    s3_bucket: str = Field(
        default_factory=lambda: os.getenv("S3_BUCKET", "codeolas-data"),
        description="S3 bucket name"
    )
    s3_prefix: str = Field(
        default="lakehouse/",
        description="Prefix path within bucket"
    )
    s3_access_key: str = Field(
        default_factory=lambda: os.getenv("S3_ACCESS_KEY_ID", ""),
        description="S3 access key ID"
    )
    s3_secret_key: str = Field(
        default_factory=lambda: os.getenv("S3_SECRET_ACCESS_KEY", ""),
        description="S3 secret access key"
    )
    s3_region: str = Field(
        default="auto",
        description="S3 region"
    )

    alias: str = Field(
        default="ducklake",
        description="DuckLake database alias"
    )

    @contextmanager
    def connect(self) -> Generator[DuckDBPyConnection, None, None]:
        """Yield a DuckDB connection attached to DuckLake."""
        conn = duckdb.connect(":memory:")
        self._setup_ducklake(conn)
        try:
            yield conn
        finally:
            conn.close()

    def _setup_ducklake(self, conn: DuckDBPyConnection) -> None:
        """Configure DuckDB connection for DuckLake.

        Installs the DuckLake extension and configures secrets for
        PostgreSQL metadata and S3 data storage.
        """
        # Install and load DuckLake extension
        conn.execute("INSTALL ducklake FROM community; LOAD ducklake;")

        # Create PostgreSQL metadata secret
        conn.execute(f"""
            CREATE OR REPLACE SECRET secret_catalog_{self.alias} (
                TYPE postgres,
                HOST '{self.pg_host}',
                PORT {self.pg_port},
                DATABASE '{self.pg_database}',
                USER '{self.pg_user}',
                PASSWORD '{self.pg_password}'
            );
        """)

        # Create S3 storage secret
        conn.execute(f"""
            CREATE OR REPLACE SECRET secret_storage_{self.alias} (
                TYPE S3,
                KEY_ID '{self.s3_access_key}',
                SECRET '{self.s3_secret_key}',
                ENDPOINT '{self.s3_endpoint}',
                URL_STYLE 'path',
                REGION '{self.s3_region}',
                USE_SSL true,
                SCOPE 's3://{self.s3_bucket}'
            );
        """)

        # Create DuckLake secret combining both
        conn.execute(f"""
            CREATE OR REPLACE SECRET secret_{self.alias} (
                TYPE DUCKLAKE,
                METADATA_PATH '',
                METADATA_PARAMETERS MAP {{'TYPE': 'postgres', 'SECRET': 'secret_catalog_{self.alias}'}},
                DATA_PATH 's3://{self.s3_bucket}/{self.s3_prefix}'
            );
        """)

        # Attach DuckLake
        conn.execute(f"ATTACH 'ducklake:secret_{self.alias}' AS {self.alias};")
        conn.execute(f"USE {self.alias};")

    def get_dlt_destination(self):
        """Return DLT destination configuration.

        Note: DLT writes to a local DuckDB file first, then we sync to DuckLake.
        For direct DuckLake writes, use the connect() method with raw SQL.
        """
        import dlt
        return dlt.destinations.duckdb(f"./.dlt_staging/{self.alias}.duckdb")

    def get_dlt_destination_name(self) -> str:
        """Return the DLT destination name string."""
        return "duckdb"  # DLT writes to DuckDB, we sync to DuckLake

    def sync_from_dlt_staging(self, dataset_name: str) -> None:
        """Sync data from DLT staging DuckDB to DuckLake.

        Args:
            dataset_name: The DLT dataset name to sync
        """
        import duckdb as local_duckdb

        staging_path = f"./.dlt_staging/{self.alias}.duckdb"

        # Read from staging
        staging_conn = local_duckdb.connect(staging_path, read_only=True)
        tables = staging_conn.execute(
            f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{dataset_name}'"
        ).fetchall()

        # Write to DuckLake
        with self.connect() as lake_conn:
            for (table_name,) in tables:
                # Create schema if not exists
                lake_conn.execute(f"CREATE SCHEMA IF NOT EXISTS {dataset_name}")

                # Copy data
                data = staging_conn.execute(
                    f"SELECT * FROM {dataset_name}.{table_name}"
                ).fetch_arrow_table()

                lake_conn.execute(f"""
                    CREATE OR REPLACE TABLE {dataset_name}.{table_name} AS
                    SELECT * FROM data
                """)

        staging_conn.close()
