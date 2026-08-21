"""Shared DLT utilities for all sruth projects."""

from .lakehouse import (
    DuckLakeConfig,
    get_lakehouse_destination,
    get_duckdb_fallback,
    create_lakehouse_pipeline,
)

__all__ = [
    "DuckLakeConfig",
    "get_lakehouse_destination",
    "get_duckdb_fallback",
    "create_lakehouse_pipeline",
]
