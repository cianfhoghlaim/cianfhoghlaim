"""PostgreSQL target for CocoIndex exports.

Provides PostgreSQL export functionality for CocoIndex flows,
with support for PlanetScale and other PostgreSQL-compatible databases.

Usage:
    from sruth.shared.storage.postgres_target import PostgreSQLTarget
    import cocoindex

    # In CocoIndex flow
    data_scope["results"].export(
        "curriculum_documents",
        PostgreSQLTarget(
            table="curriculum",
            schema="public",
            primary_key="id",
        ),
    )
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

import psycopg
from psycopg.rows import dict_row
from psycopg.sql import SQL, Identifier


@dataclass
class PostgreSQLConfig:
    """PostgreSQL connection configuration."""

    host: str
    database: str
    user: str
    password: str
    port: int = 5432
    ssl_mode: str = "require"

    @classmethod
    def from_env(cls, prefix: str = "") -> PostgreSQLConfig:
        """Create configuration from environment variables.

        Args:
            prefix: Optional prefix for env vars (e.g., "PLANETSCALE_")

        Returns:
            PostgreSQLConfig instance
        """
        prefix = prefix.upper()
        return cls(
            host=os.getenv(f"{prefix}HOST", os.getenv(f"{prefix}HOST", "")),
            database=os.getenv(f"{prefix}DATABASE", ""),
            user=os.getenv(f"{prefix}USER", os.getenv(f"{prefix}USERNAME", "")),
            password=os.getenv(f"{prefix}PASSWORD", os.getenv(f"{prefix}PASSWORD_TOKEN", "")),
            port=int(os.getenv(f"{prefix}PORT", "5432")),
            ssl_mode=os.getenv(f"{prefix}SSL_MODE", "require"),
        )


@dataclass
class ColumnDef:
    """Column definition for table creation."""

    name: str
    type: str  # varchar, text, integer, jsonb, etc.
    nullable: bool = True
    primary_key: bool = False


class PostgreSQLTarget:
    """PostgreSQL export target for CocoIndex flows.

    Handles:
    - Connection pooling
    - Automatic table creation
    - Batch inserts with upsert support
    - JSONB for flexible metadata
    """

    def __init__(
        self,
        config: PostgreSQLConfig | None = None,
        table: str = "exported_data",
        schema: str = "public",
        primary_key: str | None = None,
        columns: list[ColumnDef] | None = None,
        batch_size: int = 1000,
    ):
        """Initialize PostgreSQL target.

        Args:
            config: Database configuration
            table: Target table name
            schema: Schema name
            primary_key: Primary key column for upserts
            columns: Column definitions for table creation
            batch_size: Batch size for inserts
        """
        self.config = config or PostgreSQLConfig.from_env()
        self.table = table
        self.schema = schema
        self.primary_key = primary_key
        self.columns = columns or self._default_columns()
        self.batch_size = batch_size
        self._pool = None

    def _default_columns(self) -> list[ColumnDef]:
        """Default column definitions if not specified."""
        return [
            ColumnDef("id", "varchar", primary_key=True),
            ColumnDef("data", "jsonb"),
            ColumnDef("created_at", "timestamp", nullable=False),
        ]

    async def _get_pool(self) -> psycopg.AsyncConnection.pool.Pool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = psycopg.AsyncConnection.pool(
                host=self.config.host,
                port=self.config.port,
                dbname=self.config.database,
                user=self.config.user,
                password=self.config.password,
                sslmode=self.config.ssl_mode,
                min_size=1,
                max_size=10,
            )
        return self._pool

    async def ensure_table(self) -> None:
        """Create table if it doesn't exist."""
        pool = await self._get_pool()

        async with pool.connection() as conn:
            # Build column definitions
            col_defs = []
            for col in self.columns:
                pk = " PRIMARY KEY" if col.primary_key else ""
                null = " NOT NULL" if not col.nullable else ""
                col_defs.append(f"{col.name} {col.type}{pk}{null}")

            # Create table SQL
            sql = SQL(
                "CREATE TABLE IF NOT EXISTS {}.{} ({})"
            ).format(
                Identifier(self.schema),
                Identifier(self.table),
                SQL(", ".join(col_defs)),
            )

            await conn.execute(sql)

    async def write_batch(self, records: list[dict[str, Any]]) -> int:
        """Write a batch of records.

        Args:
            records: List of records to write

        Returns:
            Number of records written
        """
        if not records:
            return 0

        pool = await self._get_pool()
        await self.ensure_table()

        async with pool.connection() as conn:
            if self.primary_key:
                return await self._upsert_batch(conn, records)
            else:
                return await self._insert_batch(conn, records)

    async def _insert_batch(
        self,
        conn: psycopg.AsyncConnection,
        records: list[dict[str, Any]],
    ) -> int:
        """Insert batch without upsert."""
        cols = list(records[0].keys())
        placeholders = [f"${i + 1}" for i in range(len(cols))]

        sql = SQL(
            "INSERT INTO {}.{} ({}) VALUES ({})"
        ).format(
            Identifier(self.schema),
            Identifier(self.table),
            SQL(", ".join(map(Identifier, cols))),
            SQL(", ".join(placeholders)),
        )

        values = [[r.get(col) for col in cols] for r in records]

        async with conn.cursor() as cur:
            await cur.executemany(sql, values)
            return cur.rowcount

    async def _upsert_batch(
        self,
        conn: psycopg.AsyncConnection,
        records: list[dict[str, Any]],
    ) -> int:
        """Upsert batch using ON CONFLICT."""
        cols = list(records[0].keys())
        placeholders = [f"${i + 1}" for i in range(len(cols))]
        updates = [f"{col} = EXCLUDED.{col}" for col in cols if col != self.primary_key]

        sql = SQL(
            "INSERT INTO {}.{} ({}) VALUES ({}) ON CONFLICT ({}) DO UPDATE SET {}"
        ).format(
            Identifier(self.schema),
            Identifier(self.table),
            SQL(", ".join(map(Identifier, cols))),
            SQL(", ".join(placeholders)),
            Identifier(self.primary_key),
            SQL(", ".join(updates)),
        )

        values = [[r.get(col) for col in cols] for r in records]

        async with conn.cursor() as cur:
            await cur.executemany(sql, values)
            return cur.rowcount

    async def query(
        self,
        where: str | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Query records from the table.

        Args:
            where: WHERE clause (without "WHERE" keyword)
            limit: Optional limit

        Yields:
            Records as dictionaries
        """
        pool = await self._get_pool()

        query = SQL("SELECT * FROM {}.{}").format(
            Identifier(self.schema),
            Identifier(self.table),
        )

        if where:
            query = SQL("{} WHERE {}").format(query, SQL(where))

        if limit:
            query = SQL("{} LIMIT {}").format(query, SQL(str(limit)))

        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query)
                async for row in cur:
                    yield row

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None


# ============================================================================
# CocoIndex Integration
# ============================================================================

try:
    import cocoindex

    class CocoIndexPostgresTarget(cocoindex.targets.Target):
        """CocoIndex target for PostgreSQL export.

        Usage in CocoIndex flow:
            results_index.export(
                "my_table",
                CocoIndexPostgresTarget(
                    config=PostgreSQLConfig(...),
                    table="my_table",
                    primary_key="id",
                ),
            )
        """

        def __init__(
            self,
            config: PostgreSQLConfig | None = None,
            table: str = "exported_data",
            schema: str = "public",
            primary_key: str | None = None,
        ):
            self.target = PostgreSQLTarget(
                config=config,
                table=table,
                schema=schema,
                primary_key=primary_key,
            )

        async def do_export(self, rows: AsyncIterator[cocoindex.rows.Row]) -> None:
            """Export rows to PostgreSQL.

            Args:
                rows: Async iterator of CocoIndex rows
            """
            batch = []

            async for row in rows:
                # Convert CocoIndex row to dict
                record = {k: v for k, v in row.as_dict().items()}
                batch.append(record)

                if len(batch) >= self.target.batch_size:
                    await self.target.write_batch(batch)
                    batch = []

            # Write remaining
            if batch:
                await self.target.write_batch(batch)

    COCOINDEX_AVAILABLE = True

except ImportError:
    COCOINDEX_AVAILABLE = False
    CocoIndexPostgresTarget = None  # type: ignore


# ============================================================================
# Convenience Functions
# ============================================================================


def create_planetscale_target(
    table: str,
    schema: str = "public",
    primary_key: str | None = None,
) -> PostgreSQLTarget:
    """Create PostgreSQL target for PlanetScale.

    Args:
        table: Table name
        schema: Schema name
        primary_key: Primary key column

    Returns:
        PostgreSQLTarget configured for PlanetScale
    """
    config = PostgreSQLConfig.from_env("PLANETSCALE_")
    return PostgreSQLTarget(
        config=config,
        table=table,
        schema=schema,
        primary_key=primary_key,
    )


def create_postgres_target(
    host: str,
    database: str,
    user: str,
    password: str,
    table: str = "exported_data",
    schema: str = "public",
    primary_key: str | None = None,
) -> PostgreSQLTarget:
    """Create PostgreSQL target with explicit credentials.

    Args:
        host: Database host
        database: Database name
        user: Username
        password: Password
        table: Table name
        schema: Schema name
        primary_key: Primary key column

    Returns:
        PostgreSQLTarget instance
    """
    config = PostgreSQLConfig(
        host=host,
        database=database,
        user=user,
        password=password,
    )
    return PostgreSQLTarget(
        config=config,
        table=table,
        schema=schema,
        primary_key=primary_key,
    )
