"""
LLM Router with Fallback Providers.

Routes LLM requests across multiple providers with:
- Circuit breaker for each provider
- Automatic fallback on failure
- Cost-aware routing
- Model capability matching

Based on patterns from sruth/browser/core/llm_router.py (current: meaisinfhoghlaim/process/llm_router.py)
"""

from __future__ import annotations

import logging
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ─── Local-shim CircuitBreaker (replaces the old cianfhoghlaim.core.utils import) ─
# The original lived at `sruth/oideachais/core/utils/circuit_breaker.py:54` (the
# pre-v7 location). Post-v7 the canonical home is the local file; the surface
# needed by `LLMRouter` is minimal (is_open / record_success / record_failure /
# get_status). If a richer implementation is needed later, move it to
# `meaisinfoghlaim/utils/circuit_breaker.py` and update this import.
class CircuitBreaker:
    """Minimal local circuit breaker (the old sruth/oideachais shim)."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_time: float = 60.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self._failures: dict[str, int] = {}
        self._opened_at: dict[str, float] = {}

    def is_open(self, provider_name: str) -> bool:
        opened = self._opened_at.get(provider_name)
        if opened is None:
            return False
        if time.time() - opened >= self.recovery_time:
            # Recovery window elapsed — half-open the circuit
            self._failures[provider_name] = 0
            self._opened_at.pop(provider_name, None)
            return False
        return True

    def record_success(self, provider_name: str) -> None:
        self._failures[provider_name] = 0
        self._opened_at.pop(provider_name, None)

    def record_failure(self, provider_name: str) -> None:
        self._failures[provider_name] = self._failures.get(provider_name, 0) + 1
        if self._failures[provider_name] >= self.failure_threshold:
            self._opened_at[provider_name] = time.time()

    def get_status(self, provider_name: str) -> str:
        return "open" if self.is_open(provider_name) else "closed"


# ─── Local-shim settings (replaces the old cianfhoghlaim.observability.settings_proxy) ─
# The original was a Pydantic Settings proxy injected via Locket. The two
# fields used by `LLMRouter` are local defaults; production overrides come
# from the `MEISIN_CIRCUIT_*` env vars (resolved at process startup).
class _RouterSettings:
    failure_threshold: int = 5
    recovery_time: float = 60.0

    def __init__(self) -> None:
        import os
        self.failure_threshold = int(
            os.environ.get("MEISIN_CIRCUIT_FAILURE_THRESHOLD", "5")
        )
        self.recovery_time = float(
            os.environ.get("MEISIN_CIRCUIT_RECOVERY_TIME", "60.0")
        )

    @property
    def circuit_failure_threshold(self) -> int:
        return self.failure_threshold

    @property
    def circuit_recovery_time(self) -> float:
        return self.recovery_time


settings = _RouterSettings()


class LLMCapability(Enum):
    """Capabilities that LLM providers may support."""
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    IRISH_LANGUAGE = "irish_language"
    MATH = "math"


@dataclass
class LLMProvider:
    """Configuration for an LLM provider."""
    name: str
    api_key_env: str
    base_url: str | None = None
    default_model: str = ""
    capabilities: set[LLMCapability] = field(default_factory=set)
    cost_per_1k_tokens: float = 0.0
    max_tokens: int = 4096
    priority: int = 0  # Higher = preferred
    timeout: float = 60.0

    def has_capability(self, capability: LLMCapability) -> bool:
        """Check if provider has a capability."""
        return capability in self.capabilities


@dataclass
class LLMRequest:
    """Request to an LLM provider."""
    messages: list[dict[str, Any]]
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    required_capabilities: set[LLMCapability] = field(default_factory=set)
    stream: bool = False
    tools: list[dict[str, Any]] | None = None


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    model: str
    provider: str
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    tool_calls: list[dict[str, Any]] | None = None


class LLMRouter:
    """
    Routes LLM requests to available providers with fallback.

    Usage:
        router = LLMRouter([
            LLMProvider(name="anthropic", ...),
            LLMProvider(name="openai", ...),
        ])

        response = await router.complete(LLMRequest(
            messages=[{"role": "user", "content": "Hello"}],
        ))
    """

    def __init__(
        self,
        providers: Sequence[LLMProvider],
        circuit_breaker: CircuitBreaker | None = None,
    ):
        self.providers = list(providers)
        self.circuit_breaker = circuit_breaker or CircuitBreaker(
            failure_threshold=settings.circuit_failure_threshold,
            recovery_time=settings.circuit_recovery_time,
        )

        # Sort by priority (higher first)
        self.providers.sort(key=lambda p: p.priority, reverse=True)

    def _get_available_providers(
        self,
        required_capabilities: set[LLMCapability],
    ) -> list[LLMProvider]:
        """Get providers that have required capabilities and aren't circuit-broken."""
        available = []
        for provider in self.providers:
            # Check capabilities
            if required_capabilities and not all(
                provider.has_capability(cap)
                for cap in required_capabilities
            ):
                continue

            # Check circuit breaker
            if self.circuit_breaker.is_open(provider.name):
                logger.debug(f"Provider {provider.name} circuit is open, skipping")
                continue

            available.append(provider)

        return available

    async def _call_provider(
        self,
        provider: LLMProvider,
        request: LLMRequest,
    ) -> LLMResponse:
        """Make request to a specific provider."""
        import os

        api_key = os.environ.get(provider.api_key_env, "")
        if not api_key:
            raise ValueError(f"API key not found: {provider.api_key_env}")

        model = request.model or provider.default_model

        # Use litellm for unified interface
        try:
            import litellm

            response = await litellm.acompletion(
                model=f"{provider.name}/{model}" if provider.name != "openai" else model,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or provider.max_tokens,
                stream=request.stream,
                api_key=api_key,
                api_base=provider.base_url,
                timeout=provider.timeout,
                tools=request.tools,
            )

            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=model,
                provider=provider.name,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                finish_reason=response.choices[0].finish_reason,
                tool_calls=response.choices[0].message.tool_calls,
            )

        except ImportError:
            # Fallback without litellm
            raise NotImplementedError(
                "LiteLLM not installed. Install with: pip install litellm"
            )

    async def complete(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Route request to available providers with fallback.

        Args:
            request: LLM request

        Returns:
            LLM response

        Raises:
            RuntimeError: If all providers fail
        """
        available = self._get_available_providers(request.required_capabilities)

        if not available:
            raise RuntimeError(
                f"No providers available for capabilities: {request.required_capabilities}"
            )

        errors = []

        for provider in available:
            try:
                logger.debug(f"Trying provider: {provider.name}")
                response = await self._call_provider(provider, request)
                self.circuit_breaker.record_success(provider.name)
                logger.info(f"Request completed by {provider.name}")
                return response

            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                self.circuit_breaker.record_failure(provider.name)
                errors.append((provider.name, e))

        # All providers failed
        error_msg = "; ".join(f"{name}: {e}" for name, e in errors)
        raise RuntimeError(f"All providers failed: {error_msg}")

    def get_status(self) -> dict[str, Any]:
        """Get status of all providers."""
        return {
            provider.name: {
                "capabilities": [c.value for c in provider.capabilities],
                "circuit_status": self.circuit_breaker.get_status(provider.name),
                "priority": provider.priority,
            }
            for provider in self.providers
        }


# ============================================================================
# Pre-configured providers
# ============================================================================


ANTHROPIC_PROVIDER = LLMProvider(
    name="anthropic",
    api_key_env="ANTHROPIC_API_KEY",
    default_model="claude-sonnet-4-20250514",
    capabilities={
        LLMCapability.TEXT_GENERATION,
        LLMCapability.CHAT,
        LLMCapability.VISION,
        LLMCapability.FUNCTION_CALLING,
        LLMCapability.STREAMING,
    },
    cost_per_1k_tokens=0.003,
    max_tokens=4096,
    priority=10,
)


OPENAI_PROVIDER = LLMProvider(
    name="openai",
    api_key_env="OPENAI_API_KEY",
    default_model="gpt-4o",
    capabilities={
        LLMCapability.TEXT_GENERATION,
        LLMCapability.CHAT,
        LLMCapability.VISION,
        LLMCapability.FUNCTION_CALLING,
        LLMCapability.STREAMING,
    },
    cost_per_1k_tokens=0.005,
    max_tokens=4096,
    priority=5,
)


HUGGINGFACE_IRISH_PROVIDER = LLMProvider(
    name="huggingface",
    api_key_env="HF_TOKEN",
    base_url="https://api-inference.huggingface.co/models",
    default_model="UCCIX-Llama2-13B-Instruct",
    capabilities={
        LLMCapability.TEXT_GENERATION,
        LLMCapability.CHAT,
        LLMCapability.IRISH_LANGUAGE,
    },
    cost_per_1k_tokens=0.0,  # Free tier
    max_tokens=2048,
    priority=8,  # High priority for Irish content
)


GEMINI_PROVIDER = LLMProvider(
    name="gemini",
    api_key_env="GOOGLE_API_KEY",
    default_model="gemini-1.5-flash",
    capabilities={
        LLMCapability.TEXT_GENERATION,
        LLMCapability.CHAT,
        LLMCapability.VISION,
        LLMCapability.FUNCTION_CALLING,
        LLMCapability.STREAMING,
    },
    cost_per_1k_tokens=0.001,
    max_tokens=8192,
    priority=3,
)


def get_default_router() -> LLMRouter:
    """Get router with default provider configuration."""
    return LLMRouter([
        ANTHROPIC_PROVIDER,
        HUGGINGFACE_IRISH_PROVIDER,
        OPENAI_PROVIDER,
        GEMINI_PROVIDER,
    ])


def get_irish_router() -> LLMRouter:
    """Get router optimized for Irish language content."""
    return LLMRouter([
        HUGGINGFACE_IRISH_PROVIDER,
        ANTHROPIC_PROVIDER,
        OPENAI_PROVIDER,
    ])
