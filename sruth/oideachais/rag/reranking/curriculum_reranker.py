"""
Curriculum Reranker.

Domain-aware reranking for Irish curriculum content with
learning outcome alignment and subject matching.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Optional

from .base import BaseReranker, RankedDocument

logger = logging.getLogger(__name__)


class CurriculumReranker(BaseReranker):
    """
    Domain-aware reranker for curriculum content.

    Combines:
    - Base reranker scores (optional API reranker)
    - Learning outcome alignment
    - Subject/level matching
    - Source type weighting
    - Recency for SEC content
    """

    DEFAULT_WEIGHTS = {
        "base_score": 0.3,
        "learning_outcome_match": 0.25,
        "subject_match": 0.15,
        "level_match": 0.15,
        "source_type": 0.10,
        "recency": 0.05,
    }

    # Source type preferences
    SOURCE_WEIGHTS = {
        "ncca": 1.0,  # Official curriculum
        "sec": 0.95,  # Exam papers
        "circular": 0.8,  # Department circulars
        "textbook": 0.7,  # Publisher content
        "resource": 0.6,  # Teaching resources
        "unknown": 0.5,
    }

    def __init__(
        self,
        base_reranker: Optional[BaseReranker] = None,
        weights: Optional[dict[str, float]] = None,
    ):
        """
        Initialize curriculum reranker.

        Args:
            base_reranker: Optional base reranker (Jina, Cohere, etc.)
            weights: Optional weight overrides
        """
        self.base_reranker = base_reranker
        self.weights = {**self.DEFAULT_WEIGHTS, **(weights or {})}

        # Normalize weights to sum to 1.0
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}

    @property
    def name(self) -> str:
        base_name = self.base_reranker.name if self.base_reranker else "none"
        return f"curriculum_reranker+{base_name}"

    async def rerank(
        self,
        query: str,
        documents: list[Any],
        top_k: int = 10,
        subject_filter: Optional[str] = None,
        level_filter: Optional[str] = None,
        **kwargs,
    ) -> list[RankedDocument]:
        """
        Rerank documents with curriculum-aware scoring.

        Args:
            query: Query string
            documents: List of documents/chunks to rerank
            top_k: Number of documents to return
            subject_filter: Optional subject to boost
            level_filter: Optional level to boost
            **kwargs: Additional parameters

        Returns:
            List of RankedDocument sorted by combined score
        """
        if not documents:
            return []

        # Get base scores if we have a base reranker
        base_scores: dict[int, float] = {}
        if self.base_reranker:
            try:
                base_results = await self.base_reranker.rerank(
                    query, documents, top_k=len(documents)
                )
                for i, result in enumerate(base_results):
                    # Map back to original document index
                    for j, doc in enumerate(documents):
                        if self._doc_id(doc) == self._doc_id(result.document):
                            base_scores[j] = result.score
                            break
            except Exception as e:
                logger.warning(f"Base reranker failed: {e}")

        # Extract learning outcomes from query
        query_los = self._extract_learning_outcomes(query)

        # Score each document
        ranked = []
        for i, doc in enumerate(documents):
            scores = self._calculate_scores(
                doc=doc,
                query=query,
                query_los=query_los,
                base_score=base_scores.get(i, 0.5),
                subject_filter=subject_filter,
                level_filter=level_filter,
            )

            combined_score = sum(
                scores[k] * self.weights.get(k, 0) for k in scores
            )

            ranked.append(
                RankedDocument(
                    document=doc,
                    score=combined_score,
                    original_score=getattr(doc, "score", None),
                    breakdown=scores,
                )
            )

        # Sort by score
        ranked.sort(key=lambda x: x.score, reverse=True)

        # Assign ranks
        for i, r in enumerate(ranked):
            r.rank = i + 1

        return ranked[:top_k]

    def _calculate_scores(
        self,
        doc: Any,
        query: str,
        query_los: list[str],
        base_score: float,
        subject_filter: Optional[str],
        level_filter: Optional[str],
    ) -> dict[str, float]:
        """Calculate individual score components."""
        scores = {"base_score": base_score}

        # Learning outcome match
        doc_los = self._get_doc_los(doc)
        if query_los and doc_los:
            matches = len(set(query_los) & set(doc_los))
            scores["learning_outcome_match"] = min(matches / len(query_los), 1.0)
        else:
            scores["learning_outcome_match"] = 0.0

        # Subject match
        doc_subject = getattr(doc, "subject", None) or ""
        if subject_filter and doc_subject:
            scores["subject_match"] = (
                1.0 if doc_subject.lower() == subject_filter.lower() else 0.3
            )
        elif doc_subject:
            # Check if query mentions the subject
            scores["subject_match"] = (
                0.8 if doc_subject.lower() in query.lower() else 0.4
            )
        else:
            scores["subject_match"] = 0.3

        # Level match
        doc_level = getattr(doc, "level", None) or ""
        if level_filter and doc_level:
            scores["level_match"] = (
                1.0 if doc_level.lower() == level_filter.lower() else 0.3
            )
        else:
            scores["level_match"] = 0.5

        # Source type
        source_type = getattr(doc, "source_type", "unknown") or "unknown"
        scores["source_type"] = self.SOURCE_WEIGHTS.get(source_type.lower(), 0.5)

        # Recency (for SEC exam papers)
        if source_type.lower() == "sec":
            doc_title = getattr(doc, "doc_title", "") or ""
            year_match = re.search(r"20(\d{2})", doc_title)
            if year_match:
                year = 2000 + int(year_match.group(1))
                # More recent = higher score
                scores["recency"] = min((year - 2015) / 10, 1.0)
            else:
                scores["recency"] = 0.5
        else:
            scores["recency"] = 0.5

        return scores

    def _extract_learning_outcomes(self, query: str) -> list[str]:
        """Extract learning outcome codes from query."""
        # Match patterns like TG_MAT_G_1.1 or LO 3.2
        patterns = [
            r"[A-Z]{2,3}_[A-Z]{2,4}_[A-Z]_\d+\.\d+",  # TG_MAT_G_1.1
            r"LO\s*\d+\.\d+",  # LO 3.2
            r"Learning Outcome\s*\d+\.\d+",  # Learning Outcome 3.2
        ]
        los = []
        for pattern in patterns:
            los.extend(re.findall(pattern, query, re.IGNORECASE))
        return los

    def _get_doc_los(self, doc: Any) -> list[str]:
        """Get learning outcome codes from document."""
        if hasattr(doc, "learning_outcome_codes"):
            return doc.learning_outcome_codes or []
        if hasattr(doc, "metadata"):
            return doc.metadata.get("learning_outcome_codes", [])
        return []

    def _doc_id(self, doc: Any) -> str:
        """Get document identifier."""
        if hasattr(doc, "chunk_id"):
            return doc.chunk_id
        if hasattr(doc, "doc_id"):
            return doc.doc_id
        return str(id(doc))
