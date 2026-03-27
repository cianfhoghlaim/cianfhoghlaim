"""
Tuath Storage Layer.

Provides storage utilities for the Celtic MMO project:
- SerialDatabaseExecutor: Thread-safe DuckDB operations
"""

from .serial_executor import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
)

__all__ = [
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
]
