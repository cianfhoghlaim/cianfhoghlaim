"""
DuckDB Client for sruth data pipelines.

Provides a safe, single-threaded DuckDB connection manager
that integrates with SerialDatabaseExecutor.

CRITICAL: DuckDB is SINGLE_THREADED_ONLY - concurrent access causes segfaults.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

from .serial_executor import get_executor, SerialDatabaseExecutor

logger = logging.getLogger(__name__)


class DuckDBClient:
    """
    Safe DuckDB client with automatic serial execution.

    All operations are automatically routed through SerialDatabaseExecutor
    to prevent concurrent access issues.

    Usage:
        client = DuckDBClient(path="./data/my_db.duckdb")

        # Query
        results = client.query("SELECT * FROM users WHERE active = ?", [True])

        # Execute
        client.execute("INSERT INTO users (name) VALUES (?)", ["Alice"])

        # Batch insert
        client.insert_batch("users", [{"name": "Bob"}, {"name": "Carol"}])

        # Context manager for transactions
        with client.transaction() as conn:
            conn.execute("UPDATE users SET active = false")
            conn.execute("DELETE FROM sessions")
    """

    def __init__(
        self,
        path: Union[str, Path] = ":memory:",
        read_only: bool = False,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize DuckDB client.

        Args:
            path: Database file path or ":memory:" for in-memory
            read_only: Open in read-only mode
            config: DuckDB configuration options
        """
        self.path = Path(path) if path != ":memory:" else path
        self.read_only = read_only
        self.config = config or {}
        self._connection = None
        self._executor = get_executor()

        # Ensure parent directory exists
        if isinstance(self.path, Path):
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self):
        """Get or create DuckDB connection (internal use only)."""
        if self._connection is None:
            import duckdb

            self._connection = duckdb.connect(
                str(self.path),
                read_only=self.read_only,
                config=self.config,
            )
            logger.info(f"Connected to DuckDB: {self.path}")
        return self._connection

    def query(
        self,
        sql: str,
        params: Optional[List[Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a query and return results as list of dicts.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            List of row dictionaries
        """
        def _execute():
            conn = self._get_connection()
            if params:
                result = conn.execute(sql, params)
            else:
                result = conn.execute(sql)
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]

        return self._executor.run(_execute)

    def query_df(self, sql: str, params: Optional[List[Any]] = None):
        """
        Execute a query and return results as pandas DataFrame.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            pandas DataFrame
        """
        def _execute():
            conn = self._get_connection()
            if params:
                return conn.execute(sql, params).fetchdf()
            return conn.execute(sql).fetchdf()

        return self._executor.run(_execute)

    def execute(
        self,
        sql: str,
        params: Optional[List[Any]] = None,
    ) -> int:
        """
        Execute a statement (INSERT, UPDATE, DELETE).

        Args:
            sql: SQL statement
            params: Statement parameters

        Returns:
            Number of affected rows
        """
        def _execute():
            conn = self._get_connection()
            if params:
                result = conn.execute(sql, params)
            else:
                result = conn.execute(sql)
            return result.rowcount if hasattr(result, 'rowcount') else -1

        return self._executor.run(_execute)

    def execute_many(
        self,
        sql: str,
        params_list: List[List[Any]],
    ) -> int:
        """
        Execute a statement multiple times with different parameters.

        Args:
            sql: SQL statement
            params_list: List of parameter lists

        Returns:
            Total number of affected rows
        """
        def _execute():
            conn = self._get_connection()
            total = 0
            for params in params_list:
                result = conn.execute(sql, params)
                if hasattr(result, 'rowcount'):
                    total += result.rowcount
            return total

        return self._executor.run(_execute)

    def insert_batch(
        self,
        table: str,
        rows: List[Dict[str, Any]],
        on_conflict: Optional[str] = None,
    ) -> int:
        """
        Batch insert rows from list of dicts.

        Args:
            table: Target table name
            rows: List of row dictionaries
            on_conflict: Optional conflict resolution (e.g., "DO NOTHING")

        Returns:
            Number of inserted rows
        """
        if not rows:
            return 0

        def _execute():
            import duckdb

            conn = self._get_connection()

            # Create DataFrame and insert
            import pandas as pd
            df = pd.DataFrame(rows)

            # Register as view and insert
            conn.register("_batch_insert_temp", df)

            conflict_clause = f" ON CONFLICT {on_conflict}" if on_conflict else ""
            sql = f"INSERT INTO {table} SELECT * FROM _batch_insert_temp{conflict_clause}"

            result = conn.execute(sql)
            conn.unregister("_batch_insert_temp")

            return len(rows)

        return self._executor.run(_execute)

    def table_exists(self, table: str) -> bool:
        """Check if a table exists."""
        result = self.query(
            "SELECT COUNT(*) as cnt FROM information_schema.tables WHERE table_name = ?",
            [table],
        )
        return result[0]["cnt"] > 0

    def get_schema(self, table: str) -> List[Dict[str, Any]]:
        """Get table schema information."""
        return self.query(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = ?
            ORDER BY ordinal_position
            """,
            [table],
        )

    @contextmanager
    def transaction(self) -> Generator[Any, None, None]:
        """
        Context manager for transactions.

        Usage:
            with client.transaction() as conn:
                conn.execute("UPDATE users SET active = false")
                conn.execute("DELETE FROM sessions")
        """
        def _begin():
            conn = self._get_connection()
            conn.execute("BEGIN TRANSACTION")
            return conn

        def _commit():
            self._get_connection().execute("COMMIT")

        def _rollback():
            self._get_connection().execute("ROLLBACK")

        conn = self._executor.run(_begin)
        try:
            yield conn
            self._executor.run(_commit)
        except Exception:
            self._executor.run(_rollback)
            raise

    def close(self) -> None:
        """Close the database connection."""
        def _close():
            if self._connection:
                self._connection.close()
                self._connection = None
                logger.info(f"Closed DuckDB connection: {self.path}")

        self._executor.run(_close)

    def __enter__(self) -> "DuckDBClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
