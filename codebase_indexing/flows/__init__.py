"""CocoIndex flows for code analysis.

Provides:
- Repository embedding flow (TreeSitter + BGE-M3 → LanceDB)
- File graph flow (AST → Memgraph)
"""

from .repo_embedding import (
    EXCLUDE_PATTERNS,
    INCLUDE_PATTERNS,
    create_repo_embedding_flow,
    run_indexing,
    search_code,
)
from .file_graph import (
    EdgeType,
    GraphEdge,
    GraphNode,
    MemgraphClient,
    NodeType,
    extract_relationships_from_ast,
    get_memgraph_client,
)

__all__ = [
    # Repo Embedding
    "INCLUDE_PATTERNS",
    "EXCLUDE_PATTERNS",
    "create_repo_embedding_flow",
    "run_indexing",
    "search_code",
    # File Graph
    "NodeType",
    "EdgeType",
    "GraphNode",
    "GraphEdge",
    "MemgraphClient",
    "extract_relationships_from_ast",
    "get_memgraph_client",
]
