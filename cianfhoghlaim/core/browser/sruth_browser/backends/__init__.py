"""Browser backend implementations.

This module provides the abstract base classes and routing infrastructure
for browser automation backends.

Backend categories (post browserbase-removal):
- Self-hosted ($0 cost): CDP, Stagehand, Crawl4AI, Skyvern
- Paid: Firecrawl, Z.AI Vision

Browserbase was removed 2026-06-29 per the
`2026-06-29-browser-stack-crawl4ai-refactor` change (no credits,
no replacement plan). Z.AI Vision is deprecated and will be
removed in a follow-up.
"""

from .base import BrowserBackend, ResearchCapableBackend

# Paid backends
from .paid import (
    FirecrawlBackend,
    ZAIMCPClient,
    ZAIVisionBackend,
    get_zai_mcp_client,
)
from .router import BackendRouter, CircuitBreaker, get_router

# Self-hosted backends ($0 cost)
from .selfhosted import (
    CDPBackend,
    Crawl4AIBackend,
    SkyvernBackend,
    StagehandBackend,
)

__all__ = [
    # Base classes
    "BrowserBackend",
    "ResearchCapableBackend",
    "BackendRouter",
    "CircuitBreaker",
    "get_router",
    # Self-hosted backends
    "CDPBackend",
    "Crawl4AIBackend",
    "SkyvernBackend",
    "StagehandBackend",
    # Paid backends
    "FirecrawlBackend",
    "ZAIVisionBackend",
    "ZAIMCPClient",
    "get_zai_mcp_client",
]
