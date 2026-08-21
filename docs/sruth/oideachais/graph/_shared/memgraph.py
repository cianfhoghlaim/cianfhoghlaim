"""
Memgraph Client Implementation.

Provides graph database operations for Memgraph using the Bolt protocol.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional, Sequence

from .interface import GraphClient, GraphEdge, GraphNode, GraphQueryResult

logger = logging.getLogger(__name__)


class MemgraphClient(GraphClient):
    """
    Memgraph graph database client.

    Usage:
        client = MemgraphClient(uri="bolt://localhost:7687")
        client.connect()

        # Create document node
        doc_id = client.create_node(
            labels=["Document"],
            properties={"title": "My Doc", "path": "/path"}
        )

        # Query relationships
        results = client.query(
            "MATCH (d:Document)-[:COVERS]->(t:Topic) RETURN d, t"
        )
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "",
        password: str = "",
        database: str = "memgraph",
    ):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._driver = None
        self._connected = False

    def connect(self) -> None:
        """Establish connection to Memgraph."""
        try:
            from neo4j import GraphDatabase

            auth = (self.username, self.password) if self.username else None
            self._driver = GraphDatabase.driver(self.uri, auth=auth)
            self._driver.verify_connectivity()
            self._connected = True
            logger.info(f"Connected to Memgraph at {self.uri}")
        except ImportError:
            raise ImportError(
                "neo4j package required for Memgraph client. Install with: pip install neo4j"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Memgraph: {e}")
            raise

    def close(self) -> None:
        """Close the database connection."""
        if self._driver:
            self._driver.close()
            self._connected = False
            logger.info("Disconnected from Memgraph")

    def _ensure_connected(self) -> None:
        """Ensure we're connected to the database."""
        if not self._connected or not self._driver:
            self.connect()

    def query(
        self,
        cypher: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> GraphQueryResult:
        """Execute a Cypher query."""
        self._ensure_connected()

        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        raw_results: List[Dict[str, Any]] = []

        try:
            with self._driver.session(database=self.database) as session:
                result = session.run(cypher, params or {})
                records = list(result)

                for record in records:
                    row = dict(record)
                    raw_results.append(row)

                    # Extract nodes and relationships from result
                    for value in row.values():
                        if hasattr(value, "labels"):  # Node
                            nodes.append(
                                GraphNode(
                                    id=str(value.get("id", value.id)),
                                    labels=list(value.labels),
                                    properties=dict(value),
                                )
                            )
                        elif hasattr(value, "type"):  # Relationship
                            edges.append(
                                GraphEdge(
                                    id=str(value.id),
                                    type=value.type,
                                    source_id=str(value.start_node.id),
                                    target_id=str(value.end_node.id),
                                    properties=dict(value),
                                )
                            )

            return GraphQueryResult(
                nodes=nodes,
                edges=edges,
                raw_result=raw_results,
                query=cypher,
            )

        except Exception as e:
            logger.error(f"Query failed: {cypher[:100]}... Error: {e}")
            raise

    def create_node(
        self,
        labels: Sequence[str],
        properties: Dict[str, Any],
        node_id: Optional[str] = None,
    ) -> str:
        """Create a node in the graph."""
        self._ensure_connected()

        node_id = node_id or str(uuid.uuid4())
        labels_str = ":".join(labels) if labels else "Node"
        properties["id"] = node_id

        # Build property string
        props = ", ".join(f"{k}: ${k}" for k in properties.keys())

        cypher = f"CREATE (n:{labels_str} {{{props}}}) RETURN n.id as id"

        result = self.query(cypher, properties)

        if result.raw_result:
            return result.raw_result[0].get("id", node_id)
        return node_id

    def create_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create an edge between two nodes."""
        self._ensure_connected()

        edge_id = str(uuid.uuid4())
        props = properties or {}
        props["id"] = edge_id

        # Build property string
        props_str = ", ".join(f"{k}: ${k}" for k in props.keys())
        props_clause = f" {{{props_str}}}" if props_str else ""

        cypher = f"""
        MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
        CREATE (a)-[r:{edge_type}{props_clause}]->(b)
        RETURN r.id as id
        """

        params = {"source_id": source_id, "target_id": target_id, **props}
        result = self.query(cypher, params)

        if result.raw_result:
            return result.raw_result[0].get("id", edge_id)
        return edge_id

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        self._ensure_connected()

        result = self.query(
            "MATCH (n {id: $node_id}) RETURN n",
            {"node_id": node_id},
        )

        if result.nodes:
            return result.nodes[0]
        return None

    def get_neighbors(
        self,
        node_id: str,
        edge_types: Optional[Sequence[str]] = None,
        direction: str = "both",
        depth: int = 1,
    ) -> List[GraphNode]:
        """Get neighboring nodes."""
        self._ensure_connected()

        # Build relationship pattern
        rel_types = "|".join(edge_types) if edge_types else ""
        rel_pattern = f"[:{rel_types}*1..{depth}]" if rel_types else f"[*1..{depth}]"

        # Direction
        if direction == "out":
            pattern = f"(a)-{rel_pattern}->(b)"
        elif direction == "in":
            pattern = f"(a)<-{rel_pattern}-(b)"
        else:
            pattern = f"(a)-{rel_pattern}-(b)"

        cypher = f"""
        MATCH {pattern}
        WHERE a.id = $node_id
        RETURN DISTINCT b
        """

        result = self.query(cypher, {"node_id": node_id})
        return result.nodes

    def delete_node(self, node_id: str, cascade: bool = False) -> bool:
        """Delete a node."""
        self._ensure_connected()

        if cascade:
            cypher = "MATCH (n {id: $node_id}) DETACH DELETE n RETURN count(n) as count"
        else:
            cypher = "MATCH (n {id: $node_id}) DELETE n RETURN count(n) as count"

        result = self.query(cypher, {"node_id": node_id})

        if result.raw_result:
            return result.raw_result[0].get("count", 0) > 0
        return False

    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge."""
        self._ensure_connected()

        result = self.query(
            "MATCH ()-[r {id: $edge_id}]->() DELETE r RETURN count(r) as count",
            {"edge_id": edge_id},
        )

        if result.raw_result:
            return result.raw_result[0].get("count", 0) > 0
        return False

    # =========================================================================
    # Memgraph-Specific Methods
    # =========================================================================

    def create_index(self, label: str, property: str) -> None:
        """Create an index on a label/property combination."""
        self._ensure_connected()
        self.query(f"CREATE INDEX ON :{label}({property})")
        logger.info(f"Created index on :{label}({property})")

    def create_constraint(self, label: str, property: str) -> None:
        """Create a uniqueness constraint."""
        self._ensure_connected()
        self.query(f"CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE")
        logger.info(f"Created constraint on :{label}({property})")

    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information."""
        self._ensure_connected()

        # Get node labels
        labels_result = self.query("CALL db.labels()")
        labels = [r.get("label") for r in labels_result.raw_result if r.get("label")]

        # Get relationship types
        types_result = self.query("CALL db.relationshipTypes()")
        rel_types = [
            r.get("relationshipType") for r in types_result.raw_result if r.get("relationshipType")
        ]

        return {
            "labels": labels,
            "relationship_types": rel_types,
            "node_count": self.count_nodes(),
            "edge_count": self.count_edges(),
        }
