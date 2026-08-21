"""
Embedding utilities for sruth data pipelines.

Provides batched embedding generation with performance optimizations
and multi-provider support.
"""

from .batcher import (
    EmbeddingBatcher,
    batch_embed,
    MIN_BATCH_SIZE,
    DEFAULT_BATCH_SIZE,
)
from .service import (
    EmbeddingService,
    EmbeddingProvider,
    EmbeddingModel,
    EMBEDDING_MODELS,
    get_embedding_service,
    embed_texts,
)

__all__ = [
    # Batcher
    "EmbeddingBatcher",
    "batch_embed",
    "MIN_BATCH_SIZE",
    "DEFAULT_BATCH_SIZE",
    # Service
    "EmbeddingService",
    "EmbeddingProvider",
    "EmbeddingModel",
    "EMBEDDING_MODELS",
    "get_embedding_service",
    "embed_texts",
]
