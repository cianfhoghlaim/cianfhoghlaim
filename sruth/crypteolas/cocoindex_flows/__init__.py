"""
CocoIndex Flows for Crypteolas.

Provides:
- Unified embedding for documents and code
- Live documentation sync via Firecrawl
- Protocol relationship graph
- Code-specific embedding with Tree-sitter

CRITICAL CONSTRAINTS:
- Embedding batching: MANDATORY minimum 100 per call
- HNSW indexes: DROP before bulk inserts >50 rows
- DuckDB: Single-threaded only
"""

__all__ = [
    # Unified Embedding
    "UnifiedEmbeddingConfig",
    "DocumentSourceType",
    "unified_embedding_flow",
    "code_embedding_flow",
    "unified_search",
    "code_search",
    "batch_embed_texts",
    "process_bulk_documents",
    "MIN_BATCH_SIZE",
    "HNSW_DROP_THRESHOLD",
    # Live Docs
    "ProtocolDocConfig",
    "LiveDocumentationSync",
    "PROTOCOL_CONFIGS",
    "sync_protocol_docs",
    "sync_all_protocol_docs",
    "get_configured_protocols",
    # Protocol Graph
    "ProtocolEntityType",
    "ProtocolRelationType",
    "ProtocolEntity",
    "ProtocolRelationship",
    "ProtocolGraphClient",
    "get_protocol_graph",
    "initialize_protocol_graph",
]


def __getattr__(name: str):
    """Lazy import to avoid cocoindex decorator issues at load time."""
    # Unified embedding
    if name in (
        "UnifiedEmbeddingConfig",
        "DocumentSourceType",
        "unified_embedding_flow",
        "code_embedding_flow",
        "unified_search",
        "code_search",
        "batch_embed_texts",
        "process_bulk_documents",
        "MIN_BATCH_SIZE",
        "HNSW_DROP_THRESHOLD",
    ):
        from . import unified_embedding
        return getattr(unified_embedding, name)

    # Live docs
    if name in (
        "ProtocolDocConfig",
        "LiveDocumentationSync",
        "PROTOCOL_CONFIGS",
        "sync_protocol_docs",
        "sync_all_protocol_docs",
        "get_configured_protocols",
    ):
        from . import live_docs
        return getattr(live_docs, name)

    # Protocol graph
    if name in (
        "ProtocolEntityType",
        "ProtocolRelationType",
        "ProtocolEntity",
        "ProtocolRelationship",
        "ProtocolGraphClient",
        "get_protocol_graph",
        "initialize_protocol_graph",
    ):
        from . import protocol_graph
        return getattr(protocol_graph, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
