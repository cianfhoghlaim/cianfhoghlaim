"""
Storage utilities for database access.

Provides thread-safe, serial access to databases that require
single-threaded operation (DuckDB, LanceDB within-process).

Includes clients for:
- DuckDB: SQL analytics with single-threaded safety
- LanceDB: Vector storage with HNSW index management
"""

from .duckdb_client import DuckDBClient
from .lancedb_client import HNSW_DROP_THRESHOLD, LanceDBClient
from .serial_executor import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
)

__all__ = [
    # Serial execution
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
    # Clients
    "DuckDBClient",
    "LanceDBClient",
    "HNSW_DROP_THRESHOLD",
]
