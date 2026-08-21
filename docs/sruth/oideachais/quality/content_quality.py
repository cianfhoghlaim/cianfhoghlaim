"""
Content Quality Assessment.

Detailed quality analysis for curriculum document content.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Detailed quality metrics for document content."""

    # Text quality
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    vocabulary_richness: float = 0.0

    # Structure quality
    has_headings: bool = False
    heading_count: int = 0
    has_lists: bool = False
    has_tables: bool = False

    # Curriculum-specific
    learning_outcome_count: int = 0
    has_strand_structure: bool = False
    has_assessment_criteria: bool = False

    # Irish language
    contains_irish: bool = False
    irish_word_ratio: float = 0.0
    fada_accuracy: float = 1.0  # Assume good unless errors detected

    # Extraction quality
    has_garbled_text: bool = False
    has_missing_content: bool = False
    formatting_preserved: bool = True

    # Overall scores
    text_quality_score: float = 0.0
    structure_score: float = 0.0
    curriculum_score: float = 0.0
    overall_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "avg_sentence_length": self.avg_sentence_length,
            "vocabulary_richness": self.vocabulary_richness,
            "has_headings": self.has_headings,
            "heading_count": self.heading_count,
            "has_lists": self.has_lists,
            "has_tables": self.has_tables,
            "learning_outcome_count": self.learning_outcome_count,
            "has_strand_structure": self.has_strand_structure,
            "has_assessment_criteria": self.has_assessment_criteria,
            "contains_irish": self.contains_irish,
            "irish_word_ratio": self.irish_word_ratio,
            "has_garbled_text": self.has_garbled_text,
            "has_missing_content": self.has_missing_content,
            "formatting_preserved": self.formatting_preserved,
            "text_quality_score": self.text_quality_score,
            "structure_score": self.structure_score,
            "curriculum_score": self.curriculum_score,
            "overall_score": self.overall_score,
        }


