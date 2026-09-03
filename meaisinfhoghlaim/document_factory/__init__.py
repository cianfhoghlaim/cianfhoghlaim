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
    DocumentConverter,
    DocumentSource,
    ExtractionResult,
)
from .curriculum_document import (
    ContentQuality,
    CurriculumDocument,
    CurriculumMetadata,
    LearningOutcome,
)
from .format_detectors import (
    FormatDetector,
    detect_document_source,
)
from .metrics_db import (
    ExtractionTask,
    ExtractorComparison,
    MetricsDatabase,
)
from .pdf_factory import (
    LazyPDFFactory,
    PDFConverter,
    get_pdf_factory,
)

__all__ = [
    "ContentQuality",
    # Document model
    "CurriculumDocument",
    "CurriculumMetadata",
    "DocumentConverter",
    # Base
    "DocumentSource",
    "ExtractionResult",
    "ExtractionTask",
    "ExtractorComparison",
    # Format detection
    "FormatDetector",
    # PDF factory
    "LazyPDFFactory",
    "LearningOutcome",
    # Metrics
    "MetricsDatabase",
    "PDFConverter",
    "detect_document_source",
    "get_pdf_factory",
]
