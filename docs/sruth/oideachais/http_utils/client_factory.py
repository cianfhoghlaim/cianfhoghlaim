"""
HTTP Client Factory for DLT Sources.

Provides a unified HTTP client factory with:
- Circuit breaker for service health
- Rate limiting to prevent API throttling
- Retry with exponential backoff
- Configurable authentication strategies

Usage:
    factory = HttpClientFactory(
        base_url="https://api.example.com",
        auth=BearerTokenAuth(token=os.environ["API_TOKEN"]),
    )

    async with factory.create_async_client() as client:
        response = await client.get("/endpoint")
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Generator, Optional

import httpx

from ..core.utils import CircuitBreaker, CircuitBreakerOpen, RateLimiter

logger = logging.getLogger(__name__)


# =========================================================================
# Authentication Strategies
# =========================================================================


class AuthStrategy(ABC):
    """Base class for authentication strategies."""

    @abstractmethod
    def apply(self, headers: dict[str, str]) -> dict[str, str]:
        """Apply authentication to request headers."""
        pass


@dataclass
class BearerTokenAuth(AuthStrategy):
    """Bearer token authentication."""

    token: str
    header_name: str = "Authorization"

    def apply(self, headers: dict[str, str]) -> dict[str, str]:
        headers[self.header_name] = f"Bearer {self.token}"
        return headers


@dataclass
class ApiKeyAuth(AuthStrategy):
    """API key authentication (header or query param)."""

    api_key: str
    header_name: str = "X-API-Key"
    as_query_param: bool = False
    query_param_name: str = "api_key"

    def apply(self, headers: dict[str, str]) -> dict[str, str]:
        if not self.as_query_param:
            headers[self.header_name] = self.api_key
        return headers

    def apply_to_url(self, url: str) -> str:
        """Add API key as query parameter if configured."""
        if self.as_query_param:
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}{self.query_param_name}={self.api_key}"
        return url


@dataclass
class BasicAuth(AuthStrategy):
    """Basic authentication."""

    username: str
    password: str

    def apply(self, headers: dict[str, str]) -> dict[str, str]:
        import base64

        credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers["Authorization"] = f"Basic {credentials}"
        return headers


# =========================================================================
# HTTP Client Factory
# =========================================================================


@dataclass
class HttpClientFactory:
    """
    Factory for creating HTTP clients with resilience patterns.

    Features:
    - Circuit breaker to prevent cascading failures
    - Rate limiting to respect API limits
    - Configurable authentication
    - Request/response logging

    Usage:
        factory = HttpClientFactory(
            base_url="https://api.defillama.com",
            auth=BearerTokenAuth(token="..."),
            rate_limit=10.0,  # 10 requests per second
        )

        # Sync client
        with factory.create_client() as client:
            response = client.get("/protocols")

        # Async client
        async with factory.create_async_client() as client:
            response = await client.get("/protocols")
    """

    base_url: str
    auth: Optional[AuthStrategy] = None
    timeout: float = 30.0
    rate_limit: Optional[float] = None  # Requests per second
    circuit_breaker_threshold: int = 3
    circuit_breaker_recovery: float = 60.0
    user_agent: str = "sruth-dlt/1.0"
    extra_headers: dict[str, str] = field(default_factory=dict)

    # Internal state
    _circuit_breaker: CircuitBreaker = field(init=False)
    _rate_limiter: Optional[RateLimiter] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=self.circuit_breaker_threshold,
            recovery_time=self.circuit_breaker_recovery,
        )
        if self.rate_limit:
            self._rate_limiter = RateLimiter(
                max_per_second=self.rate_limit,
            )

    def _build_headers(self) -> dict[str, str]:
        """Build request headers with auth and extras."""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            **self.extra_headers,
        }
        if self.auth:
            headers = self.auth.apply(headers)
        return headers

    def _service_name(self) -> str:
        """Extract service name from base URL for circuit breaker."""
        from urllib.parse import urlparse

        parsed = urlparse(self.base_url)
        return parsed.netloc or self.base_url

    async def _pre_request_async(self) -> None:
        """Pre-request hooks: rate limiting, circuit breaker check."""
        service = self._service_name()

        # Check circuit breaker
        if self._circuit_breaker.is_open(service):
            state = self._circuit_breaker._get_state(service)
            retry_after = (state.last_failure + self._circuit_breaker.recovery_time) - __import__(
                "time"
            ).time()
            raise CircuitBreakerOpen(service, retry_after)

        # Apply rate limiting
        if self._rate_limiter:
            await self._rate_limiter.acquire_async()

    def _pre_request_sync(self) -> None:
        """Sync version of pre-request hooks."""
        service = self._service_name()

        if self._circuit_breaker.is_open(service):
            state = self._circuit_breaker._get_state(service)
            retry_after = (state.last_failure + self._circuit_breaker.recovery_time) - __import__(
                "time"
            ).time()
            raise CircuitBreakerOpen(service, retry_after)

        if self._rate_limiter:
            self._rate_limiter.acquire()

    def _track_response(self, response: httpx.Response) -> None:
        """Track response for circuit breaker."""
        service = self._service_name()

        if response.is_success:
            self._circuit_breaker.record_success(service)
        elif response.status_code >= 500:
            self._circuit_breaker.record_failure(service)
            logger.warning(f"HTTP {response.status_code} from {service}: {response.text[:200]}")

    @contextmanager
    def create_client(self) -> Generator[httpx.Client, None, None]:
        """Create a synchronous HTTP client."""
        client = httpx.Client(
            base_url=self.base_url,
            headers=self._build_headers(),
            timeout=self.timeout,
            event_hooks={
                "response": [self._track_response],
            },
        )

        try:
            yield client
        finally:
            client.close()

    @asynccontextmanager
    async def create_async_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Create an asynchronous HTTP client."""
        client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._build_headers(),
            timeout=self.timeout,
            event_hooks={
                "response": [self._track_response],
            },
        )

        try:
            yield client
        finally:
            await client.aclose()

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """Convenience method for GET request."""
        self._pre_request_sync()
        with self.create_client() as client:
            return client.get(path, **kwargs)

    async def get_async(self, path: str, **kwargs: Any) -> httpx.Response:
        """Convenience method for async GET request."""
        await self._pre_request_async()
        async with self.create_async_client() as client:
            return await client.get(path, **kwargs)


