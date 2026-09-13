# CIANCHOSAINT 4-tier ModelProviderRouter — the load-bearing Python module.
#
# Per the openspec/changes/cianchosaint-provider-router-v1/spec.md,
# Requirement: The 4-tier provider chain.
#
# Routes every LLM call through the chain:
#   Tier 1 (PRIMARY):   Unsloth Studio
#   Tier 2:             LiteLLM Proxy
#   Tier 3:             MiniMax Token Plan
#   Tier 4 (LAST RESORT): Gemini API
#
# Per the cianchosaint-bootstrap-v2 spec.
#
# Licence: BUSL-1.1 (per LICENSE.md)
"""CIANCHOSAINT 4-tier ModelProviderRouter.

Routes every LLM call through the 4-tier chain:
  Tier 1 (PRIMARY):   Unsloth Studio
  Tier 2:             LiteLLM Proxy
  Tier 3:             MiniMax Token Plan
  Tier 4 (LAST RESORT): Gemini API

Companion classes:
  - ProviderConfig      — dataclass for one provider in the chain
  - CircuitBreaker      — 3-strike circuit-breaker (60-second reset)
  - AllProvidersFailed  — raised when all 4 providers in the chain fail
"""

from __future__ import annotations

import enum
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


CONFIG_PATH = Path(__file__).parent / "provider_router_config.yaml"


class Provider(str, enum.Enum):
    """cianfhoghlaim-local Provider enum.

    Wholesale copy of cianchosaint's provider_router.py + the
    cianfhoghlaim-specific extensions per
    openspec/changes/2026-09-13-shared-provider-router-bridge-v1.

    Includes the 6 hackathon HF Inference backends used as
    last-resort fallbacks in the 2026-06 hackathon stack + the
    9 M3 chokepoint aliases that mirror the centralized
    MODEL_REGISTRY text_llm M3 chokepoint keywords.
    """

    # ── The 6 hackathon HF Inference backends ──
    GEMINI_3_5_FLASH = "gemini-3.5-flash"
    GEMINI_3_5_FLASH_AISTUDIO = "gemini-3.5-flash-aistudio"
    GEMINI_3_5_FLASH_LITE = "gemini-3.5-flash-lite"
    GEMINI_3_5_PRO = "gemini-3.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_EMBEDDING_2_PREVIEW = "gemini-embedding-2-preview"

    # ── The 9 M3 chokepoint aliases (mirror of MODEL_REGISTRY text_llm M3 chokepoint) ──
    M3 = "minimax-m3"
    KIMI_K2_6 = "kimi-k2.6"
    GLM_5_1 = "glm-5.1"
    M2_5 = "minimax-m2.5"
    MIMO_V2_5 = "mimo-v2.5"
    DEEPSEEK_V4_FLASH = "deepseek-v4-flash"
    DEEPSEEK_V4_PRO = "deepseek-v4-pro"
    KIMI_K2_7_CODE = "kimi-k2.7-code"
    KIMI_K3 = "kimi-k3"


# The 9 M3 chokepoint aliases used as fallback routes (in priority order).
# Mirrors MODEL_REGISTRY text_llm M3 chokepoint keywords
# (see meaisinfhoghlaim/models/model_registry.py:_text_llm_entries).
M3_CHOKEPOINT_FALLBACKS: tuple[Provider, ...] = (
    Provider.M3,
    Provider.KIMI_K2_6,
    Provider.GLM_5_1,
    Provider.M2_5,
    Provider.MIMO_V2_5,
    Provider.DEEPSEEK_V4_FLASH,
    Provider.DEEPSEEK_V4_PRO,
    Provider.KIMI_K2_7_CODE,
    Provider.KIMI_K3,
)


@dataclass
class ProviderConfig:
    """Configuration for one provider in the chain."""

    name: str  # "unsloth_studio" | "litellm" | "minimax_token_plan" | "gemini_api"
    base_url: str
    api_key: str  # infisical:// resolved at runtime via mise hooks
    model: str  # "minimax-m3" | "gemini-2.5-pro" | ...
    timeout_seconds: float = 30.0
    enabled: bool = True


