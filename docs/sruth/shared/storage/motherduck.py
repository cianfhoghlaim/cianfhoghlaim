"""MotherDuck + PlanetScale hybrid OLTP/OLAP storage.

This module provides unified access to:
- MotherDuck: Serverless DuckDB for analytics (OLAP)
- PlanetScale: Distributed PostgreSQL for transactions (OLTP)

The pg_duckdb extension enables querying PlanetScale data directly
from MotherDuck, creating a hybrid database experience.

Usage:
    from sruth.shared.storage.motherduck import get_motherduck_storage

    storage = get_motherduck_storage()

    # OLAP: Fast analytics in MotherDuck
    analytics = storage.analyze(
        "SELECT subject, COUNT(*) FROM curriculum.pages GROUP BY subject"
    )

    # OLTP: Transactional writes to PlanetScale
    storage.write_transaction("curriculum_state", {"subject": "math", "progress": 0.5})

    # Sync: PlanetScale -> MotherDuck
    storage.sync_table("curriculum_state", "curriculum", "state_snapshot")
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import duckdb


@dataclass
class MotherDuckConfig:
    """MotherDuck configuration."""

    token: str
    database: str = "sruth"
    schemas: list[str] | None = None

    @classmethod
    def from_env(cls) -> MotherDuckConfig:
        """Create from environment variables."""
        token = os.getenv("MOTHERDUCK_TOKEN")
        if not token:
            raise ValueError("MOTHERDUCK_TOKEN environment variable required")
        return cls(
            token=token,
            database=os.getenv("MOTHERDUCK_DATABASE", "sruth"),
            schemas=os.getenv("MOTHERDUCK_SCHEMAS", "curriculum,exam_materials,embeddings").split(","),
        )


@dataclass
class PlanetScaleConfig:
    """PlanetScale configuration for OLTP."""

    host: str
    database: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> PlanetScaleConfig | None:
        """Create from environment variables."""
        host = os.getenv("PLANETSCALE_HOST")
        if not host:
            return None
        return cls(
            host=host,
            database=os.getenv("PLANETSCALE_DATABASE", "sruth"),
            user=os.getenv("PLANETSCALE_USER", os.getenv("PLANETSCALE_USERNAME", "")),
            password=os.getenv("PLANETSCALE_PASSWORD", os.getenv("PLANETSCALE_PASSWORD_TOKEN", "")),
        )


class MotherDuckStorage:
    """Hybrid MotherDuck + PlanetScale storage.

    Provides:
    - MotherDuck connection for OLAP queries
    - PlanetScale attachment for hybrid queries
    - Direct PlanetScale access for transactions
    """

    def __init__(
        self,
        motherduck_config: MotherDuckConfig | None = None,
        planetscale_config: PlanetScaleConfig | None = None,
    ):
        """Initialize hybrid storage.

        Args:
            motherduck_config: MotherDuck configuration
            planetscale_config: PlanetScale configuration (optional)
        """
        self.md_config = motherduck_config or MotherDuckConfig.from_env()
        self.ps_config = planetscale_config or PlanetScaleConfig.from_env()
        self._md_conn: duckdb.DuckDBPyConnection | None = None
        self._ps_conn: Any | None = None

    @property
    def md_conn(self) -> duckdb.DuckDBPyConnection:
        """Get or create MotherDuck connection."""
        if self._md_conn is None:
            conn_str = f"md:?motherduck_token={self.md_config.token}&database={self.md_config.database}"
            self._md_conn = duckdb.connect(conn_str)

            # Attach PlanetScale if configured
            if self.ps_config:
                self._attach_planetscale()

        return self._md_conn

    def _attach_planetscale(self) -> None:
        """Attach PlanetScale as 'pscale' schema in DuckDB."""
        try:
            pg_conn_str = (
                f"postgresql://{self.ps_config.user}:{self.ps_config.password}"
                f"@{self.ps_config.host}/{self.ps_config.database}"
            )
            self.md_conn.execute(f"ATTACH '{pg_conn_str}' AS pscale (TYPE postgres)")
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to attach PlanetScale: {e}")

    def analyze(self, sql: str, params: dict[str, Any] | None = None) -> Any:
        """Run OLAP query on MotherDuck.

        Args:
            sql: SQL query
            params: Query parameters

        Returns:
            Query result
        """
        if params:
            return self.md_conn.execute(sql, params)
        return self.md_conn.execute(sql)

    def read_table(
        self,
        schema: str,
        table: str,
        columns: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> list[tuple]:
        """Read table from MotherDuck.

        Args:
            schema: Schema name
            table: Table name
            columns: Columns to select
            filters: WHERE clause filters
            limit: Row limit

        Returns:
            List of rows
        """
        col_clause = "*" if not columns else ", ".join(columns)
        query = f"SELECT {col_clause} FROM {schema}.{table}"

        if filters:
            conditions = [f"{k} = {repr(v)}" for k, v in filters.items()]
            query += " WHERE " + " AND ".join(conditions)

        if limit:
            query += f" LIMIT {limit}"

        return self.md_conn.execute(query).fetchall()

    def write_table(
        self,
        schema: str,
        table: str,
        data: list[dict] | list[tuple],
        mode: str = "append",
        primary_key: str | list[str] | None = None,
    ) -> int:
        """Write data to MotherDuck table.

        Args:
            schema: Schema name
            table: Table name
            data: Data to write
            mode: Write mode (append, overwrite, merge)
            primary_key: Primary key column(s)

        Returns:
            Number of rows written
        """
        if not data:
            return 0

        # Create schema if needed
        self.md_conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        if mode == "overwrite":
            self.md_conn.execute(f"DROP TABLE IF EXISTS {schema}.{table}")
            return self._create_and_insert(schema, table, data)

        # Check if table exists
        exists = self.md_conn.execute(
            f"SELECT COUNT(*) FROM information_schema.tables "
            f"WHERE table_schema = '{schema}' AND table_name = '{table}'"
        ).fetchone()[0] > 0

        if not exists:
            return self._create_and_insert(schema, table, data)

        if mode == "merge" and primary_key:
            pk_list = primary_key if isinstance(primary_key, list) else [primary_key]
            pk_cols = ", ".join(pk_list)
            # Delete existing rows with same keys
            self.md_conn.execute(f"DELETE FROM {schema}.{table} WHERE ({pk_cols}) IN (SELECT {pk_cols} FROM data)")

        # Insert data
        self.md_conn.execute(f"INSERT INTO {schema}.{table} SELECT * FROM data")
        return len(data)

    def _create_and_insert(self, schema: str, table: str, data: list[dict] | list[tuple]) -> int:
        """Create table and insert data."""
        # Create data view
        self.md_conn.execute("CREATE OR REPLACE VIEW data AS SELECT * FROM input_data")

        # Create table from view
        self.md_conn.execute(f"CREATE TABLE {schema}.{table} AS SELECT * FROM data")
        return len(data)

    def sync_from_planetscale(
        self,
        pscale_table: str,
        md_schema: str,
        md_table: str,
        where_clause: str | None = None,
    ) -> int:
        """Sync table from PlanetScale to MotherDuck.

        Args:
            pscale_table: Source table in PlanetScale (from pscale schema)
            md_schema: Target schema in MotherDuck
            md_table: Target table in MotherDuck
            where_clause: Optional WHERE clause

        Returns:
            Number of rows synced
        """
        if not self.ps_config:
            raise RuntimeError("PlanetScale not configured")

        where = f" WHERE {where_clause}" if where_clause else ""
        sql = f"""
            CREATE OR REPLACE TABLE {md_schema}.{md_table} AS
            SELECT * FROM pscale.{pscale_table}{where}
        """
        self.md_conn.execute(sql)

        return self.md_conn.execute(
            f"SELECT COUNT(*) FROM {md_schema}.{md_table}"
        ).fetchone()[0]

    def hybrid_query(
        self,
        sql: str,
        use_planetscale: bool = True,
    ) -> Any:
        """Run query that can access both MotherDuck and PlanetScale.

        Args:
            sql: SQL query (can use 'pscale.' schema for PlanetScale tables)
            use_planetscale: Whether PlanetScale is available

        Returns:
            Query result
        """
        if use_planetscale and not self.ps_config:
            raise RuntimeError("PlanetScale not configured for hybrid query")

        return self.md_conn.execute(sql)

    def export_parquet(
        self,
        schema: str,
        table: str,
        path: str,
        compression: str = "zstd",
    ) -> None:
        """Export table to Parquet.

        Args:
            schema: Source schema
            table: Source table
            path: Output path (S3 or local)
            compression: Compression type
        """
        self.md_conn.execute(
            f"COPY {schema}.{table} TO '{path}' "
            f"(FORMAT PARQUET, COMPRESSION {compression})"
        )

    def import_parquet(
        self,
        schema: str,
        table: str,
        path: str,
        mode: str = "append",
    ) -> int:
        """Import Parquet file.

        Args:
            schema: Target schema
            table: Target table
            path: Source path (S3 or local)
            mode: Write mode

        Returns:
            Number of rows imported
        """
        self.md_conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        if mode == "overwrite":
            self.md_conn.execute(f"DROP TABLE IF EXISTS {schema}.{table}")

        self.md_conn.execute(
            f"CREATE TABLE IF NOT EXISTS {schema}.{table} AS "
            f"SELECT * FROM read_parquet('{path}')"
        )

        return self.md_conn.execute(f"SELECT COUNT(*) FROM {schema}.{table}").fetchone()[0]

    def close(self) -> None:
        """Close connections."""
        if self._md_conn:
            self._md_conn.close()
            self._md_conn = None
        if self._ps_conn:
            self._ps_conn.close()
            self._ps_conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# Singleton instance
_motherduck_storage: MotherDuckStorage | None = None


def get_motherduck_storage(
    motherduck_config: MotherDuckConfig | None = None,
    planetscale_config: PlanetScaleConfig | None = None,
) -> MotherDuckStorage:
    """Get MotherDuck storage singleton.

    Args:
        motherduck_config: MotherDuck configuration (auto-detect if None)
        planetscale_config: PlanetScale configuration (auto-detect if None)

    Returns:
        MotherDuckStorage instance
    """
    global _motherduck_storage
    if _motherduck_storage is None:
        _motherduck_storage = MotherDuckStorage(motherduck_config, planetscale_config)
    return _motherduck_storage


def reset_motherduck_storage() -> None:
    """Reset the singleton (useful for testing)."""
    global _motherduck_storage
    if _motherduck_storage:
        _motherduck_storage.close()
    _motherduck_storage = None
