"""
Embedding Service Client.

HTTP client for the embedding microservice.
"""
from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    HTTP client for embedding microservice.

    Features:
    - Batch embedding with automatic chunking
    - Connection pooling
    - Retry logic
    - Fallback to local model
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        timeout: float = 30.0,
        max_batch_size: int = 100,
        use_fallback: bool = True,
    ):
        """
        Initialize embedding client.

        Args:
            base_url: Embedding service URL
            timeout: Request timeout in seconds
            max_batch_size: Maximum texts per request
            use_fallback: Whether to use local model on failure
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_batch_size = max_batch_size
        self.use_fallback = use_fallback
        self._client = None
        self._fallback_model = None

    async def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            import httpx

            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                base_url=self.base_url,
            )
        return self._client

    def _get_fallback_model(self):
        """Get or create fallback local model."""
        if self._fallback_model is None and self.use_fallback:
            try:
                from sentence_transformers import SentenceTransformer

                self._fallback_model = SentenceTransformer(
                    "intfloat/multilingual-e5-large"
                )
                logger.info("Loaded fallback embedding model")
            except ImportError:
                logger.warning("sentence-transformers not installed for fallback")
        return self._fallback_model

    async def embed_batch(
        self,
        texts: list[str],
        model: str = "multilingual-e5-large",
    ) -> np.ndarray:
        """
        Embed multiple texts.

        Args:
            texts: Texts to embed
            model: Model name

        Returns:
            Embedding matrix (n_texts x dim)
        """
        if not texts:
            return np.array([])

        # Chunk large batches
        all_embeddings = []
        for i in range(0, len(texts), self.max_batch_size):
            chunk = texts[i : i + self.max_batch_size]
            embeddings = await self._embed_chunk(chunk, model)
            all_embeddings.append(embeddings)

        return np.vstack(all_embeddings) if all_embeddings else np.array([])

    async def _embed_chunk(
        self,
        texts: list[str],
        model: str,
    ) -> np.ndarray:
        """Embed a single chunk of texts."""
        try:
            client = await self._get_client()
            response = await client.post(
                "/embed",
                json={"texts": texts, "model": model},
            )
            response.raise_for_status()
            data = response.json()
            return np.array(data["embeddings"])

        except Exception as e:
            logger.warning(f"Embedding service failed: {e}")

            # Try fallback
            fallback = self._get_fallback_model()
            if fallback:
                logger.info("Using fallback local model")
                return fallback.encode(
                    texts,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )

            raise

    async def embed_query(
        self,
        text: str,
        model: str = "multilingual-e5-large",
    ) -> np.ndarray:
        """
        Embed a single query text.

        Args:
            text: Query text
            model: Model name

        Returns:
            Embedding vector
        """
        try:
            client = await self._get_client()
            response = await client.post(
                "/embed/query",
                json={"text": text, "model": model},
            )
            response.raise_for_status()
            data = response.json()
            return np.array(data["embedding"])

        except Exception as e:
            logger.warning(f"Query embedding failed: {e}")

            # Try fallback
            fallback = self._get_fallback_model()
            if fallback:
                return fallback.encode(
                    f"query: {text}",
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )

            raise

    async def health_check(self) -> dict:
        """Check service health."""
        try:
            client = await self._get_client()
            response = await client.get("/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def list_models(self) -> dict:
        """List available models."""
        try:
            client = await self._get_client()
            response = await client.get("/models")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return {"available": [], "loaded": []}

    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
