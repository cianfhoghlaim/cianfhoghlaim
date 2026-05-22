"""
Embedding Batcher for sruth data pipelines.

CRITICAL: Always batch embeddings for 100x performance improvement.
- Unbatched 1000 texts: ~100s
- Batched 1000 texts: ~1s

This module enforces minimum batch sizes and provides utilities
for efficient embedding generation.

Note: Migrated from sruth/aleyum/_shared/embeddings/batcher.py
"""

import asyncio
import logging
from collections.abc import AsyncIterator, Callable

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

    Async Usage:
        batcher = EmbeddingBatcher(embed_fn=model.encode)
        async for batch_embeddings in batcher.embed_async(texts):
            process(batch_embeddings)
    """

    def __init__(
        self,
        embed_fn: Callable[[list[str]], list[list[float]]],
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

    def embed(self, texts: list[str]) -> list[list[float]]:
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

        embeddings: list[list[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_embeddings = self.embed_fn(batch)
            embeddings.extend(batch_embeddings)
            self._total_embedded += len(batch)

            if i > 0 and i % (self.batch_size * 10) == 0:
                logger.info(f"Embedded {i + len(batch)}/{len(texts)} texts")

        logger.info(f"Embedded {len(texts)} texts in batches of {self.batch_size}")
        return embeddings

    async def embed_async(
        self,
        texts: list[str],
        concurrency: int = 4,
    ) -> AsyncIterator[list[list[float]]]:
        """
        Generate embeddings asynchronously with controlled concurrency.

        Args:
            texts: List of texts to embed
            concurrency: Maximum concurrent embedding operations

        Yields:
            Batches of embedding vectors
        """
        if not texts:
            return

        if len(texts) < self.min_batch_size:
            logger.warning(
                f"Small batch size ({len(texts)} texts). "
                f"Consider batching at least {self.min_batch_size} texts."
            )

        semaphore = asyncio.Semaphore(concurrency)

        async def embed_batch(batch: list[str]) -> list[list[float]]:
            async with semaphore:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, self.embed_fn, batch)

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_embeddings = await embed_batch(batch)
            self._total_embedded += len(batch)
            yield batch_embeddings

    @property
    def total_embedded(self) -> int:
        """Total number of texts embedded by this batcher."""
        return self._total_embedded


def batch_embed(
    texts: list[str],
    embed_fn: Callable[[list[str]], list[list[float]]],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[list[float]]:
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
