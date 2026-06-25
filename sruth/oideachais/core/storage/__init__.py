"""
Storage utilities for database access.

Provides thread-safe, serial access to databases that require
single-threaded operation (DuckDB, LanceDB within-process).

Includes clients for:
- DuckDB: SQL analytics with single-threaded safety
- LanceDB: Vector storage with HNSW index management
- DuckLake: Postgres-catalog + Garage S3 connection (with OCR storage + filesystem)
- LanceDB Cloud: Managed cloud integration (paused $100 credits)
- Lance + Iceberg: Multi-modal backend
- Multi-backend config: Cognee, DuckLake, FalkorDB, Garage, Lakehouse, LanceDB,
  Memgraph, PlanetScale
- Curriculum-specific vector search (BGE-M3 powered)
"""

from .config import (
    CogneeConfig,
    DuckLakeConfig,
    FalkorDBConfig,
    GarageConfig,
    LakehouseConfig,
    LanceDBConfig,
    MemgraphConfig,
    PlanetScaleConfig,
    RedisConfig,
    StorageConfig,
    get_config,
    reset_config,
)
from .connections import (
    StorageBackend,
    StorageManager,
    get_storage_backend,
    get_storage_manager,
)
from .curriculum_vectors import (
    DEFAULT_EMBEDDING_DIM,
    CurriculumEmbedding,
    CurriculumVectorSearch,
    SimpleHashEmbedder,
    get_curriculum_search,
)
from .duckdb_client import DuckDBClient
from .init_schemas import (
    create_spatial_indexes,
    init_database,
)
from .lance_iceberg import (
    LanceIcebergBackend,
    LanceIcebergClient,
    LanceTableInfo,
    get_lance_iceberg_backend,
)
from .lancedb_client import HNSW_DROP_THRESHOLD, LanceDBClient
from .serial_executor import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
)

# Clients subpackage (DuckLake variants + LanceDB Cloud)
# Note: `core/storage/ducklake.py` (legacy Garage+PlanetScale variant) and
# `core/storage/clients/ducklake.py` (newer SQLite/Postgres variant) both
# define DuckLakeClient / DuckLakeSnapshot / DuckLakeBackend /
# get_ducklake_backend / CELTIC_MANUSCRIPT_SCHEMAS. We re-export the
# `clients/` variant as the canonical; the legacy `ducklake.py` remains
# importable explicitly via `sruth.oideachais.core.storage.ducklake`.
from .clients.ducklake import (
    CELTIC_MANUSCRIPT_SCHEMAS,
    CatalogType,
    DuckLakeBackend,
    DuckLakeClient,
    DuckLakeConfig,
    DuckLakeSnapshot,
    get_ducklake_backend,
)
from .clients.ducklake_filesystem import (
    DuckLakeOCRStorage,
    MockConnection,
    OCR_STORAGE_SCHEMAS,
    OCRResultRecord,
    OCRStorageConfig,
    create_storage,
    get_default_storage,
)
from .clients.lancedb_cloud import (
    EmbeddingBatch,
    LanceDBCloudClient,
    LanceDBCloudConfig,
    LanceDBEnvironment,
    get_lancedb_client,
)

__all__ = [
    # Serial execution
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
    # Core clients
    "DuckDBClient",
    "LanceDBClient",
    "HNSW_DROP_THRESHOLD",
    # Config (multi-backend)
    "CogneeConfig",
    "DuckLakeConfig",
    "FalkorDBConfig",
    "GarageConfig",
    "LakehouseConfig",
    "LanceDBConfig",
    "MemgraphConfig",
    "PlanetScaleConfig",
    "RedisConfig",
    "StorageConfig",
    "get_config",
    "reset_config",
    # Connections / Storage abstraction
    "StorageBackend",
    "StorageManager",
    "get_storage_backend",
    "get_storage_manager",
    # DuckLake (canonical: clients/ variant)
    "CELTIC_MANUSCRIPT_SCHEMAS",
    "CatalogType",
    "DuckLakeBackend",
    "DuckLakeClient",
    "DuckLakeConfig",
    "DuckLakeSnapshot",
    "get_ducklake_backend",
    # DuckLake Filesystem (OCR storage)
    "DuckLakeOCRStorage",
    "MockConnection",
    "OCR_STORAGE_SCHEMAS",
    "OCRResultRecord",
    "OCRStorageConfig",
    "create_storage",
    "get_default_storage",
    # Schema bootstrap
    "create_spatial_indexes",
    "init_database",
    # Lance + Iceberg
    "LanceIcebergBackend",
    "LanceIcebergClient",
    "LanceTableInfo",
    "get_lance_iceberg_backend",
    # LanceDB Cloud
    "EmbeddingBatch",
    "LanceDBCloudClient",
    "LanceDBCloudConfig",
    "LanceDBEnvironment",
    "get_lancedb_client",
    # Curriculum-specific
    "DEFAULT_EMBEDDING_DIM",
    "CurriculumEmbedding",
    "CurriculumVectorSearch",
    "SimpleHashEmbedder",
    "get_curriculum_search",
]
