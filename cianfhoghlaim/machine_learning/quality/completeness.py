"""
Completeness Scoring System.

Weighted scoring for curriculum document completeness based on
historical-document-analysis patterns.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class ContentQuality(StrEnum):
    """Document quality levels."""

    HIGH = "high"  # >= 0.8 completeness
    MEDIUM = "medium"  # >= 0.6 completeness
    LOW = "low"  # >= 0.3 completeness
    MINIMAL = "minimal"  # < 0.3 completeness


@dataclass
class CompletenessBreakdown:
    """Detailed breakdown of completeness score."""

    total_score: float
    quality: ContentQuality
    scores: dict[str, float] = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_score": self.total_score,
            "quality": self.quality.value,
            "scores": self.scores,
            "missing_fields": self.missing_fields,
            "recommendations": self.recommendations,
        }


class CompletenessScorer:
    """
    Calculate document completeness scores.

    Based on historical-document-analysis weighted scoring pattern.
    Configurable weights for different curriculum contexts.
    """

    # Default weights for curriculum documents
    DEFAULT_WEIGHTS = {
        # Core curriculum metadata (40%)
        "title": 0.05,
        "subject": 0.10,
        "level": 0.10,
        "learning_outcomes": 0.15,
        # Content (40%)
        "content_text": 0.20,
        "content_quality": 0.10,
        "irish_content": 0.10,
        # Classification (15%)
        "strand": 0.05,
        "topic": 0.05,
        "year_group": 0.05,
        # Provenance (5%)
        "source_url": 0.03,
        "extraction_date": 0.02,
    }

    # Weights optimized for SEC exam papers
    SEC_WEIGHTS = {
        "title": 0.05,
        "subject": 0.10,
        "level": 0.10,
        "exam_year": 0.10,
        "exam_level": 0.10,  # Higher/Ordinary/Foundation
        "content_text": 0.20,
        "content_quality": 0.10,
        "marking_scheme": 0.10,
        "total_marks": 0.05,
        "source_url": 0.05,
        "extraction_date": 0.05,
    }

    # Weights for NCCA curriculum specifications
    NCCA_WEIGHTS = {
        "title": 0.05,
        "subject": 0.10,
        "level": 0.10,
        "learning_outcomes": 0.20,
        "strand": 0.10,
        "strand_unit": 0.10,
        "content_text": 0.15,
        "content_quality": 0.10,
        "irish_version": 0.05,
        "source_url": 0.03,
        "extraction_date": 0.02,
    }

    def __init__(
        self,
        weights: dict[str, float] | None = None,
        source_type: str | None = None,
    ):
        """
        Initialize scorer.

        Args:
            weights: Custom weight overrides
            source_type: Document source type for preset weights
        """
        # Select base weights
        if source_type == "sec":
            base_weights = self.SEC_WEIGHTS.copy()
        elif source_type == "ncca":
            base_weights = self.NCCA_WEIGHTS.copy()
        else:
            base_weights = self.DEFAULT_WEIGHTS.copy()

        # Apply overrides
        if weights:
            base_weights.update(weights)

        # Normalize to sum to 1.0
        total = sum(base_weights.values())
        self.weights = {k: v / total for k, v in base_weights.items()}

    def score(self, document: Any) -> CompletenessBreakdown:
        """
        Calculate completeness score for a document.

        Args:
            document: CurriculumDocument or dict with document data

        Returns:
            CompletenessBreakdown with detailed scoring
        """
        # Convert to dict if needed
        if hasattr(document, "to_dict"):
            doc = document.to_dict()
        elif hasattr(document, "__dict__"):
            doc = document.__dict__
        else:
            doc = dict(document)

        scores: dict[str, float] = {}
        missing: list[str] = []
        recommendations: list[str] = []

        # Score each field
        for field, weight in self.weights.items():
            field_score = self._score_field(field, doc)
            scores[field] = field_score * weight

            if field_score == 0:
                missing.append(field)
            elif field_score < 0.5:
                recommendations.append(
                    f"Improve {field}: current score {field_score:.1%}"
                )

        total = sum(scores.values())
        quality = self._determine_quality(total)

        # Add recommendations for low scores
        if quality == ContentQuality.MINIMAL:
            recommendations.insert(
                0, "Document has minimal completeness. Major fields missing."
            )
        elif quality == ContentQuality.LOW:
            recommendations.insert(
                0, "Document has low completeness. Consider adding missing metadata."
            )

        return CompletenessBreakdown(
            total_score=total,
            quality=quality,
            scores=scores,
            missing_fields=missing,
            recommendations=recommendations[:5],  # Top 5 recommendations
        )

    def _score_field(self, field: str, doc: dict) -> float:
        """Score a single field."""
        # Handle nested metadata
        metadata = doc.get("metadata", {})

        # Field-specific scoring logic
        match field:
            case "title":
                value = doc.get("title", "")
                if not value:
                    return 0.0
                return min(len(value) / 20, 1.0)  # Prefer titles > 20 chars

            case "subject":
                value = metadata.get("subject") or doc.get("subject", "")
                if not value or value.lower() == "unknown":
                    return 0.0
                return 1.0

            case "level":
                value = metadata.get("level") or doc.get("level", "")
                if not value or value.lower() == "unknown":
                    return 0.0
                return 1.0

            case "learning_outcomes":
                los = metadata.get("learning_outcomes", [])
                if not los:
                    return 0.0
                # More LOs = higher score (up to 10)
                return min(len(los) / 10, 1.0)

            case "content_text":
                content = doc.get("content_text", "")
                if not content:
                    return 0.0
                word_count = len(content.split())
                # Prefer content > 500 words
                return min(word_count / 500, 1.0)

            case "content_quality":
                # Use extraction confidence if available
                return doc.get("extraction_confidence", 0.5)

            case "irish_content" | "irish_version":
                has_irish = metadata.get("has_irish_version", False)
                primary_lang = metadata.get("primary_language", "en")
                if has_irish or primary_lang == "ga":
                    return 1.0
                # Check for Irish content in text
                content = doc.get("content_text", "")
                if self._contains_irish(content):
                    return 0.7
                return 0.0

            case "strand":
                value = metadata.get("strand") or doc.get("strand", "")
                return 1.0 if value else 0.0

            case "strand_unit":
                value = metadata.get("strand_unit") or doc.get("strand_unit", "")
                return 1.0 if value else 0.0

            case "topic":
                value = metadata.get("topic") or doc.get("topic", "")
                return 1.0 if value else 0.0

            case "year_group":
                value = metadata.get("year_group") or doc.get("year_group", "")
                return 1.0 if value else 0.0

            case "exam_year":
                assessment = metadata.get("assessment", {})
                value = assessment.get("exam_year") or doc.get("exam_year")
                return 1.0 if value else 0.0

            case "exam_level":
                assessment = metadata.get("assessment", {})
                value = assessment.get("exam_level") or doc.get("exam_level")
                return 1.0 if value else 0.0

            case "total_marks":
                assessment = metadata.get("assessment", {})
                value = assessment.get("total_marks") or doc.get("total_marks")
                return 1.0 if value else 0.0

            case "marking_scheme":
                # Check if we have marking scheme content
                content = doc.get("content_text", "").lower()
                if "marking scheme" in content or "mark scheme" in content:
                    return 1.0
                return 0.0

            case "source_url":
                value = doc.get("source_url", "")
                return 1.0 if value else 0.0

            case "extraction_date":
                value = doc.get("extracted_at") or doc.get("created_at")
                return 1.0 if value else 0.0

            case _:
                # Unknown field - check if present
                value = doc.get(field) or metadata.get(field)
                return 1.0 if value else 0.0

    def _contains_irish(self, text: str) -> bool:
        """Check if text contains Irish language content."""
        # Irish-specific patterns
        irish_patterns = [
            r"[áéíóú]",  # Fada vowels
            r"\b(?:an|na|agus|le|ar|ag|is|atá|bhí|sé|sí)\b",  # Common words
            r"\b(?:Gaeilge|Éire|Scoil|Rang)\b",  # School-related
        ]
        text_lower = text.lower()
        matches = sum(
            1 for pattern in irish_patterns if re.search(pattern, text_lower)
        )
        return matches >= 2

    def _determine_quality(self, score: float) -> ContentQuality:
        """Determine quality level from score."""
        if score >= 0.8:
            return ContentQuality.HIGH
        elif score >= 0.6:
            return ContentQuality.MEDIUM
        elif score >= 0.3:
            return ContentQuality.LOW
        return ContentQuality.MINIMAL

    def batch_score(
        self,
        documents: list[Any],
    ) -> list[CompletenessBreakdown]:
        """Score multiple documents."""
        return [self.score(doc) for doc in documents]

    def get_statistics(
        self,
        breakdowns: list[CompletenessBreakdown],
    ) -> dict[str, Any]:
        """Get aggregate statistics for a set of scores."""
        if not breakdowns:
            return {}

        scores = [b.total_score for b in breakdowns]
        qualities = [b.quality for b in breakdowns]

        return {
            "count": len(breakdowns),
            "mean_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "quality_distribution": {
                q.value: qualities.count(q) for q in ContentQuality
            },
            "common_missing_fields": self._get_common_missing(breakdowns),
        }

    def _get_common_missing(
        self,
        breakdowns: list[CompletenessBreakdown],
    ) -> list[tuple[str, int]]:
        """Get most commonly missing fields."""
        from collections import Counter

        missing_counts: Counter = Counter()
        for b in breakdowns:
            missing_counts.update(b.missing_fields)

        return missing_counts.most_common(5)
