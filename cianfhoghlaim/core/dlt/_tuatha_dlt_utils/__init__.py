"""
DLT utilities for tuath pipeline.

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
    "DuckLakeConfig",
    "create_pipeline",
    "destinations",
    "get_dlt_destination",
    "get_duckdb_fallback",
]
