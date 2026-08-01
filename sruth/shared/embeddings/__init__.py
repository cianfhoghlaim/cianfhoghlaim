"""
Shared Embedding Module for Sruth Pipelines.

This module provides canonical implementations for:
- Embedding generation with mandatory batching (min 100)
- Embedding caching for performance
- Dagster asset templates for embedding workflows

CRITICAL: Per CLAUDE.md MODIFICATION_RULES:
- ALWAYS batch embeddings (min: 100, max: provider_limit)
- Drop HNSW indexes before bulk inserts >50 rows (20x speedup)
- Recreate indexes after batch complete

Usage:
    from sruth.shared.embeddings import EmbeddingClient, EmbeddingCache
    from sruth.shared.embeddings import create_embedding_asset

    # Generate embeddings
    client = EmbeddingClient(model="BAAI/bge-m3")
    embeddings = client.embed_batch(texts)  # Auto-batched

    # Or use Dagster asset template
    @asset
    def my_embeddings(context):
        return create_embedding_asset(context, texts)
"""

from __future__ import annotations

import logging
from typing import Any

from sruth.shared.embeddings.cache import EmbeddingCache
from sruth.shared.embeddings.client import EmbeddingClient
from sruth.shared.embeddings.models import (
    EmbeddingConfig,
    EmbeddingModels,
    ModelProvider,
)

__all__ = [
    "EmbeddingClient",
    "EmbeddingCache",
    "EmbeddingConfig",
    "EmbeddingModels",
    "ModelProvider",
    # Convenience functions
    "get_embedding_client",
    "get_embedding_cache",
]

logger = logging.getLogger(__name__)


# Singleton instances for reuse
_client_cache: dict[str, EmbeddingClient] = {}
_cache_cache: dict[str, EmbeddingCache] = {}


def get_embedding_client(
    model: str = EmbeddingModels.BGE_M3,
    batch_size: int = 100,
    **kwargs,
) -> EmbeddingClient:
    """Get or create an embedding client (singleton per model).

    Args:
        model: Model name (default: BAAI/bge-m3)
        batch_size: Minimum batch size for performance (default: 100)
        **kwargs: Additional arguments for EmbeddingClient

    Returns:
        EmbeddingClient instance
    """
    cache_key = f"{model}:{batch_size}"
    if cache_key not in _client_cache:
        _client_cache[cache_key] = EmbeddingClient(
            model=model,
            batch_size=batch_size,
            **kwargs,
        )
    return _client_cache[cache_key]


def get_embedding_cache(
    cache_dir: str | None = None,
    max_size: int = 10_000,
) -> EmbeddingCache:
    """Get or create an embedding cache (singleton).

    Args:
        cache_dir: Directory for cache storage
        max_size: Maximum number of cached embeddings

    Returns:
        EmbeddingCache instance
    """
    cache_key = f"{cache_dir}:{max_size}"
    if cache_key not in _cache_cache:
        _cache_cache[cache_key] = EmbeddingCache(
            cache_dir=cache_dir,
            max_size=max_size,
        )
    return _cache_cache[cache_key]
