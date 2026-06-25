"""
Embedding Batcher for Aleyum.

CRITICAL: Always batch embeddings for 100x performance improvement.
- Unbatched 1000 texts: ~100s
- Batched 1000 texts: ~1s

This module enforces minimum batch sizes and provides utilities
for efficient embedding generation.
"""

import logging
from typing import Callable, List

logger = logging.getLogger(__name__)

# Minimum batch size for optimal performance
MIN_BATCH_SIZE = 100
DEFAULT_BATCH_SIZE = 256


class EmbeddingBatcher:
    """
    Batched embedding generator with performance optimizations.

    Usage:
        batcher = EmbeddingBatcher(embed_fn=model.encode)
        embeddings = batcher.embed(texts)

    The batcher automatically:
    - Batches texts for optimal API performance
    - Warns if batch sizes are suboptimal
    - Handles large text lists efficiently
    """

    def __init__(
        self,
        embed_fn: Callable[[List[str]], List[List[float]]],
        batch_size: int = DEFAULT_BATCH_SIZE,
        min_batch_size: int = MIN_BATCH_SIZE,
    ):
        """
        Initialize the embedding batcher.

        Args:
            embed_fn: Function that takes list of texts, returns list of embeddings
            batch_size: Number of texts per batch
            min_batch_size: Minimum batch size before warning
        """
        self.embed_fn = embed_fn
        self.batch_size = batch_size
        self.min_batch_size = min_batch_size
        self._total_embedded = 0

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts with batching.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        if len(texts) < self.min_batch_size:
            logger.warning(
                f"Small batch size ({len(texts)} texts). "
                f"Consider batching at least {self.min_batch_size} texts for optimal performance."
            )

        embeddings: List[List[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_embeddings = self.embed_fn(batch)
            embeddings.extend(batch_embeddings)
            self._total_embedded += len(batch)

            if i > 0 and i % (self.batch_size * 10) == 0:
                logger.info(f"Embedded {i + len(batch)}/{len(texts)} texts")

        logger.info(f"Embedded {len(texts)} texts in batches of {self.batch_size}")
        return embeddings

    @property
    def total_embedded(self) -> int:
        """Total number of texts embedded by this batcher."""
        return self._total_embedded


def batch_embed(
    texts: List[str],
    embed_fn: Callable[[List[str]], List[List[float]]],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> List[List[float]]:
    """
    Convenience function for one-shot batch embedding.

    Args:
        texts: List of texts to embed
        embed_fn: Embedding function
        batch_size: Batch size

    Returns:
        List of embedding vectors
    """
    batcher = EmbeddingBatcher(embed_fn=embed_fn, batch_size=batch_size)
    return batcher.embed(texts)
