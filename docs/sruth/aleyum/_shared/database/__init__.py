"""
Database utilities for Aleyum.

Re-exports SerialDatabaseExecutor from sruth.shared for single-threaded
DuckDB/LanceDB access, plus adds aleyum-specific database clients.
"""

from sruth.shared import SerialDatabaseExecutor, get_executor, run_serial

__all__ = [
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
]
