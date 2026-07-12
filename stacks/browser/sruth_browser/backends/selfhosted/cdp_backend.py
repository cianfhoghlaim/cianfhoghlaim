"""Chrome DevTools Protocol backend using Playwright."""

import base64
import time
from typing import Any

import structlog

from ...config import BrowserConfig, get_config
from ...exceptions import BackendError, BackendTimeoutError, NavigationError
from ...browser_types import (
    BackendType,
    ExtractionFormat,
    ExtractionResult,
    InteractionResult,
    NavigationResult,
    ScreenshotResult,
)
from ..base import BrowserBackend

logger = structlog.get_logger()


class CDPBackend(BrowserBackend):
    """Direct CDP connection to browser-grid via Playwright."""

    backend_type = BackendType.CDP_LOCAL

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._playwright: Any = None
        self._browser: Any = None
        self._context: Any = None
        self._page: Any = None

    async def initialize(self) -> None:
        """Connect to browser-grid via CDP."""
        try:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.connect_over_cdp(
                self.config.cdp_url
            )
            self._context = await self._browser.new_context(
                viewport={"width": 1920, "height": 1080},
            )
            self._page = await self._context.new_page()

            logger.info("cdp_connected", url=self.config.cdp_url)

        except Exception as e:
            raise BackendError(
                f"CDP connection failed: {e}",
                self.backend_type,
                retryable=True,
            ) from e

    async def close(self) -> None:
        """Close CDP connection."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None

    async def health_check(self) -> bool:
        """Check if CDP connection is healthy."""
        try:
            if not self._page:
                return False
            # Try a simple evaluation
            await self._page.evaluate("() => true")
            return True
        except Exception:
            return False

    async def navigate(
        self,
        url: str,
        *,
        wait_until: str = "load",
        timeout: float | None = None,
    ) -> NavigationResult:
        """Navigate to URL using CDP."""
        if not self._page:
            raise BackendError("CDP not initialized", self.backend_type)

        timeout_ms = int((timeout or self.config.navigation_timeout) * 1000)
        start_time = time.perf_counter()

        try:
            response = await self._page.goto(
                url,
                wait_until=wait_until,
                timeout=timeout_ms,
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            return NavigationResult(
                success=True,
                url=self._page.url,
                title=await self._page.title(),
                status_code=response.status if response else None,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            error_msg = str(e)

            if "Timeout" in error_msg:
                raise BackendTimeoutError(
                    self.backend_type,
                    timeout or self.config.navigation_timeout,
                ) from e

            return NavigationResult(
                success=False,
                url=url,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=error_msg,
            )

    async def extract(
        self,
        url: str,
        *,
        formats: list[ExtractionFormat] | None = None,
        schema: dict[str, Any] | None = None,
        prompt: str | None = None,
        timeout: float | None = None,
    ) -> ExtractionResult:
        """Extract content from page using CDP.

        Note: CDP provides raw HTML/text only. For structured extraction
        with LLM, use Crawl4AI or Firecrawl backends.
        """
        if not self._page:
            raise BackendError("CDP not initialized", self.backend_type)

        formats = formats or [ExtractionFormat.HTML]
        start_time = time.perf_counter()

        try:
            # Navigate if needed
            if self._page.url != url:
                await self.navigate(url, timeout=timeout)

            content: dict[str, Any] = {}

            for fmt in formats:
                if fmt == ExtractionFormat.HTML:
                    content["html"] = await self._page.content()
                elif fmt == ExtractionFormat.TEXT:
                    content["text"] = await self._page.evaluate(
                        "() => document.body.innerText"
                    )
                elif fmt == ExtractionFormat.LINKS:
                    content["links"] = await self._page.evaluate("""
                        () => Array.from(document.querySelectorAll('a[href]'))
                            .map(a => ({href: a.href, text: a.innerText.trim()}))
                            .filter(l => l.href.startsWith('http'))
                    """)
                elif fmt == ExtractionFormat.SCREENSHOT:
                    screenshot = await self._page.screenshot(full_page=True)
                    content["screenshot"] = base64.b64encode(screenshot).decode()

            latency_ms = (time.perf_counter() - start_time) * 1000

            return ExtractionResult(
                success=True,
                url=self._page.url,
                content=content,
                format=formats[0],
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ExtractionResult(
                success=False,
                url=url,
                content={},
                format=formats[0] if formats else ExtractionFormat.HTML,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def interact(
        self,
        action: str,
        *,
        selector: str | None = None,
        value: str | None = None,
        timeout: float | None = None,
    ) -> InteractionResult:
        """Perform browser interaction via CDP."""
        if not self._page:
            raise BackendError("CDP not initialized", self.backend_type)

        timeout_ms = int((timeout or self.config.interaction_timeout) * 1000)
        start_time = time.perf_counter()

        try:
            if action == "click" and selector:
                await self._page.click(selector, timeout=timeout_ms)

            elif action == "fill" and selector and value is not None:
                await self._page.fill(selector, value, timeout=timeout_ms)

            elif action == "type" and selector and value is not None:
                await self._page.type(selector, value, timeout=timeout_ms)

            elif action == "scroll":
                if selector:
                    await self._page.evaluate(
                        f"document.querySelector('{selector}').scrollIntoView()"
                    )
                else:
                    await self._page.evaluate(
                        f"window.scrollBy(0, {value or 500})"
                    )

            elif action == "hover" and selector:
                await self._page.hover(selector, timeout=timeout_ms)

            elif action == "press" and value:
                await self._page.keyboard.press(value)

            elif action == "wait":
                if selector:
                    await self._page.wait_for_selector(selector, timeout=timeout_ms)
                elif value:
                    await self._page.wait_for_timeout(int(float(value) * 1000))

            else:
                raise BackendError(
                    f"Unknown action: {action}",
                    self.backend_type,
                    retryable=False,
                )

            latency_ms = (time.perf_counter() - start_time) * 1000

            return InteractionResult(
                success=True,
                action=action,
                selector=selector,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return InteractionResult(
                success=False,
                action=action,
                selector=selector,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def screenshot(
        self,
        *,
        url: str | None = None,
        full_page: bool = False,
        selector: str | None = None,
        timeout: float | None = None,
    ) -> ScreenshotResult:
        """Capture screenshot via CDP."""
        if not self._page:
            raise BackendError("CDP not initialized", self.backend_type)

        start_time = time.perf_counter()

        try:
            if url and self._page.url != url:
                await self.navigate(url, timeout=timeout)

            if selector:
                element = await self._page.query_selector(selector)
                if not element:
                    raise BackendError(
                        f"Selector not found: {selector}",
                        self.backend_type,
                        retryable=False,
                    )
                screenshot_bytes = await element.screenshot()
            else:
                screenshot_bytes = await self._page.screenshot(full_page=full_page)

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Get dimensions
            viewport = self._page.viewport_size
            width = viewport["width"] if viewport else 1920
            height = viewport["height"] if viewport else 1080

            return ScreenshotResult(
                success=True,
                url=self._page.url,
                image_data=base64.b64encode(screenshot_bytes).decode(),
                format="png",
                width=width,
                height=height,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ScreenshotResult(
                success=False,
                url=url or "",
                image_data="",
                width=0,
                height=0,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def click_coordinates(
        self,
        x: int,
        y: int,
        *,
        button: str = "left",
        click_count: int = 1,
        timeout: float | None = None,
    ) -> InteractionResult:
        """Click at specific pixel coordinates.

        This is the key method for visual healing workflow.
        After GLM-4.6v returns coordinates, use this to click.

        Args:
            x: X coordinate in pixels
            y: Y coordinate in pixels
            button: Mouse button (left, right, middle)
            click_count: Number of clicks (1 for single, 2 for double)
            timeout: Optional timeout

        Returns:
            InteractionResult with click details
        """
        if not self._page:
            raise BackendError("CDP not initialized", self.backend_type)

        start_time = time.perf_counter()

        try:
            await self._page.mouse.click(
                x,
                y,
                button=button,
                click_count=click_count,
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "cdp_click_coordinates",
                x=x,
                y=y,
                button=button,
                click_count=click_count,
            )

            return InteractionResult(
                success=True,
                action=f"click_coordinates({x}, {y})",
                selector=None,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return InteractionResult(
                success=False,
                action=f"click_coordinates({x}, {y})",
                selector=None,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def hover_coordinates(
        self,
        x: int,
        y: int,
        *,
        timeout: float | None = None,
    ) -> InteractionResult:
        """Hover at specific pixel coordinates.

        Args:
            x: X coordinate in pixels
            y: Y coordinate in pixels
            timeout: Optional timeout

        Returns:
            InteractionResult with hover details
        """
        if not self._page:
            raise BackendError("CDP not initialized", self.backend_type)

        start_time = time.perf_counter()

        try:
            await self._page.mouse.move(x, y)

            latency_ms = (time.perf_counter() - start_time) * 1000

            return InteractionResult(
                success=True,
                action=f"hover_coordinates({x}, {y})",
                selector=None,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return InteractionResult(
                success=False,
                action=f"hover_coordinates({x}, {y})",
                selector=None,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def save_screenshot(
        self,
        path: str,
        *,
        full_page: bool = False,
    ) -> str:
        """Save screenshot to file for visual healing.

        Args:
            path: File path to save screenshot
            full_page: Whether to capture full page

        Returns:
            Path to saved screenshot
        """
        if not self._page:
            raise BackendError("CDP not initialized", self.backend_type)

        await self._page.screenshot(path=path, full_page=full_page)
        return path

    def get_viewport_size(self) -> dict[str, int]:
        """Get current viewport size.

        Returns:
            Dict with width and height
        """
        if not self._page:
            return {"width": 1920, "height": 1080}

        viewport = self._page.viewport_size
        return viewport or {"width": 1920, "height": 1080}
