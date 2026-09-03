"""
Embedding Service Registry for sruth data pipelines.

Provides multi-provider embedding support with automatic fallback,
model selection, and performance optimization.

CRITICAL: Always batch embeddings - 100x performance difference.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from .batcher import EmbeddingBatcher, MIN_BATCH_SIZE, DEFAULT_BATCH_SIZE

logger = logging.getLogger(__name__)


class EmbeddingProvider(str, Enum):
    """Supported embedding providers."""

    OPENAI = "openai"
    COHERE = "cohere"
    VOYAGE = "voyage"
    HUGGINGFACE = "huggingface"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class EmbeddingModel:
    """Configuration for an embedding model."""

    name: str
    provider: EmbeddingProvider
    dimensions: int
    max_tokens: int = 8192
    batch_size: int = DEFAULT_BATCH_SIZE
    api_key_env: Optional[str] = None
    base_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# Pre-configured models
EMBEDDING_MODELS: Dict[str, EmbeddingModel] = {
    # OpenAI
    "text-embedding-3-small": EmbeddingModel(
        name="text-embedding-3-small",
        provider=EmbeddingProvider.OPENAI,
        dimensions=1536,
        max_tokens=8191,
        api_key_env="OPENAI_API_KEY",
    ),
    "text-embedding-3-large": EmbeddingModel(
        name="text-embedding-3-large",
        provider=EmbeddingProvider.OPENAI,
        dimensions=3072,
        max_tokens=8191,
        api_key_env="OPENAI_API_KEY",
    ),
    # Cohere
    "embed-english-v3.0": EmbeddingModel(
        name="embed-english-v3.0",
        provider=EmbeddingProvider.COHERE,
        dimensions=1024,
        max_tokens=512,
        batch_size=96,
        api_key_env="COHERE_API_KEY",
    ),
    "embed-multilingual-v3.0": EmbeddingModel(
        name="embed-multilingual-v3.0",
        provider=EmbeddingProvider.COHERE,
        dimensions=1024,
        max_tokens=512,
        batch_size=96,
        api_key_env="COHERE_API_KEY",
    ),
    # Voyage
    "voyage-large-2": EmbeddingModel(
        name="voyage-large-2",
        provider=EmbeddingProvider.VOYAGE,
        dimensions=1536,
        max_tokens=16000,
        api_key_env="VOYAGE_API_KEY",
    ),
    # HuggingFace / Sentence Transformers (local)
    "BAAI/bge-m3": EmbeddingModel(
        name="BAAI/bge-m3",
        provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        dimensions=1024,
        max_tokens=8192,
        batch_size=32,  # Lower for local GPU
    ),
    "BAAI/bge-large-en-v1.5": EmbeddingModel(
        name="BAAI/bge-large-en-v1.5",
        provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        dimensions=1024,
        max_tokens=512,
        batch_size=32,
    ),
    "intfloat/e5-large-v2": EmbeddingModel(
        name="intfloat/e5-large-v2",
        provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        dimensions=1024,
        max_tokens=512,
        batch_size=32,
    ),
    # Ollama (local)
    "nomic-embed-text": EmbeddingModel(
        name="nomic-embed-text",
        provider=EmbeddingProvider.OLLAMA,
        dimensions=768,
        max_tokens=8192,
        batch_size=32,
        base_url="http://localhost:11434",
    ),
    "mxbai-embed-large": EmbeddingModel(
        name="mxbai-embed-large",
        provider=EmbeddingProvider.OLLAMA,
        dimensions=1024,
        max_tokens=512,
        batch_size=32,
        base_url="http://localhost:11434",
    ),
}


class EmbeddingBackend(ABC):
    """Base class for embedding backends."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Return embedding dimensions."""
        pass


class OpenAIEmbeddings(EmbeddingBackend):
    """OpenAI embeddings backend."""

    def __init__(self, model: EmbeddingModel):
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            api_key = os.environ.get(self.model.api_key_env or "OPENAI_API_KEY")
            self._client = OpenAI(api_key=api_key)
        return self._client

    def embed(self, texts: List[str]) -> List[List[float]]:
        client = self._get_client()
        response = client.embeddings.create(input=texts, model=self.model.name)
        return [item.embedding for item in response.data]

    @property
    def dimensions(self) -> int:
        return self.model.dimensions


class CohereEmbeddings(EmbeddingBackend):
    """Cohere embeddings backend."""

    def __init__(self, model: EmbeddingModel):
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import cohere

            api_key = os.environ.get(self.model.api_key_env or "COHERE_API_KEY")
            self._client = cohere.Client(api_key)
        return self._client

    def embed(self, texts: List[str]) -> List[List[float]]:
        client = self._get_client()
        response = client.embed(texts=texts, model=self.model.name, input_type="search_document")
        return response.embeddings

    @property
    def dimensions(self) -> int:
        return self.model.dimensions


