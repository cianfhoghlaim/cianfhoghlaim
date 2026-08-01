"""DSPy extraction modules for structured data extraction.

Provides reusable DSPy modules for:
- Curriculum document extraction
- Exam metadata extraction
- General structured extraction from text/images

Usage:
    from sruth.shared.extraction.dspy_modules import CurriculumExtractor

    extractor = CurriculumExtractor()
    result = extractor(pdf_content=pdf_bytes)
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
# Base Extractor
# ============================================================================


class BaseExtractor:
    """Base class for DSPy extractors."""

    def __init__(self, model: str | None = None):
        if not dspy_available:
            raise ImportError("DSPy is not installed. Install with: pip install dspy-ai")
        self.model = model

    def _get_lm(self) -> Any:
        """Get configured language model."""
        if dspy is None:
            raise ImportError("DSPy is not installed")
        return dspy.LM(model=self.model or "openai/gpt-4o")


# ============================================================================
# Curriculum Extraction
# ============================================================================


@dataclass
class CurriculumData:
    """Structured curriculum data."""

    title: str
    subject: str
    level: str  # junior_cycle, senior_cycle, etc.
    strand: str | None = None
    strand_unit: str | None = None
    learning_outcomes: list[str] | None = None
    language: str = "en"
    nation: str = "ireland"


class CurriculumExtractor(BaseExtractor):
    """Extract structured curriculum data from documents.

    Uses DSPy ChainOfThought for reliable extraction.
    """

    def __init__(self, model: str | None = None):
        super().__init__(model)
        if not dspy_available:
            return

        # Define signature
        class CurriculumSignature(dspy.Signature):
            """Extract curriculum information from document content."""

            pdf_content: str = dspy.InputField(desc="PDF document content or text")
            curriculum_data: CurriculumData = dspy.OutputField(
                desc="Structured curriculum data with all fields"
            )

        self.extractor = dspy.ChainOfThought(CurriculumSignature)

    def extract(self, content: str) -> CurriculumData:
        """Extract curriculum data from text content.

        Args:
            content: Document text content

        Returns:
            Structured curriculum data
        """
        if not dspy_available:
            raise ImportError("DSPy is not installed")

        result = self.extractor(pdf_content=content)
        return result.curriculum_data

    def __call__(self, content: str) -> CurriculumData:
        """Allow direct call."""
        return self.extract(content)


# ============================================================================
# Exam Metadata Extraction
# ============================================================================


@dataclass
class ExamMetadata:
    """Structured exam paper metadata."""

    year: int
    subject: str
    level: str  # higher, ordinary, foundation, etc.
    exam_type: str  # junior_cert, leaving_cert, etc.
    paper: int | None = None
    questions: list[str] | None = None
    marking_scheme: bool = False
    language: str = "en"
    nation: str = "ireland"


class ExamExtractor(BaseExtractor):
    """Extract structured exam metadata from SEC documents."""

    def __init__(self, model: str | None = None):
        super().__init__(model)
        if not dspy_available:
            return

        class ExamSignature(dspy.Signature):
            """Extract exam metadata from document content."""

            pdf_content: str = dspy.InputField(desc="Exam paper content")
            exam_metadata: ExamMetadata = dspy.OutputField(
                desc="Structured exam metadata with all fields"
            )

        self.extractor = dspy.ChainOfThought(ExamSignature)

    def extract(self, content: str) -> ExamMetadata:
        """Extract exam metadata from text content.

        Args:
            content: Exam paper text content

        Returns:
            Structured exam metadata
        """
        if not dspy_available:
            raise ImportError("DSPy is not installed")

        result = self.extractor(pdf_content=content)
        return result.exam_metadata

    def __call__(self, content: str) -> ExamMetadata:
        """Allow direct call."""
        return self.extract(content)


# ============================================================================
# Generic Structured Extraction
# ============================================================================


class StructuredExtractor(BaseExtractor):
    """Generic structured extraction with configurable schema.

    Uses DSPy to extract data matching a Pydantic schema.
    """

    def __init__(
        self,
        schema: type,
        model: str | None = None,
        instructions: str | None = None,
    ):
        """Initialize generic extractor.

        Args:
            schema: Pydantic model for extraction
            model: LLM to use
            instructions: Custom extraction instructions
        """
        super().__init__(model)
        self.schema = schema
        self.instructions = instructions or f"Extract data matching {schema.__name__} schema"

        if not dspy_available:
            return

        # Create dynamic signature
        self._create_signature()

    def _create_signature(self) -> None:
        """Create DSPy signature from schema."""

        class GenericSignature(dspy.Signature):
            """Generic extraction signature."""

            content: str = dspy.InputField(desc="Text content to extract from")
            extracted_data: self.schema = dspy.OutputField(  # type: ignore
                desc=f"Extracted {self.schema.__name__} data"
            )

        self.signature = GenericSignature
        self.extractor = dspy.ChainOfThought(self.signature)

    def extract(self, content: str) -> Any:
        """Extract structured data from content.

        Args:
            content: Text content

        Returns:
            Structured data matching schema
        """
        if not dspy_available:
            raise ImportError("DSPy is not installed")

        result = self.extractor(content=content)
        return result.extracted_data

    def __call__(self, content: str) -> Any:
        """Allow direct call."""
        return self.extract(content)


# ============================================================================
# Multi-Modal Extraction (for images/PDFs)
# ============================================================================


class VisionExtractor(BaseExtractor):
    """Multi-modal extraction using vision models.

    Processes images and PDFs for visual document understanding.
    """

    def __init__(self, model: str | None = None):
        super().__init__(model or "openai/gpt-4o")
        if not dspy_available:
            return

        # Vision-specific signature
        class VisionSignature(dspy.Signature):
            """Extract structured data from images."""

            images: list[dspy.Image] = dspy.InputField(desc="Document images")
            extracted_text: str = dspy.OutputField(desc="Extracted text content")
            metadata: dict = dspy.OutputField(desc="Document metadata")

        self.extractor = dspy.ChainOfThought(VisionSignature)

    def extract_from_images(
        self,
        images: list[Any],  # dspy.Image objects
        return_metadata: bool = True,
    ) -> tuple[str, dict | None]:
        """Extract text and metadata from document images.

        Args:
            images: List of dspy.Image objects
            return_metadata: Whether to return metadata

        Returns:
            Tuple of (extracted_text, metadata)
        """
        if not dspy_available:
            raise ImportError("DSPy is not installed")

        result = self.extractor(images=images)
        metadata = result.metadata if return_metadata else None
        return result.extracted_text, metadata


# ============================================================================
# Batch Extraction
# ============================================================================


def batch_extract(
    items: list[tuple[str, str]],  # (id, content) tuples
    extractor: BaseExtractor,
    batch_size: int = 10,
) -> list[tuple[str, Any, bool | Exception]]:
    """Extract from multiple items with error handling.

    Args:
        items: List of (id, content) tuples
        extractor: Extractor instance to use
        batch_size: Processing batch size

    Returns:
        List of (id, result, success_or_error) tuples
    """
    results = []

    for item_id, content in items:
        try:
            result = extractor.extract(content)
            results.append((item_id, result, True))
        except Exception as e:
            results.append((item_id, e, False))

    return results


# ============================================================================
# Convenience Functions
# ============================================================================


def extract_curriculum(content: str) -> CurriculumData:
    """Convenience function for curriculum extraction.

    Args:
        content: Document text content

    Returns:
        Structured curriculum data
    """
    extractor = CurriculumExtractor()
    return extractor.extract(content)


def extract_exam_metadata(content: str) -> ExamMetadata:
    """Convenience function for exam metadata extraction.

    Args:
        content: Exam paper text content

    Returns:
        Structured exam metadata
    """
    extractor = ExamExtractor()
    return extractor.extract(content)
