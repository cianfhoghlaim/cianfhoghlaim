"""
Shared graph database interfaces and base clients.

Provides a unified interface for graph database operations
across Memgraph, FalkorDB, and Neo4j.
"""

from .falkordb import FalkorDBClient
from .interface import (
    GraphClient,
    GraphEdge,
    GraphNode,
    GraphQueryResult,
)
from .memgraph import MemgraphClient
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
