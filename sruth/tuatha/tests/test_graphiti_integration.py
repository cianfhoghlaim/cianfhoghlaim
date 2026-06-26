"""
Tests for Graphiti knowledge graph integration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tuatha.knowledge_graph.graphiti import (
    CELTIC_ENTITY_TYPES,
    CELTIC_RELATION_TYPES,
    add_character,
    add_curriculum_unit,
    add_location,
    add_mythology_episode,
    add_story,
    find_story_connections,
    get_curriculum_for_mythology,
    get_graphiti_client,
    get_player_knowledge_graph,
    query_character_timeline,
    record_player_progress,
)


class TestCelticEntityTypes:
    """Test Celtic entity type definitions."""

    def test_character_type_exists(self):
        """Test Character entity type is defined."""
        assert "Character" in CELTIC_ENTITY_TYPES

    def test_location_type_exists(self):
        """Test Location entity type is defined."""
        assert "Location" in CELTIC_ENTITY_TYPES

    def test_story_type_exists(self):
        """Test Story entity type is defined."""
        assert "Story" in CELTIC_ENTITY_TYPES

    def test_curriculum_type_exists(self):
        """Test CurriculumUnit entity type is defined."""
        assert "CurriculumUnit" in CELTIC_ENTITY_TYPES

    def test_player_type_exists(self):
        """Test Player entity type is defined."""
        assert "Player" in CELTIC_ENTITY_TYPES

    def test_all_expected_types(self):
        """Test all expected entity types are present."""
        expected = [
            "Character",
            "Location",
            "Story",
            "Artifact",
            "Tradition",
            "Cycle",
            "CurriculumUnit",
            "LearningOutcome",
            "Player",
            "Quest",
        ]
        for entity_type in expected:
            assert entity_type in CELTIC_ENTITY_TYPES


class TestCelticRelationTypes:
    """Test Celtic relation type definitions."""

    def test_appears_in_relation(self):
        """Test APPEARS_IN relation exists."""
        assert "APPEARS_IN" in CELTIC_RELATION_TYPES

    def test_related_to_relation(self):
        """Test RELATED_TO relation exists."""
        assert "RELATED_TO" in CELTIC_RELATION_TYPES

    def test_teaches_relation(self):
        """Test TEACHES relation exists."""
        assert "TEACHES" in CELTIC_RELATION_TYPES

    def test_all_expected_relations(self):
        """Test all expected relation types are present."""
        expected = [
            "APPEARS_IN",
            "LOCATED_AT",
            "RELATED_TO",
            "POSSESSES",
            "PART_OF",
            "TEACHES",
            "REFERENCES",
            "COMPLETED",
            "LEARNED",
            "BELONGS_TO",
        ]
        for relation_type in expected:
            assert relation_type in CELTIC_RELATION_TYPES


class TestGraphitiClient:
    """Test Graphiti client configuration."""

    def test_get_client_function_exists(self):
        """Test get_graphiti_client function exists."""
        assert callable(get_graphiti_client)

    @patch.dict(
        "os.environ",
        {
            "NEO4J_URI": "bolt://test:7687",
            "NEO4J_USER": "test_user",
            "NEO4J_PASSWORD": "test_pass",
        },
    )
    def test_client_uses_env_vars(self):
        """Test client configuration from environment variables."""
        # This would test actual client creation, but requires Graphiti installed
        # For now, just verify the function is callable
        assert callable(get_graphiti_client)


class TestAddCharacter:
    """Test adding characters to knowledge graph."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Graphiti client."""
        client = MagicMock()
        client.add_episode = AsyncMock(return_value=MagicMock(uuid="test-uuid-123"))
        return client

    @pytest.mark.asyncio
    async def test_add_character_basic(self, mock_client):
        """Test adding a basic character."""
        uuid = await add_character(
            client=mock_client,
            name="Cú Chulainn",
            native_name="Cú Chulainn",
            tradition="irish_mythology",
            cycle="ulster_cycle",
            character_type="hero",
            description="The Hound of Ulster",
        )

        assert uuid == "test-uuid-123"
        mock_client.add_episode.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_character_with_powers(self, mock_client):
        """Test adding a character with powers."""
        uuid = await add_character(
            client=mock_client,
            name="Cú Chulainn",
            native_name="Cú Chulainn",
            tradition="irish_mythology",
            cycle="ulster_cycle",
            character_type="hero",
            description="The Hound of Ulster",
            powers=["Ríastrad", "Gáe Bulg mastery"],
        )

        assert uuid == "test-uuid-123"

    @pytest.mark.asyncio
    async def test_add_character_with_relationships(self, mock_client):
        """Test adding a character with relationships."""
        uuid = await add_character(
            client=mock_client,
            name="Cú Chulainn",
            native_name="Cú Chulainn",
            tradition="irish_mythology",
            cycle="ulster_cycle",
            character_type="hero",
            description="The Hound of Ulster",
            relationships=[
                {"type": "wife", "name": "Emer"},
                {"type": "teacher", "name": "Scáthach"},
            ],
        )

        assert uuid == "test-uuid-123"


