"""
DLT utilities for aleyum pipeline.

Provides environment-aware DuckLake destination factory for concurrent writes.
"""

from . import destinations
from .destinations import (
    DuckLakeConfig,
    create_pipeline,
    get_dlt_destination,
    get_duckdb_fallback,
)

__all__ = [
    "destinations",
    "DuckLakeConfig",
    "get_dlt_destination",
    "get_duckdb_fallback",
    "create_pipeline",
]
