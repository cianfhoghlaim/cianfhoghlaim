"""
Embedding service for códeolas.

Provides batched embedding generation with automatic model loading.
CRITICAL: Embeddings must be batched (minimum 100) for 100x performance.
"""

import logging
from typing import Any

from sruth.codeolas.core.config import get_config

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating code embeddings.

    Uses sentence-transformers with BGE-M3 by default.
    IMPORTANT: Always use batch embedding for performance (100x difference).
    """

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
    ):
        config = get_config()
        self.model_name = model_name or config.embedding_model
        self.device = device
        self._model = None
        self._dimension: int | None = None

    def _get_model(self):
        """Lazy load the embedding model."""
        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            )

        logger.info(f"Loading embedding model: {self.model_name}")
        self._model = SentenceTransformer(self.model_name, device=self.device)
        self._dimension = self._model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded (dimension={self._dimension})")

        return self._model

    @property
    def model(self):
        """Get the embedding model."""
        return self._get_model()

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        if self._dimension is None:
            self._get_model()
        return self._dimension or get_config().embedding_dimension

    def embed_text(self, text: str) -> list[float]:
        """
        Embed a single text.

        WARNING: For multiple texts, use embed_batch() for 100x better performance.
        """
        logger.warning(
            "embed_text() called for single text. Use embed_batch() for better performance."
        )
        embeddings = self.model.encode([text], convert_to_numpy=True)
        return embeddings[0].tolist()

    def embed_batch(
        self,
        texts: list[str],
        batch_size: int | None = None,
        show_progress: bool = False,
    ) -> list[list[float]]:
        """
        Embed multiple texts in batches.

        CRITICAL: This is the recommended method. Batching is mandatory for performance.
        Unbatched 1000 texts: ~100s
        Batched 1000 texts: ~1s

        Args:
            texts: List of texts to embed
            batch_size: Batch size (minimum 100 enforced)
            show_progress: Show progress bar

        Returns:
            List of embedding vectors
        """
        config = get_config()

        # Enforce minimum batch size
        if batch_size is None:
            batch_size = config.min_batch_size
        elif batch_size < config.min_batch_size:
            logger.warning(
                f"batch_size {batch_size} below minimum {config.min_batch_size}, using minimum"
            )
            batch_size = config.min_batch_size

        if not texts:
            return []

        logger.info(f"Embedding {len(texts)} texts (batch_size={batch_size})")

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )

        return [emb.tolist() for emb in embeddings]

    def embed_code_chunks(
        self,
        chunks: list[Any],  # list[CodeChunk]
        text_field: str = "text",
        batch_size: int | None = None,
    ) -> list[tuple[Any, list[float]]]:
        """
        Embed code chunks and return (chunk, embedding) pairs.

        Args:
            chunks: List of CodeChunk objects
            text_field: Field name containing text to embed
            batch_size: Batch size for embedding

        Returns:
            List of (chunk, embedding) tuples
        """
        if not chunks:
            return []

        # Extract texts
        texts = [getattr(chunk, text_field) for chunk in chunks]

        # Embed
        embeddings = self.embed_batch(texts, batch_size=batch_size)

        # Pair chunks with embeddings
        return list(zip(chunks, embeddings, strict=False))


# Singleton instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service(
    model_name: str | None = None,
    device: str | None = None,
) -> EmbeddingService:
    """Get the embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(model_name, device)
    return _embedding_service
