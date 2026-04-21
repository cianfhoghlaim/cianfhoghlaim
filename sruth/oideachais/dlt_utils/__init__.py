"""
DLT (Data Load Tool) utilities for oideachais pipeline.

Provides:
- Source mixins for common patterns (pagination, rate limiting, caching)
- DuckLake destination factory (local/production switching)
- SerialDatabaseExecutor integration for DuckDB safety
- Embedding batching utilities for 100x performance improvement
"""

# Source mixins
# Batching utilities
from .batching import (
    HNSW_DROP_THRESHOLD,
    MINIMUM_BATCH_SIZE,
    EmbeddingBatcher,
    batch_embeddings,
    batch_items,
    calculate_optimal_batch_size,
    should_drop_hnsw,
)

# Destination factory
from .destinations import (
    create_pipeline,
    get_dlt_destination,
    get_duckdb_fallback_destination,
)
from .mixins import (
    AuthenticatedSourceMixin,
    CachedSourceMixin,
    IncrementalSourceMixin,
    PaginatedSourceMixin,
    RateLimitedSourceMixin,
)

# Safety wrappers
from .safety import (
    safe_dataset_query,
    safe_dlt_load,
    safe_dlt_normalize,
    safe_dlt_run,
)

__all__ = [
    # Mixins
    "PaginatedSourceMixin",
    "RateLimitedSourceMixin",
    "CachedSourceMixin",
    "AuthenticatedSourceMixin",
    "IncrementalSourceMixin",
    # Destinations
    "get_dlt_destination",
    "get_duckdb_fallback_destination",
    "create_pipeline",
    # Safety
    "safe_dlt_run",
    "safe_dlt_normalize",
    "safe_dlt_load",
    "safe_dataset_query",
    # Batching
    "MINIMUM_BATCH_SIZE",
    "HNSW_DROP_THRESHOLD",
    "batch_embeddings",
    "batch_items",
    "EmbeddingBatcher",
    "should_drop_hnsw",
    "calculate_optimal_batch_size",
]
