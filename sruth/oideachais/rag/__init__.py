"""
RAG Query System.

Advanced retrieval-augmented generation with 6 query modes,
multi-level caching, and domain-aware reranking.

Includes OpenRAG-inspired multimodal document processing.
"""
from __future__ import annotations

from .query_modes import CurriculumQueryMode, CurriculumQueryParam
from .query_engine import CurriculumQueryEngine, QueryResult

# OpenRAG multimodal processing
from .openrag import (
    DocumentPipeline,
    process_document,
    DocumentConverter,
    ImageProcessor,
    TableExtractor,
    DocumentType,
    ProcessedDocument,
    ProcessingConfig,
)

__all__ = [
    # Query system
    "CurriculumQueryMode",
    "CurriculumQueryParam",
    "CurriculumQueryEngine",
    "QueryResult",
    # OpenRAG multimodal
    "DocumentPipeline",
    "process_document",
    "DocumentConverter",
    "ImageProcessor",
    "TableExtractor",
    "DocumentType",
    "ProcessedDocument",
    "ProcessingConfig",
]
