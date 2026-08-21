"""
Document Factory for Oideachais Pipeline.

Provides unified document model and format detection for curriculum sources:
- NCCA Curriculum Online
- SEC Examinations (exam papers, marking schemes)
- Department of Education Circulars
- Textbooks and Resources

Based on historical-document-analysis GenizahDocument patterns.
"""
from __future__ import annotations

from .base import (
    DocumentSource,
    ExtractionResult,
    DocumentConverter,
)
from .curriculum_document import (
    CurriculumDocument,
    CurriculumMetadata,
    LearningOutcome,
    ContentQuality,
)
from .format_detectors import (
    FormatDetector,
    detect_document_source,
)
from .pdf_factory import (
    LazyPDFFactory,
    PDFConverter,
    get_pdf_factory,
)
from .metrics_db import (
    MetricsDatabase,
    ExtractionTask,
    ExtractorComparison,
)

__all__ = [
    # Base
    "DocumentSource",
    "ExtractionResult",
    "DocumentConverter",
    # Document model
    "CurriculumDocument",
    "CurriculumMetadata",
    "LearningOutcome",
    "ContentQuality",
    # Format detection
    "FormatDetector",
    "detect_document_source",
    # PDF factory
    "LazyPDFFactory",
    "PDFConverter",
    "get_pdf_factory",
    # Metrics
    "MetricsDatabase",
    "ExtractionTask",
    "ExtractorComparison",
]
