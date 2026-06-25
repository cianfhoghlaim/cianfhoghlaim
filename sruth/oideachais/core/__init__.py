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
    # Storage
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
    "DuckDBClient",
    "LanceDBClient",
    "HNSW_DROP_THRESHOLD",
    # Utils
    "CircuitBreaker",
    "CircuitBreakerOpen",
    "RateLimiter",
    "SlidingWindowRateLimiter",
    "RetryableError",
    "RateLimitError",
    "retry_with_backoff",
    "retry_with_backoff_async",
    "Retryer",
]
