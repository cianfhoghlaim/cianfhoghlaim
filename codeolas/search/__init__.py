"""
Search module for códeolas.

Provides semantic search, reranking, and multi-hop research capabilities.
"""

from codeolas.search.multihop import (
    multihop_search,
    expand_semantic_neighborhood,
)
from codeolas.search.reranker import rerank_results

__all__ = [
    "multihop_search",
    "expand_semantic_neighborhood",
    "rerank_results",
]
