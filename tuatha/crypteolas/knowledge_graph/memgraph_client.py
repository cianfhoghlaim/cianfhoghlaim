"""
Compatibility shim for the legacy `crypteolas.knowledge_graph.memgraph_client` import.

Memgraph is the in-memory graph database used by the static (Cognee)
knowledge graph. A real implementation would expose a Bolt driver
connection pool and Cypher executor. This stub satisfies the import
path so the test suite (which references these symbols) can be loaded
and skipped cleanly. See tuatha/crypteolas/STATUS.md.
"""

from __future__ import annotations

from typing import Any


async def get_memgraph_client() -> dict[str, Any]:
    """Stub: returns a placeholder client descriptor."""
    return {
        "backend": "memgraph",
        "uri": "bolt://localhost:7687",
        "status": "stub",
    }


async def query_protocols(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    """Stub: returns an empty result set."""
    return []


__all__ = [
    "get_memgraph_client",
    "query_protocols",
]
