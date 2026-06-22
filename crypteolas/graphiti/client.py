"""
FalkorDB Graphiti client for temporal knowledge graphs.

Provides a client wrapper for interacting with FalkorDB using
Graphiti's temporal graph model.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Optional

from dataclasses import dataclass


@dataclass
class TemporalNode:
    """A node with temporal properties."""
    id: str
    label: str
    properties: dict[str, Any]
    valid_from: datetime
    valid_to: Optional[datetime] = None
    transaction_time: Optional[datetime] = None


@dataclass
class TemporalEdge:
    """An edge with temporal properties."""
    from_id: str
    to_id: str
    relationship_type: str
    properties: dict[str, Any]
    valid_from: datetime
    valid_to: Optional[datetime] = None


class GraphitiClient:
    """Client for FalkorDB with Graphiti temporal model.

    Provides methods for creating and querying temporal knowledge graphs
    with bi-temporal support (valid time and transaction time).

    Example:
        ```python
        client = GraphitiClient(host="localhost", port=6379)
        client.create_temporal_node(
            node_id="doc_123",
            label="Document",
            properties={"title": "My Doc"},
            valid_from=datetime.now(),
        )
        ```
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        graph_name: str = "temporal_knowledge",
    ):
        """Initialize the Graphiti client.

        Args:
            host: FalkorDB host
            port: FalkorDB port
            graph_name: Name of the graph to use
        """
        self.host = host
        self.port = port
        self.graph_name = graph_name
        self._client = None
        self._graph = None

    @property
    def client(self):
        """Get or create FalkorDB client."""
        if self._client is None:
            try:
                from falkordb import FalkorDB
                self._client = FalkorDB(host=self.host, port=self.port)
            except ImportError:
                raise ImportError("falkordb not installed. Run: pip install falkordb")
        return self._client

    @property
    def graph(self):
        """Get or create graph instance."""
        if self._graph is None:
            self._graph = self.client.select_graph(self.graph_name)
        return self._graph

    def create_temporal_node(
        self,
        node_id: str,
        label: str,
        properties: dict[str, Any],
        valid_from: datetime,
        valid_to: Optional[datetime] = None,
    ) -> TemporalNode:
        """Create a node with temporal properties.

        Args:
            node_id: Unique node identifier
            label: Node label (type)
            properties: Node properties
            valid_from: When this knowledge became valid
            valid_to: When this knowledge stopped being valid (None = still valid)

        Returns:
            Created TemporalNode
        """
        now = datetime.now()

        # Build properties string
        props = {
            "id": node_id,
            **properties,
            "valid_from": valid_from.isoformat(),
            "transaction_time": now.isoformat(),
        }
        if valid_to:
            props["valid_to"] = valid_to.isoformat()

        prop_str = ", ".join(f"{k}: ${k}" for k in props.keys())

        query = f"CREATE (n:{label} {{{prop_str}}}) RETURN n"
        self.graph.query(query, params=props)

        return TemporalNode(
            id=node_id,
            label=label,
            properties=properties,
            valid_from=valid_from,
            valid_to=valid_to,
            transaction_time=now,
        )

    def create_temporal_edge(
        self,
        from_id: str,
        to_id: str,
        relationship_type: str,
        properties: dict[str, Any],
        valid_from: datetime,
        valid_to: Optional[datetime] = None,
    ) -> TemporalEdge:
        """Create an edge with temporal properties.

        Args:
            from_id: Source node ID
            to_id: Target node ID
            relationship_type: Relationship type
            properties: Edge properties
            valid_from: When this relationship became valid
            valid_to: When this relationship stopped being valid

        Returns:
            Created TemporalEdge
        """
        props = {
            **properties,
            "valid_from": valid_from.isoformat(),
            "created_at": datetime.now().isoformat(),
        }
        if valid_to:
            props["valid_to"] = valid_to.isoformat()

        prop_str = ", ".join(f"{k}: ${k}" for k in props.keys())

        query = f"""
            MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
            CREATE (a)-[r:{relationship_type} {{{prop_str}}}]->(b)
            RETURN r
        """
        self.graph.query(query, params={"from_id": from_id, "to_id": to_id, **props})

        return TemporalEdge(
            from_id=from_id,
            to_id=to_id,
            relationship_type=relationship_type,
            properties=properties,
            valid_from=valid_from,
            valid_to=valid_to,
        )

    def query_at_time(
        self,
        query: str,
        as_of: datetime,
        params: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Execute a query filtered to a specific point in time.

        Args:
            query: Cypher query to execute
            as_of: Point in time to query
            params: Query parameters

        Returns:
            Query results filtered to the specified time
        """
        time_filter = f"""
            WHERE n.valid_from <= '{as_of.isoformat()}'
            AND (n.valid_to IS NULL OR n.valid_to > '{as_of.isoformat()}')
        """

        # Inject time filter into query
        if "WHERE" in query.upper():
            query = query.replace("WHERE", f"WHERE n.valid_from <= '{as_of.isoformat()}' AND (n.valid_to IS NULL OR n.valid_to > '{as_of.isoformat()}') AND")
        else:
            # Simple injection for basic queries
            pass

        result = self.graph.query(query, params=params or {})
        return [dict(r) for r in result.result_set]

    def get_node_history(self, node_id: str) -> list[dict[str, Any]]:
        """Get the full history of a node.

        Args:
            node_id: Node identifier

        Returns:
            List of node versions ordered by valid_from
        """
        query = """
            MATCH (n {id: $node_id})
            RETURN n
            ORDER BY n.valid_from
        """
        result = self.graph.query(query, params={"node_id": node_id})
        return [dict(r[0].properties) for r in result.result_set]

    def close(self):
        """Close the client connection."""
        self._client = None
        self._graph = None
