"""
Tests for sruth.shared.graph module.

Tests:
- GraphNode and GraphEdge dataclasses
- GraphQueryResult
- GraphClient interface compliance
"""


import pytest


class TestGraphDataclasses:
    """Tests for graph dataclasses."""

    def test_graph_node_creation(self):
        """Test GraphNode creation."""
        from sruth.shared.graph import GraphNode

        node = GraphNode(
            id="node-1",
            labels=["Person", "User"],
            properties={"name": "Alice", "age": 30},
        )

        assert node.id == "node-1"
        assert "Person" in node.labels
        assert node.properties["name"] == "Alice"

    def test_graph_node_hash(self):
        """Test GraphNode is hashable by id."""
        from sruth.shared.graph import GraphNode

        node1 = GraphNode(id="1", labels=["A"], properties={})
        node2 = GraphNode(id="1", labels=["B"], properties={"x": 1})
        node3 = GraphNode(id="2", labels=["A"], properties={})

        assert hash(node1) == hash(node2)  # Same ID
        assert hash(node1) != hash(node3)  # Different ID

    def test_graph_edge_creation(self):
        """Test GraphEdge creation."""
        from sruth.shared.graph import GraphEdge

        edge = GraphEdge(
            id="edge-1",
            type="KNOWS",
            source_id="person-1",
            target_id="person-2",
            properties={"since": 2020},
        )

        assert edge.id == "edge-1"
        assert edge.type == "KNOWS"
        assert edge.source_id == "person-1"
        assert edge.target_id == "person-2"

    def test_graph_query_result(self):
        """Test GraphQueryResult creation."""
        from sruth.shared.graph import GraphEdge, GraphNode, GraphQueryResult

        node = GraphNode(id="1", labels=["Test"], properties={})
        edge = GraphEdge(id="e1", type="REL", source_id="1", target_id="2", properties={})

        result = GraphQueryResult(
            nodes=[node],
            edges=[edge],
            raw_result=[{"n": "data"}],
            query="MATCH (n) RETURN n",
        )

        assert len(result.nodes) == 1
        assert len(result.edges) == 1
        assert result.query == "MATCH (n) RETURN n"


class TestGraphClientInterface:
    """Tests for GraphClient interface."""

    def test_memgraph_client_interface(self):
        """Test MemgraphClient implements GraphClient interface."""
        from sruth.shared.graph import MemgraphClient

        client = MemgraphClient()

        # Check required methods exist
        assert hasattr(client, "connect")
        assert hasattr(client, "close")
        assert hasattr(client, "query")
        assert hasattr(client, "create_node")
        assert hasattr(client, "create_edge")
        assert hasattr(client, "get_node")
        assert hasattr(client, "get_neighbors")
        assert hasattr(client, "delete_node")
        assert hasattr(client, "delete_edge")

    def test_falkordb_client_interface(self):
        """Test FalkorDBClient implements GraphClient interface."""
        from sruth.shared.graph import FalkorDBClient

        client = FalkorDBClient()

        # Check required methods exist
        assert hasattr(client, "connect")
        assert hasattr(client, "close")
        assert hasattr(client, "query")
        assert hasattr(client, "create_node")
        assert hasattr(client, "create_edge")
        assert hasattr(client, "get_node")
        assert hasattr(client, "get_neighbors")
        assert hasattr(client, "delete_node")
        assert hasattr(client, "delete_edge")

    def test_neo4j_client_interface(self):
        """Test Neo4jClient implements GraphClient interface."""
        from sruth.shared.graph import Neo4jClient

        client = Neo4jClient()

        # Check required methods exist
        assert hasattr(client, "connect")
        assert hasattr(client, "close")
        assert hasattr(client, "query")
        assert hasattr(client, "create_node")
        assert hasattr(client, "create_edge")
        assert hasattr(client, "get_node")
        assert hasattr(client, "get_neighbors")
        assert hasattr(client, "delete_node")
        assert hasattr(client, "delete_edge")

        # Neo4j-specific methods
        assert hasattr(client, "create_triple")
        assert hasattr(client, "fulltext_search")


class TestGraphClientConvenienceMethods:
    """Tests for GraphClient convenience methods."""

    def test_count_nodes_method(self):
        """Test count_nodes convenience method exists."""
        from sruth.shared.graph import MemgraphClient

        client = MemgraphClient()
        assert hasattr(client, "count_nodes")
        assert callable(client.count_nodes)

    def test_count_edges_method(self):
        """Test count_edges convenience method exists."""
        from sruth.shared.graph import MemgraphClient

        client = MemgraphClient()
        assert hasattr(client, "count_edges")
        assert callable(client.count_edges)

    def test_get_path_method(self):
        """Test get_path convenience method exists."""
        from sruth.shared.graph import MemgraphClient

        client = MemgraphClient()
        assert hasattr(client, "get_path")
        assert callable(client.get_path)

    def test_create_nodes_batch_method(self):
        """Test create_nodes_batch convenience method exists."""
        from sruth.shared.graph import MemgraphClient

        client = MemgraphClient()
        assert hasattr(client, "create_nodes_batch")
        assert callable(client.create_nodes_batch)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
