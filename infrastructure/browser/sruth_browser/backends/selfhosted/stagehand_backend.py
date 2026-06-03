"""Stagehand backend using the official Python SDK.

Architecture:
  Stagehand SEA binary → /v1/responses → stagehand-proxy → /v1/chat/completions → OpenCode Go

The SEA binary inherits OPENAI_BASE_URL from os.environ, pointing to our local proxy
that translates between OpenAI Responses API and Chat Completions format.
"""

import json
import os
import time
import urllib.request
from typing import Any

import structlog

from ...browser_types import (
    BackendType,
    ExtractionFormat,
    ExtractionResult,
    InteractionResult,
    NavigationResult,
    ScreenshotResult,
)
from ...config import BrowserConfig, get_config
from ...exceptions import BackendError
from ..base import BrowserBackend

try:
    from playwright.async_api import async_playwright
    from stagehand import AsyncStagehand
except ImportError:
    pass

logger = structlog.get_logger()

PROXY_DEFAULT_HOST = "127.0.0.1"
PROXY_DEFAULT_PORT = 4005


class StagehandBackend(BrowserBackend):
    """Stagehand backend for AI-powered browser interactions using the official Python SDK.

    Features:
    - Official Stagehand Python SDK integration with local SEA binary
    - CDP connection to Stealth Browser Grid (Patchright)
    - Routes LLM calls through stagehand-proxy for Responses API translation
    - Natural language action execution (observe → act pattern)
    """

    backend_type = BackendType.STAGEHAND_LOCAL

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._client: AsyncStagehand | None = None
        self._session = None
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    async def initialize(self) -> None:
        """Initialize connection to Stealth Grid and Stagehand SDK."""
        cdp_url_env = os.environ.get("BROWSER_CDP_URL", "http://127.0.0.1:9223")
        bb_api_key = os.environ.get("BROWSERBASE_API_KEY", "local")
        model_api_key = os.environ.get("MODEL_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""

        # Point OPENAI_BASE_URL to the stagehand-proxy so the SEA binary routes
        # /v1/responses requests through our proxy which translates them to
        # /v1/chat/completions for OpenCode Go.
        proxy_host = os.environ.get("STAGEHAND_PROXY_HOST", PROXY_DEFAULT_HOST)
        proxy_port = os.environ.get("STAGEHAND_PROXY_PORT", str(PROXY_DEFAULT_PORT))
        proxy_url = f"http://{proxy_host}:{proxy_port}/v1"
        os.environ["OPENAI_BASE_URL"] = proxy_url
        logger.info("stagehand_proxy_configured", proxy_url=proxy_url)

        # Resolve the actual WS URL via the proxy /json/version
        if cdp_url_env.startswith("http://"):
            try:
                version_url = cdp_url_env.rstrip("/") + "/json/version"
                req = urllib.request.Request(version_url)
                with urllib.request.urlopen(req, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                cdp_url = payload.get("webSocketDebuggerUrl")
                if not cdp_url:
                    raise BackendError(
                        "No webSocketDebuggerUrl in /json/version",
                        self.backend_type,
                    )
            except Exception as e:
                raise BackendError(
                    f"Failed to resolve CDP WS URL from {cdp_url_env}: {e}",
                    self.backend_type,
                )
        else:
            cdp_url = cdp_url_env

        # Normalize CDP URL for container networking
        if "0.0.0.0" in cdp_url:
            cdp_url = cdp_url.replace("0.0.0.0", "127.0.0.1")

        # Initialize the official Stagehand client — SEA binary inherits os.environ
        # so it picks up OPENAI_BASE_URL pointing to our proxy.
        self._client = AsyncStagehand(
            server="local",
            browserbase_api_key=bb_api_key,
            model_api_key=model_api_key,
            local_ready_timeout_s=30.0,
        )

        try:
            logger.info("Initializing Stagehand Playwright connection", cdp_url=cdp_url)
            self._playwright = await async_playwright().start()

            if "playwright" in cdp_url:
                self._browser = await self._playwright.chromium.connect(cdp_url)
            else:
                self._browser = await self._playwright.chromium.connect_over_cdp(cdp_url)

            self._context = (
                self._browser.contexts[0]
                if self._browser.contexts
                else await self._browser.new_context()
            )
            self._page = (
                self._context.pages[0]
                if self._context.pages
                else await self._context.new_page()
            )

            # Use openai/ provider — the SEA binary will route through our proxy
            # which translates Responses API → Chat Completions for OpenCode Go.
            model_name = os.environ.get("STAGEHAND_MODEL", "openai/deepseek-v4-pro")

            self._session = await self._client.sessions.start(
                model_name=model_name,
                browser={
                    "type": "local",
                    "launchOptions": {"cdpUrl": cdp_url},
                },
                verbose=1
            )
            logger.info("stagehand_initialized", session_id=self._session.id, model=model_name)

        except Exception as e:
            logger.warning("stagehand_local_init_failed", error=str(e))
            await self.close()
            raise BackendError(f"Failed to initialize Stagehand: {e}", self.backend_type)

    async def close(self) -> None:
        """Close connections."""
        if self._session and self._client:
            try:
                await self._session.end()
            except Exception:
                pass
        self._session = None

        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
        self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
        self._playwright = None

        if self._client:
            self._client = None

    async def health_check(self) -> bool:
        return self._session is not None and self._page is not None

    async def _ensure_session(self) -> None:
        if not self._session or not self._page:
            await self.initialize()

    async def navigate(
        self,
        url: str,
        *,
        wait_until: str = "load",
        timeout: float | None = None,
    ) -> NavigationResult:
        await self._ensure_session()
        start_time = time.perf_counter()

        try:
            # We map playwright wait_until terms
            pw_wait = "domcontentloaded" if wait_until == "domcontentloaded" else "load"
            timeout = (timeout or self.config.navigation_timeout) * 1000
            await self._page.goto(url, wait_until=pw_wait, timeout=timeout)
            latency_ms = (time.perf_counter() - start_time) * 1000

            title = await self._page.title()
            return NavigationResult(
                success=True,
                url=self._page.url,
                title=title,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return NavigationResult(
                success=False,
                url=url,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
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
        await self._ensure_session()
        start_time = time.perf_counter()

        try:
            if self._page.url != url and url:
                nav_result = await self.navigate(url, timeout=timeout)
                if not nav_result.success:
                    return ExtractionResult(
                        success=False,
                        url=url,
                        content={},
                        format=ExtractionFormat.JSON,
                        backend_used=self.backend_type,
                        latency_ms=nav_result.latency_ms,
                        error=nav_result.error,
                    )

            # Build kwargs for stagehand SDK extract
            kwargs = {
                "instruction": prompt or "Extract all relevant information from this page",
                "page": self._page
            }
            if schema:
                kwargs["schema"] = schema

            result = await self._session.extract(**kwargs)
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Stagehand SDK returns a SessionExtractResponse with .data attribute
            # .data contains the structured extraction result
            raw = result
            if hasattr(result, "data"):
                raw = result.data
            # If data is a Data instance, unwrap its result attribute
            if hasattr(raw, "result"):
                raw = raw.result
            # If still a string, try JSON parse
            if isinstance(raw, str):
                try:
                    raw = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    pass

            return ExtractionResult(
                success=True,
                url=self._page.url,
                content={"extracted": raw},
                format=ExtractionFormat.JSON,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ExtractionResult(
                success=False, url=url, content={}, format=ExtractionFormat.JSON,
                backend_used=self.backend_type, latency_ms=latency_ms, error=str(e),
            )

    async def interact(
        self,
        action: str,
        *,
        selector: str | None = None,
        value: str | None = None,
        timeout: float | None = None,
    ) -> InteractionResult:
        await self._ensure_session()
        start_time = time.perf_counter()

        try:
            instruction = action
            if selector and action in ("click", "fill", "type"):
                instruction = f"{action} the element matching '{selector}'"
                if value:
                    instruction += f" with value '{value}'"
            elif value:
                instruction += f": {value}"

            # Execute action using the official SDK
            result = await self._session.act(
                input=instruction,
                page=self._page
            )
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            success = getattr(result, "success", True) if hasattr(result, "success") else True

            return InteractionResult(
                success=success,
                action=action,
                selector=selector,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return InteractionResult(
                success=False, action=action, selector=selector,
                backend_used=self.backend_type, latency_ms=latency_ms, error=str(e),
            )

    async def screenshot(
        self,
        *,
        url: str | None = None,
        full_page: bool = False,
        selector: str | None = None,
        timeout: float | None = None,
    ) -> ScreenshotResult:
        await self._ensure_session()
        start_time = time.perf_counter()

        try:
            if url and self._page.url != url:
                await self.navigate(url, timeout=timeout)

            # Playwright native screenshot
            screenshot_bytes = await self._page.screenshot(full_page=full_page)
            import base64
            b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            # Approximating dimensions for full page
            viewport = self._page.viewport_size
            width = viewport["width"] if viewport else 1920
            height = viewport["height"] if viewport else 1080

            return ScreenshotResult(
                success=True,
                url=self._page.url,
                image_data=b64_img,
                format="png",
                width=width,
                height=height,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ScreenshotResult(
                success=False, url=url or "", image_data="", width=0, height=0,
                backend_used=self.backend_type, latency_ms=latency_ms, error=str(e),
            )

    async def observe(
        self,
        instruction: str,
        *,
        timeout: float | None = None,
    ) -> list[dict[str, Any]]:
        await self._ensure_session()
        try:
            result = await self._session.observe(
                instruction=instruction,
                page=self._page
            )
            # Stagehand observe returns a Data object with .result attribute
            raw = result
            if hasattr(result, "data"):
                raw = result.data
            if hasattr(raw, "result"):
                raw = raw.result
            # Normalize to list of dicts
            if isinstance(raw, str):
                try:
                    parsed = json.loads(raw)
                    return parsed if isinstance(parsed, list) else [parsed]
                except (json.JSONDecodeError, TypeError):
                    return [{"observation": raw}]
            if isinstance(raw, list):
                return raw
            if isinstance(raw, dict):
                return [raw]
            return [{"observation": str(raw)}]
        except Exception as e:
            logger.warning("observe_failed", error=str(e))
            return []

