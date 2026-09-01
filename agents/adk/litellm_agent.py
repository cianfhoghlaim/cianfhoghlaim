"""Shared LiteLlm-wrapped LlmAgent constructor.

Per the `centralized-model-registry` capability, every ADK agent
constructor in `agents/adk/*.py` uses this helper instead of
`LlmAgent(model=config.model_name)` so the model string is
**explicit** (the LiteLlm wrapper makes the LiteLLM alias routing
visible at agent construction time) and **resolves through the
unified MODEL_REGISTRY** at construction time.

The historical pattern used `LlmAgent(model=config.model_name)`
where `config.model_name` defaulted to `"gemini-2.0-flash"` —
hardcoded, bypassing the Cianfhoghlaim `minimax` 7-tier LiteLLM fallback
alias (the Agent 06 P0-#1 drift finding). As of
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`:

  1. `agents/adk/config.py:AgentConfig.model_name` uses a lazy
     `default_factory` that resolves through MODEL_REGISTRY
     (so the historical `model=config.model_name` pattern still
     resolves through the registry — doesn't break).

  2. **This module** wraps the explicit `LiteLlm(model="minimax")`
     form so the LiteLLM routing is visible at every LlmAgent
     construction site, not hidden inside `config.model_name`.

Per `.agents/skills/google-adk/SKILL.md:407-414`.
"""

from __future__ import annotations

import os
from typing import Any, Type

# Lazy imports — Google ADK and LiteLLM are optional deps at type-check
# time but always available at runtime in the Cianfhoghlaim agent surface.
try:
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm
    _HAS_ADK = True
except ImportError:
    _HAS_ADK = False
    LlmAgent = None  # type: ignore
    LiteLlm = None  # type: ignore


def make_litellm_agent(
    name: str,
    description: str,
    *,
    model_alias: str = "minimax",
    temperature: float = 0.7,
    max_output_tokens: int = 8192,
    **kwargs: Any,
) -> Any:
    """Construct an LlmAgent with the LiteLlm wrapper around the
    Cianfhoghlaim LiteLLM gateway.

    Args:
        name: The agent name (e.g. ``"statistics_agent"``).
        description: The agent's description (used by the routing
            layer).
        model_alias: The LiteLLM alias to route through
            (default ``"minimax"`` — the Cianfhoghlaim 7-tier fallback).
        temperature: Sampling temperature (default 0.7).
        max_output_tokens: Max output tokens (default 8192).
        **kwargs: Additional kwargs forwarded to ``LlmAgent(...)``
            (e.g. ``tools``, ``instruction``, ``input_schema``).

    Returns:
        An ``LlmAgent`` instance with ``model=LiteLlm(model=alias,
        api_base=LITELLM_API_BASE)``.

    Reference:
        openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
    """
    if not _HAS_ADK:
        raise ImportError(
            "google-adk + litellm are required to construct an ADK "
            "agent. Install with `uv add google-adk litellm`."
        )

    api_base = os.getenv("LITELLM_API_BASE", "https://litellm.cianfhoghlaim.ie")
    api_key = os.getenv("LITELLM_API_KEY", "")

    model = LiteLlm(
        model=model_alias,
        api_base=api_base,
        api_key=api_key or "sk-placeholder",  # Locket sidecar injects real key
    )

    return LlmAgent(
        name=name,
        model=model,
        description=description,
        generate_content_config={
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        },
        **kwargs,
    )


def litellm_model(
    model_alias: str = "minimax",
) -> Any:
    """Return a LiteLlm model wrapper around the Cianfhoghlaim LiteLLM gateway.

    Use this when constructing agents manually:

        agent = LlmAgent(
            name="my_agent",
            model=litellm_model("minimax"),
            ...
        )
    """
    if not _HAS_ADK:
        raise ImportError(
            "google-adk + litellm are required. Install with `uv add "
            "google-adk litellm`."
        )
    api_base = os.getenv("LITELLM_API_BASE", "https://litellm.cianfhoghlaim.ie")
    api_key = os.getenv("LITELLM_API_KEY", "")
    return LiteLlm(
        model=model_alias,
        api_base=api_base,
        api_key=api_key or "sk-placeholder",
    )


__all__ = ["make_litellm_agent", "litellm_model"]
