"""Database utilities for Croílár.

Provides a singleton DuckDB connection pool with typed query helpers.
Replaces the previous sruth.shared dependency so the croilar subproject
can be imported standalone.
"""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Sequence

import duckdb

_DEFAULT_DB_PATH = "./data/croilar.duckdb"

_lock = threading.Lock()
_conn: duckdb.DuckDBPyConnection | None = None


def get_db_path() -> Path:
    """Resolve the DuckDB file path.

    Priority:
      1. CROILAR_DUCKDB_PATH env var
      2. DUCKDB_PATH env var
      3. ./data/croilar.duckdb (default)
    """
    env = os.environ.get("CROILAR_DUCKDB_PATH") or os.environ.get("DUCKDB_PATH")
    if env:
        return Path(env).expanduser().resolve()
    return Path(_DEFAULT_DB_PATH).expanduser().resolve()


def get_connection() -> duckdb.DuckDBPyConnection:
    """Return a process-singleton read-only DuckDB connection.

    DuckDB has a single-writer lock, but unlimited readers. The web SSR
    loaders only need reads, so a singleton read-only connection is safe.
    """
    global _conn
    if _conn is None:
        with _lock:
            if _conn is None:
                path = str(get_db_path())
                _conn = duckdb.connect(path, read_only=True)
    return _conn


@contextmanager
def writer() -> Iterator[duckdb.DuckDBPyConnection]:
    """Yield a write connection (caller is responsible for committing).

    Use sparingly — DuckDB serialises writes. Prefer the DLT pipelines
    for bulk ingestion.
    """
    path = str(get_db_path())
    conn = duckdb.connect(path)
    try:
        yield conn
    finally:
        conn.close()


def query(sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
    """Execute a SELECT and return all rows as dicts (or typed rows)."""
    conn = get_connection()
    if params:
        result = conn.execute(sql, list(params))
    else:
        result = conn.execute(sql)
    columns = [d[0] for d in result.description]
    return [dict(zip(columns, row)) for row in result.fetchall()]


def query_one(sql: str, params: Sequence[Any] | None = None) -> dict[str, Any] | None:
    """Execute a SELECT and return the first row or None."""
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: Sequence[Any] | None = None) -> None:
    """Execute a write SQL statement. Use writer() context manager for transactions."""
    with writer() as conn:
        if params:
            conn.execute(sql, list(params))
        else:
            conn.execute(sql)


def close() -> None:
    """Close the singleton connection. Useful in tests."""
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


__all__ = [
    "get_db_path",
    "get_connection",
    "writer",
    "query",
    "query_one",
    "execute",
    "close",
]
