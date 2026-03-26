"""
Multi-Database Storage Layer for Celtic Education Pipeline.

Provides unified access to:
- LanceDB (local/remote) for vector storage with namespacing
- PlanetScale PostgreSQL for structured metadata
- DuckDB/MotherDuck for analytics with Spatial extension
- Garage S3-compatible storage for PDFs and documents
- DuckLake SQL catalog for ACID transactions and time-travel
- Lance via Iceberg REST catalog for unified discovery
"""

# Serial executor from core.storage (authoritative location)
from ..core.storage import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
)
from .config import (
    CogneeConfig,
    DuckLakeConfig,
    FalkorDBConfig,
    GarageConfig,
    LakehouseConfig,
    LanceDBConfig,
    MemgraphConfig,
    PlanetScaleConfig,
    StorageConfig,
    get_config,
    reset_config,
)
from .connections import (
    DuckLakeBackend,
    GarageBackend,
    LanceDBBackend,
    PlanetScaleBackend,
    StorageBackend,
    StorageManager,
    get_storage_backend,
    get_storage_manager,
)
from .ducklake import (
    CELTIC_MANUSCRIPT_SCHEMAS,
    DuckLakeClient,
    DuckLakeSnapshot,
    get_ducklake_backend,
)
from .ducklake_filesystem import (
    OCR_STORAGE_SCHEMAS,
    ComparisonRecord,
    DuckLakeOCRStorage,
    OCRResultRecord,
    OCRStorageConfig,
    SnapshotRecord,
    create_storage,
    get_default_storage,
)
from .lance_iceberg import (
    LanceIcebergBackend,
    LanceIcebergClient,
    LanceTableInfo,
    get_lance_iceberg_backend,
)

__all__ = [
    # Config classes
    "PlanetScaleConfig",
    "LanceDBConfig",
    "DuckLakeConfig",
    "GarageConfig",
    "LakehouseConfig",
    "MemgraphConfig",
    "FalkorDBConfig",
    "CogneeConfig",
    "StorageConfig",
    "get_config",
    "reset_config",
    # Storage backends
    "StorageBackend",
    "LanceDBBackend",
    "PlanetScaleBackend",
    "DuckLakeBackend",
    "GarageBackend",
    "StorageManager",
    "get_storage_backend",
    "get_storage_manager",
    # DuckLake
    "CELTIC_MANUSCRIPT_SCHEMAS",
    "DuckLakeClient",
    "DuckLakeSnapshot",
    "get_ducklake_backend",
    # Lance Iceberg
    "LanceIcebergClient",
    "LanceIcebergBackend",
    "LanceTableInfo",
    "get_lance_iceberg_backend",
    # OCR Storage
    "OCRStorageConfig",
    "OCR_STORAGE_SCHEMAS",
    "OCRResultRecord",
    "ComparisonRecord",
    "SnapshotRecord",
    "DuckLakeOCRStorage",
    "create_storage",
    "get_default_storage",
    # Serial executor
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
]
