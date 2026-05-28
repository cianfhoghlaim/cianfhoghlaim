"""
Resilient HTTP client for DLT sources.

Provides a pre-configured httpx client with:
- Retry with exponential backoff
- Rate limiting
- Circuit breaker
- Timeout configuration
- Structured logging

Usage:
    from data_platform.dlt_sources.http_client import get_client

    async with get_client() as client:
        response = await client.get("https://api.example.com/data")
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

import httpx
from settings import settings
from shared.utils import (
    CircuitBreaker,
    CircuitBreakerOpen,
    RateLimiter,
    RateLimitError,
    RetryableError,
)

logger = logging.getLogger(__name__)


# Retryable HTTP status codes
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class HTTPError(RetryableError):
    """HTTP-specific retryable error."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: httpx.Response | None = None,
    ):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


@dataclass
class ClientConfig:
    """Configuration for HTTP client."""
    timeout: float = 30.0
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    max_requests_per_second: float = 10.0
    circuit_failure_threshold: int = 3
    circuit_recovery_time: float = 60.0
    user_agent: str = "oideachais-dlt/1.0"
    follow_redirects: bool = True


@dataclass
class ResilientClient:
    """
    HTTP client with retry, rate limiting, and circuit breaker.

    Wraps httpx.AsyncClient with resilience patterns.
    """
    config: ClientConfig = field(default_factory=ClientConfig)
    _client: httpx.AsyncClient | None = field(default=None, init=False)
    _rate_limiter: RateLimiter = field(init=False)
    _circuit_breaker: CircuitBreaker = field(init=False)

    def __post_init__(self) -> None:
        self._rate_limiter = RateLimiter(
            max_per_second=self.config.max_requests_per_second
        )
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.circuit_failure_threshold,
            recovery_time=self.config.circuit_recovery_time,
        )

    async def __aenter__(self) -> ResilientClient:
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout),
            follow_redirects=self.config.follow_redirects,
            headers={"User-Agent": self.config.user_agent},
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_service_name(self, url: str) -> str:
        """Extract service name from URL for circuit breaker."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make request with retry logic."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context.")

        service = self._get_service_name(url)
        last_error: Exception | None = None

        for attempt in range(self.config.max_retries):
            try:
                # Check circuit breaker
                if self._circuit_breaker.is_open(service):
                    status = self._circuit_breaker.get_status(service)
                    raise CircuitBreakerOpen(
                        service,
                        status["last_failure"] + self.config.circuit_recovery_time
                    )

                # Rate limiting
                await self._rate_limiter.acquire_async()

                # Make request
                response = await self._client.request(method, url, **kwargs)

                # Check for retryable errors
                if response.status_code in RETRYABLE_STATUS_CODES:
                    if response.status_code == 429:
                        # Rate limit - check Retry-After header
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            try:
                                delay = float(retry_after)
                                raise RateLimitError(
                                    f"Rate limited by {service}",
                                    retry_after=delay,
                                )
                            except ValueError:
                                pass

                    self._circuit_breaker.record_failure(service)
                    raise HTTPError(
                        f"HTTP {response.status_code} from {service}",
                        status_code=response.status_code,
                        response=response,
                    )

                # Success
                self._circuit_breaker.record_success(service)
                return response

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                self._circuit_breaker.record_failure(service)
                last_error = HTTPError(f"Connection error to {service}: {e}")

            except HTTPError as e:
                last_error = e

            except CircuitBreakerOpen:
                raise

            # Calculate backoff delay
            if attempt < self.config.max_retries - 1:
                import asyncio
                import random

                delay = min(
                    self.config.base_delay * (2 ** attempt),
                    self.config.max_delay,
                )
                delay = delay * (1 + 0.1 * random.random())  # Add jitter

                logger.warning(
                    f"Request to {url} failed (attempt {attempt + 1}/"
                    f"{self.config.max_retries}). Retrying in {delay:.2f}s"
                )
                await asyncio.sleep(delay)

        # All retries exhausted
        if last_error:
            raise last_error
        raise HTTPError(f"Request to {url} failed after {self.config.max_retries} attempts")

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """GET request with retry."""
        return await self._request_with_retry("GET", url, params=params, **kwargs)

    async def post(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """POST request with retry."""
        return await self._request_with_retry(
            "POST", url, json=json, data=data, **kwargs
        )

    async def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """GET request and parse JSON response."""
        response = await self.get(url, params=params, **kwargs)
        response.raise_for_status()
        return response.json()

    async def paginate(
        self,
        url: str,
        pagination_strategy: Any,
        params: dict[str, Any] | None = None,
        data_path: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[Any, None]:
        """
        Paginate through API results.

        Args:
            url: Base URL
            pagination_strategy: PaginationStrategy instance
            params: Initial query parameters
            data_path: Path to data in response (e.g., "data", "items")
            **kwargs: Additional request kwargs

        Yields:
            Items from each page
        """
        from .pagination import PaginationState

        state = PaginationState()
        current_url = url
        current_params = params or {}

        while state.has_more:
            response = await self.get(current_url, params=current_params, **kwargs)
            response.raise_for_status()
            data = response.json()

            # Extract items
            items = data
            if data_path:
                for part in data_path.split("."):
                    if isinstance(items, dict):
                        items = items.get(part, [])

            if isinstance(items, list):
                for item in items:
                    yield item
            else:
                yield items

            # Update state and get next request
            state = pagination_strategy.update_state(response, data, state)
            next_url, next_params = pagination_strategy.get_next_request(
                url, response, state
            )

            if next_url:
                current_url = next_url
                current_params = {**current_params, **next_params}
            else:
                break


@asynccontextmanager
async def get_client(
    config: ClientConfig | None = None,
) -> AsyncGenerator[ResilientClient, None]:
    """
    Get a configured HTTP client.

    Usage:
        async with get_client() as client:
            response = await client.get("https://api.example.com/data")
    """
    if config is None:
        config = ClientConfig(
            timeout=settings.request_timeout,
            max_retries=settings.max_retries,
            base_delay=settings.retry_base_delay,
            max_delay=settings.retry_max_delay,
            max_requests_per_second=settings.max_requests_per_second,
            circuit_failure_threshold=settings.circuit_failure_threshold,
            circuit_recovery_time=settings.circuit_recovery_time,
        )

    client = ResilientClient(config=config)
    async with client:
        yield client
