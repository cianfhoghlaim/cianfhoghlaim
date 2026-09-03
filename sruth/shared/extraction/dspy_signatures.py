"""DSPy signatures for structured extraction.

Defines reusable DSPy signatures for common extraction patterns.
Signatures define the input/output contract for DSPy modules.

Usage:
    from sruth.shared.extraction.dspy_signatures import (
        CurriculumExtractionSignature,
        ExamMetadataSignature,
    )
    import dspy

    curriculum_extractor = dspy.ChainOfThought(CurriculumExtractionSignature)
    result = curriculum_extractor(pdf_content=doc_text)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    import dspy
    dspy_available = True
except ImportError:
    dspy_available = False
    dspy = None


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class CurriculumEntity:
    """Curriculum learning outcome or strand unit."""

    id: str
    title: str
    description: str
    subject: str
    strand: str | None = None
    strand_unit: str | None = None
    level: str = "senior_cycle"  # junior_cycle, senior_cycle
    language: str = "en"


@dataclass
class ExamQuestion:
    """Exam question or part."""

    number: str
    text: str
    marks: int | None = None
    parts: list[str] | None = None
    topics: list[str] | None = None


@dataclass
class ExamPaper:
    """Complete exam paper metadata."""

    year: int
    subject: str
    level: str  # higher, ordinary, foundation
    paper: int | None = None
    questions: list[ExamQuestion] | None = None
    total_marks: int | None = None
    duration_minutes: int | None = None
    exam_type: str = "leaving_cert"  # junior_cert, leaving_cert


@dataclass
class DocumentMetadata:
    """General document metadata."""

    title: str
    author: str | None = None
    date: str | None = None
    subject: str | None = None
    document_type: str | None = None  # curriculum, exam, circular, etc.
    language: str = "en"
    page_count: int | None = None
    keywords: list[str] | None = None


# ============================================================================
# DSPy Signatures
# ============================================================================


class CurriculumExtractionSignature(dspy.Signature):
    """Extract structured curriculum data from document content.

    Input: PDF or text content from curriculum documents
    Output: Structured curriculum with learning outcomes
    """

    pdf_content: str = dspy.InputField(
        desc="PDF document content or extracted text from curriculum document"
    )
    curriculum_data: CurriculumEntity = dspy.OutputField(
        desc="Structured curriculum data with strand, strand unit, and learning outcomes"
    )


class ExamMetadataSignature(dspy.Signature):
    """Extract structured exam metadata from SEC exam papers.

    Input: Exam paper text content
    Output: Structured exam metadata with questions
    """

    exam_content: str = dspy.InputField(
        desc="Exam paper content including questions and marks"
    )
    exam_metadata: ExamPaper = dspy.OutputField(
        desc="Structured exam metadata with year, subject, level, questions, and marks"
    )


class DocumentClassificationSignature(dspy.Signature):
    """Classify documents by type and extract metadata.

    Input: Document text content
    Output: Document type and metadata
    """

    document_content: str = dspy.InputField(
        desc="Document text content to classify"
    )
    document_metadata: DocumentMetadata = dspy.OutputField(
        desc="Document metadata including type, subject, language, and keywords"
    )


class LearningOutcomeExtractionSignature(dspy.Signature):
    """Extract individual learning outcomes from curriculum text.

    Input: Section of curriculum text
    Output: List of structured learning outcomes
    """

    section_text: str = dspy.InputField(
        desc="Section of curriculum text containing learning outcomes"
    )
    learning_outcomes: list[str] = dspy.OutputField(
        desc="List of individual learning outcomes as strings"
    )
    strand: str = dspy.OutputField(
        desc="The strand this section belongs to"
    )
    strand_unit: str = dspy.OutputField(
        desc="The strand unit this section belongs to"
    )


class QuestionExtractionSignature(dspy.Signature):
    """Extract questions and their structure from exam papers.

    Input: Exam paper text
    Output: Structured questions with marks and parts
    """

    exam_text: str = dspy.InputField(
        desc="Exam paper text containing questions"
    )
    questions: list[ExamQuestion] = dspy.OutputField(
        desc="List of structured questions with numbers, text, marks, and parts"
    )


class IrishTranslationSignature(dspy.Signature):
    """Translate educational content between English and Irish.

    Input: Text in source language
    Output: Text in target language
    """

    source_text: str = dspy.InputField(
        desc="Text to translate"
    )
    source_lang: str = dspy.InputField(
        desc="Source language (en, ga, cy, gd)"
    )
    target_lang: str = dspy.InputField(
        desc="Target language (en, ga, cy, gd)"
    )
    translated_text: str = dspy.OutputField(
        desc="Translated text maintaining educational terminology"
    )
    confidence: float = dspy.OutputField(
        desc="Translation confidence score 0-1"
    )


class MultiLanguageExtractionSignature(dspy.Signature):
    """Extract structured data from multilingual Celtic language documents.

    Input: Document text in Celtic language
    Output: Structured data with detected language
    """

    document_text: str = dspy.InputField(
        desc="Document text in Irish, Welsh, Scottish Gaelic, or Manx"
    )
    detected_language: str = dspy.OutputField(
        desc="Detected language (ga, cy, gd, gv)"
    )
    structured_data: dict = dspy.OutputField(
        desc="Extracted structured data from the document"
    )
    english_translation: str = dspy.OutputField(
        desc="English translation of the document text"
    )


class CurriculumAlignmentSignature(dspy.Signature):
    """Align curriculum standards across different nations.

    Input: Learning outcomes from two nations
    Output: Alignment mapping between outcomes
    """

    source_outcomes: list[str] = dspy.InputField(
        desc="Learning outcomes from source nation curriculum"
    )
    target_outcomes: list[str] = dspy.InputField(
        desc="Learning outcomes from target nation curriculum"
    )
    source_nation: str = dspy.InputField(
        desc="Source nation (ireland, uk, wales, scotland)"
    )
    target_nation: str = dspy.InputField(
        desc="Target nation (ireland, uk, wales, scotland)"
    )
    alignments: list[dict] = dspy.OutputField(
        desc="List of alignments with source_outcome, target_outcome, and similarity_score"
    )


# ============================================================================
# Signature Registry
# ============================================================================


SIGNATURES = {
    "curriculum_extraction": CurriculumExtractionSignature,
    "exam_metadata": ExamMetadataSignature,
    "document_classification": DocumentClassificationSignature,
    "learning_outcome_extraction": LearningOutcomeExtractionSignature,
    "question_extraction": QuestionExtractionSignature,
    "irish_translation": IrishTranslationSignature,
    "multilingual_extraction": MultiLanguageExtractionSignature,
    "curriculum_alignment": CurriculumAlignmentSignature,
}


def get_signature(name: str) -> type[dspy.Signature]:
    """Get a signature by name.

    Args:
        name: Signature name from registry

    Returns:
        DSPy Signature class

    Raises:
        KeyError: If signature not found
    """
    if name not in SIGNATURES:
        raise KeyError(f"Unknown signature: {name}. Available: {list(SIGNATURES.keys())}")
    return SIGNATURES[name]


def list_signatures() -> list[str]:
    """List all available signatures."""
    return list(SIGNATURES.keys())
