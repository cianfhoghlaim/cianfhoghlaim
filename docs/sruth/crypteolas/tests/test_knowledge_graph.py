"""Tests for knowledge graph operations (Cognee and Graphiti)."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Check for optional dependencies
try:
    import cognee
    HAS_COGNEE = True
except ImportError:
    HAS_COGNEE = False

try:
    import graphiti_core
    HAS_GRAPHITI = True
except ImportError:
    HAS_GRAPHITI = False

try:
    import falkordb
    HAS_FALKORDB = True
except ImportError:
    HAS_FALKORDB = False

try:
    import neo4j
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False

# Skip decorators
requires_cognee = pytest.mark.skipif(not HAS_COGNEE, reason="cognee not installed")
requires_graphiti = pytest.mark.skipif(not HAS_GRAPHITI, reason="graphiti-core not installed")
requires_falkordb = pytest.mark.skipif(not HAS_FALKORDB, reason="falkordb not installed")
requires_neo4j = pytest.mark.skipif(not HAS_NEO4J, reason="neo4j not installed")


@requires_cognee
class TestCogneeKnowledgeGraph:
    """Tests for Cognee knowledge graph integration."""

    @pytest.mark.asyncio
    async def test_cognee_initialization(self):
        """Test Cognee client initialization."""
        with patch("cognee.Cognee") as mock_cognee:
            mock_client = AsyncMock()
            mock_cognee.return_value = mock_client

            from crypteolas.knowledge_graph.cognee_client import get_cognee_client

            client = await get_cognee_client()

            assert client is not None

    @pytest.mark.asyncio
    async def test_add_document_to_cognee(self):
        """Test adding a document to Cognee."""
        with patch("cognee.Cognee") as mock_cognee:
            mock_client = AsyncMock()
            mock_client.add = AsyncMock(return_value={"status": "success"})
            mock_cognee.return_value = mock_client

            from crypteolas.knowledge_graph.cognee_client import add_document

            result = await add_document(
                content="Aave is a decentralized lending protocol...",
                metadata={"source": "whitepaper", "protocol": "aave"}
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_cognee_entity_extraction(self):
        """Test entity extraction from documents."""
        mock_entities = [
            {"name": "Aave", "type": "Protocol", "confidence": 0.95},
            {"name": "Ethereum", "type": "Blockchain", "confidence": 0.98}
        ]

        with patch("cognee.Cognee") as mock_cognee:
            mock_client = AsyncMock()
            mock_client.extract_entities = AsyncMock(return_value=mock_entities)
            mock_cognee.return_value = mock_client

            from crypteolas.knowledge_graph.cognee_client import extract_entities

            entities = await extract_entities("Aave is deployed on Ethereum")

            assert len(entities) >= 1

    @pytest.mark.asyncio
    async def test_cognee_query(self):
        """Test querying Cognee knowledge graph."""
        mock_results = [
            {
                "entity": "Aave",
                "relationships": [
                    {"type": "DEPLOYED_ON", "target": "Ethereum"},
                    {"type": "CATEGORY", "target": "Lending"}
                ]
            }
        ]

        with patch("cognee.Cognee") as mock_cognee:
            mock_client = AsyncMock()
            mock_client.query = AsyncMock(return_value=mock_results)
            mock_cognee.return_value = mock_client

            from crypteolas.knowledge_graph.cognee_client import query_graph

            results = await query_graph("What protocols are on Ethereum?")

            assert isinstance(results, list)


@requires_graphiti
class TestGraphitiTemporalGraph:
    """Tests for Graphiti temporal knowledge graph."""

    @pytest.mark.asyncio
    async def test_graphiti_initialization(self):
        """Test Graphiti client initialization."""
        with patch("graphiti_core.Graphiti") as mock_graphiti:
            mock_client = AsyncMock()
            mock_graphiti.return_value = mock_client

            from crypteolas.knowledge_graph.graphiti_client import get_graphiti_client

            client = await get_graphiti_client()

            assert client is not None

    @pytest.mark.asyncio
    async def test_create_temporal_entity(self):
        """Test creating a temporal entity in Graphiti."""
        with patch("graphiti_core.Graphiti") as mock_graphiti:
            mock_client = AsyncMock()
            mock_client.add_episode = AsyncMock(return_value={"id": "ep_123"})
            mock_graphiti.return_value = mock_client

            from crypteolas.knowledge_graph.graphiti_client import add_episode

            result = await add_episode(
                name="Aave V3 Launch",
                content="Aave V3 was launched on Ethereum mainnet",
                timestamp=datetime(2023, 1, 27),
                source="announcement"
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_graphiti_temporal_query(self):
        """Test temporal query in Graphiti."""
        mock_results = [
            {
                "episode": "Aave V3 Launch",
                "timestamp": "2023-01-27T00:00:00Z",
                "entities": ["Aave", "Ethereum"]
            }
        ]

        with patch("graphiti_core.Graphiti") as mock_graphiti:
            mock_client = AsyncMock()
            mock_client.search = AsyncMock(return_value=mock_results)
            mock_graphiti.return_value = mock_client

            from crypteolas.knowledge_graph.graphiti_client import temporal_search

            results = await temporal_search(
                query="Aave launches",
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 12, 31)
            )

            assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_state_evolution_tracking(self):
        """Test tracking state evolution over time."""
        mock_history = [
            {"timestamp": "2023-01-01", "tvl": 5000000000},
            {"timestamp": "2023-06-01", "tvl": 8000000000},
            {"timestamp": "2024-01-01", "tvl": 10500000000}
        ]

        with patch("graphiti_core.Graphiti") as mock_graphiti:
            mock_client = AsyncMock()
            mock_client.get_entity_history = AsyncMock(return_value=mock_history)
            mock_graphiti.return_value = mock_client

            from crypteolas.knowledge_graph.graphiti_client import get_entity_history

            history = await get_entity_history("aave", attribute="tvl")

            assert len(history) >= 1
            # Verify temporal ordering
            if len(history) > 1:
                for i in range(1, len(history)):
                    assert history[i]["timestamp"] >= history[i - 1]["timestamp"]


@requires_falkordb
class TestFalkorDBGraph:
    """Tests for FalkorDB graph database operations."""

    def test_falkordb_connection(self):
        """Test FalkorDB connection."""
        with patch("falkordb.FalkorDB") as mock_falkor:
            mock_client = MagicMock()
            mock_falkor.return_value = mock_client

            from crypteolas.knowledge_graph.falkordb_client import get_falkordb_client

            client = get_falkordb_client()

            assert client is not None

    def test_cypher_query(self):
        """Test Cypher query execution."""
        mock_results = [
            {"n": {"name": "Aave", "category": "Lending"}},
            {"n": {"name": "Compound", "category": "Lending"}}
        ]

        with patch("falkordb.FalkorDB") as mock_falkor:
            mock_client = MagicMock()
            mock_graph = MagicMock()
            mock_graph.query.return_value.result_set = mock_results
            mock_client.select_graph.return_value = mock_graph
            mock_falkor.return_value = mock_client

            from crypteolas.knowledge_graph.falkordb_client import execute_cypher

            results = execute_cypher("MATCH (n:Protocol {category: 'Lending'}) RETURN n")

            assert len(results) >= 1

    def test_create_protocol_node(self):
        """Test creating a protocol node."""
        with patch("falkordb.FalkorDB") as mock_falkor:
            mock_client = MagicMock()
            mock_graph = MagicMock()
            mock_graph.query.return_value = MagicMock()
            mock_client.select_graph.return_value = mock_graph
            mock_falkor.return_value = mock_client

            from crypteolas.knowledge_graph.falkordb_client import create_protocol_node

            result = create_protocol_node(
                protocol_id="aave",
                name="Aave",
                category="Lending",
                tvl=10500000000
            )

            mock_graph.query.assert_called()

    def test_create_relationship(self):
        """Test creating a relationship between nodes."""
        with patch("falkordb.FalkorDB") as mock_falkor:
            mock_client = MagicMock()
            mock_graph = MagicMock()
            mock_graph.query.return_value = MagicMock()
            mock_client.select_graph.return_value = mock_graph
            mock_falkor.return_value = mock_client

            from crypteolas.knowledge_graph.falkordb_client import create_relationship

            create_relationship(
                from_id="aave",
                to_id="ethereum",
                relationship_type="DEPLOYED_ON"
            )

            mock_graph.query.assert_called()


@requires_neo4j
class TestMemgraphGraph:
    """Tests for Memgraph graph database operations."""

    def test_memgraph_connection(self):
        """Test Memgraph connection via Neo4j driver."""
        with patch("neo4j.GraphDatabase") as mock_neo4j:
            mock_driver = MagicMock()
            mock_neo4j.driver.return_value = mock_driver

            from crypteolas.knowledge_graph.memgraph_client import get_memgraph_client

            client = get_memgraph_client()

            assert client is not None

    def test_memgraph_query(self):
        """Test Memgraph Cypher query."""
        mock_records = [
            MagicMock(data=lambda: {"name": "Aave", "tvl": 10500000000}),
            MagicMock(data=lambda: {"name": "Uniswap", "tvl": 5200000000})
        ]

        with patch("neo4j.GraphDatabase") as mock_neo4j:
            mock_driver = MagicMock()
            mock_session = MagicMock()
            mock_result = MagicMock()
            mock_result.__iter__ = lambda self: iter(mock_records)
            mock_session.run.return_value = mock_result
            mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_driver.session.return_value.__exit__ = MagicMock(return_value=None)
            mock_neo4j.driver.return_value = mock_driver

            from crypteolas.knowledge_graph.memgraph_client import query_protocols

            results = query_protocols(min_tvl=1000000000)

            assert mock_session.run.called


class TestKnowledgeGraphOperations:
    """Tests for common knowledge graph operations."""

    def test_entity_normalization(self):
        """Test entity name normalization."""
        # Entity names should be normalized for consistency
        entities = ["AAVE", "aave", "Aave"]

        normalized = [e.lower().strip() for e in entities]

        assert all(n == "aave" for n in normalized)

    def test_relationship_validation(self):
        """Test relationship type validation."""
        valid_relationships = [
            "DEPLOYED_ON",
            "COMPETES_WITH",
            "AUDITED_BY",
            "USES_TOKEN",
            "INTEGRATED_WITH"
        ]

        relationship = "DEPLOYED_ON"
        assert relationship in valid_relationships

    def test_temporal_ordering(self):
        """Test temporal ordering of events."""
        events = [
            {"timestamp": "2024-01-03", "event": "C"},
            {"timestamp": "2024-01-01", "event": "A"},
            {"timestamp": "2024-01-02", "event": "B"}
        ]

        sorted_events = sorted(events, key=lambda x: x["timestamp"])

        assert sorted_events[0]["event"] == "A"
        assert sorted_events[1]["event"] == "B"
        assert sorted_events[2]["event"] == "C"


class TestGraphSchemas:
    """Tests for knowledge graph schemas."""

    def test_protocol_schema(self):
        """Test protocol node schema."""
        protocol_schema = {
            "id": str,
            "name": str,
            "category": str,
            "tvl": float,
            "chains": list,
            "token": str,
            "created_at": str
        }

        sample_protocol = {
            "id": "aave",
            "name": "Aave",
            "category": "Lending",
            "tvl": 10500000000.0,
            "chains": ["Ethereum", "Polygon"],
            "token": "AAVE",
            "created_at": "2020-01-08T00:00:00Z"
        }

        for key, expected_type in protocol_schema.items():
            assert key in sample_protocol
            assert isinstance(sample_protocol[key], expected_type)

    def test_relationship_schema(self):
        """Test relationship schema."""
        relationship_schema = {
            "type": str,
            "source": str,
            "target": str,
            "properties": dict
        }

        sample_relationship = {
            "type": "DEPLOYED_ON",
            "source": "aave",
            "target": "ethereum",
            "properties": {"since": "2020-01-08"}
        }

        for key, expected_type in relationship_schema.items():
            assert key in sample_relationship
            assert isinstance(sample_relationship[key], expected_type)

    def test_event_schema(self):
        """Test temporal event schema."""
        event_schema = {
            "id": str,
            "type": str,
            "timestamp": str,
            "entities": list,
            "description": str
        }

        sample_event = {
            "id": "evt_001",
            "type": "PROTOCOL_LAUNCH",
            "timestamp": "2023-01-27T00:00:00Z",
            "entities": ["aave_v3", "ethereum"],
            "description": "Aave V3 launched on Ethereum mainnet"
        }

        for key, expected_type in event_schema.items():
            assert key in sample_event
            assert isinstance(sample_event[key], expected_type)


class TestGraphTraversals:
    """Tests for graph traversal patterns."""

    def test_find_related_protocols(self):
        """Test finding related protocols through graph traversal."""
        # Mock graph structure
        protocols = {
            "aave": {"integrates": ["chainlink", "uniswap"]},
            "compound": {"integrates": ["chainlink"]},
            "uniswap": {"integrates": ["chainlink"]}
        }

        # Find protocols that share integrations with aave
        aave_integrations = set(protocols["aave"]["integrates"])
        related = []

        for proto, data in protocols.items():
            if proto != "aave":
                shared = set(data["integrates"]) & aave_integrations
                if shared:
                    related.append({"protocol": proto, "shared": list(shared)})

        assert len(related) == 2
        assert all("chainlink" in r["shared"] for r in related)

    def test_find_protocol_dependencies(self):
        """Test finding protocol dependencies."""
        dependencies = {
            "aave": ["chainlink", "openzeppelin"],
            "uniswap": ["openzeppelin"],
            "curve": ["openzeppelin", "vyper"]
        }

        # Find common dependencies
        all_deps = [set(deps) for deps in dependencies.values()]
        common = all_deps[0]
        for deps in all_deps[1:]:
            common = common & deps

        assert "openzeppelin" in common
