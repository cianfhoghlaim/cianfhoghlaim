"""
Curriculum Document Model.

Unified Pydantic model for Irish curriculum documents,
based on historical-document-analysis GenizahDocument patterns.

Supports:
- NCCA Curriculum specifications
- SEC Exam papers and marking schemes
- Department of Education circulars
- Textbook and resource content
"""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field

from .base import DocumentSource, DocumentFormat

logger = logging.getLogger(__name__)


class ContentQuality(str, Enum):
    """Document content quality levels."""

    HIGH = "high"  # >= 0.8 completeness
    MEDIUM = "medium"  # >= 0.6 completeness
    LOW = "low"  # >= 0.3 completeness
    MINIMAL = "minimal"  # < 0.3 completeness


class EducationLevel(str, Enum):
    """Irish education levels."""

    PRIMARY = "primary"
    JUNIOR_CYCLE = "junior"
    SENIOR_CYCLE = "senior"
    FURTHER_EDUCATION = "further"
    UNKNOWN = "unknown"


class Language(str, Enum):
    """Content language."""

    ENGLISH = "en"
    IRISH = "ga"
    BILINGUAL = "bilingual"


class LearningOutcome(BaseModel):
    """A curriculum learning outcome."""

    code: str = Field(description="Learning outcome code (e.g., 'TG_MAT_G_1.1')")
    text: str = Field(description="Learning outcome text")
    strand: Optional[str] = Field(default=None, description="Curriculum strand")
    strand_unit: Optional[str] = Field(default=None, description="Strand unit")

    # Optional enrichment
    level: Optional[EducationLevel] = None
    subject: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "text": self.text,
            "strand": self.strand,
            "strand_unit": self.strand_unit,
            "level": self.level.value if self.level else None,
            "subject": self.subject,
            "keywords": self.keywords,
        }


class AssessmentInfo(BaseModel):
    """SEC examination metadata."""

    exam_year: Optional[int] = None
    exam_level: Optional[str] = None  # Higher, Ordinary, Foundation
    paper_number: Optional[int] = None
    section: Optional[str] = None
    question_numbers: list[str] = Field(default_factory=list)
    total_marks: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "exam_year": self.exam_year,
            "exam_level": self.exam_level,
            "paper_number": self.paper_number,
            "section": self.section,
            "question_numbers": self.question_numbers,
            "total_marks": self.total_marks,
        }


class CurriculumMetadata(BaseModel):
    """Rich curriculum metadata."""

    # Classification
    subject: str = Field(description="Subject name")
    level: EducationLevel = Field(default=EducationLevel.UNKNOWN)
    year_group: Optional[str] = Field(default=None, description="Year group (e.g., '5th Year')")
    strand: Optional[str] = Field(default=None, description="Curriculum strand")
    strand_unit: Optional[str] = Field(default=None, description="Strand unit")
    topic: Optional[str] = Field(default=None, description="Topic within strand")

    # Language
    primary_language: Language = Field(default=Language.ENGLISH)
    has_irish_version: bool = False

    # Learning outcomes
    learning_outcomes: list[LearningOutcome] = Field(default_factory=list)

    # Assessment (for SEC content)
    assessment: Optional[AssessmentInfo] = None

    # Circular info (for Dept circulars)
    circular_number: Optional[str] = None
    circular_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "level": self.level.value,
            "year_group": self.year_group,
            "strand": self.strand,
            "strand_unit": self.strand_unit,
            "topic": self.topic,
            "primary_language": self.primary_language.value,
            "has_irish_version": self.has_irish_version,
            "learning_outcomes": [lo.to_dict() for lo in self.learning_outcomes],
            "assessment": self.assessment.to_dict() if self.assessment else None,
            "circular_number": self.circular_number,
        }


