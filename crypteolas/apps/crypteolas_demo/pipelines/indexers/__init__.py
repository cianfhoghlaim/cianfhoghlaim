"""
Document indexing modules for crypto knowledge base.

Uses CocoIndex for semantic chunking and embedding.
"""

from pipelines.indexers.cocoindex_flow import (
    CryptoDocumentFlow,
    index_crypto_docs,
    query_crypto_knowledge,
)

__all__ = [
    "CryptoDocumentFlow",
    "index_crypto_docs",
    "query_crypto_knowledge",
]
