"""Standalone backend initializer for scripts and tests.

This module provides initialization that can be called from:
- Standalone scripts (tests, scrapers, Dagster assets)
- Server lifespan handler (FastAPI/MCP)
- Any code that needs browser backends without starting the full server

Example:
    from sruth.browser.sruth_browser.backends.initializer import initialize_backends

    # Initialize backends for standalone use
    await initialize_backends(
        cdp=True,
        stagehand=True,
        browserbase=False,
    )
"""

import asyncio
from typing import Literal

import structlog

from ..config import BrowserConfig, get_config
from ..browser_types import BackendType
from .router import get_router

logger = structlog.get_logger()

# Track initialized backends for cleanup
_initialized_backends: list[BackendType] = []


async def initialize_backends(
    cdp: bool = True,
    crawl4ai: bool = True,
    skyvern: bool = False,
    stagehand: bool = True,
    browserbase: bool = False,
    firecrawl: bool = False,
    zai: bool = False,
    config: BrowserConfig | None = None,
) -> list[BackendType]:
    """Initialize browser backends for standalone use.

    This function can be called from scripts, tests, or Dagster assets
    to initialize browser backends without starting the full server.

    Args:
        cdp: Initialize Chrome DevTools Protocol backend (local Chrome)
        crawl4ai: Initialize Crawl4AI backend (bulk scraping)
        skyvern: Initialize Skyvern backend (vision-based RPA)
        stagehand: Initialize Stagehand backend (AI-powered, GLM-4.6/7)
        browserbase: Initialize Browserbase backend (cloud fallback)
        firecrawl: Initialize Firecrawl backend (cloud fallback)
        zai: Initialize Z.AI backend (GLM-4.6v vision)
        config: Optional custom config (uses get_config() if None)

    Returns:
        List of successfully initialized backend types

    Example:
        from sruth.browser.sruth_browser.backends.initializer import initialize_backends

        backends = await initialize_backends(
            cdp=True,
            stagehand=True,
        )
        print(f"Initialized: {[b.value for b in backends]}")
    """
    global _initialized_backends
    config = config or get_config()
    router = get_router()
    initialized: list[BackendType] = []

    # Check if already initialized (avoid duplicate initialization)
    existing_backends = router.registered_backends()
    if existing_backends:
        logger.info(
            "backends_already_initialized",
            backends=[b.value for b in existing_backends],
        )
        return existing_backends

    # Self-hosted backends (priority order: $0 cost)

    if cdp:
        try:
            from .selfhosted import CDPBackend

            cdp_backend = CDPBackend(config)
            await cdp_backend.initialize()
            router.register_backend(cdp_backend)
            initialized.append(BackendType.CDP_LOCAL)
            logger.info("backend_initialized", backend="cdp_local")
        except Exception as e:
            logger.warning("cdp_init_failed", error=str(e))

    if crawl4ai:
        try:
            from .selfhosted import Crawl4AIBackend

            crawl4ai_backend = Crawl4AIBackend(config)
            await crawl4ai_backend.initialize()
            router.register_backend(crawl4ai_backend)
            initialized.append(BackendType.CRAWL4AI_LOCAL)
            logger.info("backend_initialized", backend="crawl4ai_local")
        except Exception as e:
            logger.warning("crawl4ai_init_failed", error=str(e))

    if skyvern:
        try:
            from .selfhosted import SkyvernBackend

            skyvern_backend = SkyvernBackend(config)
            await skyvern_backend.initialize()
            router.register_backend(skyvern_backend)
            initialized.append(BackendType.SKYVERN_LOCAL)
            logger.info("backend_initialized", backend="skyvern_local")
        except Exception as e:
            logger.warning("skyvern_init_failed", error=str(e))

    if stagehand:
        try:
            from .selfhosted import StagehandBackend

            stagehand_backend = StagehandBackend(config)
            await stagehand_backend.initialize()
            router.register_backend(stagehand_backend)
            initialized.append(BackendType.STAGEHAND_LOCAL)
            logger.info("backend_initialized", backend="stagehand_local")
        except Exception as e:
            logger.warning("stagehand_init_failed", error=str(e))

    # Paid fallbacks (only if credentials available)

    if browserbase and config.has_browserbase:
        try:
            from .paid import BrowserbaseBackend

            bb_backend = BrowserbaseBackend(config)
            await bb_backend.initialize()
            router.register_backend(bb_backend)
            initialized.append(BackendType.BROWSERBASE_MCP)
            logger.info("backend_initialized", backend="browserbase_mcp")
        except Exception as e:
            logger.warning("browserbase_init_failed", error=str(e))

    if firecrawl and config.has_firecrawl:
        try:
            from .paid import FirecrawlBackend

            fc_backend = FirecrawlBackend(config)
            await fc_backend.initialize()
            router.register_backend(fc_backend)
            initialized.append(BackendType.FIRECRAWL_MCP)
            logger.info("backend_initialized", backend="firecrawl_mcp")
        except Exception as e:
            logger.warning("firecrawl_init_failed", error=str(e))

    if zai and config.has_zai:
        try:
            from .paid import ZAIBackend

            zai_backend = ZAIBackend(config)
            await zai_backend.initialize()
            router.register_backend(zai_backend)
            initialized.append(BackendType.ZAI_VISION)
            logger.info("backend_initialized", backend="zai_vision")
        except Exception as e:
            logger.warning("zai_init_failed", error=str(e))

    _initialized_backends = initialized
    logger.info(
        "initialization_complete",
        backends=[b.value for b in initialized],
        count=len(initialized),
    )

    return initialized