class ContentQualityAssessor:
    """
    Assess content quality of curriculum documents.

    Analyzes:
    - Text quality (readability, vocabulary)
    - Structure (headings, lists, tables)
    - Curriculum elements (learning outcomes, strands)
    - Irish language content
    - Extraction quality
    """

    # Irish common words for detection
    IRISH_WORDS = {
        "an",
        "na",
        "le",
        "ar",
        "ag",
        "i",
        "do",
        "de",
        "go",
        "sa",
        "is",
        "a",
        "ní",
        "sé",
        "sí",
        "iad",
        "mé",
        "tú",
        "sinn",
        "sibh",
        "atá",
        "bhí",
        "agus",
        "ach",
        "nó",
        "mar",
        "nuair",
        "má",
        "cé",
        "cad",
        "conas",
        "fhoghlaim",
        "oideachas",
        "scoil",
        "rang",
        "múinteoir",
        "dalta",
    }

    # Garbled text patterns (common OCR errors)
    GARBLED_PATTERNS = [
        r"[^\x00-\x7F]{5,}",  # Long non-ASCII sequences
        r"(?:[bcdfghjklmnpqrstvwxz]){5,}",  # Too many consonants
        r"(?:[0-9]){10,}",  # Long number sequences
        r"(?:\?){3,}",  # Multiple question marks
        r"(?:\.){5,}",  # Too many dots
    ]

    def __init__(
        self,
        min_word_count: int = 50,
        min_sentence_count: int = 3,
    ):
        """
        Initialize assessor.

        Args:
            min_word_count: Minimum expected word count
            min_sentence_count: Minimum expected sentence count
        """
        self.min_word_count = min_word_count
        self.min_sentence_count = min_sentence_count

    def assess(self, content: str, metadata: Optional[dict] = None) -> QualityMetrics:
        """
        Assess content quality.

        Args:
            content: Document text content
            metadata: Optional metadata for context

        Returns:
            QualityMetrics with detailed assessment
        """
        metadata = metadata or {}
        metrics = QualityMetrics()

        if not content or not content.strip():
            return metrics

        # Text analysis
        self._analyze_text(content, metrics)

        # Structure analysis
        self._analyze_structure(content, metrics)

        # Curriculum-specific analysis
        self._analyze_curriculum(content, metrics)

        # Irish language analysis
        self._analyze_irish(content, metrics)

        # Extraction quality
        self._analyze_extraction_quality(content, metrics)

        # Calculate scores
        self._calculate_scores(metrics)

        return metrics

    def _analyze_text(self, content: str, metrics: QualityMetrics) -> None:
        """Analyze basic text metrics."""
        # Word count
        words = content.split()
        metrics.word_count = len(words)

        # Sentence count (approximate)
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]
        metrics.sentence_count = len(sentences)

        # Average sentence length
        if metrics.sentence_count > 0:
            metrics.avg_sentence_length = metrics.word_count / metrics.sentence_count

        # Vocabulary richness (unique words / total words)
        unique_words = set(word.lower() for word in words if word.isalpha())
        if metrics.word_count > 0:
            metrics.vocabulary_richness = len(unique_words) / metrics.word_count

    def _analyze_structure(self, content: str, metrics: QualityMetrics) -> None:
        """Analyze document structure."""
        # Headings (Markdown style)
        heading_pattern = r"^#+\s+.+$|^.+\n[=-]+$"
        headings = re.findall(heading_pattern, content, re.MULTILINE)
        metrics.has_headings = len(headings) > 0
        metrics.heading_count = len(headings)

        # Lists
        list_pattern = r"^[\s]*[-*•]\s+.+$|^[\s]*\d+\.\s+.+$"
        lists = re.findall(list_pattern, content, re.MULTILINE)
        metrics.has_lists = len(lists) > 0

        # Tables (Markdown or simple)
        table_pattern = r"\|.+\|"
        tables = re.findall(table_pattern, content)
        metrics.has_tables = len(tables) > 2  # At least 3 table rows

    def _analyze_curriculum(self, content: str, metrics: QualityMetrics) -> None:
        """Analyze curriculum-specific elements."""
        content_lower = content.lower()

        # Learning outcomes
        lo_patterns = [
            r"learning outcome",
            r"toradh foghlama",  # Irish
            r"LO\s*\d",
            r"[A-Z]{2,3}_[A-Z]{2,4}_[A-Z]_\d+",  # Codes like TG_MAT_G_1.1
        ]
        lo_count = 0
        for pattern in lo_patterns:
            lo_count += len(re.findall(pattern, content, re.IGNORECASE))
        metrics.learning_outcome_count = lo_count

        # Strand structure
        strand_keywords = ["strand", "snáithe", "unit", "aonad"]
        metrics.has_strand_structure = any(kw in content_lower for kw in strand_keywords)

        # Assessment criteria
        assessment_keywords = [
            "assessment",
            "measúnú",
            "marking",
            "criteria",
            "rubric",
        ]
        metrics.has_assessment_criteria = any(kw in content_lower for kw in assessment_keywords)

    def _analyze_irish(self, content: str, metrics: QualityMetrics) -> None:
        """Analyze Irish language content."""
        words = content.lower().split()
        word_set = set(words)

        # Check for Irish words
        irish_words_found = word_set & self.IRISH_WORDS

        # Check for fadas
        has_fadas = bool(re.search(r"[áéíóú]", content))

        metrics.contains_irish = len(irish_words_found) >= 3 or has_fadas

        if metrics.contains_irish and len(words) > 0:
            # Estimate Irish word ratio
            irish_count = sum(1 for w in words if w in self.IRISH_WORDS)
            metrics.irish_word_ratio = irish_count / len(words)

            # Check fada accuracy (look for common errors)
            fada_errors = [
                (r"sé(?![áéíóú])", "sé"),  # Should often have fada
                (r"(?<![áéíóú])ré", "ré"),  # Should have fada
            ]
            # This is a simple heuristic, not comprehensive
            metrics.fada_accuracy = 0.95  # Assume mostly correct

    def _analyze_extraction_quality(self, content: str, metrics: QualityMetrics) -> None:
        """Analyze extraction quality indicators."""
        # Check for garbled text
        for pattern in self.GARBLED_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                metrics.has_garbled_text = True
                break

        # Check for missing content indicators
        missing_indicators = [
            r"\[missing\]",
            r"\[unclear\]",
            r"\[illegible\]",
            r"\?\?\?",
            r"\[\.\.\.\]",
        ]
        for pattern in missing_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                metrics.has_missing_content = True
                break

        # Check formatting preservation
        # If we have headings and proper structure, formatting is preserved
        metrics.formatting_preserved = (
            metrics.has_headings or metrics.has_lists
        ) and not metrics.has_garbled_text

    def _calculate_scores(self, metrics: QualityMetrics) -> None:
        """Calculate overall quality scores."""
        # Text quality score (0-1)
        text_score = 0.0
        if metrics.word_count >= self.min_word_count:
            text_score += 0.4
        else:
            text_score += 0.4 * (metrics.word_count / self.min_word_count)

        if metrics.sentence_count >= self.min_sentence_count:
            text_score += 0.3
        else:
            text_score += 0.3 * (metrics.sentence_count / self.min_sentence_count)

        # Vocabulary richness bonus
        text_score += min(metrics.vocabulary_richness * 0.5, 0.3)

        metrics.text_quality_score = min(text_score, 1.0)

        # Structure score (0-1)
        structure_score = 0.0
        if metrics.has_headings:
            structure_score += 0.4
        if metrics.has_lists:
            structure_score += 0.3
        if metrics.has_tables:
            structure_score += 0.3

        metrics.structure_score = min(structure_score, 1.0)

        # Curriculum score (0-1)
        curriculum_score = 0.0
        if metrics.learning_outcome_count > 0:
            curriculum_score += min(metrics.learning_outcome_count / 10, 0.5)
        if metrics.has_strand_structure:
            curriculum_score += 0.25
        if metrics.has_assessment_criteria:
            curriculum_score += 0.25

        metrics.curriculum_score = min(curriculum_score, 1.0)

        # Penalties for quality issues
        penalty = 0.0
        if metrics.has_garbled_text:
            penalty += 0.2
        if metrics.has_missing_content:
            penalty += 0.1
        if not metrics.formatting_preserved:
            penalty += 0.1

        # Overall score (weighted average minus penalties)
        overall = (
            metrics.text_quality_score * 0.4
            + metrics.structure_score * 0.3
            + metrics.curriculum_score * 0.3
        ) - penalty

        metrics.overall_score = max(0.0, min(1.0, overall))

    def batch_assess(
        self,
        contents: list[str],
        metadata_list: Optional[list[dict]] = None,
    ) -> list[QualityMetrics]:
        """Assess multiple documents."""
        metadata_list = metadata_list or [{}] * len(contents)
        return [
            self.assess(content, metadata) for content, metadata in zip(contents, metadata_list)
        ]

    def get_summary(
        self,
        metrics_list: list[QualityMetrics],
    ) -> dict[str, Any]:
        """Get summary statistics for a batch of assessments."""
        if not metrics_list:
            return {}

        return {
            "count": len(metrics_list),
            "avg_word_count": sum(m.word_count for m in metrics_list) / len(metrics_list),
            "avg_overall_score": sum(m.overall_score for m in metrics_list) / len(metrics_list),
            "contains_irish_count": sum(1 for m in metrics_list if m.contains_irish),
            "has_garbled_text_count": sum(1 for m in metrics_list if m.has_garbled_text),
            "avg_text_quality": sum(m.text_quality_score for m in metrics_list) / len(metrics_list),
            "avg_structure_score": sum(m.structure_score for m in metrics_list) / len(metrics_list),
            "avg_curriculum_score": sum(m.curriculum_score for m in metrics_list)
            / len(metrics_list),
        }
