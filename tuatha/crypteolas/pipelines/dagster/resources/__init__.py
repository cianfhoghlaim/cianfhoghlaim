"""
Dagster resource definitions for the ingestion pipeline.

Resources:
- DuckDBResource: Local DuckDB database destination
- DuckLakeResource: Production DuckLake with S3/R2 storage
"""

from .duckdb_resource import DuckDBResource
from .ducklake_resource import DuckLakeResource

__all__ = [
    "DuckDBResource",
    "DuckLakeResource",
]
