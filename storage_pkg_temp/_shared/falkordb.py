"""
FalkorDB Client Implementation.

Provides graph database operations for FalkorDB (Redis-based graph).
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence
from typing import Any

from .interface import GraphClient, GraphEdge, GraphNode, GraphQueryResult

logger = logging.getLogger(__name__)


class FalkorDBClient(GraphClient):
    """
    FalkorDB graph database client.

    FalkorDB is a Redis-based graph database that supports Cypher queries.
    It's particularly useful for temporal knowledge graphs (via Graphiti).

    Usage:
        client = FalkorDBClient(host="localhost", port=6379, graph_name="curriculum")
        client.connect()

        # Create topic node
        topic_id = client.create_node(
            labels=["Topic"],
            properties={"name": "OOP", "subject": "Computer Science"}
        )

        # Query prerequisites
        results = client.query(
            "MATCH (t1:Topic)-[:PREREQUISITE_FOR]->(t2:Topic) "
            "WHERE t2.name = 'Design Patterns' "
            "RETURN t1"
        )
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        graph_name: str = "knowledge",
        password: str | None = None,
    ):
        self.host = host
        self.port = port
        self.graph_name = graph_name
        self.password = password
        self._client = None
        self._graph = None
        self._connected = False

    def connect(self) -> None:
        """Establish connection to FalkorDB."""
        try:
            from falkordb import FalkorDB

            self._client = FalkorDB(
                host=self.host,
                port=self.port,
                password=self.password,
            )
            self._graph = self._client.select_graph(self.graph_name)
            self._connected = True
            logger.info(f"Connected to FalkorDB at {self.host}:{self.port}/{self.graph_name}")
        except ImportError:
            raise ImportError(
                "falkordb package required for FalkorDB client. "
                "Install with: pip install falkordb"
            )
        except Exception as e:
            logger.error(f"Failed to connect to FalkorDB: {e}")
            raise

    def close(self) -> None:
        """Close the database connection."""
        if self._client:
            # FalkorDB doesn't have explicit close
            self._connected = False
            logger.info("Disconnected from FalkorDB")

    def _ensure_connected(self) -> None:
        """Ensure we're connected to the database."""
        if not self._connected or not self._graph:
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
            # FalkorDB uses different parameter syntax
            if params:
                # Convert params to FalkorDB format
                result = self._graph.query(cypher, params)
            else:
                result = self._graph.query(cypher)

            # Process result set
            if result.result_set:
                for record in result.result_set:
                    row = {}
                    for i, value in enumerate(record):
                        col_name = result.header[i][1] if result.header else f"col_{i}"
                        row[col_name] = value

                        # Extract nodes and edges
                        if hasattr(value, "labels"):  # Node
                            nodes.append(
                                GraphNode(
                                    id=str(value.properties.get("id", value.id)),
                                    labels=list(value.labels),
                                    properties=dict(value.properties),
                                )
                            )
                        elif hasattr(value, "relation"):  # Edge
                            edges.append(
                                GraphEdge(
                                    id=str(value.properties.get("id", value.id)),
                                    type=value.relation,
                                    source_id=str(value.src_node),
                                    target_id=str(value.dest_node),
                                    properties=dict(value.properties),
                                )
                            )

                    raw_results.append(row)

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

        # Build property string for FalkorDB
        props_parts = []
        for k, v in properties.items():
            if isinstance(v, str):
                props_parts.append(f'{k}: "{v}"')
            elif isinstance(v, bool):
                props_parts.append(f"{k}: {str(v).lower()}")
            elif v is None:
                props_parts.append(f"{k}: null")
            else:
                props_parts.append(f"{k}: {v}")

        props_str = ", ".join(props_parts)
        cypher = f"CREATE (n:{labels_str} {{{props_str}}}) RETURN n.id as id"

        result = self.query(cypher)

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
        props_parts = []
        for k, v in props.items():
            if isinstance(v, str):
                props_parts.append(f'{k}: "{v}"')
            elif isinstance(v, bool):
                props_parts.append(f"{k}: {str(v).lower()}")
            elif v is None:
                props_parts.append(f"{k}: null")
            else:
                props_parts.append(f"{k}: {v}")

        props_str = ", ".join(props_parts)
        props_clause = f" {{{props_str}}}" if props_str else ""

        cypher = f"""
        MATCH (a {{id: "{source_id}"}}), (b {{id: "{target_id}"}})
        CREATE (a)-[r:{edge_type}{props_clause}]->(b)
        RETURN r.id as id
        """

        result = self.query(cypher)

        if result.raw_result:
            return result.raw_result[0].get("id", edge_id)
        return edge_id

    def get_node(self, node_id: str) -> GraphNode | None:
        """Get a node by ID."""
        self._ensure_connected()

        result = self.query(f'MATCH (n {{id: "{node_id}"}}) RETURN n')

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
        WHERE a.id = "{node_id}"
        RETURN DISTINCT b
        """

        result = self.query(cypher)
        return result.nodes

    def delete_node(self, node_id: str, cascade: bool = False) -> bool:
        """Delete a node."""
        self._ensure_connected()

        if cascade:
            cypher = f'MATCH (n {{id: "{node_id}"}}) DETACH DELETE n RETURN count(n) as count'
        else:
            cypher = f'MATCH (n {{id: "{node_id}"}}) DELETE n RETURN count(n) as count'

        result = self.query(cypher)

        if result.raw_result:
            return result.raw_result[0].get("count", 0) > 0
        return False

    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge."""
        self._ensure_connected()

        result = self.query(
            f'MATCH ()-[r {{id: "{edge_id}"}}]->() DELETE r RETURN count(r) as count'
        )

        if result.raw_result:
            return result.raw_result[0].get("count", 0) > 0
        return False

    # =========================================================================
    # FalkorDB-Specific Methods
    # =========================================================================

    def create_index(self, label: str, property: str) -> None:
        """Create an index on a label/property combination."""
        self._ensure_connected()
        self.query(f"CREATE INDEX FOR (n:{label}) ON (n.{property})")
        logger.info(f"Created index on :{label}({property})")

    def get_schema(self) -> dict[str, Any]:
        """Get database schema information."""
        self._ensure_connected()

        # FalkorDB schema introspection
        labels_result = self.query("CALL db.labels()")
        labels = [next(iter(r.values())) for r in labels_result.raw_result if r]

        types_result = self.query("CALL db.relationshipTypes()")
        rel_types = [next(iter(r.values())) for r in types_result.raw_result if r]

        return {
            "labels": labels,
            "relationship_types": rel_types,
            "node_count": self.count_nodes(),
            "edge_count": self.count_edges(),
        }
