"""Storage backends for códeolas.

Provides:
- LanceDB vector storage for code embeddings
- HNSW index management
- Batch embedding operations
"""

from .lance import (
    CodeChunk,
    LanceCatalog,
    LanceCatalogConfig,
    get_lance_catalog,
)

__all__ = [
    "CodeChunk",
    "LanceCatalog",
    "LanceCatalogConfig",
    "get_lance_catalog",
]
