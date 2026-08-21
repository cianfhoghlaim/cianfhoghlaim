"""Dagster Component for Iceberg I/O management.

Creates Iceberg I/O managers with Lakekeeper catalog integration.

Example YAML:
    type: sruth.shared.dagster.components.IcebergIOComponent
    attributes:
      name: "iceberg_io"
      catalog_uri: "http://lakekeeper:8181"
      warehouse: "s3://garage/warehouse"
      namespace: "curriculum"
      compute_kind: "polars"
"""

from __future__ import annotations

import os

# Note: No longer using dataclass decorator - using Pydantic via dg.Model
from typing import Any

import dagster as dg


class IcebergIOComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for Iceberg I/O manager.

    Provides Iceberg table storage via Lakekeeper REST catalog
    with S3-compatible storage (Garage/R2/MinIO).
    """

    # Resource name
    name: str = "iceberg_io"

    # Lakekeeper catalog configuration
    catalog_uri: str = ""
    warehouse: str = ""
    namespace: str = "default"

    # S3/Garage configuration
    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_region: str = "garage"
    s3_use_ssl: bool = False

    # I/O manager configuration
    compute_kind: str = "polars"  # "polars", "pandas", "pyarrow", "daft"
    table_properties: dict[str, str] = {}

    def _get_catalog_uri(self) -> str:
        """Get catalog URI from config or environment."""
        return self.catalog_uri or os.getenv(
            "LAKEKEEPER_CATALOG_URI",
            "http://lakekeeper:8181",
        )

    def _get_warehouse(self) -> str:
        """Get warehouse location from config or environment."""
        return self.warehouse or os.getenv(
            "ICEBERG_WAREHOUSE",
            "s3://garage/warehouse",
        )

    def _get_s3_config(self) -> dict[str, Any]:
        """Get S3 configuration."""
        return {
            "endpoint_url": self.s3_endpoint
            or os.getenv("GARAGE_ENDPOINT_URL", "http://garage:3900"),
            "aws_access_key_id": self.s3_access_key or os.getenv("GARAGE_ACCESS_KEY", "garage_key"),
            "aws_secret_access_key": self.s3_secret_key
            or os.getenv("GARAGE_SECRET_KEY", "garage_secret"),
            "region": self.s3_region or os.getenv("AWS_REGION", "garage"),
            "use_ssl": self.s3_use_ssl,
        }

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build Iceberg I/O manager resource."""
        from sruth.shared.dagster.resources import LakeKeeperResource

        resource = LakeKeeperResource(
            catalog_uri=self._get_catalog_uri(),
            warehouse=self._get_warehouse(),
            namespace=self.namespace,
            endpoint_url=self._get_s3_config()["endpoint_url"],
            access_key=self._get_s3_config()["aws_access_key_id"],
            secret_key=self._get_s3_config()["aws_secret_access_key"],
        )

        return dg.Definitions(
            resources={
                self.name: resource,
                "lakekeeper": resource,  # Also register as default
            }
        )


class DuckDBComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for DuckDB I/O manager.

    Provides DuckDB storage for local development and analytics.
    """

    # Resource name
    name: str = "duckdb_io"

    # Database configuration
    database_path: str = "./data.duckdb"
    schema_name: str = "main"  # Renamed to avoid shadowing Pydantic's schema

    # Extensions to load
    extensions: list[str] = ["httpfs", "iceberg"]

    # I/O manager configuration
    compute_kind: str = "duckdb"

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build DuckDB I/O manager resource."""

        @dg.resource(config_schema={"path": str, "schema": str})
        def duckdb_io_resource(init_context):
            """DuckDB I/O manager resource."""
            import duckdb

            class DuckDBIOManager:
                def __init__(self, path: str, schema: str):
                    self.path = path
                    self.schema = schema
                    self._conn = None

                def get_connection(self):
                    if self._conn is None:
                        self._conn = duckdb.connect(self.path)
                        # Load extensions
                        for ext in self.extensions:
                            try:
                                self._conn.execute(f"INSTALL {ext}")
                                self._conn.execute(f"LOAD {ext}")
                            except Exception:
                                pass
                    return self._conn

                def handle_output(self, context, obj):
                    conn = self.get_connection()
                    table_name = context.asset_key.to_user_string()
                    obj.to_sql(table_name, conn, if_exists="replace")
                    return obj

                def load_input(self, context):
                    conn = self.get_connection()
                    table_name = context.asset_key.to_user_string()
                    return conn.execute(f"SELECT * FROM {table_name}").fetchdf()

            path = init_context.resource_config.get("path", self.database_path)
            schema = init_context.resource_config.get("schema", self.schema_name)

            return DuckDBIOManager(path, schema)

        return dg.Definitions(
            resources={
                self.name: duckdb_io_resource.configured(
                    {
                        "path": self.database_path,
                        "schema": self.schema_name,
                    }
                )
            }
        )
