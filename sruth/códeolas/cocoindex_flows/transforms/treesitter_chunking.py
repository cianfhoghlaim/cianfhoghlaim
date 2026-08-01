"""TreeSitter-based code chunking using cAST algorithm.

DEPRECATED: This module re-exports from sruth.códeolas.chunking.
Update imports: from sruth.códeolas import chunk_code_file, ChunkType, CodeChunk
"""

import warnings

warnings.warn(
    "sruth.códeolas.cocoindex_flows.transforms.treesitter_chunking is deprecated. "
    "Import from sruth.códeolas instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from shared
from sruth.códeolas.chunking import (
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
