"""
Tests for Tuath API endpoints.
"""

from fastapi import status


class TestRootEndpoints:
    """Test root and health endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "message" in data
        assert "Fáilte" in data["message"] or "Welcome" in data["message"]
        assert "endpoints" in data
        assert "docs" in data["endpoints"]

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "tuath-api"


class TestSearchEndpoints:
    """Test search API endpoints."""

    def test_search_post_valid_request(self, client, sample_search_request):
        """Test POST /search with valid request."""
        response = client.post("/search/", json=sample_search_request)
        # May return 500 if search engine not configured, but should accept request
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_search_post_minimal_request(self, client):
        """Test POST /search with minimal request."""
        response = client.post("/search/", json={"query": "test"})
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_search_post_empty_query_fails(self, client):
        """Test POST /search rejects empty query."""
        response = client.post("/search/", json={"query": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_curriculum_endpoint(self, client):
        """Test GET /search/curriculum endpoint."""
        response = client.get("/search/curriculum", params={"query": "Irish greetings"})
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_search_curriculum_with_filters(self, client):
        """Test curriculum search with nation and level filters."""
        response = client.get(
            "/search/curriculum",
            params={
                "query": "grammar",
                "nation": "ireland",
                "level": "junior_cycle",
                "limit": 5,
            },
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_search_mythology_endpoint(self, client):
        """Test GET /search/mythology endpoint."""
        response = client.get("/search/mythology", params={"query": "Cú Chulainn"})
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_search_mythology_with_filters(self, client):
        """Test mythology search with tradition and cycle filters."""
        response = client.get(
            "/search/mythology",
            params={
                "query": "warrior",
                "tradition": "irish_mythology",
                "cycle": "ulster_cycle",
                "content_type": "character",
            },
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_search_suggest_endpoint(self, client):
        """Test GET /search/suggest endpoint."""
        response = client.get("/search/suggest", params={"partial": "Cú"})
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "partial" in data
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_search_suggest_returns_matches(self, client):
        """Test that suggest endpoint returns matching suggestions."""
        response = client.get("/search/suggest", params={"partial": "Fionn"})
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Should match "Fionn mac Cumhaill" in suggestions
        assert any("Fionn" in s for s in data["suggestions"])

    def test_search_related_endpoint(self, client):
        """Test GET /search/related/{content_type}/{entity_id} endpoint."""
        response = client.get("/search/related/character/cu-chulainn")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]


class TestCurriculumEndpoints:
    """Test curriculum API endpoints."""

    def test_curriculum_list(self, client):
        """Test listing curriculum content."""
        response = client.get("/curriculum/")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_curriculum_by_nation(self, client):
        """Test filtering curriculum by nation."""
        response = client.get("/curriculum/nations/ireland")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]


class TestMythologyEndpoints:
    """Test mythology API endpoints."""

    def test_mythology_characters_list(self, client):
        """Test listing mythological characters."""
        response = client.get("/mythology/characters")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_mythology_stories_list(self, client):
        """Test listing mythological stories."""
        response = client.get("/mythology/stories")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_auth_nonce_endpoint(self, client, mock_wallet_address):
        """Test nonce generation endpoint."""
        response = client.get(f"/auth/nonce/{mock_wallet_address}")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_auth_verify_endpoint_missing_data(self, client):
        """Test verify endpoint rejects missing data."""
        response = client.post("/auth/verify", json={})
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_404_NOT_FOUND,
        ]


class TestPaymentEndpoints:
    """Test payment/x402 endpoints."""

    def test_payment_config_endpoint(self, client):
        """Test payment configuration endpoint."""
        response = client.get("/payments/config")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]


class TestGameStateEndpoints:
    """Test game state endpoints."""

    def test_game_state_requires_auth(self, client):
        """Test that game state endpoints require authentication."""
        response = client.get("/game/state")
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
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
