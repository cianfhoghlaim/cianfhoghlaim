"""
Dagster resource definitions for the ingestion pipeline.

Resources:
- DuckDBResource: Local DuckDB database destination
- DuckLakeResource: Production DuckLake with S3/R2 storage
"""

from dagster.resources.duckdb_resource import DuckDBResource
from dagster.resources.ducklake_resource import DuckLakeResource

__all__ = [
    "DuckDBResource",
    "DuckLakeResource",
]