# =========================================================================
# Convenience Functions
# =========================================================================


def create_client(
    base_url: str,
    auth: Optional[AuthStrategy] = None,
    timeout: float = 30.0,
    rate_limit: Optional[float] = None,
) -> HttpClientFactory:
    """
    Create an HTTP client factory with default settings.

    Usage:
        factory = create_client(
            base_url="https://api.example.com",
            auth=BearerTokenAuth(token="..."),
        )
    """
    return HttpClientFactory(
        base_url=base_url,
        auth=auth,
        timeout=timeout,
        rate_limit=rate_limit,
    )


# Pre-configured factories for common APIs
def defillama_client() -> HttpClientFactory:
    """Pre-configured client for DeFiLlama API."""
    return HttpClientFactory(
        base_url="https://api.llama.fi",
        rate_limit=5.0,
        user_agent="sruth-crypteolas/1.0",
    )


def coingecko_client(api_key: Optional[str] = None) -> HttpClientFactory:
    """Pre-configured client for CoinGecko API."""
    auth = ApiKeyAuth(api_key=api_key, header_name="x-cg-pro-api-key") if api_key else None
    return HttpClientFactory(
        base_url="https://api.coingecko.com/api/v3",
        auth=auth,
        rate_limit=10.0 if api_key else 0.5,  # Free tier is heavily limited
        user_agent="sruth-crypteolas/1.0",
    )


