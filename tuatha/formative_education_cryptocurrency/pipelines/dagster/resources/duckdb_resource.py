"""DuckDB destination resource for local development."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Generator

import dagster as dg
import duckdb
from pydantic import Field

if TYPE_CHECKING:
    from duckdb import DuckDBPyConnection


class DuckDBResource(dg.ConfigurableResource):
    """DuckDB resource for local development destination.

    Provides connection management and DLT destination configuration
    for local DuckDB database files.

    Example:
        ```python
        @asset(required_resource_keys={"destination"})
        def my_asset(context):
            with context.resources.destination.connect() as conn:
                conn.execute("SELECT * FROM my_table")
        ```
    """

    database_path: str = Field(
        default_factory=lambda: os.getenv(
            "DUCKDB_PATH",
            "./data/github_intelligence.duckdb"
        ),
        description="Path to DuckDB database file"
    )

    @contextmanager
    def connect(self) -> Generator[DuckDBPyConnection, None, None]:
        """Yield a DuckDB connection.

        Creates parent directories if they don't exist.
        """
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect(self.database_path)
        try:
            yield conn
        finally:
            conn.close()

    def get_dlt_destination(self):
        """Return DLT destination configuration for DuckDB."""
        import dlt
        return dlt.destinations.duckdb(self.database_path)

    def get_dlt_destination_name(self) -> str:
        """Return the DLT destination name string."""
        return "duckdb"

    def get_connection_string(self) -> str:
        """Return the database path for direct connections."""
        return self.database_path
