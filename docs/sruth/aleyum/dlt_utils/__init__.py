"""
DLT utilities for aleyum pipeline.

Provides environment-aware DuckLake destination factory for concurrent writes.
"""

from . import destinations
from .destinations import (
    DuckLakeConfig,
    get_dlt_destination,
    get_duckdb_fallback,
    create_pipeline,
)

__all__ = [
    "destinations",
    "DuckLakeConfig",
    "get_dlt_destination",
    "get_duckdb_fallback",
    "create_pipeline",
]
