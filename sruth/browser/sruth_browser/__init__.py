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
from .browser_types import (
    BackendType,
    BrowserOperation,
    ExtractionFormat,
    SessionState,
    NavigationResult,
    ExtractionResult,
    InteractionResult,
    ScreenshotResult,
    ResearchResult,
    BackendHealth,
    CircuitState,
    BACKEND_PRIORITY,
    BACKEND_COST,
)

# Config
from .config import (
    BrowserConfig,
    get_config,
)

# Exceptions
from .exceptions import (
    BrowserAgentError,
    BackendError,
    BackendTimeoutError,
    CircuitOpenError,
    FallbackExhaustedError,
    NavigationError,
    ExtractionError,
    SessionError,
    SchemaValidationError,
)

# Client (for external consumers)
from .client.http_client import BrowserClient

# Backends
from .backends import (
    BrowserBackend,
    ResearchCapableBackend,
    BackendRouter,
    CircuitBreaker,
    get_router,
)

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
]
