"""
Core module for códeolas.

Contains the fundamental types, configuration, and analyzer classes.
"""

from sruth.codeolas.chunking.treesitter import chunk_code_file, detect_language
from sruth.codeolas.chunking.types import (
    ChunkType,
    CodeChunk,
)
from sruth.codeolas.core.analyzer import CodebaseAnalyzer
from sruth.codeolas.core.config import Config, get_config
from sruth.codeolas.core.embeddings import EmbeddingService, get_embedding_service
from sruth.codeolas.core.entities import EntityExtractor, deduplicate_entities
from sruth.codeolas.core.types import SourceRange

__all__ = [
    "ChunkType",
    "CodeChunk",
    "CodebaseAnalyzer",
    "Config",
    "EmbeddingService",
    "EntityExtractor",
    "SourceRange",
    "chunk_code_file",
    "deduplicate_entities",
    "detect_language",
    "get_config",
    "get_embedding_service",
]
