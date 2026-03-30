"""
Pytest fixtures for Tuath tests.
"""

import pytest
from fastapi.testclient import TestClient

from tuath.api.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_wallet_address():
    """Mock Ethereum wallet address for testing."""
    return "0x742d35Cc6634C0532925a3b844Bc9e7595f5d123"


@pytest.fixture
def mock_siwe_message(mock_wallet_address):
    """Mock SIWE message for authentication testing."""
    return {
        "domain": "localhost:3000",
        "address": mock_wallet_address,
        "statement": "Sign in to Tuath Celtic MMO",
        "uri": "http://localhost:3000",
        "version": "1",
        "chain_id": 1,
        "nonce": "test_nonce_123",
        "issued_at": "2024-01-15T12:00:00Z",
    }


@pytest.fixture
def sample_curriculum_data():
    """Sample curriculum data for testing."""
    return {
        "title": "Introduction to Irish Greetings",
        "nation": "ireland",
        "level": "junior_cycle",
        "subject": "language",
        "content": "Learn basic Irish greetings including Dia duit, Slán, and Conas atá tú.",
        "learning_outcomes": [
            "Greet others in Irish",
            "Respond to greetings",
            "Ask how someone is feeling",
        ],
    }


@pytest.fixture
def sample_mythology_data():
    """Sample mythology data for testing."""
    return {
        "name": "Cú Chulainn",
        "native_name": "Cú Chulainn",
        "tradition": "irish_mythology",
        "cycle": "ulster_cycle",
        "character_type": "hero",
        "description": "The Hound of Ulster, greatest warrior of Irish mythology.",
        "powers": ["Ríastrad (warp spasm)", "Gáe Bulg mastery", "Superhuman strength"],
    }


@pytest.fixture
def sample_search_request():
    """Sample search request for testing."""
    return {
        "query": "Celtic warriors",
        "mode": "hybrid",
        "limit": 10,
        "vector_weight": 0.6,
        "graph_weight": 0.4,
        "include_relationships": True,
    }


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f5d123",
        "username": "CelticLearner",
        "current_level": 5,
        "xp_total": 1250,
        "vocabulary_learned": 150,
        "quests_completed": 12,
        "current_region": "Connacht",
    }
