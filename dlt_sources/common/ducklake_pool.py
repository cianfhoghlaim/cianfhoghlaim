"""DuckLake connection pool + time-travel helper.

Per the 2026-08-07-biep-v3-hardening-v1 change.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any


class DuckLakeConnectionPool:
    """A simple connection pool for DuckLake connections.

    Used by the 8 BIEP v3 jurisdiction pipelines + the 4-path OCR ensemble
    so we don't spin up 32 fresh connections per materialization.
    """

    def __init__(self, max_size: int = 8):
        self.max_size = max_size
        self._connections: list[Any] = []
        self._in_use: set[Any] = set()

    @contextmanager
    def acquire(self, uri: str = "md:cianfhoghlaim"):
        """Acquire a connection from the pool."""
        # Try to reuse a free connection
        for conn in self._connections:
            if conn not in self._in_use:
                self._in_use.add(conn)
                try:
                    yield conn
                finally:
                    self._in_use.discard(conn)
                return

        # Create a new connection (or wait if pool full)
        if len(self._in_use) < self.max_size:
            try:
                import duckdb
                conn = duckdb.connect(uri, read_only=False)
            except ImportError as exc:
                raise ImportError("duckdb required for DuckLakeConnectionPool") from exc
            self._connections.append(conn)
            self._in_use.add(conn)
            try:
                yield conn
            finally:
                self._in_use.discard(conn)
            return

        # Pool exhausted
        raise RuntimeError(
            f"DuckLakeConnectionPool exhausted ({self.max_size} connections in use)"
        )


def time_travel_query(
    conn,
    table: str,
    at_timestamp: str | None = None,
    version: int | None = None,
) -> Any:
    """Query a DuckLake table at a specific timestamp or version.

    Per the DuckLake 1.0 docs, the syntax is `SELECT * FROM tbl AT
    (TIMESTAMP => '...')` or `AT (VERSION => N)`.
    """
    if at_timestamp is None and version is None:
        raise ValueError("either at_timestamp or version must be provided")
    if at_timestamp is not None:
        sql = f"SELECT * FROM {table} AT (TIMESTAMP => '{at_timestamp}')"
    else:
        sql = f"SELECT * FROM {table} AT (VERSION => {version})"
    return conn.sql(sql).execute()


__all__ = ["DuckLakeConnectionPool", "time_travel_query"]
