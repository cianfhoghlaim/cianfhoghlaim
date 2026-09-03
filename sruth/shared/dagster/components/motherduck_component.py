"""Dagster Component for MotherDuck + PlanetScale hybrid storage.

Creates MotherDuck resources with optional PlanetScale attachment for
hybrid OLTP/OLAP workloads.

Example YAML:
    type: sruth.shared.dagster.components.MotherDuckComponent
    attributes:
      name: "motherduck_io"
      database: "sruth_analytics"
      schemas: ["curriculum", "exam_materials", "embeddings"]

      # PlanetScale for OLTP
      planetscale_host: "${PLANETSCALE_HOST}"
      planetscale_database: "${PLANETSCALE_DATABASE}"
      planetscale_user: "${PLANETSCALE_USER}"
      planetscale_password: "${PLANETSCALE_PASSWORD}"
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import dagster as dg


@dataclass
class MotherDuckComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for MotherDuck cloud data warehouse.

    MotherDuck provides serverless DuckDB for OLAP analytics.
    With PlanetScale attached via pg_duckdb, enables hybrid OLTP/OLAP.
    """

    # Resource name
    name: str = "motherduck"

    # MotherDuck configuration
    token: str = ""  # Service token (or use MOTHERDUCK_TOKEN env var)
    database: str = "sruth"
    schemas: list[str] = field(default_factory=lambda: ["curriculum", "exam_materials", "embeddings"])

    # PlanetScale integration for hybrid OLTP/OLAP
    planetscale_host: str = ""
    planetscale_database: str = ""
    planetscale_user: str = ""
    planetscale_password: str = ""

    # Auto-initialize schemas
    init_schemas: bool = True

    def _get_token(self) -> str:
        """Get token from config or environment."""
        return self.token or os.getenv("MOTHERDUCK_TOKEN", "")

    def _get_planetscale_config(self) -> dict[str, str] | None:
        """Get PlanetScale configuration if available."""
        host = self.planetscale_host or os.getenv("PLANETSCALE_HOST")
        if not host:
            return None
        return {
            "host": host,
            "database": self.planetscale_database or os.getenv("PLANETSCALE_DATABASE", ""),
            "user": self.planetscale_user or os.getenv("PLANETSCALE_USER", os.getenv("PLANETSCALE_USERNAME", "")),
            "password": self.planetscale_password or os.getenv("PLANETSCALE_PASSWORD", os.getenv("PLANETSCALE_PASSWORD_TOKEN", "")),
        }

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build MotherDuck resource."""
        from sruth.shared.dagster.resources import MotherDuckResource

        ps_config = self._get_planetscale_config()

        resource = MotherDuckResource(
            token=self._get_token(),
            database=self.database,
            schemas=self.schemas,
            planetscale_host=ps_config["host"] if ps_config else None,
            planetscale_database=ps_config.get("database") if ps_config else None,
            planetscale_user=ps_config.get("user") if ps_config else None,
            planetscale_password=ps_config.get("password") if ps_config else None,
        )

        # Initialize schemas if requested
        if self.init_schemas:
            try:
                resource.init_schemas()
            except Exception:
                # Don't fail if initialization fails (might not have token yet)
                pass

        return dg.Definitions(
            resources={
                self.name: resource,
                "motherduck": resource,  # Also register as default
            }
        )


@dataclass
class MotherDuckIOComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for MotherDuck I/O manager.

    Provides Dagster I/O manager that stores data in MotherDuck.
    Supports both pandas and polars dataframes.
    """

    # Resource name
    name: str = "motherduck_io"

    # MotherDuck configuration
    token: str = ""
    database: str = "sruth"
    default_schema: str = "main"

    # I/O manager configuration
    compute_kind: str = "duckdb"  # For lineage metadata

    def _get_token(self) -> str:
        """Get token from config or environment."""
        return self.token or os.getenv("MOTHERDUCK_TOKEN", "")

    def _get_conn_str(self) -> str:
        """Get MotherDuck connection string."""
        return f"md:?motherduck_token={self._get_token()}&database={self.database}"

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build MotherDuck I/O manager."""

        @dg.io_manager(config_schema={
            "token": str,
            "database": str,
            "schema": str,
        })
        def motherduck_io_manager(init_context):
            """MotherDuck I/O manager for storing dataframes."""
            import duckdb

            token = init_context.resource_config.get("token") or self._get_token()
            database = init_context.resource_config.get("database", self.database)
            schema = init_context.resource_config.get("schema", self.default_schema)

            conn_str = f"md:?motherduck_token={token}&database={database}"

            class MotherDuckIOManager:
                def __init__(self, conn_str: str, schema: str):
                    self.conn_str = conn_str
                    self.schema = schema
                    self._conn = None

                def get_connection(self):
                    if self._conn is None:
                        self._conn = duckdb.connect(self.conn_str)
                        self._conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")
                    return self._conn

                def handle_output(self, context, obj):
                    conn = self.get_connection()
                    table_path = context.asset_key.path
                    table_name = "_".join(table_path)

                    # Convert to list of dicts if needed
                    if hasattr(obj, "to_dict"):
                        # pandas/polars DataFrame
                        data = obj.to_dict("records")
                    elif isinstance(obj, list):
                        data = obj
                    elif isinstance(obj, dict):
                        data = [obj]
                    else:
                        data = obj

                    # Create table and insert data
                    full_table = f"{self.schema}.{table_name}"
                    conn.execute(f"DROP TABLE IF EXISTS {full_table}")
                    conn.execute(f"CREATE TABLE {full_table} AS SELECT * FROM data")

                    return obj

                def load_input(self, context):
                    conn = self.get_connection()
                    table_path = context.asset_key.path
                    table_name = "_".join(table_path)
                    full_table = f"{self.schema}.{table_name}"

                    return conn.execute(f"SELECT * FROM {full_table}").fetchdf()

            return MotherDuckIOManager(conn_str, schema)

        return dg.Definitions(
            io_managers={
                self.name: motherduck_io_manager.configured({
                    "token": self._get_token(),
                    "database": self.database,
                    "schema": self.default_schema,
                })
            }
        )


@dataclass
class PlanetScaleComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for PlanetScale PostgreSQL connection.

    Provides PlanetScale resource for OLTP transactions.
    Can be queried from MotherDuck via pg_duckdb attachment.
    """

    # Resource name
    name: str = "planetscale"

    # PlanetScale configuration
    host: str = ""
    database: str = ""
    user: str = ""
    password: str = ""

    # Connection pool settings
    pool_size: int = 5
    max_overflow: int = 10

    def _get_config(self) -> dict[str, str]:
        """Get PlanetScale configuration."""
        return {
            "host": self.host or os.getenv("PLANETSCALE_HOST", ""),
            "database": self.database or os.getenv("PLANETSCALE_DATABASE", ""),
            "user": self.user or os.getenv("PLANETSCALE_USER", os.getenv("PLANETSCALE_USERNAME", "")),
            "password": self.password or os.getenv("PLANETSCALE_PASSWORD", os.getenv("PLANETSCALE_PASSWORD_TOKEN", "")),
        }

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build PlanetScale resource."""

        @dg.resource(config_schema={
            "host": str,
            "database": str,
            "user": str,
            "password": str,
        })
        def planetscale_resource(init_context):
            """PlanetScale PostgreSQL resource."""
            import psycopg

            config = {
                "host": init_context.resource_config.get("host") or self._get_config()["host"],
                "dbname": init_context.resource_config.get("database") or self._get_config()["database"],
                "user": init_context.resource_config.get("user") or self._get_config()["user"],
                "password": init_context.resource_config.get("password") or self._get_config()["password"],
            }

            class PlanetScaleConnection:
                def __init__(self, config: dict):
                    self.config = config
                    self._conn = None

                def get_connection(self):
                    if self._conn is None:
                        self._conn = psycopg.connect(**self.config)
                    return self._conn

                def execute(self, sql: str, params: tuple | None = None):
                    conn = self.get_connection()
                    cur = conn.cursor()
                    cur.execute(sql, params)
                    if sql.strip().upper().startswith(("SELECT", "WITH", "SHOW")):
                        result = cur.fetchall()
                        cur.close()
                        return result
                    conn.commit()
                    cur.close()
                    return cur.rowcount

                def close(self):
                    if self._conn:
                        self._conn.close()
                        self._conn = None

            return PlanetScaleConnection(config)

        return dg.Definitions(
            resources={
                self.name: planetscale_resource.configured(self._get_config())
            }
        )
