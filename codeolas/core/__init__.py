"""
Core module for códeolas.

Contains the fundamental types, configuration, and analyzer classes.
"""

from codeolas.core.analyzer import CodebaseAnalyzer
from codeolas.core.config import Config, get_config
from codeolas.core.embeddings import EmbeddingService, get_embedding_service
from codeolas.core.entities import EntityExtractor, deduplicate_entities
from codeolas.chunking.treesitter import chunk_code_file, detect_language
from codeolas.chunking.types import (
    ChunkType,
    CodeChunk,
)
from codeolas.core.types import SourceRange

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
