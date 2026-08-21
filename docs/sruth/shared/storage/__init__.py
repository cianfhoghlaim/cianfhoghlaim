"""Shared storage utilities for all sruth flows.

Provides unified interface for:
- Table storage (DuckDB, Iceberg/Lakekeeper, PostgreSQL)
- Object storage (S3, Garage, R2)
- Vector storage (LanceDB, Qdrant)
- Hybrid storage (MotherDuck + PlanetScale)
- PostgreSQL targets (CocoIndex export)
- Lance namespaces with Lakekeeper integration
- PDF storage with content-addressing (S3/Garage)
"""

from .unified_storage import (
    # Abstract interfaces
    TableStorage,
    ObjectStorage,
    VectorStorage,
    # References
    TableRef,
    ObjectRef,
    # Results
    TableWriteResult,
    # Storage types
    StorageType,
    # Implementations
    DuckDBTableStorage,
    S3ObjectStorage,
    IcebergTableStorage,
    # Unified interface
    UnifiedStorage,
    get_storage,
    get_default_storage,
)

from .motherduck import (
    MotherDuckConfig,
    PlanetScaleConfig,
    MotherDuckStorage,
    get_motherduck_storage,
    reset_motherduck_storage,
)

from .postgres_target import (
    PostgreSQLConfig,
    PostgreSQLTarget,
    ColumnDef,
    create_planetscale_target,
    create_postgres_target,
)

from .lance_namespace import (
    EDUCATION_NAMESPACES,
    LanceTableConfig,
    LanceNamespaceManager,
    create_curriculum_namespace,
    get_lance_config,
)

from .pdf_storage import (
    PDFStorageResource,
    pdf_storage_resource,
    PDFMetadata,
    StoreResult,
    PageImageResult,
)

__all__ = [
    # Abstract interfaces
    "TableStorage",
    "ObjectStorage",
    "VectorStorage",
    # References
    "TableRef",
    "ObjectRef",
    # Results
    "TableWriteResult",
    # Storage types
    "StorageType",
    # Implementations
    "DuckDBTableStorage",
    "S3ObjectStorage",
    "IcebergTableStorage",
    # Unified interface
    "UnifiedStorage",
    "get_storage",
    "get_default_storage",
    # MotherDuck + PlanetScale
    "MotherDuckConfig",
    "PlanetScaleConfig",
    "MotherDuckStorage",
    "get_motherduck_storage",
    "reset_motherduck_storage",
    # PostgreSQL targets
    "PostgreSQLConfig",
    "PostgreSQLTarget",
    "ColumnDef",
    "create_planetscale_target",
    "create_postgres_target",
    # Lance namespaces
    "EDUCATION_NAMESPACES",
    "LanceTableConfig",
    "LanceNamespaceManager",
    "create_curriculum_namespace",
    "get_lance_config",
    # PDF storage
    "PDFStorageResource",
    "pdf_storage_resource",
    "PDFMetadata",
    "StoreResult",
    "PageImageResult",
]