def github_client(token: Optional[str] = None) -> HttpClientFactory:
    """Pre-configured client for GitHub API."""
    token = token or os.environ.get("GITHUB_TOKEN")
    auth = BearerTokenAuth(token=token) if token else None
    return HttpClientFactory(
        base_url="https://api.github.com",
        auth=auth,
        rate_limit=5000 / 3600 if token else 60 / 3600,  # Requests per second
        user_agent="sruth-crypteolas/1.0",
        extra_headers={"Accept": "application/vnd.github.v3+json"},
    )


def binance_spot_client(api_key: Optional[str] = None) -> HttpClientFactory:
    """Pre-configured client for Binance Spot API."""
    api_key = api_key or os.environ.get("BINANCE_API_KEY")
    auth = ApiKeyAuth(api_key=api_key, header_name="X-MBX-APIKEY") if api_key else None
    return HttpClientFactory(
        base_url="https://api.binance.com/api/v3",
        auth=auth,
        rate_limit=10.0,  # Conservative limit
        user_agent="sruth-crypteolas/1.0",
    )


def binance_futures_client(api_key: Optional[str] = None) -> HttpClientFactory:
    """Pre-configured client for Binance Futures API."""
    api_key = api_key or os.environ.get("BINANCE_API_KEY")
    auth = ApiKeyAuth(api_key=api_key, header_name="X-MBX-APIKEY") if api_key else None
    return HttpClientFactory(
        base_url="https://fapi.binance.com/fapi/v1",
        auth=auth,
        rate_limit=10.0,
        user_agent="sruth-crypteolas/1.0",
    )


def defillama_yields_client() -> HttpClientFactory:
    """Pre-configured client for DeFiLlama Yields API."""
    return HttpClientFactory(
        base_url="https://yields.llama.fi",
        rate_limit=5.0,
        user_agent="sruth-crypteolas/1.0",
    )


def defillama_stablecoins_client() -> HttpClientFactory:
    """Pre-configured client for DeFiLlama Stablecoins API."""
    return HttpClientFactory(
        base_url="https://stablecoins.llama.fi",
        rate_limit=5.0,
        user_agent="sruth-crypteolas/1.0",
    )


def okx_client(api_key: Optional[str] = None) -> HttpClientFactory:
    """Pre-configured client for OKX API."""
    api_key = api_key or os.environ.get("OKX_API_KEY")
    auth = ApiKeyAuth(api_key=api_key, header_name="OK-ACCESS-KEY") if api_key else None
    return HttpClientFactory(
        base_url="https://www.okx.com/api/v5",
        auth=auth,
        rate_limit=5.0,
        user_agent="sruth-crypteolas/1.0",
    )


def bybit_client(api_key: Optional[str] = None) -> HttpClientFactory:
    """Pre-configured client for Bybit API."""
    api_key = api_key or os.environ.get("BYBIT_API_KEY")
    auth = ApiKeyAuth(api_key=api_key, header_name="X-BAPI-API-KEY") if api_key else None
    return HttpClientFactory(
        base_url="https://api.bybit.com/v5",
        auth=auth,
        rate_limit=5.0,
        user_agent="sruth-crypteolas/1.0",
    )


def beaconchain_client(api_key: Optional[str] = None) -> HttpClientFactory:
    """Pre-configured client for Beaconcha.in API."""
    api_key = api_key or os.environ.get("BEACONCHAIN_API_KEY")
    auth = ApiKeyAuth(api_key=api_key, header_name="apikey") if api_key else None
    return HttpClientFactory(
        base_url="https://beaconcha.in/api/v1",
        auth=auth,
        rate_limit=10.0 if api_key else 1.0,  # Free tier limited
        user_agent="sruth-crypteolas/1.0",
    )


def thegraph_client() -> HttpClientFactory:
    """Pre-configured client for The Graph GraphQL endpoints."""
    return HttpClientFactory(
        base_url="https://api.thegraph.com/subgraphs/name",
        rate_limit=5.0,
        user_agent="sruth-crypteolas/1.0",
        extra_headers={"Content-Type": "application/json"},
    )


