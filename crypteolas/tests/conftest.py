"""
Pytest fixtures for Crypteolas tests.
"""

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Optional imports - gracefully handle if not installed
try:
    from fastapi.testclient import TestClient
    HAS_FASTAPI = True
except ImportError:
    TestClient = None
    HAS_FASTAPI = False


# --- Path fixtures ---


@pytest.fixture
def project_root() -> Path:
    """Return the crypteolas project root."""
    return Path(__file__).parent.parent


@pytest.fixture
def fixtures_path() -> Path:
    """Return the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


# --- Database fixtures ---


@pytest.fixture
def tmp_lancedb(tmp_path):
    """Create a temporary LanceDB for tests."""
    try:
        import lancedb
    except ImportError:
        pytest.skip("lancedb not installed")

    db_path = tmp_path / "lancedb"
    db = lancedb.connect(str(db_path))
    return db


@pytest.fixture
def tmp_duckdb(tmp_path):
    """Create a temporary DuckDB for tests."""
    try:
        import duckdb
    except ImportError:
        pytest.skip("duckdb not installed")

    db_path = tmp_path / "test.duckdb"
    conn = duckdb.connect(str(db_path))
    yield conn
    conn.close()


# --- API client fixtures ---


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    if not HAS_FASTAPI:
        pytest.skip("FastAPI not installed")
    from tuatha.crypteolas.api.main import app

    return TestClient(app)


@pytest.fixture
def mock_httpx_client():
    """Mock synchronous httpx client for external API calls."""
    with patch("httpx.Client") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
        mock_client.return_value.__exit__ = MagicMock(return_value=None)
        yield client_instance


@pytest.fixture
def mock_httpx_async_client():
    """Mock async httpx client for external API calls."""
    with patch("httpx.AsyncClient") as mock_client:
        client_instance = AsyncMock()
        mock_client.return_value.__aenter__ = AsyncMock(return_value=client_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        yield client_instance


@pytest.fixture
def mock_github_repo():
    """Mock GitHub repository data for testing."""
    return {
        "owner": "anthropics",
        "name": "anthropic-sdk-python",
        "full_name": "anthropics/anthropic-sdk-python",
        "description": "Python SDK for the Anthropic API",
        "stars": 1500,
        "forks": 200,
        "language": "Python",
        "topics": ["ai", "llm", "claude", "anthropic"],
        "created_at": "2023-03-15T10:00:00Z",
        "updated_at": "2024-01-15T15:30:00Z",
    }


@pytest.fixture
def mock_protocol_data():
    """Mock DeFi protocol data for testing."""
    return {
        "id": "aave",
        "name": "Aave",
        "chain": "ethereum",
        "category": "lending",
        "tvl": 10500000000,
        "tvl_change_24h": 2.5,
        "token": "AAVE",
        "description": "Open source liquidity protocol for earning interest on deposits.",
    }


@pytest.fixture
def mock_pool_data():
    """Mock DeFi pool data for testing."""
    return {
        "id": "aave-eth-usdc",
        "protocol": "aave",
        "chain": "ethereum",
        "pool_type": "lending",
        "assets": ["ETH", "USDC"],
        "tvl": 500000000,
        "apy": 3.5,
        "apy_7d_avg": 3.2,
        "volume_24h": 15000000,
    }


@pytest.fixture
def sample_search_request():
    """Sample search request for testing."""
    return {
        "query": "lending protocols with high TVL",
        "mode": "hybrid",
        "limit": 10,
        "content_types": ["protocol", "pool"],
    }


@pytest.fixture
def sample_github_search_request():
    """Sample GitHub search request for testing."""
    return {
        "query": "DeFi smart contracts",
        "language": "Solidity",
        "min_stars": 100,
        "topics": ["defi", "ethereum"],
        "limit": 20,
    }


@pytest.fixture
def mock_commit_data():
    """Mock GitHub commit data for testing."""
    return {
        "sha": "abc123def456",
        "message": "feat: add flash loan support",
        "author": "developer",
        "date": "2024-01-15T10:30:00Z",
        "additions": 150,
        "deletions": 20,
        "files_changed": 5,
    }


@pytest.fixture
def mock_contributor_data():
    """Mock GitHub contributor data for testing."""
    return {
        "login": "top-contributor",
        "contributions": 250,
        "repositories": ["protocol-a", "protocol-b"],
        "profile_url": "https://github.com/top-contributor",
    }


# --- GitHub pagination fixtures ---


@pytest.fixture
def mock_github_repos_page():
    """Mock paginated GitHub repos response."""
    return [
        {
            "id": 1,
            "full_name": "org/repo-1",
            "name": "repo-1",
            "description": "First repo",
            "stargazers_count": 500,
            "forks_count": 50,
            "language": "Python",
            "topics": ["ml", "ai"],
        },
        {
            "id": 2,
            "full_name": "org/repo-2",
            "name": "repo-2",
            "description": "Second repo",
            "stargazers_count": 300,
            "forks_count": 30,
            "language": "Rust",
            "topics": ["blockchain"],
        },
    ]


@pytest.fixture
def mock_github_commits_page():
    """Mock paginated GitHub commits response."""
    return [
        {
            "sha": "abc123",
            "commit": {
                "message": "feat: initial commit",
                "author": {"name": "dev", "date": "2024-01-15T10:00:00Z"},
            },
            "stats": {"additions": 100, "deletions": 0},
        },
        {
            "sha": "def456",
            "commit": {
                "message": "fix: bug fix",
                "author": {"name": "dev", "date": "2024-01-16T11:00:00Z"},
            },
            "stats": {"additions": 10, "deletions": 5},
        },
    ]


# --- DeFiLlama fixtures ---


@pytest.fixture
def mock_defillama_protocols():
    """Mock DeFiLlama protocols list response."""
    return [
        {
            "id": "aave",
            "name": "Aave",
            "symbol": "AAVE",
            "chain": "Ethereum",
            "category": "Lending",
            "tvl": 10500000000,
            "chainTvls": {"Ethereum": 8000000000, "Polygon": 2500000000},
            "change_1h": 0.1,
            "change_1d": 2.5,
            "change_7d": -1.2,
        },
        {
            "id": "uniswap",
            "name": "Uniswap",
            "symbol": "UNI",
            "chain": "Ethereum",
            "category": "DEX",
            "tvl": 5200000000,
            "chainTvls": {"Ethereum": 4000000000, "Arbitrum": 1200000000},
            "change_1h": -0.2,
            "change_1d": 1.8,
            "change_7d": 3.5,
        },
    ]


@pytest.fixture
def mock_defillama_yields():
    """Mock DeFiLlama yield pools response."""
    return {
        "data": [
            {
                "pool": "aave-eth",
                "chain": "Ethereum",
                "project": "aave",
                "symbol": "ETH",
                "tvlUsd": 2000000000,
                "apy": 3.5,
                "apyBase": 2.0,
                "apyReward": 1.5,
            },
            {
                "pool": "compound-usdc",
                "chain": "Ethereum",
                "project": "compound",
                "symbol": "USDC",
                "tvlUsd": 1500000000,
                "apy": 4.2,
                "apyBase": 3.8,
                "apyReward": 0.4,
            },
        ]
    }


@pytest.fixture
def mock_defillama_protocol_tvl():
    """Mock DeFiLlama protocol TVL history."""
    return {
        "tvl": [
            {"date": "2024-01-01", "totalLiquidityUSD": 9000000000},
            {"date": "2024-01-02", "totalLiquidityUSD": 9500000000},
            {"date": "2024-01-03", "totalLiquidityUSD": 10500000000},
        ]
    }


# --- Cognee/Knowledge Graph fixtures ---


@pytest.fixture
def mock_cognee_client():
    """Mock Cognee knowledge graph client."""
    with patch("cognee.Cognee") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_graphiti_client():
    """Mock Graphiti temporal graph client."""
    with patch("graphiti_core.Graphiti") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


# --- Pytest configuration ---


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "external: marks tests requiring external services")
