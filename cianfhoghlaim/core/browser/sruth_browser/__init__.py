"""
Browser Agent Stack

Multi-backend browser automation with intelligent routing.

Architecture:
- Hunter (Skyvern): Vision-based semantic navigation
- Operator (Stagehand): Precision interactions with caching
- Gatherer (Crawl4AI): Bulk extraction with LLM strategies
- Evaluator (BAML): Quality validation and schema enforcement

Backend Priority:
1. Self-hosted ($0): CDP Local, Skyvern API, Crawl4AI, Stagehand
2. Paid (fallback): Firecrawl MCP, Browserbase MCP, Z.AI Vision

Frontend Protocols:
- TanStack AI: /chat (SSE stream)
- MCP-UI: /mcp (JSON-RPC)
- AG-UI: /agui (17-event SSE)
"""

# Types
# Backends
from .backends import (
    BackendRouter,
    BrowserBackend,
    CircuitBreaker,
    ResearchCapableBackend,
    get_router,
)
from .browser_types import (
    BACKEND_COST,
    BACKEND_PRIORITY,
    BackendHealth,
    BackendType,
    BrowserOperation,
    CircuitState,
    ExtractionFormat,
    ExtractionResult,
    InteractionResult,
    NavigationResult,
    ResearchResult,
    ScreenshotResult,
    SessionState,
)

# Client (for external consumers)
from .client.http_client import BrowserClient

# Config
from .config import (
    BrowserConfig,
    get_config,
)

# Exceptions
from .exceptions import (
    BackendError,
    BackendTimeoutError,
    BrowserAgentError,
    CircuitOpenError,
    ExtractionError,
    FallbackExhaustedError,
    NavigationError,
    SchemaValidationError,
    SessionError,
)

# Strategist (the thin wrapper used by oideachais DAG assets)
from .scrape_strategist import ScrapeStrategist

__version__ = "0.1.0"
__all__ = [
    # Client
    "BrowserClient",
    # Types
    "BackendType",
    "BrowserOperation",
    "ExtractionFormat",
    "SessionState",
    "NavigationResult",
    "ExtractionResult",
    "InteractionResult",
    "ScreenshotResult",
    "ResearchResult",
    "BackendHealth",
    "CircuitState",
    "BACKEND_PRIORITY",
    "BACKEND_COST",
    # Config
    "BrowserConfig",
    "get_config",
    # Exceptions
    "BrowserAgentError",
    "BackendError",
    "BackendTimeoutError",
    "CircuitOpenError",
    "FallbackExhaustedError",
    "NavigationError",
    "ExtractionError",
    "SessionError",
    "SchemaValidationError",
    # Backends
    "BrowserBackend",
    "ResearchCapableBackend",
    "BackendRouter",
    "CircuitBreaker",
    "get_router",
    # Strategist (the thin wrapper used by oideachais DAG assets)
    "ScrapeStrategist",
]