class SentenceTransformersEmbeddings(EmbeddingBackend):
    """Sentence Transformers (local) embeddings backend."""

    def __init__(self, model: EmbeddingModel):
        self.model = model
        self._encoder = None

    def _get_encoder(self):
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer

            self._encoder = SentenceTransformer(self.model.name)
        return self._encoder

    def embed(self, texts: List[str]) -> List[List[float]]:
        encoder = self._get_encoder()
        embeddings = encoder.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    @property
    def dimensions(self) -> int:
        return self.model.dimensions


class OllamaEmbeddings(EmbeddingBackend):
    """Ollama (local) embeddings backend."""

    def __init__(self, model: EmbeddingModel):
        self.model = model
        self.base_url = model.base_url or "http://localhost:11434"

    def embed(self, texts: List[str]) -> List[List[float]]:
        import httpx

        embeddings = []
        for text in texts:
            response = httpx.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model.name, "prompt": text},
            )
            response.raise_for_status()
            embeddings.append(response.json()["embedding"])
        return embeddings

    @property
    def dimensions(self) -> int:
        return self.model.dimensions


# Backend registry
BACKEND_REGISTRY: Dict[EmbeddingProvider, Type[EmbeddingBackend]] = {
    EmbeddingProvider.OPENAI: OpenAIEmbeddings,
    EmbeddingProvider.COHERE: CohereEmbeddings,
    EmbeddingProvider.SENTENCE_TRANSFORMERS: SentenceTransformersEmbeddings,
    EmbeddingProvider.OLLAMA: OllamaEmbeddings,
}


class EmbeddingService:
    """
    Multi-provider embedding service with automatic batching and fallback.

    Usage:
        service = EmbeddingService(model="BAAI/bge-m3")

        # Single embedding
        vector = service.embed_one("Hello world")

        # Batch embeddings (recommended)
        vectors = service.embed(["Hello", "World", ...])

        # With fallback
        service = EmbeddingService(
            model="text-embedding-3-small",
            fallback_model="BAAI/bge-m3",
        )
    """

    def __init__(
        self,
        model: str = "BAAI/bge-m3",
        fallback_model: Optional[str] = None,
        batch_size: Optional[int] = None,
        custom_backend: Optional[EmbeddingBackend] = None,
    ):
        """
        Initialize embedding service.

        Args:
            model: Model name (from EMBEDDING_MODELS or custom)
            fallback_model: Fallback model if primary fails
            batch_size: Override default batch size
            custom_backend: Custom embedding backend
        """
        self.model_name = model
        self.fallback_model_name = fallback_model

        # Get model config
        if model in EMBEDDING_MODELS:
            self.model_config = EMBEDDING_MODELS[model]
        else:
            # Assume sentence-transformers for unknown models
            self.model_config = EmbeddingModel(
                name=model,
                provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                dimensions=1024,  # Will be updated on first use
            )

        # Create backend
        if custom_backend:
            self._backend = custom_backend
        else:
            backend_class = BACKEND_REGISTRY.get(self.model_config.provider)
            if not backend_class:
                raise ValueError(f"No backend for provider: {self.model_config.provider}")
            self._backend = backend_class(self.model_config)

        # Create fallback backend
        self._fallback_backend: Optional[EmbeddingBackend] = None
        if fallback_model and fallback_model in EMBEDDING_MODELS:
            fallback_config = EMBEDDING_MODELS[fallback_model]
            fallback_class = BACKEND_REGISTRY.get(fallback_config.provider)
            if fallback_class:
                self._fallback_backend = fallback_class(fallback_config)

        # Setup batcher
        self._batch_size = batch_size or self.model_config.batch_size
        self._batcher = EmbeddingBatcher(
            embed_fn=self._embed_with_fallback,
            batch_size=self._batch_size,
        )

    def _embed_with_fallback(self, texts: List[str]) -> List[List[float]]:
        """Embed with automatic fallback on error."""
        try:
            return self._backend.embed(texts)
        except Exception as e:
            if self._fallback_backend:
                logger.warning(f"Primary embedding failed ({e}), using fallback")
                return self._fallback_backend.embed(texts)
            raise

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Automatically batches for optimal performance.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return self._batcher.embed(texts)

    def embed_one(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Note: For multiple texts, use embed() for better performance.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        return self._embed_with_fallback([text])[0]

    @property
    def dimensions(self) -> int:
        """Return embedding dimensions."""
        return self._backend.dimensions

    @property
    def total_embedded(self) -> int:
        """Total number of texts embedded."""
        return self._batcher.total_embedded


# Convenience functions
def get_embedding_service(
    model: str = "BAAI/bge-m3",
    **kwargs,
) -> EmbeddingService:
    """Get an embedding service instance."""
    return EmbeddingService(model=model, **kwargs)


def embed_texts(
    texts: List[str],
    model: str = "BAAI/bge-m3",
) -> List[List[float]]:
    """Convenience function for one-shot embedding."""
    service = EmbeddingService(model=model)
    return service.embed(texts)