async def shutdown_backends() -> None:
    """Shutdown all initialized backends.

    This should be called when done with browser operations to properly
    release resources (close browser sessions, etc.).

    Example:
        try:
            backends = await initialize_backends()
            # ... do work ...
        finally:
            await shutdown_backends()
    """
    global _initialized_backends
    router = get_router()

    for backend_type in list(_initialized_backends):
        try:
            backend = router.get_backend(backend_type)
            if backend and hasattr(backend, "close"):
                await backend.close()
                logger.info("backend_closed", backend=backend_type.value)
        except Exception as e:
            logger.warning("backend_close_failed", backend=backend_type.value, error=str(e))

    _initialized_backends = []
    logger.info("shutdown_complete")


def is_initialized() -> bool:
    """Check if any backends have been initialized.

    Returns:
        True if at least one backend is registered, False otherwise
    """
    router = get_router()
    return len(router.registered_backends()) > 0


async def ensure_initialized(
    preferred_backends: list[BackendType] | None = None,
) -> list[BackendType]:
    """Ensure backends are initialized, initializing if needed.

    This is a convenience function that checks if backends are already
    initialized and initializes them if not. Useful for functions
    that want to work both in server and standalone contexts.

    Args:
        preferred_backends: List of preferred backend types to initialize.
            If None, defaults to [CDP_LOCAL, STAGEHAND_LOCAL].

    Returns:
        List of available backend types

    Example:
        from sruth.browser.sruth_browser.backends.initializer import ensure_initialized

        # In a scraper - works standalone or via server
        available = await ensure_initialized()
        if BackendType.STAGEHAND_LOCAL in available:
            # Use Stagehand
            ...
    """
    if is_initialized():
        router = get_router()
        return router.registered_backends()

    # Default to CDP + Stagehand for most use cases
    if preferred_backends is None:
        preferred_backends = [BackendType.CDP_LOCAL, BackendType.STAGEHAND_LOCAL]

    # Map BackendType to initialize_backends kwargs
    kwargs = {
        "cdp": BackendType.CDP_LOCAL in preferred_backends,
        "crawl4ai": BackendType.CRAWL4AI_LOCAL in preferred_backends,
        "skyvern": BackendType.SKYVERN_LOCAL in preferred_backends,
        "stagehand": BackendType.STAGEHAND_LOCAL in preferred_backends,
        "browserbase": BackendType.BROWSERBASE_MCP in preferred_backends,
        "firecrawl": BackendType.FIRECRAWL_MCP in preferred_backends,
        "zai": BackendType.ZAI_VISION in preferred_backends,
    }

    return await initialize_backends(**kwargs)


# Context manager for automatic cleanup
class BackendSession:
    """Context manager for backend initialization and cleanup.

    Example:
        from sruth.browser.sruth_browser.backends.initializer import BackendSession

        async with BackendSession(cdp=True, stagehand=True):
            # Backends are initialized
            await do_scraping()
        # Backends are automatically cleaned up
    """

    def __init__(
        self,
        cdp: bool = True,
        crawl4ai: bool = False,
        skyvern: bool = False,
        stagehand: bool = True,
        browserbase: bool = False,
        firecrawl: bool = False,
        zai: bool = False,
        config: BrowserConfig | None = None,
    ):
        self.cdp = cdp
        self.crawl4ai = crawl4ai
        self.skyvern = skyvern
        self.stagehand = stagehand
        self.browserbase = browserbase
        self.firecrawl = firecrawl
        self.zai = zai
        self.config = config
        self._initialized: list[BackendType] = []

    async def __aenter__(self) -> list[BackendType]:
        self._initialized = await initialize_backends(
            cdp=self.cdp,
            crawl4ai=self.crawl4ai,
            skyvern=self.skyvern,
            stagehand=self.stagehand,
            browserbase=self.browserbase,
            firecrawl=self.firecrawl,
            zai=self.zai,
            config=self.config,
        )
        return self._initialized

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await shutdown_backends()
