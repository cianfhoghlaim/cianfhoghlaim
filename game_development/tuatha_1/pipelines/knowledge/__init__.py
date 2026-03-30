"""
Knowledge graph modules for crypto intelligence.

Uses Cognee for ECL (Extract-Cognify-Load) pipeline
and dual-graph architecture with Memgraph + FalkorDB.
"""

from pipelines.knowledge.cognee_pipeline import (
    CryptoCogneePipeline,
    cognify_crypto_docs,
    query_knowledge_graph,
)
from pipelines.knowledge.graph_schema import (
    CryptoEntitySchema,
    ENTITY_TYPES,
    RELATIONSHIP_TYPES,
)

__all__ = [
    "CryptoCogneePipeline",
    "cognify_crypto_docs",
    "query_knowledge_graph",
    "CryptoEntitySchema",
    "ENTITY_TYPES",
    "RELATIONSHIP_TYPES",
]
