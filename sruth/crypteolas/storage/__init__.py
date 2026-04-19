"""
Crypteolas Storage Layer.

Provides unified access to multi-tier storage:
- LanceDB: Vector embeddings with Lance REST catalog
- Garage: S3-compatible object storage for raw documents
- DuckDB + MotherDuck: Analytics and hybrid queries
- DuckLake: ACID lakehouse with time-travel
- PlanetScale PostgreSQL: Metadata and Lakekeeper storage
- Lakekeeper: Lance REST catalog namespace

Architecture:
    Raw Documents (PDFs, HTML) -> Garage S3
    Markdown/Text -> DuckLake tables
    Embeddings -> LanceDB with Lakekeeper catalog
    Analytics -> DuckDB/MotherDuck
"""

from .config import StorageConfig, get_storage_config
from .ducklake_client import DuckLakeClient, DuckLakeConfig, get_ducklake_client
from .garage_client import GarageClient, GarageConfig, get_garage_client
from .lakekeeper_client import LakekeeperClient, LakekeeperConfig, get_lakekeeper_client
from .lance_catalog import LanceCatalog, get_lance_catalog

# TODO: Import serial executor from shared infrastructure when available
# from sruth.shared.storage import (
#     SerialDatabaseExecutor,
#     get_executor,
#     run_serial,
# )

__all__ = [
    # Config
    "StorageConfig",
    "get_storage_config",
    # DuckLake
    "DuckLakeClient",
    "DuckLakeConfig",
    "get_ducklake_client",
    # Garage S3
    "GarageClient",
    "GarageConfig",
    "get_garage_client",
    # Lakekeeper
    "LakekeeperClient",
    "LakekeeperConfig",
    "get_lakekeeper_client",
    # Lance Catalog
    "LanceCatalog",
    "get_lance_catalog",
    # TODO: Serial executor (disabled until shared infrastructure available)
    # "SerialDatabaseExecutor",
    # "get_executor",
    # "run_serial",
]
