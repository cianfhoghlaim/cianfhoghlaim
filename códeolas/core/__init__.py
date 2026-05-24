"""
Core module for códeolas.

Contains the fundamental types, configuration, and analyzer classes.
"""

from sruth.códeolas.core.analyzer import CodebaseAnalyzer
from sruth.códeolas.core.config import Config, get_config
from sruth.códeolas.core.embeddings import EmbeddingService, get_embedding_service
from sruth.códeolas.core.entities import EntityExtractor, deduplicate_entities
from sruth.códeolas.chunking.treesitter import chunk_code_file, detect_language
from sruth.códeolas.chunking.types import (
    ChunkType,
    CodeChunk,
)
from sruth.códeolas.core.types import SourceRange

__all__ = [
    "CodebaseAnalyzer",
    "Config",
    "get_config",
    "chunk_code_file",
    "detect_language",
    "EmbeddingService",
    "get_embedding_service",
    "EntityExtractor",
    "deduplicate_entities",
    "ChunkType",
    "CodeChunk",
    "SourceRange",
]
