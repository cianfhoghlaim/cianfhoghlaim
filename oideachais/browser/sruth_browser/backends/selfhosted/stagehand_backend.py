"""Stagehand backend for precision browser interactions with local-first + cloud fallback."""

import time
from typing import Any

import httpx
import structlog

from ...config import BrowserConfig, get_config
from ...exceptions import BackendError, BackendTimeoutError
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

# Anti-bot error patterns that trigger cloud fallback
FALLBACK_ERROR_PATTERNS = [
    "cloudflare",
    "captcha",
    "verify",
    "blocked",
    "403",
    "forbidden",
    "rate limit",
    "too many requests",
    "connection refused",
    "econnrefused",
]


class StagehandBackend(BrowserBackend):
    """Stagehand backend for AI-powered browser interactions.

    Features:
    - Local browser first (CDP/Playwright) for $0 cost
    - Automatic Browserbase fallback when anti-bot detected
    - Natural language action execution (observe → act pattern)
    - Intelligent element observation with cached selectors
    - Structured data extraction with LLM
    - Multi-LLM support (GLM-4.6, Gemini 3 Flash)
    """

    backend_type = BackendType.STAGEHAND_LOCAL

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._client: httpx.AsyncClient | None = None
        self._session_id: str | None = None
        self._using_cloud: bool = False
        self._fallback_count: int = 0

    async def initialize(self) -> None:
        """Initialize connection to Stagehand local server."""
        stagehand_url = getattr(self.config, "stagehand_local_url", None) or self.config.stagehand_url
        self._client = httpx.AsyncClient(
            base_url=stagehand_url,
            timeout=httpx.Timeout(self.config.interaction_timeout * 2),
        )

        # Create local session
        try:
            response = await self._client.post(
                "/session/create",
                json={
                    "modelName": getattr(self.config, "stagehand_model", "glm-4.6"),
                    "useCloud": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            self._session_id = data.get("sessionId")
            self._using_cloud = False
            logger.info(
                "stagehand_initialized",
                url=stagehand_url,
                session_id=self._session_id,
                env="LOCAL",
            )
        except Exception as e:
            logger.warning("stagehand_local_init_failed", error=str(e))
            # Try cloud fallback if auto_fallback enabled
            if getattr(self.config, "stagehand_auto_fallback", True):
                await self._fallback_to_cloud()
            else:
                raise BackendError(f"Failed to initialize Stagehand: {e}", self.backend_type)

    def _should_fallback(self, error: Exception | str) -> bool:
        """Determine if error warrants cloud fallback."""
        error_str = str(error).lower()
        return any(pattern in error_str for pattern in FALLBACK_ERROR_PATTERNS)

    async def _fallback_to_cloud(self) -> None:
        """Fallback to Browserbase cloud when local fails."""
        if self._using_cloud:
            return

        logger.info("stagehand_falling_back_to_cloud", session_id=self._session_id)
        self._fallback_count += 1

        # Close local session if exists
        if self._session_id and self._client:
            try:
                await self._client.post(f"/session/{self._session_id}/close")
            except Exception:
                pass

        # Create cloud session
        try:
            response = await self._client.post(
                "/session/create",
                json={
                    "modelName": getattr(self.config, "stagehand_model", "glm-4.6"),
                    "useCloud": True,
                    "browserbaseApiKey": self.config.browserbase_api_key,
                    "browserbaseProjectId": self.config.browserbase_project_id,
                },
            )
            response.raise_for_status()
            data = response.json()
            self._session_id = data.get("sessionId")
            self._using_cloud = True
            logger.info(
                "stagehand_cloud_initialized",
                session_id=self._session_id,
                fallback_count=self._fallback_count,
            )
        except Exception as e:
            raise BackendError(f"Failed to fallback to cloud: {e}", self.backend_type)

    @property
    def is_using_cloud(self) -> bool:
        """Check if currently using cloud backend."""
        return self._using_cloud

    async def close(self) -> None:
        """Close Stagehand connection and session."""
        if self._client and self._session_id:
            try:
                await self._client.post("/session/close")
            except Exception:
                pass
        if self._client:
            await self._client.aclose()
            self._client = None
        self._session_id = None

    async def health_check(self) -> bool:
        """Check Stagehand health."""
        try:
            if not self._client:
                return False
            response = await self._client.get("/health")
            return response.status_code == 200
        except Exception:
            return False

    async def _ensure_session(self) -> str:
        """Ensure we have an active Stagehand session."""
        if not self._client:
            raise BackendError("Stagehand not initialized", self.backend_type)

        if not self._session_id:
            response = await self._client.post("/session/create")
            response.raise_for_status()
            data = response.json()
            self._session_id = data.get("sessionId")
            logger.info("stagehand_session_created", session_id=self._session_id)

        return self._session_id

    async def navigate(
        self,
        url: str,
        *,
        wait_until: str = "load",
        timeout: float | None = None,
    ) -> NavigationResult:
        """Navigate using Stagehand with automatic anti-bot detection and fallback."""
        if not self._client:
            raise BackendError("Stagehand not initialized", self.backend_type)

        await self._ensure_session()
        start_time = time.perf_counter()

        try:
            response = await self._client.post(
                "/navigate",
                json={"sessionId": self._session_id, "url": url},
                timeout=timeout or self.config.navigation_timeout,
            )
            response.raise_for_status()
            data = response.json()

            # Check for anti-bot detection
            if data.get("shouldFallback") and not self._using_cloud:
                logger.info(
                    "stagehand_antibot_on_navigate",
                    url=url,
                    signals=data.get("signals"),
                )
                await self._fallback_to_cloud()
                # Retry with cloud
                return await self.navigate(url, wait_until=wait_until, timeout=timeout)

            latency_ms = (time.perf_counter() - start_time) * 1000

            return NavigationResult(
                success=True,
                url=data.get("url", url),
                title=data.get("title"),
                backend_used=BackendType.BROWSERBASE_MCP if self._using_cloud else self.backend_type,
                latency_ms=latency_ms,
            )

        except httpx.TimeoutException as e:
            raise BackendTimeoutError(
                self.backend_type,
                timeout or self.config.navigation_timeout,
            ) from e

        except Exception as e:
            # Check if we should fallback on error
            if not self._using_cloud and self._should_fallback(e):
                logger.info("stagehand_navigate_fallback", url=url, error=str(e))
                await self._fallback_to_cloud()
                return await self.navigate(url, wait_until=wait_until, timeout=timeout)

            latency_ms = (time.perf_counter() - start_time) * 1000
            return NavigationResult(
                success=False,
                url=url,
                backend_used=BackendType.BROWSERBASE_MCP if self._using_cloud else self.backend_type,
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
        """Extract structured data using Stagehand's extract capability."""
        if not self._client:
            raise BackendError("Stagehand not initialized", self.backend_type)

        await self._ensure_session()
        start_time = time.perf_counter()

        try:
            # Navigate first
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

            # Use Stagehand extract
            extract_payload = {
                "instruction": prompt or "Extract all relevant information from this page",
            }

            response = await self._client.post(
                "/extract",
                json=extract_payload,
                timeout=timeout or self.config.extraction_timeout,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            return ExtractionResult(
                success=True,
                url=url,
                content={"extracted": data},
                format=ExtractionFormat.JSON,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ExtractionResult(
                success=False,
                url=url,
                content={},
                format=ExtractionFormat.JSON,
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
        """Perform interaction using Stagehand's observe → act pattern.

        Stagehand uses natural language instructions rather than selectors.
        The 'action' parameter should be a natural language description.

        If anti-bot measures are detected, automatically falls back to cloud.
        """
        if not self._client:
            raise BackendError("Stagehand not initialized", self.backend_type)

        await self._ensure_session()
        start_time = time.perf_counter()

        try:
            # Build action instruction
            if selector and action in ("click", "fill", "type"):
                # Convert selector-based to natural language
                instruction = f"{action} the element matching '{selector}'"
                if value:
                    instruction += f" with value '{value}'"
            else:
                # Use action as natural language instruction
                instruction = action
                if value:
                    instruction += f": {value}"

            # First observe to find elements (recommended pattern)
            observe_response = await self._client.post(
                "/observe",
                json={"sessionId": self._session_id, "instruction": instruction},
                timeout=timeout or self.config.interaction_timeout,
            )
            observe_data = observe_response.json()

            # Then act on observed element or directly
            if observe_data.get("elements"):
                act_response = await self._client.post(
                    "/act",
                    json={
                        "sessionId": self._session_id,
                        "observedElement": observe_data["elements"][0],
                    },
                    timeout=timeout or self.config.interaction_timeout,
                )
            else:
                act_response = await self._client.post(
                    "/act",
                    json={"sessionId": self._session_id, "action": instruction},
                    timeout=timeout or self.config.interaction_timeout,
                )

            act_response.raise_for_status()
            data = act_response.json()

            # Check for fallback signal from server
            if data.get("shouldFallback") and not self._using_cloud:
                logger.info("stagehand_antibot_detected", signals=data.get("signals"))
                await self._fallback_to_cloud()
                # Retry with cloud
                return await self.interact(action, selector=selector, value=value, timeout=timeout)

            latency_ms = (time.perf_counter() - start_time) * 1000

            return InteractionResult(
                success=data.get("success", True),
                action=action,
                selector=selector,
                backend_used=BackendType.BROWSERBASE_MCP if self._using_cloud else self.backend_type,
                latency_ms=latency_ms,
            )

        except httpx.TimeoutException as e:
            raise BackendTimeoutError(
                self.backend_type,
                timeout or self.config.interaction_timeout,
            ) from e

        except Exception as e:
            # Check if we should fallback on error
            if not self._using_cloud and self._should_fallback(e):
                logger.info("stagehand_error_fallback", error=str(e))
                await self._fallback_to_cloud()
                return await self.interact(action, selector=selector, value=value, timeout=timeout)

            latency_ms = (time.perf_counter() - start_time) * 1000
            return InteractionResult(
                success=False,
                action=action,
                selector=selector,
                backend_used=BackendType.BROWSERBASE_MCP if self._using_cloud else self.backend_type,
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
        """Capture screenshot using Stagehand."""
        if not self._client:
            raise BackendError("Stagehand not initialized", self.backend_type)

        await self._ensure_session()
        start_time = time.perf_counter()

        try:
            if url:
                nav_result = await self.navigate(url, timeout=timeout)
                if not nav_result.success:
                    return ScreenshotResult(
                        success=False,
                        url=url or "",
                        image_data="",
                        width=0,
                        height=0,
                        backend_used=self.backend_type,
                        latency_ms=nav_result.latency_ms,
                        error=nav_result.error,
                    )

            response = await self._client.post(
                "/screenshot",
                json={"fullPage": full_page},
                timeout=timeout or self.config.interaction_timeout,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            return ScreenshotResult(
                success=True,
                url=url or "",
                image_data=data.get("screenshot", ""),
                format="png",
                width=data.get("width", 1920),
                height=data.get("height", 1080),
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

    async def observe(
        self,
        instruction: str,
        *,
        timeout: float | None = None,
    ) -> list[dict[str, Any]]:
        """Observe interactive elements on the page.

        Returns elements that match the instruction with
        their selectors and descriptions.
        """
        if not self._client:
            raise BackendError("Stagehand not initialized", self.backend_type)

        await self._ensure_session()

        try:
            response = await self._client.post(
                "/observe",
                json={"instruction": instruction},
                timeout=timeout or self.config.interaction_timeout,
            )
            response.raise_for_status()
            data = response.json()

            return data.get("elements", [])

        except Exception as e:
            logger.warning("observe_failed", error=str(e))
            return []
