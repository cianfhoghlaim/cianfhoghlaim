"""Shared Pipeline Utilities.

Common utilities for all Aleyum data pipelines.
"""

from pipelines.shared.destinations import create_duckdb_destination, create_ducklake_destination
from pipelines.shared.r2_client import R2Client

__all__ = ["R2Client", "create_duckdb_destination", "create_ducklake_destination"]
