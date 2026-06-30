"""
browser — the canonical namespace for the browser stack.

This module is the deprecation alias for the old `sruth_browser` module
(v4 cleanup per openspec/changes/2026-06-29-browser-stack-crawl4ai-refactor).

The actual code lives at `sruth_browser/` (a sibling module under
`cianfhoghlaim.core.browser`). Existing import sites using
`from sruth_browser import ...` will continue to work during the
deprecation window.

New code should use:
    from cianfhoghlaim.core.browser import BrowserClient, ScrapeStrategist, ...

The 5-backends final state (Moderate choice; 3 default + 2 opt-in):
1. Crawl4AI (self-hosted, port 11235)        — default ON
2. Firecrawl (paid fallback, MCP API)        — default ON
3. Playwright CDP (self-hosted, port 9222)  — default ON
4. Skyvern (opt-in via BROWSER_ENABLE_SKYVERN=1)
5. Stagehand (opt-in via BROWSER_ENABLE_STAGEHAND=1)

Browserbase was removed 2026-06-29 (no credits, no replacement plan).
Z.AI Vision is deprecated; will be removed in a follow-up.
"""
from cianfhoghlaim.core.browser.sruth_browser import (  # noqa: F401
    # Client
    BrowserClient,
    # Types
    BACKEND_COST,
    BACKEND_PRIORITY,
    BackendHealth,
    BackendType,
    BrowserOperation,
    BrowserBackend,
    CircuitBreaker,
    CircuitState,
    ExtractionFormat,
    ExtractionResult,
    InteractionResult,
    NavigationResult,
    ResearchCapableBackend,
    ResearchResult,
    ScreenshotResult,
    SessionState,
    # Config
    BrowserConfig,
    get_config,
    # Exceptions
    BackendError,
    BackendTimeoutError,
    BrowserAgentError,
    CircuitOpenError,
    ExtractionError,
    FallbackExhaustedError,
    NavigationError,
    SchemaValidationError,
    SessionError,
    # Strategist
    ScrapeStrategist,
    # Router
    BackendRouter,
    get_router,
)

__version__ = "0.1.0"

__all__ = [
    "BrowserClient",
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
    "BrowserConfig",
    "get_config",
    "BrowserAgentError",
    "BackendError",
    "BackendTimeoutError",
    "CircuitOpenError",
    "FallbackExhaustedError",
    "NavigationError",
    "ExtractionError",
    "SessionError",
    "SchemaValidationError",
    "BrowserBackend",
    "ResearchCapableBackend",
    "BackendRouter",
    "CircuitBreaker",
    "get_router",
    "ScrapeStrategist",
    "__version__",
]
