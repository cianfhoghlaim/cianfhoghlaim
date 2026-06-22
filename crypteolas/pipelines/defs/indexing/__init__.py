"""
Indexing assets for vector and graph storage.

Assets:
- code_vector_index: Code files → LanceDB vectors
- docs_vector_index: Documentation → LanceDB vectors
- docs_graph_index: Documentation → Memgraph relationships
- cocoindex_*: CocoIndex semantic code search
"""

from defs.indexing.code_vectors import code_vector_index
from defs.indexing.docs_vectors import docs_vector_index
from defs.indexing.docs_graph import docs_graph_index
from defs.indexing.cocoindex_vectors import cocoindex_assets

__all__ = [
    "code_vector_index",
    "docs_vector_index",
    "docs_graph_index",
    "cocoindex_assets",
]