class TestAddStory:
    """Test adding stories to knowledge graph."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Graphiti client."""
        client = MagicMock()
        client.add_episode = AsyncMock(return_value=MagicMock(uuid="story-uuid-123"))
        return client

    @pytest.mark.asyncio
    async def test_add_story_basic(self, mock_client):
        """Test adding a basic story."""
        uuid = await add_story(
            client=mock_client,
            title="Táin Bó Cúailnge",
            english_title="The Cattle Raid of Cooley",
            tradition="irish_mythology",
            cycle="ulster_cycle",
            summary="Epic tale of the conflict between Ulster and Connacht.",
        )

        assert uuid == "story-uuid-123"

    @pytest.mark.asyncio
    async def test_add_story_with_themes(self, mock_client):
        """Test adding a story with themes."""
        uuid = await add_story(
            client=mock_client,
            title="Táin Bó Cúailnge",
            english_title="The Cattle Raid of Cooley",
            tradition="irish_mythology",
            cycle="ulster_cycle",
            summary="Epic tale.",
            themes=["heroism", "conflict", "sovereignty"],
            main_characters=["Cú Chulainn", "Medb", "Fergus"],
        )

        assert uuid == "story-uuid-123"


class TestAddLocation:
    """Test adding locations to knowledge graph."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Graphiti client."""
        client = MagicMock()
        client.add_episode = AsyncMock(return_value=MagicMock(uuid="loc-uuid-123"))
        return client

    @pytest.mark.asyncio
    async def test_add_location_basic(self, mock_client):
        """Test adding a basic location."""
        uuid = await add_location(
            client=mock_client,
            name="Emain Macha",
            english_name="Navan Fort",
            tradition="irish_mythology",
            location_type="capital",
            description="Royal seat of Ulster.",
        )

        assert uuid == "loc-uuid-123"

    @pytest.mark.asyncio
    async def test_add_location_with_coordinates(self, mock_client):
        """Test adding a location with coordinates."""
        uuid = await add_location(
            client=mock_client,
            name="Emain Macha",
            english_name="Navan Fort",
            tradition="irish_mythology",
            location_type="capital",
            description="Royal seat of Ulster.",
            coordinates=(54.4500, -6.7000),
        )

        assert uuid == "loc-uuid-123"


class TestAddCurriculumUnit:
    """Test adding curriculum units to knowledge graph."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Graphiti client."""
        client = MagicMock()
        client.add_episode = AsyncMock(return_value=MagicMock(uuid="curr-uuid-123"))
        return client

    @pytest.mark.asyncio
    async def test_add_curriculum_unit(self, mock_client):
        """Test adding a curriculum unit."""
        uuid = await add_curriculum_unit(
            client=mock_client,
            title="Introduction to Irish Greetings",
            nation="ireland",
            level="junior_cycle",
            subject="language",
            content="Learn basic Irish greetings.",
            learning_outcomes=["Greet others in Irish"],
            related_mythology=["Cú Chulainn"],
        )

        assert uuid == "curr-uuid-123"


class TestRecordPlayerProgress:
    """Test recording player progress."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Graphiti client."""
        client = MagicMock()
        client.add_episode = AsyncMock(return_value=MagicMock(uuid="prog-uuid-123"))
        return client

    @pytest.mark.asyncio
    async def test_record_quest_completion(self, mock_client):
        """Test recording quest completion."""
        uuid = await record_player_progress(
            client=mock_client,
            player_id="player-001",
            event_type="quest_complete",
            details="Completed the Ulster Introduction quest.",
            metadata={"quest_id": "ulster-intro", "xp_earned": 100},
        )

        assert uuid == "prog-uuid-123"

    @pytest.mark.asyncio
    async def test_record_vocabulary_learned(self, mock_client):
        """Test recording vocabulary learning."""
        uuid = await record_player_progress(
            client=mock_client,
            player_id="player-001",
            event_type="vocabulary_learned",
            details="Learned the word 'laoch' (hero).",
        )

        assert uuid == "prog-uuid-123"


class TestQueryFunctions:
    """Test query functions."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Graphiti client with search results."""
        client = MagicMock()
        mock_result = MagicMock()
        mock_result.fact = "Test fact"
        mock_result.score = 0.9
        client.search = AsyncMock(return_value=[mock_result])
        return client

    @pytest.mark.asyncio
    async def test_query_character_timeline(self, mock_client):
        """Test querying character timeline."""
        timeline = await query_character_timeline(
            client=mock_client,
            character_name="Cú Chulainn",
        )

        assert isinstance(timeline, list)
        assert mock_client.search.called

    @pytest.mark.asyncio
    async def test_find_story_connections(self, mock_client):
        """Test finding story connections."""
        connections = await find_story_connections(
            client=mock_client,
            story_title="Táin Bó Cúailnge",
        )

        assert isinstance(connections, list)
        assert mock_client.search.called

    @pytest.mark.asyncio
    async def test_get_curriculum_for_mythology(self, mock_client):
        """Test finding curriculum for mythology."""
        curriculum = await get_curriculum_for_mythology(
            client=mock_client,
            mythology_element="Cú Chulainn",
        )

        assert isinstance(curriculum, list)
        assert mock_client.search.called

    @pytest.mark.asyncio
    async def test_get_player_knowledge_graph(self, mock_client):
        """Test getting player knowledge graph."""
        graph = await get_player_knowledge_graph(
            client=mock_client,
            player_id="player-001",
        )

        assert isinstance(graph, dict)
        assert "player_id" in graph
        assert graph["player_id"] == "player-001"
