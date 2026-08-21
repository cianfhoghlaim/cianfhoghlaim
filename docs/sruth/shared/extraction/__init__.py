"""Structured extraction utilities for sruth pipelines.

Provides:
- DSPy modules for LLM-based extraction
- DSPy signatures for common patterns
- PostgreSQL target for structured data
- CocoIndex integration components
- DoclingResource: PDF parsing + hierarchy-aware chunking
- VLMExtractionResource: Vision-language model extraction via LiteLLM
- BAMLExtractionResource: Type-safe extraction with BAML schemas
- PaddleOCRResource: Table/formula extraction

Usage:
    from sruth.shared.extraction import (
        CurriculumExtractor,
        ExamMetadataExtractor,
        get_signature,
        docling_resource,
        vlm_resource,
        baml_resource,
        paddleocr_resource,
    )

    extractor = CurriculumExtractor()
    result = extractor.extract(document_text)
"""

from .dspy_modules import (
    BaseExtractor,
    CurriculumExtractor,
    ExamExtractor,
    StructuredExtractor,
    VisionExtractor,
    batch_extract,
    extract_curriculum,
    extract_exam_metadata,
)
from .dspy_signatures import (
    CurriculumEntity,
    CurriculumExtractionSignature,
    CurriculumAlignmentSignature,
    DocumentClassificationSignature,
    DocumentMetadata,
    ExamMetadataSignature,
    ExamPaper,
    ExamQuestion,
    IrishTranslationSignature,
    LearningOutcomeExtractionSignature,
    MultiLanguageExtractionSignature,
    QuestionExtractionSignature,
    SIGNATURES,
    get_signature,
    list_signatures,
)

__all__ = [
    # Modules
    "BaseExtractor",
    "CurriculumExtractor",
    "ExamExtractor",
    "StructuredExtractor",
    "VisionExtractor",
    # Convenience functions
    "batch_extract",
    "extract_curriculum",
    "extract_exam_metadata",
    # Signatures
    "CurriculumExtractionSignature",
    "ExamMetadataSignature",
    "DocumentClassificationSignature",
    "LearningOutcomeExtractionSignature",
    "QuestionExtractionSignature",
    "IrishTranslationSignature",
    "MultiLanguageExtractionSignature",
    "CurriculumAlignmentSignature",
    # Data models
    "CurriculumEntity",
    "ExamPaper",
    "ExamQuestion",
    "DocumentMetadata",
    # Signature utilities
    "SIGNATURES",
    "get_signature",
    "list_signatures",
    # Dagster Resources
    "DoclingResource",
    "docling_resource",
    "Chunk",
    "PageImage",
    "VLMExtractionResource",
    "vlm_resource",
    "ExtractionResult",
    "StructuredExtractionResult",
    "BAMLExtractionResource",
    "baml_resource",
    "BAMLExtractionResult",
    "PaddleOCRResource",
    "paddleocr_resource",
    "TableCell",
    "FormulaResult",
    "LayoutElement",
    "OCRResult",
]

# Dagster Resources for document processing
from .docling_resource import (
    DoclingResource,
    docling_resource,
    Chunk,
    PageImage,
)
from .vlm_resource import (
    VLMExtractionResource,
    vlm_resource,
    ExtractionResult,
    StructuredExtractionResult,
)
from .baml_resource import (
    BAMLExtractionResource,
    baml_resource,
    BAMLExtractionResult,
)
from .paddleocr_resource import (
    PaddleOCRResource,
    paddleocr_resource,
    TableCell,
    FormulaResult,
    LayoutElement,
    OCRResult,
)
