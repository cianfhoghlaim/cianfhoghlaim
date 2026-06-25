"""TreeSitter-based code chunking using cAST algorithm.

DEPRECATED: This module re-exports from codeolas.chunking.
Update imports: from codeolas import chunk_code_file, ChunkType, CodeChunk
"""

import warnings

warnings.warn(
    "codeolas.cocoindex_flows.transforms.treesitter_chunking is deprecated. "
    "Import from codeolas instead.",
    DeprecationWarning,
    stacklevel=2,
)

from sruth.codeolas.chunking import (
    ChunkType,
    CodeChunk,
    EXTENSION_TO_LANGUAGE,
    LANGUAGE_EXTENSIONS,
    chunk_code_file,
    detect_language,
)

__all__ = [
    "ChunkType",
    "CodeChunk",
    "EXTENSION_TO_LANGUAGE",
    "LANGUAGE_EXTENSIONS",
    "chunk_code_file",
    "detect_language",
]
