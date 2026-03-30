"""
Knowledge Graph for Tuath Celtic Educational MMO.

Provides hybrid search combining:
- Vector similarity (LanceDB with BGE-M3)
- Graph traversal (Graphiti on FalkorDB)
- Keyword matching

Domain coverage:
- Celtic mythology (characters, stories, locations)
- Educational curriculum (NCCA, WJEC, SQA)
- Player learning progressions
"""

from .hybrid_search import (
    HybridSearchConfig,
    HybridSearchEngine,
    SearchMode,
    SearchResult,
    get_search_engine,
    hybrid_search,
)

__all__ = [
    "HybridSearchConfig",
    "HybridSearchEngine",
    "SearchMode",
    "SearchResult",
    "get_search_engine",
    "hybrid_search",
]
