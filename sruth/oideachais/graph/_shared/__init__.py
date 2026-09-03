"""
Shared graph database interfaces and base clients.

Provides a unified interface for graph database operations
across Memgraph, FalkorDB, and Neo4j.
"""

from .interface import (
    GraphClient,
    GraphNode,
    GraphEdge,
    GraphQueryResult,
)
from .memgraph import MemgraphClient
from .falkordb import FalkorDBClient
from .neo4j import Neo4jClient

__all__ = [
    "GraphClient",
    "GraphNode",
    "GraphEdge",
    "GraphQueryResult",
    "MemgraphClient",
    "FalkorDBClient",
    "Neo4jClient",
]
