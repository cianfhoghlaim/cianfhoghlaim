"""
Compatibility shim for the legacy `crypteolas.knowledge_graph.cognee_client` import.

The real implementation lives at `cognee.static_knowledge`. This module
re-exports the relevant functions so that test files and any other
caller that still uses the old `cognee_client` import path can find them.

When updating the test suite, prefer importing from
`tuatha.crypteolas.knowledge_graph.cognee.static_knowledge` directly.
"""

from __future__ import annotations

from sruth.tuatha.crypteolas.knowledge_graph.cognee.static_knowledge import (
    add_audit_report,
    add_code_knowledge,
    add_protocol_knowledge,
    compare_protocols,
    get_entity_relationships,
    get_vulnerability_patterns,
    search_knowledge,
    setup_cognee,
)

# Aliases for the legacy test API.
get_cognee_client = setup_cognee


async def add_document(*args, **kwargs):
    """Legacy alias: route to ``add_protocol_knowledge``."""
    return await add_protocol_knowledge(*args, **kwargs)


async def extract_entities(*args, **kwargs):
    """Legacy alias: route to ``search_knowledge`` for entity extraction."""
    return await search_knowledge(*args, **kwargs)


async def query_graph(*args, **kwargs):
    """Legacy alias: route to ``search_knowledge`` for graph queries."""
    return await search_knowledge(*args, **kwargs)


__all__ = [
    "setup_cognee",
    "get_cognee_client",
    "add_audit_report",
    "add_code_knowledge",
    "add_protocol_knowledge",
    "add_document",
    "compare_protocols",
    "extract_entities",
    "get_entity_relationships",
    "get_vulnerability_patterns",
    "query_graph",
    "search_knowledge",
]
