"""Embedding Generation for CocoIndex.

Provides embedding functions for code and documentation indexing.
Uses SentenceTransformers for local embedding generation.
"""

import functools
from typing import Any

import numpy as np
from numpy.typing import NDArray


@functools.cache
def get_embedding_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """Get a cached SentenceTransformer embedding model.

    Args:
        model_name: Name of the model to load

    Returns:
        SentenceTransformer model instance
    """
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name)


def generate_embedding(
    text: str,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> NDArray[np.float32]:
    """Generate an embedding for a single text.

    Args:
        text: Text to embed
        model_name: Embedding model name

    Returns:
        Embedding as numpy array
    """
    model = get_embedding_model(model_name)
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.astype(np.float32)


def generate_embeddings_batch(
    texts: list[str],
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    batch_size: int = 32,
) -> NDArray[np.float32]:
    """Generate embeddings for a batch of texts.

    Args:
        texts: List of texts to embed
        model_name: Embedding model name
        batch_size: Batch size for encoding

    Returns:
        Array of embeddings
    """
    model = get_embedding_model(model_name)
    embeddings = model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
    return embeddings.astype(np.float32)


# CocoIndex-compatible transform function
def code_to_embedding(text: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> list[float]:
    """Transform function for CocoIndex flows.

    Converts text to embedding in a format compatible with CocoIndex.

    Args:
        text: Text to embed
        model_name: Embedding model name

    Returns:
        Embedding as list of floats
    """
    embedding = generate_embedding(text, model_name)
    return embedding.tolist()


class EmbeddingFunction:
    """Callable embedding function for LanceDB.

    This class provides a callable interface compatible with LanceDB's
    embedding function requirements.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = get_embedding_model(self.model_name)
        return self._model

    def __call__(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query.

        Args:
            query: Query text

        Returns:
            Query embedding
        """
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding.tolist()

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Embed a list of documents.

        Args:
            documents: List of document texts

        Returns:
            List of embeddings
        """
        return self(documents)

    @property
    def ndims(self) -> int:
        """Return embedding dimensions."""
        # all-MiniLM-L6-v2 produces 384-dimensional embeddings
        return self.model.get_sentence_embedding_dimension()
