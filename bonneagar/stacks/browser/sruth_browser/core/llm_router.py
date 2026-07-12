"""Multi-provider LLM router with fallback support."""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import httpx
import structlog

from ..config import BrowserConfig, get_config
from ..exceptions import BackendError

logger = structlog.get_logger()


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    GLM_4_6V = "glm-4.6v"
    GEMINI_FLASH = "gemini-2.0-flash"
    GEMINI_PRO = "gemini-2.0-pro"
    OPENAI_GPT4O = "openai/gpt-4o"
    OPENAI_GPT4O_MINI = "openai/gpt-4o-mini"
    ANTHROPIC_CLAUDE = "anthropic/claude-3-5-sonnet"


@dataclass
class ProviderHealth:
    """Health status for an LLM provider."""

    provider: LLMProvider
    is_available: bool = True
    failure_count: int = 0
    last_failure: datetime | None = None
    last_success: datetime | None = None
    avg_latency_ms: float = 0.0
    circuit_open_until: datetime | None = None

    def record_success(self, latency_ms: float) -> None:
        """Record a successful request."""
        self.is_available = True
        self.failure_count = 0
        self.last_success = datetime.utcnow()
        self.circuit_open_until = None
        self.avg_latency_ms = (self.avg_latency_ms * 0.9) + (latency_ms * 0.1)

    def record_failure(self, recovery_timeout: float = 30.0) -> None:
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure = datetime.utcnow()

        if self.failure_count >= 3:
            self.is_available = False
            self.circuit_open_until = datetime.utcnow() + timedelta(seconds=recovery_timeout)

    def check_recovery(self) -> None:
        """Check if circuit should close."""
        if self.circuit_open_until and datetime.utcnow() > self.circuit_open_until:
            self.is_available = True
            self.failure_count = 0
            self.circuit_open_until = None


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    success: bool
    content: str
    provider: LLMProvider
    model: str
    latency_ms: float
    tokens_used: int | None = None
    error: str | None = None
    raw_response: dict[str, Any] | None = None


