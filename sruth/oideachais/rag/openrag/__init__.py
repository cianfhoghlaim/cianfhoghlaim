"""
OpenRAG-inspired multimodal document processing.

Provides document ingestion, multimodal handling (PDF, images, tables),
and integration with curriculum RAG pipelines.
"""

from .multimodal import (
    DocumentConverter,
    ImageProcessor,
    TableExtractor,
    get_document_converter,
)
from .pipeline import DocumentPipeline, process_document
from .types import (
    DocumentChunk,
    DocumentType,
    ExtractedImage,
    ExtractedTable,
    ProcessedDocument,
    ProcessingConfig,
)

__all__ = [
    "DocumentPipeline",
    "process_document",
    "DocumentConverter",
    "ImageProcessor",
    "TableExtractor",
    "get_document_converter",
    "DocumentType",
    "ProcessedDocument",
    "DocumentChunk",
    "ExtractedTable",
    "ExtractedImage",
    "ProcessingConfig",
]
