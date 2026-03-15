"""
Graph Database Interface.

Defines the protocol for graph database operations,
enabling consistent usage across Memgraph, FalkorDB, and Neo4j.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Represents a node in the graph."""

    id: str
    labels: list[str]
    properties: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class GraphEdge:
    """Represents an edge/relationship in the graph."""

    id: str
    type: str
    source_id: str
    target_id: str
    properties: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class GraphQueryResult:
    """Result from a graph query."""

    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    raw_result: list[dict[str, Any]] = field(default_factory=list)
    query: str = ""


class GraphClient(ABC):
    """
    Abstract interface for graph database operations.

    Implementations:
    - MemgraphClient: For Memgraph (Cypher)
    - FalkorDBClient: For FalkorDB (Cypher with Redis)
    - Neo4jClient: For Neo4j (used by LightRAG)

    Usage:
        client = MemgraphClient(uri="bolt://localhost:7687")

        # Create nodes
        node_id = client.create_node(
            labels=["Document"],
            properties={"title": "My Doc", "path": "/path/to/doc"}
        )

        # Create relationships
        client.create_edge(
            source_id=node_id,
            target_id=topic_id,
            edge_type="COVERS",
            properties={"confidence": 0.95}
        )

        # Query
        results = client.query("MATCH (d:Document)-[:COVERS]->(t:Topic) RETURN d, t")
    """

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the database."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def query(
        self,
        cypher: str,
        params: dict[str, Any] | None = None,
    ) -> GraphQueryResult:
        """
        Execute a Cypher query.

        Args:
            cypher: Cypher query string
            params: Query parameters

        Returns:
            GraphQueryResult with nodes, edges, and raw results
        """
        pass

    @abstractmethod
    def create_node(
        self,
        labels: Sequence[str],
        properties: dict[str, Any],
        node_id: str | None = None,
    ) -> str:
        """
        Create a node in the graph.

        Args:
            labels: Node labels (e.g., ["Document", "PDF"])
            properties: Node properties
            node_id: Optional explicit ID (generated if not provided)

        Returns:
            Node ID
        """
        pass

    @abstractmethod
    def create_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        properties: dict[str, Any] | None = None,
    ) -> str:
        """
        Create an edge between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Relationship type (e.g., "COVERS", "PREREQUISITE_FOR")
            properties: Edge properties

        Returns:
            Edge ID
        """
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> GraphNode | None:
        """
        Get a node by ID.

        Args:
            node_id: Node ID

        Returns:
            GraphNode or None if not found
        """
        pass

    @abstractmethod
    def get_neighbors(
        self,
        node_id: str,
        edge_types: Sequence[str] | None = None,
        direction: str = "both",
        depth: int = 1,
    ) -> list[GraphNode]:
        """
        Get neighboring nodes.

        Args:
            node_id: Starting node ID
            edge_types: Filter by relationship types
            direction: "in", "out", or "both"
            depth: Maximum traversal depth

        Returns:
            List of neighboring nodes
        """
        pass

    @abstractmethod
    def delete_node(self, node_id: str, cascade: bool = False) -> bool:
        """
        Delete a node.

        Args:
            node_id: Node ID
            cascade: If True, delete connected edges

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def delete_edge(self, edge_id: str) -> bool:
        """
        Delete an edge.

        Args:
            edge_id: Edge ID

        Returns:
            True if deleted, False if not found
        """
        pass

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def create_nodes_batch(
        self,
        nodes: list[dict[str, Any]],
    ) -> list[str]:
        """
        Create multiple nodes in a batch.

        Args:
            nodes: List of dicts with "labels" and "properties"

        Returns:
            List of created node IDs
        """
        return [
            self.create_node(
                labels=n.get("labels", []),
                properties=n.get("properties", {}),
                node_id=n.get("id"),
            )
            for n in nodes
        ]

    def create_edges_batch(
        self,
        edges: list[dict[str, Any]],
    ) -> list[str]:
        """
        Create multiple edges in a batch.

        Args:
            edges: List of dicts with "source_id", "target_id", "type", "properties"

        Returns:
            List of created edge IDs
        """
        return [
            self.create_edge(
                source_id=e["source_id"],
                target_id=e["target_id"],
                edge_type=e["type"],
                properties=e.get("properties"),
            )
            for e in edges
        ]

    def get_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5,
    ) -> list[GraphNode]:
        """
        Find shortest path between two nodes.

        Args:
            start_id: Starting node ID
            end_id: Target node ID
            max_depth: Maximum path length

        Returns:
            List of nodes in the path (empty if no path)
        """
        result = self.query(
            f"""
            MATCH path = shortestPath(
                (a)-[*..{max_depth}]-(b)
            )
            WHERE a.id = $start_id AND b.id = $end_id
            RETURN nodes(path) as nodes
            """,
            {"start_id": start_id, "end_id": end_id},
        )
        return result.nodes

    def count_nodes(self, label: str | None = None) -> int:
        """Count nodes, optionally filtered by label."""
        if label:
            result = self.query(f"MATCH (n:{label}) RETURN count(n) as count")
        else:
            result = self.query("MATCH (n) RETURN count(n) as count")

        if result.raw_result:
            return result.raw_result[0].get("count", 0)
        return 0

    def count_edges(self, edge_type: str | None = None) -> int:
        """Count edges, optionally filtered by type."""
        if edge_type:
            result = self.query(f"MATCH ()-[r:{edge_type}]->() RETURN count(r) as count")
        else:
            result = self.query("MATCH ()-[r]->() RETURN count(r) as count")

        if result.raw_result:
            return result.raw_result[0].get("count", 0)
        return 0
