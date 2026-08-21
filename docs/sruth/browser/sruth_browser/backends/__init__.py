"""Browser backend implementations.

This module provides the abstract base classes and routing infrastructure
for browser automation backends.

Backend categories:
- Self-hosted ($0 cost): CDP, Stagehand, Crawl4AI, Skyvern
- Paid: Browserbase, Firecrawl, Z.AI Vision
"""

from .base import BrowserBackend, ResearchCapableBackend
from .router import BackendRouter, CircuitBreaker, get_router

# Self-hosted backends ($0 cost)
from .selfhosted import (
    CDPBackend,
    Crawl4AIBackend,
    SkyvernBackend,
    StagehandBackend,
)

# Paid backends
from .paid import (
    BrowserbaseBackend,
    FirecrawlBackend,
    ZAIVisionBackend,
    ZAIMCPClient,
    get_zai_mcp_client,
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
    "BrowserbaseBackend",
    "FirecrawlBackend",
    "ZAIVisionBackend",
    "ZAIMCPClient",
    "get_zai_mcp_client",
]
