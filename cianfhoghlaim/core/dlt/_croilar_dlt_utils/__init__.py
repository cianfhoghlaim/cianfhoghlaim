"""
DLT utilities for croilar pipeline.

Provides environment-aware DuckLake destination factory for concurrent writes.
"""

from . import destinations
from .destinations import (
    NAMESPACE,
    create_pipeline,
    get_dlt_destination,
    get_duckdb_fallback_destination,
)

__all__ = [
    "NAMESPACE",
    "create_pipeline",
    "destinations",
    "get_dlt_destination",
    "get_duckdb_fallback_destination",
]
