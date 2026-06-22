"""
Shared utilities for crypto data pipelines.
"""

from pipelines.shared.config_loader import (
    load_sources_config,
    load_databases_config,
    get_source_config,
    get_database_config,
    SourceConfig,
    DatabaseConfig,
)
from pipelines.shared.duckdb_destination import (
    create_duckdb_destination,
    get_duckdb_connection,
    create_destination,
)

__all__ = [
    "load_sources_config",
    "load_databases_config",
    "get_source_config",
    "get_database_config",
    "SourceConfig",
    "DatabaseConfig",
    "create_duckdb_destination",
    "get_duckdb_connection",
    "create_destination",
]
