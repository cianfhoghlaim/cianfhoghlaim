"""
Embedding utilities for sruth data pipelines.

Provides batched embedding generation with performance optimizations
and multi-provider support.
"""

from .batcher import (
    DEFAULT_BATCH_SIZE,
    MIN_BATCH_SIZE,
    EmbeddingBatcher,
    batch_embed,
)
from .service import (
    EMBEDDING_MODELS,
    EmbeddingModel,
    EmbeddingProvider,
    EmbeddingService,
    embed_texts,
    get_embedding_service,
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
