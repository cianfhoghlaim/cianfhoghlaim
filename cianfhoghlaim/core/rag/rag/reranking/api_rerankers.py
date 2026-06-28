"""
API Rerankers.

Implementations for external reranking APIs (Jina, Cohere, etc.).
"""
from __future__ import annotations

import logging
from typing import Any

from .base import BaseReranker, RankedDocument

logger = logging.getLogger(__name__)


class JinaReranker(BaseReranker):
    """
    Reranker using Jina AI Rerank API.

    Provides high-quality semantic reranking with
    multilingual support (good for Irish content).
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "jina-reranker-v2-base-multilingual",
        base_url: str = "https://api.jina.ai/v1/rerank",
    ):
        """
        Initialize Jina reranker.

        Args:
            api_key: Jina API key (or from JINA_API_KEY env var)
            model: Reranker model to use
            base_url: API endpoint
        """
        import os

        self.api_key = api_key or os.getenv("JINA_API_KEY")
        self.model = model
        self.base_url = base_url
        self._client = None

    @property
    def name(self) -> str:
        return f"jina:{self.model}"

    def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            import httpx

            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def rerank(
        self,
        query: str,
        documents: list[Any],
        top_k: int = 10,
        **kwargs,
    ) -> list[RankedDocument]:
        """Rerank documents using Jina API."""
        if not self.api_key:
            logger.warning("Jina API key not configured")
            return [
                RankedDocument(document=doc, score=0.5, rank=i + 1)
                for i, doc in enumerate(documents[:top_k])
            ]

        if not documents:
            return []

        try:
            client = self._get_client()

            # Extract text from documents
            doc_texts = [self._get_text(doc) for doc in documents]

            response = await client.post(
                self.base_url,
                json={
                    "model": self.model,
                    "query": query,
                    "documents": doc_texts,
                    "top_n": min(top_k, len(documents)),
                },
            )
            response.raise_for_status()
            data = response.json()

            # Map results back to original documents
            ranked = []
            for result in data.get("results", []):
                idx = result["index"]
                ranked.append(
                    RankedDocument(
                        document=documents[idx],
                        score=result["relevance_score"],
                        original_score=getattr(documents[idx], "score", None),
                        rank=len(ranked) + 1,
                        breakdown={"jina_score": result["relevance_score"]},
                    )
                )

            return ranked

        except Exception as e:
            logger.error(f"Jina rerank failed: {e}")
            # Fallback to original order
            return [
                RankedDocument(document=doc, score=0.5, rank=i + 1)
                for i, doc in enumerate(documents[:top_k])
            ]

    def _get_text(self, doc: Any) -> str:
        """Extract text content from document."""
        if isinstance(doc, str):
            return doc
        if hasattr(doc, "content"):
            return doc.content
        if hasattr(doc, "text"):
            return doc.text
        return str(doc)


class CohereReranker(BaseReranker):
    """
    Reranker using Cohere Rerank API.

    High-quality reranking with English focus.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "rerank-english-v3.0",
    ):
        """
        Initialize Cohere reranker.

        Args:
            api_key: Cohere API key (or from COHERE_API_KEY env var)
            model: Reranker model to use
        """
        import os

        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        self.model = model
        self._client = None

    @property
    def name(self) -> str:
        return f"cohere:{self.model}"

    def _get_client(self):
        """Get or create Cohere client."""
        if self._client is None:
            try:
                import cohere

                self._client = cohere.AsyncClient(api_key=self.api_key)
            except ImportError:
                logger.error("cohere package not installed")
                return None
        return self._client

    async def rerank(
        self,
        query: str,
        documents: list[Any],
        top_k: int = 10,
        **kwargs,
    ) -> list[RankedDocument]:
        """Rerank documents using Cohere API."""
        if not self.api_key:
            logger.warning("Cohere API key not configured")
            return [
                RankedDocument(document=doc, score=0.5, rank=i + 1)
                for i, doc in enumerate(documents[:top_k])
            ]

        client = self._get_client()
        if client is None:
            return [
                RankedDocument(document=doc, score=0.5, rank=i + 1)
                for i, doc in enumerate(documents[:top_k])
            ]

        if not documents:
            return []

        try:
            # Extract text from documents
            doc_texts = [self._get_text(doc) for doc in documents]

            response = await client.rerank(
                model=self.model,
                query=query,
                documents=doc_texts,
                top_n=min(top_k, len(documents)),
            )

            # Map results back to original documents
            ranked = []
            for result in response.results:
                idx = result.index
                ranked.append(
                    RankedDocument(
                        document=documents[idx],
                        score=result.relevance_score,
                        original_score=getattr(documents[idx], "score", None),
                        rank=len(ranked) + 1,
                        breakdown={"cohere_score": result.relevance_score},
                    )
                )

            return ranked

        except Exception as e:
            logger.error(f"Cohere rerank failed: {e}")
            return [
                RankedDocument(document=doc, score=0.5, rank=i + 1)
                for i, doc in enumerate(documents[:top_k])
            ]

    def _get_text(self, doc: Any) -> str:
        """Extract text content from document."""
        if isinstance(doc, str):
            return doc
        if hasattr(doc, "content"):
            return doc.content
        if hasattr(doc, "text"):
            return doc.text
        return str(doc)


class CrossEncoderReranker(BaseReranker):
    """
    Local reranker using sentence-transformers cross-encoder.

    No API costs but requires local GPU for best performance.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device: str | None = None,
    ):
        """
        Initialize cross-encoder reranker.

        Args:
            model_name: HuggingFace model name
            device: Device to use (auto-detected if None)
        """
        self.model_name = model_name
        self.device = device
        self._model = None

    @property
    def name(self) -> str:
        return f"cross-encoder:{self.model_name.split('/')[-1]}"

    def _get_model(self):
        """Get or create cross-encoder model."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(
                    self.model_name,
                    device=self.device,
                )
            except ImportError:
                logger.error("sentence-transformers package not installed")
                return None
        return self._model

    async def rerank(
        self,
        query: str,
        documents: list[Any],
        top_k: int = 10,
        **kwargs,
    ) -> list[RankedDocument]:
        """Rerank documents using local cross-encoder."""
        model = self._get_model()
        if model is None:
            return [
                RankedDocument(document=doc, score=0.5, rank=i + 1)
                for i, doc in enumerate(documents[:top_k])
            ]

        if not documents:
            return []

        try:
            # Extract text from documents
            doc_texts = [self._get_text(doc) for doc in documents]

            # Create query-document pairs
            pairs = [(query, text) for text in doc_texts]

            # Score pairs
            scores = model.predict(pairs)

            # Create ranked results
            ranked = []
            for i, (doc, score) in enumerate(zip(documents, scores, strict=False)):
                ranked.append(
                    RankedDocument(
                        document=doc,
                        score=float(score),
                        original_score=getattr(doc, "score", None),
                        breakdown={"cross_encoder_score": float(score)},
                    )
                )

            # Sort by score
            ranked.sort(key=lambda x: x.score, reverse=True)

            # Assign ranks
            for i, r in enumerate(ranked[:top_k]):
                r.rank = i + 1

            return ranked[:top_k]

        except Exception as e:
            logger.error(f"Cross-encoder rerank failed: {e}")
            return [
                RankedDocument(document=doc, score=0.5, rank=i + 1)
                for i, doc in enumerate(documents[:top_k])
            ]

    def _get_text(self, doc: Any) -> str:
        """Extract text content from document."""
        if isinstance(doc, str):
            return doc
        if hasattr(doc, "content"):
            return doc.content
        if hasattr(doc, "text"):
            return doc.text
        return str(doc)