class LLMRouter:
    """Multi-provider LLM router with automatic fallback.

    Routes requests through available providers in priority order:
    1. GLM-4.6v (Z.AI) - Best for vision tasks
    2. Gemini Flash - Fast, cost-effective
    3. OpenAI GPT-4o - Reliable fallback

    Features:
    - Circuit breaker pattern (3 failures = circuit open)
    - Automatic recovery after timeout
    - Latency-based provider selection
    - Provider-specific optimizations
    """

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._clients: dict[LLMProvider, httpx.AsyncClient] = {}
        self._health: dict[LLMProvider, ProviderHealth] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize available LLM clients."""
        # Z.AI / GLM-4.6v
        if self.config.zai_api_key:
            self._clients[LLMProvider.GLM_4_6V] = httpx.AsyncClient(
                base_url=self.config.zai_base_url,
                headers={
                    "Authorization": f"Bearer {self.config.zai_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(60.0),
            )
            self._health[LLMProvider.GLM_4_6V] = ProviderHealth(LLMProvider.GLM_4_6V)

        # Gemini
        if self.config.gemini_api_key:
            self._clients[LLMProvider.GEMINI_FLASH] = httpx.AsyncClient(
                base_url="https://generativelanguage.googleapis.com/v1beta",
                headers={"Content-Type": "application/json"},
                timeout=httpx.Timeout(60.0),
            )
            self._health[LLMProvider.GEMINI_FLASH] = ProviderHealth(LLMProvider.GEMINI_FLASH)

            self._clients[LLMProvider.GEMINI_PRO] = self._clients[LLMProvider.GEMINI_FLASH]
            self._health[LLMProvider.GEMINI_PRO] = ProviderHealth(LLMProvider.GEMINI_PRO)

        # OpenAI
        if self.config.openai_api_key:
            self._clients[LLMProvider.OPENAI_GPT4O] = httpx.AsyncClient(
                base_url="https://api.openai.com/v1",
                headers={
                    "Authorization": f"Bearer {self.config.openai_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(60.0),
            )
            self._health[LLMProvider.OPENAI_GPT4O] = ProviderHealth(LLMProvider.OPENAI_GPT4O)

        # Anthropic
        if self.config.anthropic_api_key:
            self._clients[LLMProvider.ANTHROPIC_CLAUDE] = httpx.AsyncClient(
                base_url="https://api.anthropic.com/v1",
                headers={
                    "x-api-key": self.config.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(60.0),
            )
            self._health[LLMProvider.ANTHROPIC_CLAUDE] = ProviderHealth(
                LLMProvider.ANTHROPIC_CLAUDE
            )

        self._initialized = True
        logger.info("llm_router_initialized", providers=list(self._clients.keys()))

    async def close(self) -> None:
        """Close all LLM clients."""
        closed = set()
        for provider, client in self._clients.items():
            if client not in closed:
                await client.aclose()
                closed.add(client)
        self._clients.clear()
        self._health.clear()
        self._initialized = False

    def _get_provider_order(self, prefer_vision: bool = False) -> list[LLMProvider]:
        """Get provider order based on config and availability."""
        order = []

        for provider_str in self.config.llm_fallback_order:
            try:
                provider = LLMProvider(provider_str)
                if provider in self._clients:
                    health = self._health.get(provider)
                    if health:
                        health.check_recovery()
                        if health.is_available:
                            order.append(provider)
            except ValueError:
                continue

        for provider in self._clients:
            if provider not in order:
                health = self._health.get(provider)
                if health:
                    health.check_recovery()
                    if health.is_available:
                        order.append(provider)

        if prefer_vision and LLMProvider.GLM_4_6V in order:
            order.remove(LLMProvider.GLM_4_6V)
            order.insert(0, LLMProvider.GLM_4_6V)

        return order

    async def _call_glm(
        self,
        messages: list[dict[str, Any]],
        model: str,
        **kwargs,
    ) -> LLMResponse:
        """Call Z.AI GLM API."""
        client = self._clients.get(LLMProvider.GLM_4_6V)
        if not client:
            raise BackendError("GLM client not initialized")

        start_time = time.perf_counter()

        payload = {
            "model": model,
            "messages": messages,
            **kwargs,
        }

        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        latency_ms = (time.perf_counter() - start_time) * 1000

        return LLMResponse(
            success=True,
            content=data["choices"][0]["message"]["content"],
            provider=LLMProvider.GLM_4_6V,
            model=model,
            latency_ms=latency_ms,
            tokens_used=data.get("usage", {}).get("total_tokens"),
            raw_response=data,
        )

    async def _call_gemini(
        self,
        messages: list[dict[str, Any]],
        model: str,
        **kwargs,
    ) -> LLMResponse:
        """Call Google Gemini API."""
        client = self._clients.get(LLMProvider.GEMINI_FLASH)
        if not client:
            raise BackendError("Gemini client not initialized")

        start_time = time.perf_counter()

        gemini_contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            content = msg.get("content", "")

            if isinstance(content, str):
                gemini_contents.append({"role": role, "parts": [{"text": content}]})
            elif isinstance(content, list):
                parts = []
                for part in content:
                    if part.get("type") == "text":
                        parts.append({"text": part["text"]})
                    elif part.get("type") == "image_url":
                        image_url = part["image_url"]["url"]
                        if image_url.startswith("data:"):
                            mime_type, base64_data = image_url.split(";base64,")
                            mime_type = mime_type.replace("data:", "")
                            parts.append({
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": base64_data,
                                }
                            })
                        else:
                            parts.append({"text": f"[Image: {image_url}]"})
                gemini_contents.append({"role": role, "parts": parts})

        payload = {
            "contents": gemini_contents,
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.7),
            },
        }

        thinking_level = kwargs.get("thinking_level")
        if thinking_level == "high":
            payload["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 8192}

        endpoint = f"/models/{model}:generateContent?key={self.config.gemini_api_key}"
        response = await client.post(endpoint, json=payload)
        response.raise_for_status()
        data = response.json()

        latency_ms = (time.perf_counter() - start_time) * 1000

        content = ""
        if "candidates" in data and data["candidates"]:
            parts = data["candidates"][0].get("content", {}).get("parts", [])
            content = " ".join(p.get("text", "") for p in parts if "text" in p)

        return LLMResponse(
            success=True,
            content=content,
            provider=LLMProvider.GEMINI_FLASH if "flash" in model else LLMProvider.GEMINI_PRO,
            model=model,
            latency_ms=latency_ms,
            tokens_used=data.get("usageMetadata", {}).get("totalTokenCount"),
            raw_response=data,
        )

    async def _call_openai(
        self,
        messages: list[dict[str, Any]],
        model: str,
        **kwargs,
    ) -> LLMResponse:
        """Call OpenAI API."""
        client = self._clients.get(LLMProvider.OPENAI_GPT4O)
        if not client:
            raise BackendError("OpenAI client not initialized")

        start_time = time.perf_counter()

        model_name = model.replace("openai/", "")

        payload = {
            "model": model_name,
            "messages": messages,
            **{k: v for k, v in kwargs.items() if k in ["max_tokens", "temperature", "tools"]},
        }

        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        latency_ms = (time.perf_counter() - start_time) * 1000

        return LLMResponse(
            success=True,
            content=data["choices"][0]["message"]["content"] or "",
            provider=LLMProvider.OPENAI_GPT4O,
            model=model_name,
            latency_ms=latency_ms,
            tokens_used=data.get("usage", {}).get("total_tokens"),
            raw_response=data,
        )

    async def _call_anthropic(
        self,
        messages: list[dict[str, Any]],
        model: str,
        **kwargs,
    ) -> LLMResponse:
        """Call Anthropic API."""
        client = self._clients.get(LLMProvider.ANTHROPIC_CLAUDE)
        if not client:
            raise BackendError("Anthropic client not initialized")

        start_time = time.perf_counter()

        model_name = model.replace("anthropic/", "")

        system_msg = None
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg.get("content", "")
            else:
                anthropic_messages.append(msg)

        payload = {
            "model": model_name,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
        }
        if system_msg:
            payload["system"] = system_msg

        response = await client.post("/messages", json=payload)
        response.raise_for_status()
        data = response.json()

        latency_ms = (time.perf_counter() - start_time) * 1000

        content = ""
        if data.get("content"):
            content = " ".join(
                block.get("text", "") for block in data["content"] if block.get("type") == "text"
            )

        return LLMResponse(
            success=True,
            content=content,
            provider=LLMProvider.ANTHROPIC_CLAUDE,
            model=model_name,
            latency_ms=latency_ms,
            tokens_used=data.get("usage", {}).get("input_tokens", 0)
            + data.get("usage", {}).get("output_tokens", 0),
            raw_response=data,
        )

    async def _call_provider(
        self,
        provider: LLMProvider,
        messages: list[dict[str, Any]],
        **kwargs,
    ) -> LLMResponse:
        """Call a specific provider."""
        if provider == LLMProvider.GLM_4_6V:
            model = kwargs.pop("model", self.config.zai_glm_model)
            return await self._call_glm(messages, model, **kwargs)

        elif provider in (LLMProvider.GEMINI_FLASH, LLMProvider.GEMINI_PRO):
            if provider == LLMProvider.GEMINI_FLASH:
                model = kwargs.pop("model", self.config.gemini_flash_model)
            else:
                model = kwargs.pop("model", self.config.gemini_pro_model)
            return await self._call_gemini(messages, model, **kwargs)

        elif provider == LLMProvider.OPENAI_GPT4O:
            model = kwargs.pop("model", "gpt-4o")
            return await self._call_openai(messages, model, **kwargs)

        elif provider == LLMProvider.ANTHROPIC_CLAUDE:
            model = kwargs.pop("model", "claude-3-5-sonnet-20241022")
            return await self._call_anthropic(messages, model, **kwargs)

        else:
            raise BackendError(f"Unknown provider: {provider}")

    async def complete(
        self,
        messages: list[dict[str, Any]],
        prefer_vision: bool = False,
        **kwargs,
    ) -> LLMResponse:
        """Complete a chat request with automatic fallback.

        Args:
            messages: Chat messages in OpenAI format
            prefer_vision: Prefer vision-capable models (GLM-4.6v)
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Returns:
            LLMResponse from the first successful provider
        """
        if not self._initialized:
            await self.initialize()

        provider_order = self._get_provider_order(prefer_vision=prefer_vision)

        if not provider_order:
            raise BackendError("No LLM providers available")

        last_error = None
        for provider in provider_order:
            try:
                logger.debug("llm_trying_provider", provider=provider.value)
                response = await self._call_provider(provider, messages, **kwargs)

                if response.success:
                    self._health[provider].record_success(response.latency_ms)
                    logger.info(
                        "llm_request_success",
                        provider=provider.value,
                        latency_ms=response.latency_ms,
                    )
                    return response

            except Exception as e:
                last_error = str(e)
                self._health[provider].record_failure(self.config.circuit_recovery_timeout)
                logger.warning(
                    "llm_provider_failed",
                    provider=provider.value,
                    error=last_error,
                )
                continue

        return LLMResponse(
            success=False,
            content="",
            provider=provider_order[0] if provider_order else LLMProvider.OPENAI_GPT4O,
            model="",
            latency_ms=0,
            error=f"All providers failed. Last error: {last_error}",
        )

    async def complete_with_vision(
        self,
        prompt: str,
        images: list[str],
        **kwargs,
    ) -> LLMResponse:
        """Complete a vision request with images.

        Args:
            prompt: Text prompt
            images: List of image URLs or base64 data URLs
            **kwargs: Additional parameters

        Returns:
            LLMResponse from vision-capable provider
        """
        content = []
        for image in images:
            content.append({"type": "image_url", "image_url": {"url": image}})
        content.append({"type": "text", "text": prompt})

        messages = [{"role": "user", "content": content}]

        return await self.complete(messages, prefer_vision=True, **kwargs)


_router: LLMRouter | None = None


async def get_llm_router() -> LLMRouter:
    """Get or create the LLM router singleton."""
    global _router
    if _router is None:
        _router = LLMRouter()
        await _router.initialize()
    return _router
