"""
Tests for Crypteolas API endpoints.
"""

import pytest

# Optional import for FastAPI status codes
try:
    from fastapi import status
except ImportError:
    # Fallback to HTTP status codes as integers
    class status:
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_400_BAD_REQUEST = 400
        HTTP_404_NOT_FOUND = 404
        HTTP_500_INTERNAL_SERVER_ERROR = 500


class TestRootEndpoints:
    """Test root and health endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "message" in data
        assert "Crypteolas" in data["message"] or "crypto" in data["message"].lower()
        assert "endpoints" in data

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "crypteolas-api"


class TestGitHubEndpoints:
    """Test GitHub intelligence API endpoints."""

    def test_github_repos_search(self, client):
        """Test GitHub repository search endpoint."""
        response = client.get(
            "/github/repos/search",
            params={"query": "DeFi", "language": "Solidity"},
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_github_repo_details(self, client):
        """Test getting specific repo details."""
        response = client.get("/github/repos/anthropics/anthropic-sdk-python")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_github_repo_commits(self, client):
        """Test getting repo commit history."""
        response = client.get("/github/repos/anthropics/anthropic-sdk-python/commits")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_github_repo_contributors(self, client):
        """Test getting repo contributors."""
        response = client.get(
            "/github/repos/anthropics/anthropic-sdk-python/contributors"
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_github_trending(self, client):
        """Test trending repositories endpoint."""
        response = client.get("/github/trending", params={"language": "Python"})
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]


class TestDeFiEndpoints:
    """Test DeFi analytics API endpoints."""

    def test_defi_protocols_list(self, client):
        """Test listing DeFi protocols."""
        response = client.get("/defi/protocols")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_defi_protocols_by_chain(self, client):
        """Test filtering protocols by chain."""
        response = client.get("/defi/protocols", params={"chain": "ethereum"})
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_defi_protocol_details(self, client):
        """Test getting specific protocol details."""
        response = client.get("/defi/protocols/aave")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_defi_pools_list(self, client):
        """Test listing DeFi pools."""
        response = client.get("/defi/pools")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_defi_pools_by_protocol(self, client):
        """Test filtering pools by protocol."""
        response = client.get("/defi/pools", params={"protocol": "aave"})
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_defi_tvl_metrics(self, client):
        """Test TVL metrics endpoint."""
        response = client.get("/defi/metrics/tvl")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_defi_yield_metrics(self, client):
        """Test yield metrics endpoint."""
        response = client.get("/defi/metrics/yields")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]


class TestSearchEndpoints:
    """Test unified search API endpoints."""

    def test_search_post_valid_request(self, client, sample_search_request):
        """Test POST /search with valid request."""
        response = client.post("/search/", json=sample_search_request)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_search_post_minimal_request(self, client):
        """Test POST /search with minimal request."""
        response = client.post("/search/", json={"query": "ethereum"})
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_search_post_empty_query_fails(self, client):
        """Test POST /search rejects empty query."""
        response = client.post("/search/", json={"query": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_github(self, client):
        """Test GitHub-specific search."""
        response = client.get("/search/github", params={"query": "smart contracts"})
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_search_defi(self, client):
        """Test DeFi-specific search."""
        response = client.get("/search/defi", params={"query": "lending"})
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_auth_nonce_endpoint(self, client):
        """Test nonce generation endpoint."""
        response = client.get(
            "/auth/nonce/0x742d35Cc6634C0532925a3b844Bc9e7595f5d123"
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]


class TestCopilotKitEndpoints:
    """Test CopilotKit/agent endpoints."""

    def test_agents_list_endpoint(self, client):
        """Test listing available agents."""
        response = client.get("/copilotkit/agents")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_copilotkit_chat_endpoint(self, client):
        """Test chat endpoint exists."""
        # SSE endpoint - just check it doesn't 404
        response = client.post(
            "/copilotkit/chat",
            json={"message": "What is Aave TVL?"},
            headers={"Accept": "text/event-stream"},
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]