# =========================================================================
# Irish Education & Celtic Language APIs (oideachais)
# =========================================================================


def logainm_client() -> HttpClientFactory:
    """Pre-configured client for Logainm.ie Placenames Database API."""
    return HttpClientFactory(
        base_url="https://www.logainm.ie/api/v1.1",
        rate_limit=5.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def tearma_client() -> HttpClientFactory:
    """Pre-configured client for Téarma.ie National Terminology Database."""
    return HttpClientFactory(
        base_url="https://www.tearma.ie",
        rate_limit=2.0,  # Conservative for web scraping
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def ainm_client() -> HttpClientFactory:
    """Pre-configured client for Ainm.ie National Biographical Database."""
    return HttpClientFactory(
        base_url="https://www.ainm.ie",
        rate_limit=2.0,  # Conservative for web scraping
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def duchas_client() -> HttpClientFactory:
    """Pre-configured client for Dúchas.ie National Folklore Collection."""
    return HttpClientFactory(
        base_url="https://www.duchas.ie",
        rate_limit=2.0,  # Conservative for web scraping
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def doras_client() -> HttpClientFactory:
    """Pre-configured client for Doras GAOIS linguistic APIs."""
    return HttpClientFactory(
        base_url="https://doras.gaois.ie",
        rate_limit=5.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def cso_pxstat_client() -> HttpClientFactory:
    """Pre-configured client for CSO PxStat JSON-RPC API."""
    return HttpClientFactory(
        base_url="https://ws.cso.ie/public/api.jsonrpc",
        rate_limit=2.0,  # Government API, be conservative
        user_agent="oideachais-dlt/1.0",
        timeout=120.0,  # Large datasets take time
        extra_headers={"Content-Type": "application/json"},
    )


def data_gov_ie_client() -> HttpClientFactory:
    """Pre-configured client for data.gov.ie CKAN API."""
    return HttpClientFactory(
        base_url="https://data.gov.ie/api/3/action",
        rate_limit=5.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def ncca_client() -> HttpClientFactory:
    """Pre-configured client for NCCA curriculum website."""
    return HttpClientFactory(
        base_url="https://ncca.ie",
        rate_limit=2.0,  # Conservative for web scraping
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def curriculum_online_client() -> HttpClientFactory:
    """Pre-configured client for curriculumonline.ie."""
    return HttpClientFactory(
        base_url="https://curriculumonline.ie",
        rate_limit=2.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def sec_ie_client() -> HttpClientFactory:
    """Pre-configured client for SEC (State Examinations Commission)."""
    return HttpClientFactory(
        base_url="https://www.examinations.ie",
        rate_limit=2.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


# =========================================================================
# Pan-Celtic Language APIs (tuath)
# =========================================================================


def stats_wales_client() -> HttpClientFactory:
    """Pre-configured client for StatsWales government statistics."""
    return HttpClientFactory(
        base_url="https://statswales.gov.wales",
        rate_limit=5.0,
        user_agent="tuath-dlt/1.0",
        timeout=120.0,
        extra_headers={"Accept": "application/json, application/geo+json"},
    )


def scotland_stats_client() -> HttpClientFactory:
    """Pre-configured client for Scotland's statistics portal."""
    return HttpClientFactory(
        base_url="https://statistics.gov.scot",
        rate_limit=5.0,
        user_agent="tuath-dlt/1.0",
        timeout=120.0,
        extra_headers={"Accept": "application/json, application/geo+json"},
    )


def osi_client() -> HttpClientFactory:
    """Pre-configured client for Ordnance Survey Ireland."""
    return HttpClientFactory(
        base_url="https://www.osi.ie",
        rate_limit=2.0,
        user_agent="tuath-dlt/1.0",
        timeout=120.0,
        extra_headers={"Accept": "application/json, application/geo+json"},
    )


def stats_wales_odata_client() -> HttpClientFactory:
    """Pre-configured client for StatsWales OData API."""
    return HttpClientFactory(
        base_url="https://statswales.gov.wales/OData",
        rate_limit=5.0,
        user_agent="oideachais-dlt/1.0",
        timeout=120.0,
    )


# =========================================================================
# UK Education APIs (oideachais)
# =========================================================================


def dfe_explore_client() -> HttpClientFactory:
    """Pre-configured client for England DfE Explore Education Statistics API."""
    return HttpClientFactory(
        base_url="https://api.education.gov.uk/statistics/v1",
        rate_limit=5.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def nisra_client() -> HttpClientFactory:
    """Pre-configured client for Northern Ireland NISRA statistics."""
    return HttpClientFactory(
        base_url="https://data.nisra.gov.uk/api/v1",
        rate_limit=2.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def get_info_schools_client() -> HttpClientFactory:
    """Pre-configured client for Get Information About Schools (UK)."""
    return HttpClientFactory(
        base_url="https://www.get-information-schools.service.gov.uk",
        rate_limit=2.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


# =========================================================================
# Geospatial APIs (oideachais/geospatial)
# =========================================================================


def arcgis_geohive_client() -> HttpClientFactory:
    """Pre-configured client for GeoHive.ie ArcGIS FeatureServer."""
    return HttpClientFactory(
        base_url="https://services1.arcgis.com/eNO7HHeQ3rUcBllm/arcgis/rest/services",
        rate_limit=5.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
        extra_headers={"Accept": "application/json"},
    )


def met_eireann_client() -> HttpClientFactory:
    """Pre-configured client for Met Éireann weather API."""
    return HttpClientFactory(
        base_url="https://www.met.ie/climate/available-data",
        rate_limit=2.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def met_office_uk_client() -> HttpClientFactory:
    """Pre-configured client for UK Met Office DataPoint API."""
    api_key = os.environ.get("MET_OFFICE_API_KEY", "")
    auth = (
        ApiKeyAuth(api_key=api_key, as_query_param=True, query_param_name="key")
        if api_key
        else None
    )
    return HttpClientFactory(
        base_url="http://datapoint.metoffice.gov.uk/public/data",
        auth=auth,
        rate_limit=5.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def met_office_datahub_client() -> HttpClientFactory:
    """Pre-configured client for UK Met Office DataHub API."""
    api_key = os.environ.get("METOFFICE_API_KEY", "")
    return HttpClientFactory(
        base_url="https://data.hub.api.metoffice.gov.uk/sitespecific/v0",
        rate_limit=5.0,
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
        extra_headers={"apikey": api_key, "Accept": "application/json"},
    )


def met_office_climate_client() -> HttpClientFactory:
    """Pre-configured client for UK Met Office public climate data."""
    return HttpClientFactory(
        base_url="https://www.metoffice.gov.uk/pub/data/weather/uk",
        rate_limit=2.0,
        user_agent="oideachais-dlt/1.0",
        timeout=30.0,
    )


# =========================================================================
# Celtic Language & Pronunciation APIs (oideachais/celtic)
# =========================================================================


def canuint_client() -> HttpClientFactory:
    """Pre-configured client for Canúint.ie Irish Pronunciation Database."""
    return HttpClientFactory(
        base_url="https://www.canuint.ie",
        rate_limit=2.0,  # Conservative for web scraping
        user_agent="oideachais-dlt/1.0",
        timeout=60.0,
    )


def gaois_client() -> HttpClientFactory:
    """Pre-configured client for GAOIS.ie corpus and linguistic resources."""
    return HttpClientFactory(
        base_url="https://www.gaois.ie",
        rate_limit=2.0,  # Conservative for academic resources
        user_agent="oideachais-dlt/1.0",
        timeout=120.0,  # Large TMX files can take time
    )
