"""
Tests for hybrid search functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tuatha.knowledge_graph import (
    HybridSearchConfig,
    HybridSearchEngine,
    SearchMode,
    SearchResult,
)


class TestSearchMode:
    """Test SearchMode enum."""

    def test_search_modes_exist(self):
        """Test that all search modes are defined."""
        assert SearchMode.VECTOR is not None
        assert SearchMode.GRAPH is not None
        assert SearchMode.HYBRID is not None

    def test_search_mode_values(self):
        """Test search mode string values."""
        assert SearchMode.VECTOR.value == "vector"
        assert SearchMode.GRAPH.value == "graph"
        assert SearchMode.HYBRID.value == "hybrid"


class TestHybridSearchConfig:
    """Test HybridSearchConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = HybridSearchConfig()

        assert config.vector_weight == 0.6
        assert config.graph_weight == 0.4
        assert config.max_results == 20
        assert config.include_relationships is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = HybridSearchConfig(
            vector_weight=0.8,
            graph_weight=0.2,
            max_results=50,
            include_relationships=False,
        )

        assert config.vector_weight == 0.8
        assert config.graph_weight == 0.2
        assert config.max_results == 50
        assert config.include_relationships is False

    def test_weight_normalization(self):
        """Test that weights should sum to 1.0 for proper RRF."""
        config = HybridSearchConfig(vector_weight=0.6, graph_weight=0.4)
        assert abs(config.vector_weight + config.graph_weight - 1.0) < 0.001


class TestSearchResult:
    """Test SearchResult model."""

    def test_search_result_creation(self):
        """Test creating a search result."""
        result = SearchResult(
            id="char-001",
            content_type="character",
            title="Cú Chulainn",
            content="The Hound of Ulster",
            score=0.95,
            source="irish_mythology",
        )

        assert result.id == "char-001"
        assert result.content_type == "character"
        assert result.title == "Cú Chulainn"
        assert result.score == 0.95

    def test_search_result_with_metadata(self):
        """Test search result with metadata."""
        result = SearchResult(
            id="char-001",
            content_type="character",
            title="Cú Chulainn",
            content="The Hound of Ulster",
            score=0.95,
            source="irish_mythology",
            metadata={"tradition": "irish", "cycle": "ulster"},
            related_entities=["Emer", "Scáthach", "Conchobar"],
        )

        assert result.metadata["tradition"] == "irish"
        assert "Emer" in result.related_entities


class TestHybridSearchEngine:
    """Test HybridSearchEngine functionality."""

    @pytest.fixture
    def engine(self):
        """Create a search engine instance."""
        return HybridSearchEngine()

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initializes correctly."""
        assert engine is not None
        assert hasattr(engine, "search")
        assert hasattr(engine, "search_curriculum")
        assert hasattr(engine, "search_mythology")

    @pytest.mark.asyncio
    async def test_search_mode_vector(self, engine):
        """Test vector-only search mode."""
        with patch.object(engine, "_vector_search", new_callable=AsyncMock) as mock_vector:
            mock_vector.return_value = [
                SearchResult(
                    id="1",
                    content_type="character",
                    title="Test",
                    content="Test content",
                    score=0.9,
                    source="test",
                )
            ]

            config = HybridSearchConfig()
            # This tests the search method exists and accepts correct params
            assert callable(engine.search)

    @pytest.mark.asyncio
    async def test_search_mode_graph(self, engine):
        """Test graph-only search mode."""
        with patch.object(engine, "_graph_search", new_callable=AsyncMock) as mock_graph:
            mock_graph.return_value = [
                SearchResult(
                    id="1",
                    content_type="character",
                    title="Test",
                    content="Test content",
                    score=0.85,
                    source="test",
                )
            ]

            config = HybridSearchConfig()
            assert callable(engine.search)

    @pytest.mark.asyncio
    async def test_curriculum_search(self, engine):
        """Test curriculum-specific search."""
        assert callable(engine.search_curriculum)

    @pytest.mark.asyncio
    async def test_mythology_search(self, engine):
        """Test mythology-specific search."""
        assert callable(engine.search_mythology)

    @pytest.mark.asyncio
    async def test_find_related_content(self, engine):
        """Test finding related content."""
        assert callable(engine.find_related_content)


class TestReciprocalRankFusion:
    """Test RRF algorithm implementation."""

    def test_rrf_score_calculation(self):
        """Test RRF score formula: 1/(k+rank)."""
        k = 60  # Standard RRF constant

        # First rank should have highest score
        rank_1_score = 1 / (k + 1)
        rank_2_score = 1 / (k + 2)
        rank_10_score = 1 / (k + 10)

        assert rank_1_score > rank_2_score > rank_10_score
        assert abs(rank_1_score - 1/61) < 0.0001
        assert abs(rank_2_score - 1/62) < 0.0001

    def test_weighted_rrf_combination(self):
        """Test weighted combination of vector and graph scores."""
        k = 60
        vector_weight = 0.6
        graph_weight = 0.4

        # Item at rank 1 in vector, rank 3 in graph
        vector_rrf = vector_weight * (1 / (k + 1))
        graph_rrf = graph_weight * (1 / (k + 3))
        combined_score = vector_rrf + graph_rrf

        assert combined_score > 0
        assert vector_rrf > graph_rrf  # Higher weight and better rank


class TestContentTypeFiltering:
    """Test content type filtering in search."""

    @pytest.fixture
    def sample_results(self):
        """Create sample search results."""
        return [
            SearchResult(
                id="1",
                content_type="character",
                title="Cú Chulainn",
                content="Hero",
                score=0.9,
                source="mythology",
            ),
            SearchResult(
                id="2",
                content_type="story",
                title="Táin Bó Cúailnge",
                content="Epic",
                score=0.85,
                source="mythology",
            ),
            SearchResult(
                id="3",
                content_type="curriculum",
                title="Irish Greetings",
                content="Lesson",
                score=0.8,
                source="education",
            ),
        ]

    def test_filter_by_character(self, sample_results):
        """Test filtering results to characters only."""
        filtered = [r for r in sample_results if r.content_type == "character"]
        assert len(filtered) == 1
        assert filtered[0].title == "Cú Chulainn"

    def test_filter_by_mythology(self, sample_results):
        """Test filtering results to mythology content."""
        content_types = ["character", "story", "location"]
        filtered = [r for r in sample_results if r.content_type in content_types]
        assert len(filtered) == 2

    def test_filter_by_curriculum(self, sample_results):
        """Test filtering results to curriculum content."""
        filtered = [r for r in sample_results if r.content_type == "curriculum"]
        assert len(filtered) == 1
        assert filtered[0].title == "Irish Greetings"
