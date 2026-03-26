"""
Shared helper functions for crypteolas assets.
"""

import os


def get_duckdb_path() -> str:
    """Get DuckDB database path from environment or default."""
    return os.environ.get("DUCKDB_PATH", "data/crypto_analytics.duckdb")
