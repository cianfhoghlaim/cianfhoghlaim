"""
Base Reranker Interface.

Abstract base class for reranking implementations.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RankedDocument:
    """A document with ranking score and breakdown."""

    document: Any  # RetrievedChunk or similar
    score: float
    original_score: Optional[float] = None
    rank: int = 0

    # Score breakdown for explainability
    breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document": self.document.to_dict()
            if hasattr(self.document, "to_dict")
            else str(self.document),
            "score": self.score,
            "original_score": self.original_score,
            "rank": self.rank,
            "breakdown": self.breakdown,
        }


class BaseReranker(ABC):
    """
    Abstract base class for rerankers.

    Implementations can use:
    - API rerankers (Jina, Cohere, etc.)
    - Local models (cross-encoders)
    - Domain-specific scoring
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this reranker."""
        pass

    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: list[Any],
        top_k: int = 10,
        **kwargs,
    ) -> list[RankedDocument]:
        """
        Rerank documents based on query relevance.

        Args:
            query: Query string
            documents: List of documents to rerank
            top_k: Number of documents to return
            **kwargs: Additional reranker-specific parameters

        Returns:
            List of RankedDocument sorted by score
        """
        pass

    async def score(
        self,
        query: str,
        document: Any,
    ) -> float:
        """
        Score a single document.

        Default implementation uses rerank with single doc.
        Override for more efficient single-document scoring.
        """
        results = await self.rerank(query, [document], top_k=1)
        return results[0].score if results else 0.0
