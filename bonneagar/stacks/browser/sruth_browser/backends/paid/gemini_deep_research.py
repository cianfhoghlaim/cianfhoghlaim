"""Google Gemini Deep Research API backend for long-form research.

Wraps the agentic Deep Research flow documented at
https://ai.google.dev/gemini-api/docs/deep-research.

The Deep Research API lets a developer submit a long-form research
prompt and receive a structured response with:

- `interactions` — the per-step plan the agent executed (search,
  navigate, extract)
- `synthesized_report` — the final long-form markdown answer
- `citations` — the per-claim source URLs
- `key_findings` — a short bullet list of headline takeaways

The API uses the new `google-genai` SDK (>= 1.0) with the
`interactions` field on `Client.deep_research(...)`.
"""

from __future__ import annotations

import os
import time
from typing import Any, AsyncIterator

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
from ...exceptions import BackendError, BackendTimeoutError
from ..base import ResearchCapableBackend

logger = structlog.get_logger()


class GeminiDeepResearchBackend(ResearchCapableBackend):
    """Gemini Deep Research API backend.

    Provides long-form, multi-source research via Google's
    agentic Deep Research flow. The backend is feature-superior
    to Firecrawl `/agent` for cross-source synthesis because:

    - The agent plans + executes a multi-step research plan
      (search → navigate → extract → cite) in a single API call
    - Each step is exposed as an `interaction` event that can be
      streamed to AG-UI consumers
    - Output includes both `synthesized_report` (long-form markdown)
      and structured `citations` + `key_findings`

    Per the openspec change `2026-09-06-adk-gemini-deep-research-control-plane-v1`,
    this backend is registered as the top-priority `RESEARCH` capability
    in `browser_types.py:182` `BACKEND_PRIORITY`.
    """

    backend_type = BackendType.GEMINI_DEEP_RESEARCH

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._client: Any | None = None

    async def initialize(self) -> None:
        """Initialize the google-genai async client."""
        if not self.config.gemini_api_key:
            raise BackendError(
                "Gemini API key not configured (set BROWSER_GEMINI_API_KEY)",
                self.backend_type,
                retryable=False,
            )

        try:
            from google import genai
        except ImportError as exc:
            raise BackendError(
                "google-genai package not installed. Install with: uv add google-genai",
                self.backend_type,
                retryable=False,
            ) from exc

        self._client = genai.Client(
            api_key=self.config.gemini_api_key,
        )
        logger.info("gemini_deep_research_initialized", model=self.config.gemini_pro_model)

    async def close(self) -> None:
        """Close the genai client."""
        self._client = None

    async def health_check(self) -> bool:
        """Check Gemini API connectivity."""
        if not self._client:
            return False
        try:
            await self._client.aio.models.generate_content(
                model=self.config.gemini_flash_model,
                contents="ping",
            )
        except Exception as exc:
            logger.warning("gemini_deep_research_health_failed", error=str(exc))
            return False
        return True

    async def navigate(
        self,
        url: str,
        *,
        wait_until: str = "load",
        timeout: float | None = None,
    ) -> NavigationResult:
        """Deep Research does not perform direct page navigation.

        Raises ``BackendError``. Use ``research`` instead.
        """
        raise BackendError(
            "GeminiDeepResearchBackend does not support navigate. Use research() instead.",
            self.backend_type,
            retryable=False,
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
        """Extract structured content from a URL by wrapping it in a Deep Research call."""
        if not self._client:
            raise BackendError("Gemini Deep Research not initialized", self.backend_type)

        query = prompt or f"Extract structured content from {url}"
        start_time = time.perf_counter()

        try:
            response = await self.research(query, schema=schema, timeout=timeout)
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ExtractionResult(
                success=response.get("success", False),
                url=url,
                content=response,
                format=formats[0] if formats else ExtractionFormat.MARKDOWN,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=response.get("error"),
            )
        except BackendError:
            raise
        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ExtractionResult(
                success=False,
                url=url,
                content={},
                format=formats[0] if formats else ExtractionFormat.MARKDOWN,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(exc),
            )

    async def interact(
        self,
        action: str,
        *,
        selector: str | None = None,
        value: str | None = None,
        timeout: float | None = None,
    ) -> InteractionResult:
        """Deep Research does not perform interactive operations."""
        raise BackendError(
            "GeminiDeepResearchBackend does not support interact. Use a browser backend.",
            self.backend_type,
            retryable=False,
        )

    async def screenshot(
        self,
        *,
        url: str | None = None,
        full_page: bool = False,
        selector: str | None = None,
        timeout: float | None = None,
    ) -> ScreenshotResult:
        """Deep Research does not perform screenshots."""
        raise BackendError(
            "GeminiDeepResearchBackend does not support screenshot. Use a browser backend.",
            self.backend_type,
            retryable=False,
        )

    async def research(
        self,
        query: str,
        *,
        max_urls: int = 15,
        schema: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Perform long-form Deep Research.

        Returns a dict with:

        - ``success`` (bool)
        - ``synthesized_report`` (str) — long-form markdown
        - ``interactions`` (list[dict]) — per-step plan events
        - ``citations`` (list[dict]) — per-claim source URLs
        - ``key_findings`` (list[str]) — short bullet takeaways
        - ``urls_visited`` (int)
        - ``tokens_used`` (int | None)
        - ``error`` (str | None)
        """
        if not self._client:
            raise BackendError("Gemini Deep Research not initialized", self.backend_type)

        start_time = time.perf_counter()
        timeout_s = timeout or self.config.extraction_timeout
        model = os.getenv("BROWSER_GEMINI_DEEP_RESEARCH_MODEL", "gemini-2.5-pro-deep-research")

        try:
            interactions: list[dict[str, Any]] = []
            response = await self._client.aio.deep_research(
                model=model,
                query=query,
                max_urls=max_urls,
                output_schema=schema,
                stream=True,
            )

            synthesized_chunks: list[str] = []
            citations: list[dict[str, Any]] = []
            key_findings: list[str] = []
            urls_visited = 0

            async for event in response:
                kind = getattr(event, "kind", None)
                if kind == "interaction":
                    interactions.append({
                        "interaction_id": getattr(event, "interaction_id", None),
                        "action": getattr(event, "action", None),
                        "target": getattr(event, "target", None),
                        "rationale": getattr(event, "rationale", None),
                    })
                elif kind == "url_visited":
                    urls_visited += 1
                elif kind == "content_chunk":
                    synthesized_chunks.append(getattr(event, "text", ""))
                elif kind == "citation":
                    citations.append({
                        "url": getattr(event, "url", None),
                        "title": getattr(event, "title", None),
                        "claim": getattr(event, "claim", None),
                    })
                elif kind == "key_finding":
                    key_findings.append(getattr(event, "text", ""))
                elif kind == "error":
                    raise BackendError(
                        f"Gemini Deep Research error: {getattr(event, 'message', 'unknown')}",
                        self.backend_type,
                        retryable=True,
                    )

            synthesized_report = "".join(synthesized_chunks)
            latency_ms = (time.perf_counter() - start_time) * 1000

            return {
                "success": True,
                "query": query,
                "synthesized_report": synthesized_report,
                "interactions": interactions,
                "citations": citations,
                "key_findings": key_findings,
                "urls_visited": urls_visited,
                "tokens_used": getattr(response, "usage_metadata", None) and getattr(
                    response.usage_metadata, "total_token_count", None
                ),
                "backend_used": self.backend_type,
                "latency_ms": latency_ms,
                "model": model,
                "error": None,
            }

        except BackendError:
            raise
        except TimeoutError as exc:
            raise BackendTimeoutError(
                f"Gemini Deep Research timed out after {timeout_s}s",
                self.backend_type,
                retryable=True,
            ) from exc
        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "gemini_deep_research_failed",
                query=query[:100],
                error=str(exc),
                latency_ms=latency_ms,
            )
            return {
                "success": False,
                "query": query,
                "synthesized_report": "",
                "interactions": [],
                "citations": [],
                "key_findings": [],
                "urls_visited": 0,
                "tokens_used": None,
                "backend_used": self.backend_type,
                "latency_ms": latency_ms,
                "model": model,
                "error": str(exc),
            }

    async def stream_interactions(
        self,
        query: str,
        *,
        max_urls: int = 15,
        timeout: float | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Yield Deep Research interaction events as they happen.

        Used by the AG-UI adapter to stream Deep Research progress
        to CopilotKit consumers.
        """
        if not self._client:
            raise BackendError("Gemini Deep Research not initialized", self.backend_type)

        model = os.getenv("BROWSER_GEMINI_DEEP_RESEARCH_MODEL", "gemini-2.5-pro-deep-research")

        response = await self._client.aio.deep_research(
            model=model,
            query=query,
            max_urls=max_urls,
            stream=True,
        )

        async for event in response:
            kind = getattr(event, "kind", None)
            yield {
                "kind": kind,
                "interaction_id": getattr(event, "interaction_id", None),
                "action": getattr(event, "action", None),
                "target": getattr(event, "target", None),
                "rationale": getattr(event, "rationale", None),
                "text": getattr(event, "text", None),
                "url": getattr(event, "url", None),
                "title": getattr(event, "title", None),
                "claim": getattr(event, "claim", None),
                "message": getattr(event, "message", None),
            }
