"""
Embedding utilities for Aleyum.

Provides batched embedding generation with minimum batch size enforcement
to ensure optimal performance (100x speedup with batching).
"""

from .batcher import EmbeddingBatcher, batch_embed

__all__ = [
    "EmbeddingBatcher",
    "batch_embed",
]
