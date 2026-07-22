"""
Pytest fixtures for Browser automation tests.
"""

import asyncio
import json
from datetime import datetime, timedelta
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

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    import pytest_asyncio
    HAS_PYTEST_ASYNCIO = True
except ImportError:
    HAS_PYTEST_ASYNCIO = False


# --- Skip decorators ---

requires_fastapi = pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
requires_httpx = pytest.mark.skipif(not HAS_HTTPX, reason="httpx not installed")
requires_async = pytest.mark.skipif(not HAS_PYTEST_ASYNCIO, reason="pytest-asyncio not installed")


# --- Path fixtures ---


@pytest.fixture
def project_root() -> Path:
    """Return the browser project root."""
    return Path(__file__).parent.parent


@pytest.fixture
def fixtures_path() -> Path:
    """Return the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


# --- Configuration fixtures ---


@pytest.fixture
def minimal_browser_config():
    """Minimal browser config for testing without external services."""
    return {
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "BROWSERBASE_API_KEY": "",
        "BROWSERBASE_PROJECT_ID": "",
        "FIRECRAWL_API_KEY": "",
        "ZAI_API_KEY": "",
    }


@pytest.fixture
def full_browser_config():
    """Full browser config with all services enabled."""
    return {
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "BROWSERBASE_API_KEY": "test-bb-key",
        "BROWSERBASE_PROJECT_ID": "test-project-id",
        "FIRECRAWL_API_KEY": "test-fc-key",
        "ZAI_API_KEY": "test-zai-key",
        "CDP_ENDPOINT": "ws://localhost:9222",
        "SKYVERN_ENDPOINT": "http://localhost:8080",
        "CRAWL4AI_ENDPOINT": "http://localhost:11235",
    }


@pytest.fixture
def mock_browser_config(minimal_browser_config, monkeypatch):
    """Set environment variables for minimal config."""
    for key, value in minimal_browser_config.items():
        monkeypatch.setenv(key, value)


# --- HTTP mocking fixtures ---


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


# --- Backend type fixtures ---


@pytest.fixture
def backend_types():
    """All backend types for parameterized tests."""
    try:
        from browser.core.types import BackendType
        return list(BackendType)
    except ImportError:
        pytest.skip("browser.core.types not importable")


@pytest.fixture
def self_hosted_backends():
    """Self-hosted backend types."""
    try:
        from browser.core.types import BackendType
        return [
            BackendType.CDP_LOCAL,
            BackendType.SKYVERN_LOCAL,
            BackendType.CRAWL4AI_LOCAL,
            BackendType.STAGEHAND_LOCAL,
        ]
    except ImportError:
        pytest.skip("browser.core.types not importable")


@pytest.fixture
def paid_backends():
    """Paid/cloud backend types."""
    try:
        from browser.core.types import BackendType
        return [
            BackendType.FIRECRAWL_MCP,
            BackendType.BROWSERBASE_MCP,
            BackendType.ZAI_VISION,
        ]
    except ImportError:
        pytest.skip("browser.core.types not importable")


@pytest.fixture
def operation_types():
    """All browser operation types."""
    try:
        from browser.core.types import BrowserOperation
        return list(BrowserOperation)
    except ImportError:
        pytest.skip("browser.core.types not importable")


# --- Circuit breaker fixtures ---


@pytest.fixture
def circuit_breaker_config():
    """Default circuit breaker configuration."""
    return {
        "failure_threshold": 3,
        "recovery_timeout": 30.0,
        "half_open_requests": 1,
    }


@pytest.fixture
def mock_circuit_breaker():
    """Mock circuit breaker for testing."""
    try:
        from browser.core.types import BackendType, CircuitState
    except ImportError:
        pytest.skip("browser.core.types not importable")

    class MockCircuitBreaker:
        def __init__(self, backend: BackendType):
            self.backend = backend
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.failure_threshold = 3
            self.recovery_timeout = 30.0

        async def can_execute(self) -> bool:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                    if elapsed >= self.recovery_timeout:
                        self.state = CircuitState.HALF_OPEN
                        return True
                return False
            else:  # HALF_OPEN
                return True

        async def record_success(self, latency_ms: float = 100.0):
            self.success_count += 1
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0

        async def record_failure(self, error: str = "test error"):
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

    return MockCircuitBreaker


@pytest.fixture
def closed_circuit_breaker(mock_circuit_breaker):
    """Circuit breaker in CLOSED state."""
    try:
        from browser.core.types import BackendType
    except ImportError:
        pytest.skip("browser.core.types not importable")

    return mock_circuit_breaker(BackendType.CDP_LOCAL)


@pytest.fixture
def open_circuit_breaker(mock_circuit_breaker):
    """Circuit breaker in OPEN state."""
    try:
        from browser.core.types import BackendType, CircuitState
    except ImportError:
        pytest.skip("browser.core.types not importable")

    breaker = mock_circuit_breaker(BackendType.CDP_LOCAL)
    breaker.state = CircuitState.OPEN
    breaker.failure_count = 5
    breaker.last_failure_time = datetime.now()
    return breaker


@pytest.fixture
def half_open_circuit_breaker(mock_circuit_breaker):
    """Circuit breaker in HALF_OPEN state."""
    try:
        from browser.core.types import BackendType, CircuitState
    except ImportError:
        pytest.skip("browser.core.types not importable")

    breaker = mock_circuit_breaker(BackendType.CDP_LOCAL)
    breaker.state = CircuitState.HALF_OPEN
    breaker.failure_count = 3
    breaker.last_failure_time = datetime.now() - timedelta(seconds=35)
    return breaker


# --- Backend health fixtures ---


@pytest.fixture
def healthy_backend_health():
    """Healthy backend status."""
    try:
        from browser.core.types import BackendType, CircuitState
    except ImportError:
        pytest.skip("browser.core.types not importable")

    return {
        "backend": BackendType.CDP_LOCAL,
        "available": True,
        "circuit_state": CircuitState.CLOSED,
        "failure_count": 0,
        "avg_latency_ms": 150.0,
        "last_success": datetime.now().isoformat(),
        "last_failure": None,
    }


@pytest.fixture
def unhealthy_backend_health():
    """Unhealthy backend status."""
    try:
        from browser.core.types import BackendType, CircuitState
    except ImportError:
        pytest.skip("browser.core.types not importable")

    return {
        "backend": BackendType.CDP_LOCAL,
        "available": False,
        "circuit_state": CircuitState.OPEN,
        "failure_count": 5,
        "avg_latency_ms": None,
        "last_success": None,
        "last_failure": datetime.now().isoformat(),
    }


# --- Scrape result fixtures ---


@pytest.fixture
def sample_scrape_result():
    """Sample successful scrape result."""
    return {
        "url": "https://example.com/page",
        "title": "Example Page",
        "content": "This is the main content of the page.",
        "html": "<html><body><h1>Example</h1><p>Content</p></body></html>",
        "links": [
            {"href": "https://example.com/link1", "text": "Link 1"},
            {"href": "https://example.com/link2", "text": "Link 2"},
        ],
        "metadata": {
            "status_code": 200,
            "content_type": "text/html",
            "scraped_at": datetime.now().isoformat(),
        },
    }


@pytest.fixture
def sample_screenshot_result():
    """Sample screenshot result."""
    return {
        "url": "https://example.com/page",
        "screenshot_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "viewport": {"width": 1920, "height": 1080},
        "format": "png",
    }


@pytest.fixture
def sample_extraction_result():
    """Sample data extraction result."""
    return {
        "url": "https://example.com/products",
        "extracted_data": [
            {"name": "Product 1", "price": 29.99, "in_stock": True},
            {"name": "Product 2", "price": 49.99, "in_stock": False},
        ],
        "schema_used": "product_listing",
        "confidence": 0.95,
    }


# --- HTML sample fixtures ---


@pytest.fixture
def sample_html_simple():
    """Simple HTML page for testing."""
    return """<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
    <h1>Welcome</h1>
    <p>This is a test paragraph.</p>
    <a href="/link1">Link 1</a>
    <a href="/link2">Link 2</a>
