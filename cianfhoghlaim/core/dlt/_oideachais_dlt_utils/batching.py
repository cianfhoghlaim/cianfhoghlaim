"""
Embedding batching utilities for DLT pipelines.

MANDATORY for performance - unbatched embedding calls are 100x slower.
Also provides HNSW index management for bulk inserts.

Best Practices (from CLAUDE.md):
- Minimum batch size: 100 embeddings per API call
- Drop HNSW indexes for bulk inserts >50 rows (20x speedup)
- Recreate indexes after batch complete

Usage:
    from oideachais.dlt_utils.batching import (
        batch_embeddings,
        EmbeddingBatcher,
    )

    # Simple batching
    for batch in batch_embeddings(texts, batch_size=100):
        embeddings = embed_model.encode(batch)

    # With automatic API calls
    batcher = EmbeddingBatcher(embed_model)
    all_embeddings = batcher.embed_all(texts)
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Generator, Iterable
from typing import Protocol, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Minimum batch size for embedding API calls (100x performance difference)
MINIMUM_BATCH_SIZE = 100

# Alias for the historical `MIN_EMBEDDING_BATCH_SIZE` constant that
# was defined in the oideachais.oideachais.core migration shim and
# in cocoindex_flows/* and modal_finetune/embed_batch.py. The
# canonical constant is now MINIMUM_BATCH_SIZE; this alias is
# preserved for one release for any in-flight imports.
MIN_EMBEDDING_BATCH_SIZE = MINIMUM_BATCH_SIZE

# HNSW index drop threshold (see embedding-pipeline SKILL.md for the
# bulk-insert performance rationale). The oideachais.oideachais.core
# shim previously provided this; it is now defined here as the
# canonical implementation. A backward-compat re-export is preserved
# in oideachais.oideachais.core for one release.
HNSW_DROP_THRESHOLD = 50


class EmbeddingModel(Protocol):
    """Protocol for embedding models."""

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Encode texts to embeddings."""
        ...


def batch_embeddings(
    texts: Iterable[str],
    batch_size: int = MINIMUM_BATCH_SIZE,
) -> Generator[list[str]]:
    """
    Yield batches of texts for embedding API calls.

    CRITICAL: Always use batching for embeddings - 100x performance difference.

    Args:
        texts: Iterable of texts to embed
        batch_size: Size of each batch (minimum 100 recommended)

    Yields:
        Batches of texts

    Example:
        >>> for batch in batch_embeddings(my_texts):
        ...     embeddings = model.encode(batch)
        ...     process(embeddings)
    """
    if batch_size < MINIMUM_BATCH_SIZE:
        logger.warning(
            f"Batch size {batch_size} is below recommended minimum {MINIMUM_BATCH_SIZE}. "
            "This may significantly impact performance."
        )

    batch: list[str] = []
    for text in texts:
        batch.append(text)
        if len(batch) >= batch_size:
            yield batch
            batch = []

    # Yield remaining items
    if batch:
        yield batch


def batch_items[T](
    items: Iterable[T],
    batch_size: int = MINIMUM_BATCH_SIZE,
) -> Generator[list[T]]:
    """
    Generic batching for any iterable.

    Args:
        items: Iterable of items to batch
        batch_size: Size of each batch

    Yields:
        Batches of items
    """
    batch: list[T] = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch


class EmbeddingBatcher:
    """
    Helper class for batched embedding with progress tracking.

    Provides automatic batching, progress logging, and optional caching.

    Example:
        >>> from sentence_transformers import SentenceTransformer
        >>> model = SentenceTransformer("BAAI/bge-m3")
        >>> batcher = EmbeddingBatcher(model.encode, batch_size=200)
        >>> embeddings = batcher.embed_all(my_texts)
    """

    def __init__(
        self,
        embed_fn: Callable[[list[str]], list[list[float]]],
        batch_size: int = MINIMUM_BATCH_SIZE,
        show_progress: bool = True,
    ):
        """
        Initialize the batcher.

        Args:
            embed_fn: Function that takes list of texts and returns embeddings
            batch_size: Size of each batch
            show_progress: Whether to log progress
        """
        self.embed_fn = embed_fn
        self.batch_size = batch_size
        self.show_progress = show_progress

        if batch_size < MINIMUM_BATCH_SIZE:
            logger.warning(
                f"Batch size {batch_size} below recommended {MINIMUM_BATCH_SIZE}"
            )

    def embed_all(self, texts: list[str]) -> list[list[float]]:
        """
        Embed all texts with automatic batching.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings (same order as input)
        """
        all_embeddings: list[list[float]] = []
        total = len(texts)
        processed = 0

        for batch in batch_embeddings(texts, self.batch_size):
            embeddings = self.embed_fn(batch)
            all_embeddings.extend(embeddings)
            processed += len(batch)

            if self.show_progress:
                pct = (processed / total) * 100
                logger.info(f"Embedded {processed}/{total} texts ({pct:.1f}%)")

        return all_embeddings


def should_drop_hnsw(row_count: int) -> bool:
    """
    Check if HNSW index should be dropped for bulk insert.

    Args:
        row_count: Number of rows to insert

    Returns:
        True if index should be dropped (row_count > threshold)
    """
    return row_count > HNSW_DROP_THRESHOLD


def calculate_optimal_batch_size(
    total_items: int,
    max_batch_size: int = 500,
    min_batches: int = 3,
) -> int:
    """
    Calculate optimal batch size for a given number of items.

    Tries to create at least min_batches for better progress reporting,
    while respecting the maximum batch size.

    Args:
        total_items: Total number of items to process
        max_batch_size: Maximum allowed batch size
        min_batches: Minimum number of batches to create

    Returns:
        Optimal batch size
    """
    if total_items <= max_batch_size:
        return max(total_items, MINIMUM_BATCH_SIZE)

    # Try to create at least min_batches
    optimal = total_items // min_batches

    # Clamp to valid range
    return max(MINIMUM_BATCH_SIZE, min(optimal, max_batch_size))


# Re-export the threshold for convenience
__all__ = [
    "HNSW_DROP_THRESHOLD",
    "MINIMUM_BATCH_SIZE",
    "EmbeddingBatcher",
    "batch_embeddings",
    "batch_items",
    "calculate_optimal_batch_size",
    "should_drop_hnsw",
]
