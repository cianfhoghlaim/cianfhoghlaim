"""
Códeolas - Code Analysis and Repository Intelligence.

Provides semantic code search, architecture discovery, and documentation
generation. This is the authoritative location for codeolas infrastructure.

Features:
- Syntax-aware code chunking via Tree-sitter (cAST algorithm)
- Multi-hop semantic search with LanceDB
- Knowledge graph in Memgraph
- MCP server for tool integration
- Architecture documentation generation
- Dagster pipeline assets
"""

# Core chunking (always available)
from .chunking import (
    ChunkType,
    CodeChunk,
    EXTENSION_TO_LANGUAGE,
    LANGUAGE_EXTENSIONS,
    detect_language,
    get_extensions_for_language,
    get_supported_languages,
    chunk_code_file,
)

# Storage
from .storage import (
    CodeChunk as StorageCodeChunk,  # Alias for backward compat
    LanceCatalog,
    LanceCatalogConfig,
    get_lance_catalog,
)

# Generators - core only
from .generators import (
    ArchitectureSection,
    ArchDocument,
    ArchGenerator,
    generate_arch_docs,
)

# Search
from .search import (
    multihop_search,
    expand_semantic_neighborhood,
    rerank_results,
)

# Graph
from .graph import (
    GraphBuilder,
    GraphQueries,
)

__all__ = [
    # Chunking
    "ChunkType",
    "CodeChunk",
    "EXTENSION_TO_LANGUAGE",
    "LANGUAGE_EXTENSIONS",
    "detect_language",
    "get_extensions_for_language",
    "get_supported_languages",
    "chunk_code_file",
    # Storage
    "StorageCodeChunk",
    "LanceCatalog",
    "LanceCatalogConfig",
    "get_lance_catalog",
    # Generators
    "ArchitectureSection",
    "ArchDocument",
    "ArchGenerator",
    "generate_arch_docs",
    # Search
    "multihop_search",
    "expand_semantic_neighborhood",
    "rerank_results",
    # Graph
    "GraphBuilder",
    "GraphQueries",
]

# Note: The following modules have CocoIndex/Dagster dependencies that may
# cause issues when imported at module level. Import them directly when needed:
#   from sruth.códeolas.flows import create_repo_embedding_flow, ...
#   from sruth.códeolas.pipelines import code_chunks, ...
#   from sruth.códeolas.core import CodebaseAnalyzer, ...
#   from sruth.códeolas.mcp import MCPServer, ...
