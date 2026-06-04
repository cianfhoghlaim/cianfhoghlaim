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

# Lazy re-export of the high-level CodebaseAnalyzer so that
# `from codeolas import CodebaseAnalyzer` works without paying the import
# cost of sentence-transformers / lancedb at module load time.
def __getattr__(name: str):
    if name == "CodebaseAnalyzer":
        from codeolas.core.analyzer import CodebaseAnalyzer
        return CodebaseAnalyzer
    if name in {"Config", "get_config"}:
        from codeolas.core.config import Config, get_config
        return {"Config": Config, "get_config": get_config}[name]
    if name in {"EmbeddingService", "get_embedding_service"}:
        from codeolas.core.embeddings import (
            EmbeddingService,
            get_embedding_service,
        )
        return {
            "EmbeddingService": EmbeddingService,
            "get_embedding_service": get_embedding_service,
        }[name]
    if name in {"EntityExtractor", "deduplicate_entities"}:
        from codeolas.core.entities import (
            EntityExtractor,
            deduplicate_entities,
        )
        return {
            "EntityExtractor": EntityExtractor,
            "deduplicate_entities": deduplicate_entities,
        }[name]
    if name in {"MCPServer", "main"}:
        from codeolas.mcp_server import server as mcp_server

        if name == "MCPServer":
            return mcp_server.MCPServer
        return mcp_server.main
    if name == "ChangelogGenerator":
        from codeolas.generators.changelog import ChangelogGenerator
        return ChangelogGenerator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Chunking (eagerly imported above)
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
    # Lazy
    "CodebaseAnalyzer",
    "Config",
    "get_config",
    "EmbeddingService",
    "get_embedding_service",
    "EntityExtractor",
    "deduplicate_entities",
    "MCPServer",
    "main",
    "ChangelogGenerator",
]