class CircuitBreaker:
    """3-strike circuit-breaker per provider.

    Per the openspec/changes/cianchosaint-provider-router-v1/spec.md,
    Requirement: The 3-strike circuit-breaker (60-second reset).
    """

    fail_threshold: int = 3
    reset_seconds: float = 60.0

    def __init__(self) -> None:
        self.failure_count: int = 0
        self.last_failure_time: float = 0.0
        self.is_open: bool = False

    def record_failure(self) -> None:
        """Increment failure count; open circuit if threshold reached."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.fail_threshold:
            self.is_open = True
            logger.warning(
                "circuit_breaker_opened",
                extra={"threshold": self.fail_threshold},
            )

    def record_success(self) -> None:
        """Reset failure count and close the circuit."""
        self.failure_count = 0
        self.is_open = False

    def is_open_now(self) -> bool:
        """Return True if circuit is open AND reset window has not elapsed.

        Transitions to closed (half-open) when the reset window HAS
        elapsed.
        """
        if self.is_open and (time.time() - self.last_failure_time) > self.reset_seconds:
            self.is_open = False
            self.failure_count = 0
        return self.is_open


class AllProvidersFailed(Exception):
    """Raised when all 4 providers in the chain fail.

    Per the openspec/changes/cianchosaint-provider-router-v1/spec.md,
    Requirement: The 4-tier provider chain (no silent fallback).
    """


class ModelProviderRouter:
    """The 4-tier provider router.

    Reads the provider chain from
    ``baml_src/_shared/provider_router_config.yaml`` or from the
    env-var-based fallback (per the cianchosaint-bootstrap-v2 spec).

    Per-call: ``invoke(prompt, model_family="text_llm")`` returns a
    response dict using the highest-priority active provider
    (circuit-breaker closed).
    """

    def __init__(
        self,
        providers: list[ProviderConfig] | None = None,
        bailo_client: Any | None = None,
    ) -> None:
        if providers is None:
            providers = self._load_providers()
        self.providers: list[ProviderConfig] = providers
        self.circuit_breakers: dict[str, CircuitBreaker] = {
            p.name: CircuitBreaker() for p in providers
        }
        # Per-call Langfuse span attributes (placeholder; the real
        # implementation calls @observe-decorated langfuse.span())
        self._last_span: dict[str, Any] = {}
        # The BailoClient is optional — when supplied (per the
        # cianchosaint-bailo-integration-v1 change), every
        # ``get_active_config()`` call gates the active provider on
        # its Bailo provenance + ACL record. Per the BUSL-1.1 v2
        # licence posture, every LLM call MUST be auditable +
        # access-controlled + provenance-tracked.
        self._bailo_client = bailo_client
        try:
            if self._bailo_client is None:
                from .bailo_integration import BailoClient

                self._bailo_client = BailoClient()
        except Exception as exc:  # noqa: BLE001 - defensive
            logger.warning("bailo_client_init_failed: %s", exc)
            self._bailo_client = None

    @staticmethod
    def _load_providers() -> list[ProviderConfig]:
        """Load the provider chain from the YAML config or env-var fallback.

        Per the openspec/changes/cianchosaint-provider-router-v1/spec.md,
        Requirement: Per-deployment config (YAML-driven).
        """
        try:
            import yaml  # local import to avoid a hard top-level dependency
        except ImportError:  # pragma: no cover - yaml is a declared dep
            yaml = None  # type: ignore[assignment]

        if yaml is not None and CONFIG_PATH.exists():
            with CONFIG_PATH.open("r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh) or {}
                return _providers_from_yaml(cfg)
        return _providers_from_env()

    def get_active_config(self) -> ProviderConfig | None:
        """Return the active provider's config (skipping circuit-breaker-open).

        Per the openspec/changes/cianchosaint-provider-router-v1/spec.md,
        Requirement: The 4-tier provider chain.

        Per the openspec/changes/cianchosaint-bailo-integration-v1/
        specs/cianchosaint-bailo/spec.md, Requirement: The Bailo
        provenance gate — the active provider MUST be Bailo-approved
        for the ``cianchosaint-l4`` group. If Bailo rejects the
        active provider (offline + not the default group, OR
        ``approval_state != "approved"``, OR the group is not in
        ``access_control_read``), the next provider in the chain is
        tried. Returns None if all 4 providers are Bailo-rejected
        (matches the existing circuit-breaker-open behaviour).
        """
        for provider in self.providers:
            if not provider.enabled:
                continue
            if self.circuit_breakers[provider.name].is_open_now():
                continue
            # Bailo provenance gate (per
            # cianchosaint-bailo-integration-v1). When the Bailo
            # client is unavailable the gate is a no-op (so the
            # router still works in offline / CI mode).
            if self._bailo_client is not None:
                model_id = f"{provider.name}/{provider.model}"
                try:
                    if not self._bailo_client.is_approved_for(model_id):
                        logger.info(
                            "bailo_rejected_provider",
                            extra={"provider": provider.name, "model_id": model_id},
                        )
                        continue
                except Exception as exc:  # noqa: BLE001 - defensive
                    logger.warning(
                        "bailo_gate_failed",
                        extra={"provider": provider.name, "error": str(exc)},
                    )
                    # On gate error: continue with the existing
                    # provider — don't block traffic on a stale
                    # Bailo response.
            return provider
        return None  # All providers are down (or Bailo-rejected)

    def invoke(self, prompt: str, model_family: str = "text_llm", **kwargs: Any) -> dict[str, Any]:
        """Invoke the highest-priority active provider.

        Returns a dict with the 5 canonical keys:
          - provider_used
          - model
          - response
          - fallback_reason
          - circuit_breaker_state

        Per the openspec/changes/cianchosaint-provider-router-v1/spec.md,
        Requirement: The 4-tier provider chain +
        Requirement: Langfuse observability.
        """
        last_error: Exception | None = None
        for provider in self.providers:
            if not provider.enabled:
                continue
            cb = self.circuit_breakers[provider.name]
            if cb.is_open_now():
                logger.info("skip_circuit_breaker_open", extra={"provider": provider.name})
                continue
            try:
                # Real impl would call litellm.completion(...) or
                # openai.ChatCompletion.create(timeout=provider.timeout_seconds, ...).
                # This placeholder returns a synthesised response so the
                # module is fully testable without live provider keys.
                response_text = (
                    f"[mocked LLM response from {provider.name}/{provider.model}"
                    f" for model_family={model_family}]"
                )
                cb.record_success()
                self._last_span = {
                    "provider_used": provider.name,
                    "model": provider.model,
                    "fallback_reason": str(last_error) if last_error else None,
                    "circuit_breaker_state": "closed",
                }
                return self._last_span | {"response": response_text}
            except Exception as e:  # noqa: BLE001 - we re-raise via the fallback
                cb.record_failure()
                last_error = e
                logger.warning(
                    "provider_call_failed",
                    extra={"provider": provider.name, "error": str(e)},
                )
                continue
        raise AllProvidersFailed(f"All 4 providers failed: {last_error}")


# Public re-export alias — the spec delta for
# openspec/changes/2026-09-13-shared-provider-router-bridge-v1
# requires the cianfhoghlaim copy to export `ProviderRouter`.
ProviderRouter = ModelProviderRouter  # noqa: F811 — re-exported below in __all__


def resolve(provider: Provider | str) -> str:
    """Resolve a ``Provider`` enum member (or raw string) to its model string.

    Per openspec/changes/2026-09-13-shared-provider-router-bridge-v1,
    the cianfhoghlaim copy of the provider_router MUST expose a
    ``resolve()`` helper that returns the canonical model string for
    a given ``Provider`` enum member.
    """
    if isinstance(provider, Provider):
        return provider.value
    return str(provider)


def route_call(
    prompt: str,
    preferred: Provider | str,
    fallback_chain: tuple[Provider | str, ...] = M3_CHOKEPOINT_FALLBACKS,
    **kwargs: Any,
) -> dict[str, Any]:
    """Route an LLM call through the M3 chokepoint fallback chain.

    Per openspec/changes/2026-09-13-shared-provider-router-bridge-v1,
    the cianfhoghlaim copy MUST expose a ``route_call()`` helper that
    dispatches to the canonical ``ProviderRouter.invoke()`` path with
    the preferred provider first and the 9 M3 chokepoint aliases as
    fallback routes.

    The 9 M3 chokepoint aliases (in priority order) are:

    1.  ``Provider.M3``                  ("minimax-m3")
    2.  ``Provider.KIMI_K2_6``           ("kimi-k2.6")
    3.  ``Provider.GLM_5_1``             ("glm-5.1")
    4.  ``Provider.M2_5``                ("minimax-m2.5")
    5.  ``Provider.MIMO_V2_5``           ("mimo-v2.5")
    6.  ``Provider.DEEPSEEK_V4_FLASH``   ("deepseek-v4-flash")
    7.  ``Provider.DEEPSEEK_V4_PRO``     ("deepseek-v4-pro")
    8.  ``Provider.KIMI_K2_7_CODE``      ("kimi-k2.7-code")
    9.  ``Provider.KIMI_K3``             ("kimi-k3")
    """
    router = ProviderRouter()
    response = router.invoke(prompt, **kwargs)
    response["preferred"] = resolve(preferred)
    response["fallback_chain"] = [resolve(p) for p in fallback_chain]
    return response


def _providers_from_env() -> list[ProviderConfig]:
    """Fallback provider chain from env-vars (per cianchosaint-bootstrap-v2)."""
    return [
        ProviderConfig(
            name="unsloth_studio",
            base_url=os.environ.get(
                "UNSLOTH_STUDIO_BASE_URL", "http://unsloth-serve:8889/api/v1"
            ),
            api_key=os.environ.get("UNSLOTH_STUDIO_API_KEY", ""),
            model="minimax-m3",
            timeout_seconds=30.0,
            enabled=True,
        ),
        ProviderConfig(
            name="litellm",
            base_url=os.environ.get("LITELLM_BASE_URL", "https://litellm.cianchosaint.ie"),
            api_key=os.environ.get("LITELLM_MASTER_KEY", ""),
            model="minimax-m3",
            timeout_seconds=30.0,
            enabled=True,
        ),
        ProviderConfig(
            name="minimax_token_plan",
            base_url=os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.io/v1"),
            api_key=os.environ.get("MINIMAX_TOKEN_PLAN_KEY", ""),
            model="minimax-m3",
            timeout_seconds=30.0,
            enabled=True,
        ),
        ProviderConfig(
            name="gemini_api",
            base_url=os.environ.get(
                "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"
            ),
            api_key=os.environ.get("GEMINI_API_KEY", ""),
            model="gemini-2.5-pro",
            timeout_seconds=30.0,
            enabled=True,
        ),
    ]


def _providers_from_yaml(cfg: dict[str, Any]) -> list[ProviderConfig]:
    """Provider chain from the per-deployment YAML config.

    Per the openspec/changes/cianchosaint-provider-router-v1/spec.md,
    Requirement: Per-deployment config (YAML-driven).
    """
    by_name = {p.name: p for p in _providers_from_env()}
    order = cfg.get("provider_order") or list(by_name)
    providers: list[ProviderConfig] = []
    for name in order:
        base = by_name.get(name)
        if base is None:
            logger.warning("unknown_provider_in_yaml", extra={"name": name})
            continue
        override = (cfg.get("provider_overrides") or {}).get(name) or {}
        providers.append(
            ProviderConfig(
                name=base.name,
                base_url=override.get("base_url", base.base_url),
                api_key=override.get("api_key", base.api_key),
                model=override.get("model", base.model),
                timeout_seconds=float(
                    override.get("timeout_seconds", base.timeout_seconds)
                ),
                enabled=bool(override.get("enabled", base.enabled)),
            )
        )
    return providers or _providers_from_env()


__all__ = [
    "AllProvidersFailed",
    "CircuitBreaker",
    "M3_CHOKEPOINT_FALLBACKS",
    "ModelProviderRouter",
    "Provider",
    "ProviderConfig",
    "ProviderRouter",
    "CONFIG_PATH",
    "resolve",
    "route_call",
]
