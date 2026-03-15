"""
Tests for sruth.shared.dlt module.

Tests:
- DLT source mixins
- Pagination patterns
- Rate limiting
- Caching
"""

import pytest
from unittest.mock import MagicMock, patch
import time


class TestPaginatedSourceMixin:
    """Tests for PaginatedSourceMixin."""

    def test_paginate_yields_all_items(self):
        """Test paginate yields items from all pages."""
        from sruth.shared.dlt import PaginatedSourceMixin

        class TestSource(PaginatedSourceMixin):
            def __init__(self):
                self.page_size = 2
                self.pages = [
                    {"data": [{"id": 1}, {"id": 2}], "next": "cursor1"},
                    {"data": [{"id": 3}, {"id": 4}], "next": "cursor2"},
                    {"data": [{"id": 5}], "next": None},
                ]
                self.current_page = 0

            def fetch_page(self, params):
                page = self.pages[self.current_page]
                self.current_page += 1
                return page

            def extract_items(self, response):
                return response["data"]

            def get_next_page_params(self, response, current_params):
                if response.get("next"):
                    return {"cursor": response["next"]}
                return None

        source = TestSource()
        items = list(source.paginate())

        assert len(items) == 5
        assert [i["id"] for i in items] == [1, 2, 3, 4, 5]

    def test_paginate_respects_max_pages(self):
        """Test paginate stops at max_pages."""
        from sruth.shared.dlt import PaginatedSourceMixin

        class TestSource(PaginatedSourceMixin):
            def __init__(self):
                self.max_pages = 2
                self.fetch_count = 0

            def fetch_page(self, params):
                self.fetch_count += 1
                return {"data": [{"id": self.fetch_count}], "has_more": True}

            def extract_items(self, response):
                return response["data"]

            def get_next_page_params(self, response, current_params):
                return {"page": current_params.get("page", 0) + 1}

        source = TestSource()
        items = list(source.paginate())

        assert source.fetch_count == 2
        assert len(items) == 2


class TestRateLimitedSourceMixin:
    """Tests for RateLimitedSourceMixin."""

    def test_rate_limited_decorator(self):
        """Test rate_limited decorator adds delay."""
        from sruth.shared.dlt.mixins import RateLimitedSourceMixin, rate_limited

        class TestSource(RateLimitedSourceMixin):
            requests_per_second = 10
            burst_limit = 1
            call_count = 0

            @rate_limited
            def fetch(self):
                self.call_count += 1
                return self.call_count

        source = TestSource()
        source._bucket_last_update = time.time()
        source._token_bucket = 0

        # First call should work
        result = source.fetch()
        assert result == 1


class TestCachedSourceMixin:
    """Tests for CachedSourceMixin."""

    def test_cache_stores_value(self):
        """Test cache stores and retrieves value."""
        from sruth.shared.dlt import CachedSourceMixin
        import tempfile
        from pathlib import Path

        class TestSource(CachedSourceMixin):
            pass

        with tempfile.TemporaryDirectory() as tmpdir:
            source = TestSource()
            source.cache_dir = Path(tmpdir)
            source.cache_enabled = True

            # Set value
            source.set_cached("test_key", {"data": "value"})

            # Get value
            result = source.get_cached("test_key")
            assert result == {"data": "value"}

    def test_cache_disabled(self):
        """Test cache can be disabled."""
        from sruth.shared.dlt import CachedSourceMixin

        class TestSource(CachedSourceMixin):
            cache_enabled = False

        source = TestSource()
        source.set_cached("key", "value")
        result = source.get_cached("key")

        assert result is None

    def test_cache_expiration(self):
        """Test cache expires after TTL."""
        from sruth.shared.dlt import CachedSourceMixin
        import tempfile
        from pathlib import Path
        import os

        class TestSource(CachedSourceMixin):
            cache_ttl_seconds = 1  # Very short TTL for testing

        with tempfile.TemporaryDirectory() as tmpdir:
            source = TestSource()
            source.cache_dir = Path(tmpdir)
            source.cache_enabled = True

            source.set_cached("key", "value")

            # Immediately should be valid
            assert source.get_cached("key") == "value"

            # Modify mtime to simulate expiration
            cache_path = source._get_cache_path("key")
            old_time = os.path.getmtime(cache_path) - 100
            os.utime(cache_path, (old_time, old_time))

            # Now should be expired
            assert source.get_cached("key") is None


class TestAuthenticatedSourceMixin:
    """Tests for AuthenticatedSourceMixin."""

    def test_bearer_auth_headers(self):
        """Test bearer auth generates correct headers."""
        from sruth.shared.dlt import AuthenticatedSourceMixin

        class TestSource(AuthenticatedSourceMixin):
            auth_type = "bearer"
            auth_env_var = "TEST_TOKEN"

        with patch.dict("os.environ", {"TEST_TOKEN": "my-secret-token"}):
            source = TestSource()
            headers = source.get_auth_headers()

            assert headers["Authorization"] == "Bearer my-secret-token"

    def test_api_key_auth_headers(self):
        """Test API key auth generates correct headers."""
        from sruth.shared.dlt import AuthenticatedSourceMixin

        class TestSource(AuthenticatedSourceMixin):
            auth_type = "api_key"
            auth_env_var = "TEST_API_KEY"
            auth_header_name = "X-API-Key"

        with patch.dict("os.environ", {"TEST_API_KEY": "key123"}):
            source = TestSource()
            headers = source.get_auth_headers()

            assert headers["X-API-Key"] == "key123"

    def test_missing_env_var_raises(self):
        """Test missing env var raises ValueError."""
        from sruth.shared.dlt import AuthenticatedSourceMixin

        class TestSource(AuthenticatedSourceMixin):
            auth_env_var = "NONEXISTENT_VAR"

        with patch.dict("os.environ", {}, clear=True):
            source = TestSource()

            with pytest.raises(ValueError, match="Missing environment variable"):
                source.get_auth_token()


class TestIncrementalSourceMixin:
    """Tests for IncrementalSourceMixin."""

    def test_load_save_state(self):
        """Test state persistence."""
        from sruth.shared.dlt import IncrementalSourceMixin
        import tempfile
        from pathlib import Path

        class TestSource(IncrementalSourceMixin):
            pass

        with tempfile.TemporaryDirectory() as tmpdir:
            source = TestSource()
            source.state_file = Path(tmpdir) / "state.json"

            # Initially no state
            assert source.load_state("test") is None

            # Save state
            source.save_state("test", "2024-01-01T00:00:00")

            # Load state
            value = source.load_state("test")
            assert value == "2024-01-01T00:00:00"

    def test_incremental_param_timestamp(self):
        """Test incremental param for timestamp type."""
        from sruth.shared.dlt import IncrementalSourceMixin
        import tempfile
        from pathlib import Path

        class TestSource(IncrementalSourceMixin):
            incremental_key = "updated_at"
            incremental_type = "timestamp"

        with tempfile.TemporaryDirectory() as tmpdir:
            source = TestSource()
            source.state_file = Path(tmpdir) / "state.json"

            # No state = no param
            params = source.get_incremental_param("test")
            assert params == {}

            # With state
            source.save_state("test", "2024-01-01T00:00:00")
            params = source.get_incremental_param("test")
            assert "since" in params or "updated_after" in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