</body>
</html>"""


@pytest.fixture
def sample_html_form():
    """HTML page with form for testing."""
    return """<!DOCTYPE html>
<html>
<head><title>Login Form</title></head>
<body>
    <form id="login-form" action="/login" method="post">
        <input type="text" name="username" id="username" placeholder="Username">
        <input type="password" name="password" id="password" placeholder="Password">
        <button type="submit">Login</button>
    </form>
</body>
</html>"""


@pytest.fixture
def sample_html_dynamic():
    """HTML page with JavaScript-rendered content."""
    return """<!DOCTYPE html>
<html>
<head><title>Dynamic Content</title></head>
<body>
    <div id="content">Loading...</div>
    <script>
        setTimeout(() => {
            document.getElementById('content').innerHTML = 'Loaded content';
        }, 1000);
    </script>
</body>
</html>"""


# --- API response fixtures ---


@pytest.fixture
def firecrawl_scrape_response():
    """Mock Firecrawl scrape API response."""
    return {
        "success": True,
        "data": {
            "content": "# Page Title\n\nThis is the markdown content.",
            "html": "<html><body><h1>Page Title</h1><p>Content</p></body></html>",
            "metadata": {
                "title": "Page Title",
                "description": "Page description",
                "language": "en",
                "sourceURL": "https://example.com",
            },
            "links": ["https://example.com/link1", "https://example.com/link2"],
        },
    }


@pytest.fixture
def firecrawl_map_response():
    """Mock Firecrawl map API response."""
    return {
        "success": True,
        "links": [
            "https://example.com/",
            "https://example.com/about",
            "https://example.com/products",
            "https://example.com/contact",
        ],
    }


@pytest.fixture
def firecrawl_search_response():
    """Mock Firecrawl search API response."""
    return {
        "success": True,
        "data": [
            {
                "url": "https://example.com/result1",
                "title": "Search Result 1",
                "description": "First search result description",
            },
            {
                "url": "https://example.com/result2",
                "title": "Search Result 2",
                "description": "Second search result description",
            },
        ],
    }


@pytest.fixture
def browserbase_session_response():
    """Mock Browserbase session creation response."""
    return {
        "id": "session-123-abc",
        "status": "RUNNING",
        "wsEndpoint": "wss://connect.browserbase.com/session-123-abc",
        "createdAt": datetime.now().isoformat(),
        "expiresAt": (datetime.now() + timedelta(hours=1)).isoformat(),
    }


@pytest.fixture
def crawl4ai_scrape_response():
    """Mock Crawl4AI scrape response."""
    return {
        "success": True,
        "html": "<html><body><p>Content</p></body></html>",
        "cleaned_html": "<p>Content</p>",
        "markdown": "Content",
        "extracted_content": "Content",
        "metadata": {
            "title": "Page Title",
            "links": {"internal": 5, "external": 2},
        },
    }


# --- FastAPI test client fixtures ---


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    if not HAS_FASTAPI:
        pytest.skip("FastAPI not installed")

    try:
        from browser.server import app
        return TestClient(app)
    except ImportError:
        pytest.skip("browser.server not importable")


# --- Mock backend fixtures ---


@pytest.fixture
def mock_cdp_backend():
    """Mock CDP backend for testing."""
    backend = AsyncMock()
    backend.name = "cdp_local"
    backend.scrape = AsyncMock()
    backend.screenshot = AsyncMock()
    backend.navigate = AsyncMock()
    backend.execute_script = AsyncMock()
    backend.close = AsyncMock()
    return backend


@pytest.fixture
def mock_crawl4ai_backend():
    """Mock Crawl4AI backend for testing."""
    backend = AsyncMock()
    backend.name = "crawl4ai_local"
    backend.scrape = AsyncMock()
    backend.extract = AsyncMock()
    backend.close = AsyncMock()
    return backend


@pytest.fixture
def mock_firecrawl_backend():
    """Mock Firecrawl backend for testing."""
    backend = AsyncMock()
    backend.name = "firecrawl_mcp"
    backend.scrape = AsyncMock()
    backend.map_site = AsyncMock()
    backend.search = AsyncMock()
    backend.close = AsyncMock()
    return backend


@pytest.fixture
def mock_browserbase_backend():
    """Mock Browserbase backend for testing."""
    backend = AsyncMock()
    backend.name = "browserbase_mcp"
    backend.create_session = AsyncMock()
    backend.scrape = AsyncMock()
    backend.interact = AsyncMock()
    backend.close_session = AsyncMock()
    backend.close = AsyncMock()
    return backend


# --- Error simulation fixtures ---


@pytest.fixture
def connection_error():
    """Simulated connection error."""
    if HAS_HTTPX:
        return httpx.ConnectError("Connection refused")
    return ConnectionError("Connection refused")


@pytest.fixture
def timeout_error():
    """Simulated timeout error."""
    if HAS_HTTPX:
        return httpx.TimeoutException("Request timed out")
    return TimeoutError("Request timed out")


@pytest.fixture
def rate_limit_error():
    """Simulated rate limit response."""
    response = MagicMock()
    response.status_code = 429
    response.headers = {"Retry-After": "60"}
    response.json.return_value = {"error": "Rate limit exceeded"}
    return response


# --- Pytest configuration ---


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "external: marks tests requiring external services"
    )
    config.addinivalue_line(
        "markers", "backend(name): marks tests for specific backend"
    )
