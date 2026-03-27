"""CocoIndex Integration for GitHub Intelligence.

This package provides semantic indexing capabilities using CocoIndex:
- Code indexing with tree-sitter aware chunking
- Documentation indexing for knowledge extraction
- LanceDB vector storage with hybrid search

Reference: multi_github_code_indexing example from CocoIndex
"""

from cocoindex.config import CodeIndexingConfig, DocsIndexingConfig
from cocoindex.embeddings import get_embedding_model, code_to_embedding
from cocoindex.search import LanceDBSearch

__all__ = [
    "CodeIndexingConfig",
    "DocsIndexingConfig",
    "get_embedding_model",
    "code_to_embedding",
    "LanceDBSearch",
]
