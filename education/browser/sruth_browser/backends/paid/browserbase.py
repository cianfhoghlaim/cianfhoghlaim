"""Browserbase MCP backend for cloud browser automation."""

import base64
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


class BrowserbaseBackend(BrowserBackend):
    """Browserbase cloud browser backend via MCP-style API.

    Browserbase provides:
    - Cloud-hosted Chromium instances
    - Stagehand integration for AI-powered automation
    - Session persistence
    - Stealth mode anti-detection
    """

    backend_type = BackendType.BROWSERBASE_MCP

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._client: httpx.AsyncClient | None = None
        self._session_id: str | None = None

    async def initialize(self) -> None:
        """Initialize Browserbase client."""
        if not self.config.browserbase_api_key:
            raise BackendError(
                "Browserbase API key not configured",
                self.backend_type,
                retryable=False,
            )

        self._client = httpx.AsyncClient(
            base_url="https://www.browserbase.com/v1",
            headers={
                "X-BB-API-Key": self.config.browserbase_api_key,
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(self.config.navigation_timeout * 2),
        )

        # Create a session
        await self._create_session()
        logger.info("browserbase_initialized", session_id=self._session_id)

    async def _create_session(self) -> str:
        """Create a new Browserbase session."""
        if not self._client:
            raise BackendError("Browserbase not initialized", self.backend_type)

        try:
            response = await self._client.post(
                "/sessions",
                json={
                    "projectId": self.config.browserbase_project_id,
                },
            )
            response.raise_for_status()
            data = response.json()
            self._session_id = data.get("id")
            return self._session_id

        except Exception as e:
            raise BackendError(
                f"Failed to create Browserbase session: {e}",
                self.backend_type,
            ) from e

    async def close(self) -> None:
        """Close Browserbase session."""
        if self._client and self._session_id:
            try:
                await self._client.post(f"/sessions/{self._session_id}/close")
            except Exception:
                pass
        if self._client:
            await self._client.aclose()
            self._client = None
        self._session_id = None

    async def health_check(self) -> bool:
        """Check Browserbase connectivity."""
        try:
            if not self._client:
                return False
            response = await self._client.get("/sessions")
            return response.status_code == 200
        except Exception:
            return False

    async def navigate(
        self,
        url: str,
        *,
        wait_until: str = "load",
        timeout: float | None = None,
    ) -> NavigationResult:
        """Navigate using Browserbase Stagehand."""
        if not self._client or not self._session_id:
            raise BackendError("Browserbase session not active", self.backend_type)

        start_time = time.perf_counter()

        try:
            response = await self._client.post(
                f"/sessions/{self._session_id}/stagehand/navigate",
                json={"url": url},
                timeout=timeout or self.config.navigation_timeout,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            return NavigationResult(
                success=True,
                url=data.get("url", url),
                title=data.get("title"),
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except httpx.TimeoutException as e:
            raise BackendTimeoutError(
                self.backend_type,
                timeout or self.config.navigation_timeout,
            ) from e

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
        """Extract data using Browserbase Stagehand extract."""
        if not self._client or not self._session_id:
            raise BackendError("Browserbase session not active", self.backend_type)

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

            # Extract
            extract_payload = {
                "instruction": prompt or "Extract all relevant information from this page",
            }

            response = await self._client.post(
                f"/sessions/{self._session_id}/stagehand/extract",
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
        """Perform interaction using Browserbase Stagehand act."""
        if not self._client or not self._session_id:
            raise BackendError("Browserbase session not active", self.backend_type)

        start_time = time.perf_counter()

        try:
            # Build action string
            instruction = action
            if selector:
                instruction = f"{action} on element '{selector}'"
            if value:
                instruction += f" with value '{value}'"

            response = await self._client.post(
                f"/sessions/{self._session_id}/stagehand/act",
                json={"action": instruction},
                timeout=timeout or self.config.interaction_timeout,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            return InteractionResult(
                success=data.get("success", True),
                action=action,
                selector=selector,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
            )

        except httpx.TimeoutException as e:
            raise BackendTimeoutError(
                self.backend_type,
                timeout or self.config.interaction_timeout,
            ) from e

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
        """Capture screenshot using Browserbase."""
        if not self._client or not self._session_id:
            raise BackendError("Browserbase session not active", self.backend_type)

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
                f"/sessions/{self._session_id}/screenshot",
                json={"name": "screenshot", "fullPage": full_page},
                timeout=timeout or self.config.interaction_timeout,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            return ScreenshotResult(
                success=True,
                url=url or "",
                image_data=data.get("base64", ""),
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
        """Observe elements using Browserbase Stagehand."""
        if not self._client or not self._session_id:
            raise BackendError("Browserbase session not active", self.backend_type)

        try:
            response = await self._client.post(
                f"/sessions/{self._session_id}/stagehand/observe",
                json={"instruction": instruction},
                timeout=timeout or self.config.interaction_timeout,
            )
            response.raise_for_status()
            data = response.json()

            return data.get("elements", [])

        except Exception as e:
            logger.warning("browserbase_observe_failed", error=str(e))
            return []
