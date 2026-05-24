"""Code chunking utilities using TreeSitter AST parsing.

This module provides syntax-aware code chunking via Tree-sitter.
Implements the cAST algorithm (ChunkHound pattern):

Three-phase process:
1. Parse & Extract: Tree-sitter generates AST, extract semantic concepts
2. Split: Break oversized chunks at syntax boundaries
3. Merge: Combine adjacent small chunks (respecting scope)

Supports 29+ programming languages via Tree-sitter.

Example:
    >>> from sruth.códeolas.chunking import chunk_code_file
    >>> chunks = chunk_code_file(source_code, "example.py")
    >>> for chunk in chunks:
    ...     print(f"{chunk.chunk_type}: {chunk.name} ({chunk.start_line}-{chunk.end_line})")
"""

from .types import ChunkType, CodeChunk
from .languages import (
    EXTENSION_TO_LANGUAGE,
    LANGUAGE_EXTENSIONS,
    detect_language,
    get_extensions_for_language,
    get_supported_languages,
)
from .treesitter import chunk_code_file

__all__ = [
    # Types
    "ChunkType",
    "CodeChunk",
    # Language detection
    "EXTENSION_TO_LANGUAGE",
    "LANGUAGE_EXTENSIONS",
    "detect_language",
    "get_extensions_for_language",
    "get_supported_languages",
    # Chunking
    "chunk_code_file",
]
