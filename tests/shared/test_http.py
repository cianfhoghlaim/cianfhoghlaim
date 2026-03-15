"""
Tests for sruth.shared.http module.

Tests:
- HttpClientFactory configuration
- Auth strategies
- Circuit breaker integration
"""

import pytest
from unittest.mock import MagicMock, patch


class TestAuthStrategies:
    """Tests for authentication strategies."""

    def test_bearer_token_auth(self):
        """Test BearerTokenAuth adds correct header."""
        from sruth.shared.http import BearerTokenAuth

        auth = BearerTokenAuth(token="my-secret-token")
        headers = {}
        headers = auth.apply(headers)

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer my-secret-token"

    def test_api_key_auth_header(self):
        """Test ApiKeyAuth adds header correctly."""
        from sruth.shared.http import ApiKeyAuth

        auth = ApiKeyAuth(api_key="key123", header_name="X-API-Key")
        headers = {}
        headers = auth.apply(headers)

        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == "key123"

    def test_api_key_auth_query_param(self):
        """Test ApiKeyAuth adds query param correctly."""
        from sruth.shared.http import ApiKeyAuth

        auth = ApiKeyAuth(
            api_key="key123",
            as_query_param=True,
            query_param_name="api_key",
        )
        url = auth.apply_to_url("https://api.example.com/data")

        assert "api_key=key123" in url

    def test_basic_auth(self):
        """Test BasicAuth encodes credentials."""
        from sruth.shared.http import BasicAuth
        import base64

        auth = BasicAuth(username="user", password="pass")
        headers = {}
        headers = auth.apply(headers)

        assert "Authorization" in headers
        expected = base64.b64encode(b"user:pass").decode()
        assert headers["Authorization"] == f"Basic {expected}"


class TestHttpClientFactory:
    """Tests for HttpClientFactory."""

    def test_factory_creation(self):
        """Test factory can be created."""
        from sruth.shared.http import HttpClientFactory

        factory = HttpClientFactory(
            base_url="https://api.example.com",
        )

        assert factory.base_url == "https://api.example.com"

    def test_factory_with_auth(self):
        """Test factory with authentication."""
        from sruth.shared.http import HttpClientFactory, BearerTokenAuth

        auth = BearerTokenAuth(token="secret")
        factory = HttpClientFactory(
            base_url="https://api.example.com",
            auth=auth,
        )

        assert factory.auth == auth

    def test_factory_with_rate_limit(self):
        """Test factory with rate limiting."""
        from sruth.shared.http import HttpClientFactory

        factory = HttpClientFactory(
            base_url="https://api.example.com",
            rate_limit=5.0,  # Correct param name
        )

        assert factory.rate_limit == 5.0
        assert factory._rate_limiter is not None

    def test_factory_with_circuit_breaker(self):
        """Test factory with circuit breaker."""
        from sruth.shared.http import HttpClientFactory

        factory = HttpClientFactory(
            base_url="https://api.example.com",
            circuit_breaker_threshold=5,  # Correct param name
            circuit_breaker_recovery=120.0,
        )

        assert factory.circuit_breaker_threshold == 5
        assert factory.circuit_breaker_recovery == 120.0

    def test_factory_builds_headers(self):
        """Test factory builds headers with auth."""
        from sruth.shared.http import HttpClientFactory, BearerTokenAuth

        auth = BearerTokenAuth(token="my-token")
        factory = HttpClientFactory(
            base_url="https://api.example.com",
            auth=auth,
            user_agent="test-client/1.0",
        )

        headers = factory._build_headers()

        assert headers["Authorization"] == "Bearer my-token"
        assert headers["User-Agent"] == "test-client/1.0"

    def test_factory_extra_headers(self):
        """Test factory includes extra headers."""
        from sruth.shared.http import HttpClientFactory

        factory = HttpClientFactory(
            base_url="https://api.example.com",
            extra_headers={"X-Custom": "value"},
        )

        headers = factory._build_headers()
        assert headers["X-Custom"] == "value"


class TestCreateClientFunction:
    """Tests for create_client convenience function."""

    def test_create_client_basic(self):
        """Test create_client creates factory."""
        from sruth.shared.http import create_client

        factory = create_client(
            base_url="https://api.example.com",
        )

        assert factory.base_url == "https://api.example.com"

    def test_create_client_with_auth(self):
        """Test create_client with auth strategy."""
        from sruth.shared.http import create_client, BearerTokenAuth

        auth = BearerTokenAuth(token="my-token")
        factory = create_client(
            base_url="https://api.example.com",
            auth=auth,
        )

        assert factory.auth == auth

    def test_create_client_with_rate_limit(self):
        """Test create_client with rate limit."""
        from sruth.shared.http import create_client

        factory = create_client(
            base_url="https://api.example.com",
            rate_limit=10.0,
        )

        assert factory.rate_limit == 10.0


class TestPreConfiguredClients:
    """Tests for pre-configured client factories."""

    def test_defillama_client(self):
        """Test DeFiLlama client configuration."""
        from sruth.shared.http.client_factory import defillama_client

        factory = defillama_client()

        assert "llama.fi" in factory.base_url
        assert factory.rate_limit == 5.0

    def test_coingecko_client_free(self):
        """Test CoinGecko client without API key."""
        from sruth.shared.http.client_factory import coingecko_client

        factory = coingecko_client()

        assert "coingecko.com" in factory.base_url
        assert factory.rate_limit == 0.5  # Free tier limit

    def test_coingecko_client_with_key(self):
        """Test CoinGecko client with API key."""
        from sruth.shared.http.client_factory import coingecko_client

        factory = coingecko_client(api_key="test-key")

        assert factory.rate_limit == 10.0  # Pro tier limit
        assert factory.auth is not None

    def test_github_client(self):
        """Test GitHub client configuration."""
        from sruth.shared.http.client_factory import github_client
        from unittest.mock import patch

        with patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}):
            factory = github_client()

            assert "github.com" in factory.base_url
            assert factory.auth is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
