"""
Neo4j Client Implementation.

Provides graph database operations for Neo4j, compatible with LightRAG.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence
from typing import Any

from .interface import GraphClient, GraphEdge, GraphNode, GraphQueryResult

logger = logging.getLogger(__name__)


class Neo4jClient(GraphClient):
    """
    Neo4j graph database client.

    Compatible with LightRAG's knowledge graph requirements.

    Usage:
        client = Neo4jClient(uri="bolt://localhost:7687", auth=("neo4j", "password"))
        client.connect()

        # Create entity node
        entity_id = client.create_node(
            labels=["Entity"],
            properties={"name": "Machine Learning", "type": "concept"}
        )

        # Query triples
        results = client.query(
            "MATCH (s)-[r]->(o) WHERE s.name = 'Machine Learning' RETURN s, r, o"
        )
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "",
        database: str = "neo4j",
    ):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._driver = None
        self._connected = False

    def connect(self) -> None:
        """Establish connection to Neo4j."""
        try:
            from neo4j import GraphDatabase

            auth = (self.username, self.password) if self.password else None
            self._driver = GraphDatabase.driver(self.uri, auth=auth)
            self._driver.verify_connectivity()
            self._connected = True
            logger.info(f"Connected to Neo4j at {self.uri}")
        except ImportError:
            raise ImportError(
                "neo4j package required for Neo4j client. "
                "Install with: pip install neo4j"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self) -> None:
        """Close the database connection."""
        if self._driver:
            self._driver.close()
            self._connected = False
            logger.info("Disconnected from Neo4j")

    def _ensure_connected(self) -> None:
        """Ensure we're connected to the database."""
        if not self._connected or not self._driver:
            self.connect()

    def query(
        self,
        cypher: str,
        params: dict[str, Any] | None = None,
    ) -> GraphQueryResult:
        """Execute a Cypher query."""
        self._ensure_connected()

        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        raw_results: list[dict[str, Any]] = []

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
                                    id=str(value.get("id", value.element_id)),
                                    labels=list(value.labels),
                                    properties=dict(value),
                                )
                            )
                        elif hasattr(value, "type"):  # Relationship
                            edges.append(
                                GraphEdge(
                                    id=str(value.element_id),
                                    type=value.type,
                                    source_id=str(value.start_node.element_id),
                                    target_id=str(value.end_node.element_id),
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
        properties: dict[str, Any],
        node_id: str | None = None,
    ) -> str:
        """Create a node in the graph."""
        self._ensure_connected()

        node_id = node_id or str(uuid.uuid4())
        labels_str = ":".join(labels) if labels else "Node"
        properties["id"] = node_id

        # Build property string with parameters
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
        properties: dict[str, Any] | None = None,
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

    def get_node(self, node_id: str) -> GraphNode | None:
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
        edge_types: Sequence[str] | None = None,
        direction: str = "both",
        depth: int = 1,
    ) -> list[GraphNode]:
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
    # Neo4j/LightRAG-Specific Methods
    # =========================================================================

    def create_index(self, label: str, property: str) -> None:
        """Create an index on a label/property combination."""
        self._ensure_connected()
        self.query(f"CREATE INDEX IF NOT EXISTS FOR (n:{label}) ON (n.{property})")
        logger.info(f"Created index on :{label}({property})")

    def create_constraint(self, label: str, property: str) -> None:
        """Create a uniqueness constraint."""
        self._ensure_connected()
        self.query(
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{property} IS UNIQUE"
        )
        logger.info(f"Created constraint on :{label}({property})")

    def create_fulltext_index(
        self,
        index_name: str,
        labels: list[str],
        properties: list[str],
    ) -> None:
        """Create a full-text search index (for LightRAG compatibility)."""
        self._ensure_connected()
        labels_str = ", ".join(f"'{l}'" for l in labels)
        props_str = ", ".join(f"'{p}'" for p in properties)
        self.query(
            f"CREATE FULLTEXT INDEX {index_name} IF NOT EXISTS "
            f"FOR (n:{labels[0]}) ON EACH [{props_str}]"
        )
        logger.info(f"Created fulltext index: {index_name}")

    def fulltext_search(
        self,
        index_name: str,
        query: str,
        limit: int = 10,
    ) -> list[GraphNode]:
        """Search using full-text index."""
        self._ensure_connected()
        result = self.query(
            f"""
            CALL db.index.fulltext.queryNodes('{index_name}', $query)
            YIELD node, score
            RETURN node
            LIMIT {limit}
            """,
            {"query": query},
        )
        return result.nodes

    def get_schema(self) -> dict[str, Any]:
        """Get database schema information."""
        self._ensure_connected()

        # Get node labels
        labels_result = self.query("CALL db.labels()")
        labels = [r.get("label") for r in labels_result.raw_result if r.get("label")]

        # Get relationship types
        types_result = self.query("CALL db.relationshipTypes()")
        rel_types = [
            r.get("relationshipType")
            for r in types_result.raw_result
            if r.get("relationshipType")
        ]

        return {
            "labels": labels,
            "relationship_types": rel_types,
            "node_count": self.count_nodes(),
            "edge_count": self.count_edges(),
        }

    def create_triple(
        self,
        subject: str,
        predicate: str,
        object: str,
        subject_type: str = "Entity",
        object_type: str = "Entity",
        properties: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a triple (subject-predicate-object) for LightRAG compatibility.

        Args:
            subject: Subject entity name
            predicate: Relationship type
            object: Object entity name
            subject_type: Label for subject node
            object_type: Label for object node
            properties: Additional edge properties

        Returns:
            Edge ID
        """
        self._ensure_connected()

        props = properties or {}
        props["id"] = str(uuid.uuid4())

        props_str = ", ".join(f"{k}: ${k}" for k in props.keys())
        props_clause = f" {{{props_str}}}" if props_str else ""

        cypher = f"""
        MERGE (s:{subject_type} {{name: $subject}})
        MERGE (o:{object_type} {{name: $object}})
        CREATE (s)-[r:{predicate}{props_clause}]->(o)
        RETURN r.id as id
        """

        params = {"subject": subject, "object": object, **props}
        result = self.query(cypher, params)

        if result.raw_result:
            return result.raw_result[0].get("id", props["id"])
        return props["id"]
