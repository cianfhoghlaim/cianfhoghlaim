"""
Compatibility shim for the legacy `crypteolas.knowledge_graph.falkordb_client` import.

FalkorDB is the vector+graph hybrid database backing the temporal
knowledge graph. A real implementation would expose a connection pool,
Cypher executor, and graph-construction helpers. This stub satisfies
the import path so the test suite (which references these symbols) can
be loaded and skipped cleanly. See tuatha/crypteolas/STATUS.md.
"""

from __future__ import annotations

from typing import Any


async def get_falkordb_client() -> dict[str, Any]:
    """Stub: returns a placeholder client descriptor."""
    return {
        "backend": "falkordb",
        "uri": "falkordb://localhost:6379",
        "status": "stub",
    }


async def execute_cypher(query: str, **params: Any) -> list[dict[str, Any]]:
    """Stub: returns an empty result set."""
    return []


async def create_protocol_node(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Stub: returns a placeholder node descriptor."""
    return {"kind": "Protocol", "args": list(args), "kwargs": kwargs}


async def create_relationship(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Stub: returns a placeholder edge descriptor."""
    return {"kind": "Relationship", "args": list(args), "kwargs": kwargs}


__all__ = [
    "get_falkordb_client",
    "execute_cypher",
    "create_protocol_node",
    "create_relationship",
]