class CurriculumDocument(BaseModel):
    """
    Unified curriculum document model.

    Based on GenizahDocument patterns from historical-document-analysis.
    Provides normalized representation for all curriculum sources.
    """

    # ==========================================================================
    # Core Identification
    # ==========================================================================
    doc_id: str = Field(description="Unique document identifier")
    source_type: DocumentSource = Field(default=DocumentSource.UNKNOWN)
    format_detected: DocumentFormat = Field(default=DocumentFormat.UNKNOWN)

    # ==========================================================================
    # Content
    # ==========================================================================
    title: str = Field(description="Document title")
    content_text: str = Field(description="Extracted text content")
    content_html: Optional[str] = Field(default=None, description="HTML content if available")
    content_markdown: Optional[str] = Field(default=None, description="Markdown content")

    # Summary (AI-generated)
    summary: Optional[str] = Field(default=None, description="AI-generated summary")
    key_concepts: list[str] = Field(default_factory=list, description="Key concepts extracted")

    # ==========================================================================
    # Curriculum Metadata
    # ==========================================================================
    metadata: CurriculumMetadata = Field(default_factory=lambda: CurriculumMetadata(subject="Unknown"))

    # ==========================================================================
    # Quality Metrics
    # ==========================================================================
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    # ==========================================================================
    # Provenance
    # ==========================================================================
    source_url: Optional[str] = Field(default=None, description="Original source URL")
    source_file: Optional[str] = Field(default=None, description="Source file path")
    extracted_at: datetime = Field(default_factory=datetime.now)
    extractor_used: str = Field(default="", description="Extraction library used")

    # ==========================================================================
    # Versioning
    # ==========================================================================
    version: str = Field(default="1.0")
    curriculum_year: Optional[str] = Field(default=None, description="Curriculum year (e.g., '2023-24')")

    # ==========================================================================
    # Computed Properties
    # ==========================================================================

    @computed_field
    @property
    def content_hash(self) -> str:
        """SHA256 hash of content for deduplication."""
        content = f"{self.title}|{self.content_text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @computed_field
    @property
    def content_quality(self) -> ContentQuality:
        """Assess content quality based on completeness score."""
        if self.completeness_score >= 0.8:
            return ContentQuality.HIGH
        elif self.completeness_score >= 0.6:
            return ContentQuality.MEDIUM
        elif self.completeness_score >= 0.3:
            return ContentQuality.LOW
        return ContentQuality.MINIMAL

    @computed_field
    @property
    def word_count(self) -> int:
        """Approximate word count."""
        return len(self.content_text.split())

    # ==========================================================================
    # Completeness Scoring
    # ==========================================================================

    # Weights for completeness calculation (based on historical-document-analysis)
    COMPLETENESS_WEIGHTS = {
        # Core curriculum metadata (40%)
        "title": 0.05,
        "subject": 0.10,
        "level": 0.10,
        "learning_outcomes": 0.15,

        # Content (40%)
        "content_text": 0.20,
        "content_quality": 0.10,
        "irish_translation": 0.10,

        # Classification (15%)
        "strand": 0.05,
        "topic": 0.05,
        "year_group": 0.05,

        # Provenance (5%)
        "source_url": 0.03,
        "extraction_date": 0.02,
    }

    def calculate_completeness_score(self) -> float:
        """
        Calculate document completeness score (0.0-1.0).

        Based on historical-document-analysis weighted scoring pattern.
        """
        score = 0.0

        # Title (0.05)
        if self.title and len(self.title) > 5:
            score += self.COMPLETENESS_WEIGHTS["title"]

        # Subject (0.10)
        if self.metadata.subject and self.metadata.subject != "Unknown":
            score += self.COMPLETENESS_WEIGHTS["subject"]

        # Level (0.10)
        if self.metadata.level != EducationLevel.UNKNOWN:
            score += self.COMPLETENESS_WEIGHTS["level"]

        # Learning outcomes (0.15)
        if self.metadata.learning_outcomes:
            lo_score = min(len(self.metadata.learning_outcomes) / 5, 1.0)
            score += self.COMPLETENESS_WEIGHTS["learning_outcomes"] * lo_score

        # Content text (0.20)
        if self.content_text:
            # Longer content = higher score (up to 1000 words)
            content_ratio = min(self.word_count / 1000, 1.0)
            score += self.COMPLETENESS_WEIGHTS["content_text"] * content_ratio

        # Content quality - based on extraction confidence (0.10)
        if self.extraction_confidence > 0:
            score += self.COMPLETENESS_WEIGHTS["content_quality"] * self.extraction_confidence

        # Irish translation indicator (0.10)
        if self.metadata.has_irish_version or self.metadata.primary_language == Language.IRISH:
            score += self.COMPLETENESS_WEIGHTS["irish_translation"]

        # Strand (0.05)
        if self.metadata.strand:
            score += self.COMPLETENESS_WEIGHTS["strand"]

        # Topic (0.05)
        if self.metadata.topic:
            score += self.COMPLETENESS_WEIGHTS["topic"]

        # Year group (0.05)
        if self.metadata.year_group:
            score += self.COMPLETENESS_WEIGHTS["year_group"]

        # Source URL (0.03)
        if self.source_url:
            score += self.COMPLETENESS_WEIGHTS["source_url"]

        # Extraction date - always present (0.02)
        score += self.COMPLETENESS_WEIGHTS["extraction_date"]

        return min(1.0, score)

    def update_completeness(self) -> None:
        """Recalculate and update completeness score."""
        self.completeness_score = self.calculate_completeness_score()

    # ==========================================================================
    # Export Methods
    # ==========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "doc_id": self.doc_id,
            "source_type": self.source_type.value,
            "format_detected": self.format_detected.value,
            "title": self.title,
            "content_text": self.content_text,
            "content_html": self.content_html,
            "summary": self.summary,
            "key_concepts": self.key_concepts,
            "metadata": self.metadata.to_dict(),
            "completeness_score": self.completeness_score,
            "extraction_confidence": self.extraction_confidence,
            "content_quality": self.content_quality.value,
            "word_count": self.word_count,
            "content_hash": self.content_hash,
            "source_url": self.source_url,
            "source_file": self.source_file,
            "extracted_at": self.extracted_at.isoformat(),
            "extractor_used": self.extractor_used,
            "version": self.version,
            "curriculum_year": self.curriculum_year,
        }

    def to_elasticsearch_document(
        self,
        embedding: Optional[list[float]] = None,
    ) -> dict[str, Any]:
        """Convert to Elasticsearch document format."""
        doc = {
            "doc_id": self.doc_id,
            "title": self.title,
            "content": self.content_text,
            "source_type": self.source_type.value,

            # Searchable fields
            "subject": self.metadata.subject,
            "level": self.metadata.level.value,
            "strand": self.metadata.strand,
            "topic": self.metadata.topic,
            "year_group": self.metadata.year_group,

            # Learning outcomes (nested)
            "learning_outcomes": [lo.to_dict() for lo in self.metadata.learning_outcomes],
            "learning_outcome_codes": [lo.code for lo in self.metadata.learning_outcomes],

            # Language
            "primary_language": self.metadata.primary_language.value,
            "has_irish_version": self.metadata.has_irish_version,

            # Quality
            "completeness_score": self.completeness_score,
            "content_quality": self.content_quality.value,
            "word_count": self.word_count,

            # Metadata
            "source_url": self.source_url,
            "extracted_at": self.extracted_at.isoformat(),
            "curriculum_year": self.curriculum_year,
        }

        if embedding:
            doc["embedding_vector"] = embedding

        return doc

    def to_graph_nodes(self) -> list[dict[str, Any]]:
        """Convert to knowledge graph nodes."""
        nodes = []

        # Document node
        nodes.append({
            "id": self.doc_id,
            "type": "Document",
            "properties": {
                "title": self.title,
                "source_type": self.source_type.value,
                "subject": self.metadata.subject,
                "level": self.metadata.level.value,
            },
        })

        # Learning outcome nodes
        for lo in self.metadata.learning_outcomes:
            nodes.append({
                "id": lo.code,
                "type": "LearningOutcome",
                "properties": {
                    "code": lo.code,
                    "text": lo.text,
                    "strand": lo.strand,
                    "subject": lo.subject or self.metadata.subject,
                },
            })

        return nodes

    def to_graph_edges(self) -> list[dict[str, Any]]:
        """Convert to knowledge graph edges."""
        edges = []

        # Document -> LearningOutcome edges
        for lo in self.metadata.learning_outcomes:
            edges.append({
                "source": self.doc_id,
                "target": lo.code,
                "type": "COVERS",
                "properties": {
                    "strand": lo.strand,
                },
            })

        return edges

    # ==========================================================================
    # Factory Methods
    # ==========================================================================

    @classmethod
    def from_extraction_result(
        cls,
        doc_id: str,
        title: str,
        extraction_result: "ExtractionResult",
        source_type: DocumentSource = DocumentSource.UNKNOWN,
        format_detected: DocumentFormat = DocumentFormat.UNKNOWN,
        source_url: Optional[str] = None,
        source_file: Optional[str] = None,
    ) -> "CurriculumDocument":
        """Create from an extraction result."""
        from .base import ExtractionResult

        doc = cls(
            doc_id=doc_id,
            title=title,
            source_type=source_type,
            format_detected=format_detected,
            content_text=extraction_result.content_text,
            content_html=extraction_result.content_html,
            extraction_confidence=extraction_result.extraction_confidence,
            extractor_used=extraction_result.extractor_used,
            source_url=source_url,
            source_file=source_file,
        )

        # Calculate completeness
        doc.update_completeness()

        return doc


# =============================================================================
# Factory Functions
# =============================================================================

def create_curriculum_document(
    title: str,
    content_text: str,
    subject: str,
    level: EducationLevel = EducationLevel.UNKNOWN,
    source_type: DocumentSource = DocumentSource.UNKNOWN,
    **kwargs,
) -> CurriculumDocument:
    """
    Factory function to create a CurriculumDocument with defaults.

    Args:
        title: Document title
        content_text: Extracted text content
        subject: Subject name
        level: Education level
        source_type: Document source type
        **kwargs: Additional fields

    Returns:
        Configured CurriculumDocument
    """
    import uuid

    doc_id = kwargs.pop("doc_id", f"doc_{uuid.uuid4().hex[:12]}")

    metadata = CurriculumMetadata(
        subject=subject,
        level=level,
        **{k: v for k, v in kwargs.items() if hasattr(CurriculumMetadata, k)},
    )

    doc = CurriculumDocument(
        doc_id=doc_id,
        title=title,
        content_text=content_text,
        source_type=source_type,
        metadata=metadata,
        **{k: v for k, v in kwargs.items() if hasattr(CurriculumDocument, k) and k not in ["metadata"]},
    )

    doc.update_completeness()
    return doc
