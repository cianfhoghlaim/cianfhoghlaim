"""
DLT Source Mixins for common patterns.

These mixins provide reusable functionality for DLT sources:
- Pagination handling
- Rate limiting
- Caching
- Authentication
- Incremental loading
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Generator
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PaginatedSourceMixin(ABC):
    """
    Mixin for paginated API sources.

    Supports multiple pagination strategies:
    - Cursor-based (next_cursor in response)
    - Page number (page=1, page=2, ...)
    - Offset-based (offset=0, offset=100, ...)
    - Link header (RFC 5988)

    Usage:
        class MySource(PaginatedSourceMixin):
            def fetch_page(self, page_params):
                response = self.client.get("/items", params=page_params)
                return response.json()

            def extract_items(self, response):
                return response["data"]

            def get_next_page_params(self, response, current_params):
                if response.get("next_cursor"):
                    return {"cursor": response["next_cursor"]}
                return None
    """

    page_size: int = 100
    max_pages: int | None = None

    @abstractmethod
    def fetch_page(self, page_params: dict[str, Any]) -> dict[str, Any]:
        """Fetch a single page of data."""
        pass

    @abstractmethod
    def extract_items(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract items from response."""
        pass

    @abstractmethod
    def get_next_page_params(
        self,
        response: dict[str, Any],
        current_params: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Get parameters for next page, or None if no more pages."""
        pass

    def get_initial_page_params(self) -> dict[str, Any]:
        """Get parameters for first page."""
        return {"limit": self.page_size}

    def paginate(self) -> Generator[dict[str, Any], None, None]:
        """
        Iterate through all pages.

        Yields:
            Items from each page
        """
        page_params = self.get_initial_page_params()
        page_count = 0

        while page_params is not None:
            if self.max_pages and page_count >= self.max_pages:
                logger.info(f"Reached max pages limit: {self.max_pages}")
                break

            response = self.fetch_page(page_params)
            items = self.extract_items(response)

            for item in items:
                yield item

            page_params = self.get_next_page_params(response, page_params)
            page_count += 1

            if page_count % 10 == 0:
                logger.info(f"Fetched {page_count} pages")


class RateLimitedSourceMixin:
    """
    Mixin for rate-limited API sources.

    Provides automatic rate limiting with configurable strategies:
    - Fixed delay between requests
    - Token bucket algorithm
    - Respect Retry-After headers

    Usage:
        class MySource(RateLimitedSourceMixin):
            requests_per_second = 2  # Max 2 requests/sec

            @rate_limited
            def fetch_data(self):
                return self.client.get("/data")
    """

    requests_per_second: float = 1.0
    burst_limit: int = 5
    respect_retry_after: bool = True

    _last_request_time: float = 0.0
    _token_bucket: float = 0.0
    _bucket_last_update: float = 0.0

    def _wait_for_rate_limit(self) -> None:
        """Wait if necessary to respect rate limit."""
        now = time.time()

        # Token bucket refill
        time_passed = now - self._bucket_last_update
        self._token_bucket = min(
            self.burst_limit,
            self._token_bucket + time_passed * self.requests_per_second,
        )
        self._bucket_last_update = now

        if self._token_bucket < 1.0:
            # Need to wait
            wait_time = (1.0 - self._token_bucket) / self.requests_per_second
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
            self._token_bucket = 0.0
        else:
            self._token_bucket -= 1.0

    def handle_retry_after(self, retry_after: str | None) -> None:
        """Handle Retry-After header."""
        if not retry_after or not self.respect_retry_after:
            return

        try:
            # Try parsing as seconds
            wait_seconds = int(retry_after)
        except ValueError:
            # Try parsing as HTTP date
            from email.utils import parsedate_to_datetime

            retry_date = parsedate_to_datetime(retry_after)
            wait_seconds = max(0, (retry_date - datetime.now()).total_seconds())

        logger.warning(f"Rate limited, waiting {wait_seconds}s")
        time.sleep(wait_seconds)


def rate_limited(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for rate-limited methods."""

    @wraps(func)
    def wrapper(self: RateLimitedSourceMixin, *args, **kwargs) -> T:
        self._wait_for_rate_limit()
        return func(self, *args, **kwargs)

    return wrapper


class CachedSourceMixin:
    """
    Mixin for cached API responses.

    Provides file-based caching for API responses to:
    - Speed up development/testing
    - Reduce API calls during retries
    - Enable offline development

    Usage:
        class MySource(CachedSourceMixin):
            cache_ttl_seconds = 3600  # 1 hour

            @cached("items")
            def fetch_items(self):
                return self.client.get("/items").json()
    """

    cache_dir: Path = Path.home() / ".cache" / "sruth" / "dlt"
    cache_ttl_seconds: int = 3600  # 1 hour
    cache_enabled: bool = True

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key."""
        # Hash the key for safe filenames
        key_hash = hashlib.md5(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{key_hash}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache file exists and is not expired."""
        if not cache_path.exists():
            return False

        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - mtime
        return age.total_seconds() < self.cache_ttl_seconds

    def get_cached(self, key: str) -> Any | None:
        """Get cached value if valid."""
        if not self.cache_enabled:
            return None

        cache_path = self._get_cache_path(key)
        if self._is_cache_valid(cache_path):
            logger.debug(f"Cache hit: {key}")
            return json.loads(cache_path.read_text())

        return None

    def set_cached(self, key: str, value: Any) -> None:
        """Set cached value."""
        if not self.cache_enabled:
            return

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = self._get_cache_path(key)
        cache_path.write_text(json.dumps(value))
        logger.debug(f"Cached: {key}")

    def clear_cache(self, key: str | None = None) -> None:
        """Clear cache (specific key or all)."""
        if key:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
        else:
            # Clear all cache files
            if self.cache_dir.exists():
                for f in self.cache_dir.glob("*.json"):
                    f.unlink()


def cached(cache_key: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for cached methods."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self: CachedSourceMixin, *args, **kwargs) -> T:
            # Build full cache key from function args
            full_key = f"{cache_key}:{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"

            # Try cache first
            result = self.get_cached(full_key)
            if result is not None:
                return result

            # Fetch and cache
            result = func(self, *args, **kwargs)
            self.set_cached(full_key, result)
            return result

        return wrapper

    return decorator


class AuthenticatedSourceMixin:
    """
    Mixin for authenticated API sources.

    Supports multiple authentication strategies:
    - API key (header or query param)
    - Bearer token
    - OAuth2 client credentials
    - Basic auth

    Usage:
        class MySource(AuthenticatedSourceMixin):
            auth_type = "bearer"
            auth_env_var = "MY_API_TOKEN"

            def get_client(self):
                return httpx.Client(headers=self.get_auth_headers())
    """

    auth_type: str = "bearer"  # "bearer", "api_key", "basic", "oauth2"
    auth_env_var: str = "API_KEY"
    auth_header_name: str = "Authorization"
    api_key_param_name: str = "api_key"

    _token: str | None = None
    _token_expires: datetime | None = None

    def get_auth_token(self) -> str:
        """Get authentication token from environment."""
        if self._token and self._token_expires and datetime.now() < self._token_expires:
            return self._token

        token = os.environ.get(self.auth_env_var)
        if not token:
            raise ValueError(f"Missing environment variable: {self.auth_env_var}")

        self._token = token
        return token

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        token = self.get_auth_token()

        if self.auth_type == "bearer":
            return {self.auth_header_name: f"Bearer {token}"}
        elif self.auth_type == "api_key":
            return {self.auth_header_name: token}
        elif self.auth_type == "basic":
            import base64

            encoded = base64.b64encode(token.encode()).decode()
            return {self.auth_header_name: f"Basic {encoded}"}

        return {}

    def get_auth_params(self) -> dict[str, str]:
        """Get authentication query parameters."""
        if self.auth_type == "api_key":
            return {self.api_key_param_name: self.get_auth_token()}
        return {}


class IncrementalSourceMixin:
    """
    Mixin for incremental loading sources.

    Tracks state to only fetch new/updated records:
    - Timestamp-based (updated_at > last_sync)
    - ID-based (id > last_id)
    - Cursor-based (resume from cursor)

    Usage:
        class MySource(IncrementalSourceMixin):
            incremental_key = "updated_at"
            incremental_type = "timestamp"

            def fetch_incremental(self, since):
                return self.client.get("/items", params={"since": since})
    """

    incremental_key: str = "updated_at"
    incremental_type: str = "timestamp"  # "timestamp", "id", "cursor"
    state_file: Path | None = None

    def _get_state_path(self, source_name: str) -> Path:
        """Get state file path."""
        if self.state_file:
            return self.state_file
        return Path.home() / ".cache" / "sruth" / "state" / f"{source_name}.json"

    def load_state(self, source_name: str) -> Any | None:
        """Load incremental state."""
        state_path = self._get_state_path(source_name)
        if state_path.exists():
            data = json.loads(state_path.read_text())
            return data.get("last_value")
        return None

    def save_state(self, source_name: str, value: Any) -> None:
        """Save incremental state."""
        state_path = self._get_state_path(source_name)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(
                {
                    "last_value": value,
                    "updated_at": datetime.now().isoformat(),
                }
            )
        )

    def get_incremental_param(self, source_name: str) -> dict[str, Any]:
        """Get incremental query parameter."""
        last_value = self.load_state(source_name)
        if last_value is None:
            return {}

        if self.incremental_type == "timestamp":
            return {"since": last_value, "updated_after": last_value}
        elif self.incremental_type == "id":
            return {"after_id": last_value, "min_id": last_value}
        elif self.incremental_type == "cursor":
            return {"cursor": last_value}

        return {}

    def update_incremental_state(
        self,
        source_name: str,
        items: list[dict[str, Any]],
    ) -> None:
        """Update state based on fetched items."""
        if not items:
            return

        # Find max value of incremental key
        values = [item.get(self.incremental_key) for item in items if item.get(self.incremental_key)]
        if values:
            max_value = max(values)
            self.save_state(source_name, max_value)


# DLT-specific decorators and utilities


def dlt_source_with_mixins(*mixins):
    """
    Decorator to create a DLT source class with mixins.

    Usage:
        @dlt_source_with_mixins(PaginatedSourceMixin, RateLimitedSourceMixin)
        class MySource:
            def __init__(self, api_key):
                self.api_key = api_key

            def items(self):
                return self.paginate()
    """

    def decorator(cls):
        # Create new class with mixins
        new_cls = type(cls.__name__, (*mixins, cls), {})
        return new_cls

    return decorator
