"""
Core utilities for oideachais pipeline.

Contains storage utilities and will contain utils after consolidation.
"""

# Storage (local - authoritative)
from .storage import (
    HNSW_DROP_THRESHOLD,
    DuckDBClient,
    LanceDBClient,
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
)

# Utils (local - authoritative)
from .utils import (
    CircuitBreaker,
    CircuitBreakerOpen,
    RateLimiter,
    RateLimitError,
    RetryableError,
    Retryer,
    SlidingWindowRateLimiter,
    retry_with_backoff,
    retry_with_backoff_async,
)

__all__ = [
    "HNSW_DROP_THRESHOLD",
    # Utils
    "CircuitBreaker",
    "CircuitBreakerOpen",
    "DuckDBClient",
    "LanceDBClient",
    "RateLimitError",
    "RateLimiter",
    "RetryableError",
    "Retryer",
    # Storage
    "SerialDatabaseExecutor",
    "SlidingWindowRateLimiter",
    "get_executor",
    "retry_with_backoff",
    "retry_with_backoff_async",
    "run_serial",
]
