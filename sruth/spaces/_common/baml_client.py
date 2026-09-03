"""
spaces/_common/baml_client.py
KCG LiteLLM gateway wrapper for the 4 Spaces.

This module is the thin shim that replaces the hand-rolled 3-tier
HF Inference fallback chain. The Spaces still call
`chat_complete_json(messages=...)` for the schema-less codepath,
but the HTTP call now goes through the canonical LiteLLM gateway
(`http://litellm:4000/v1`) instead of raw `api-inference.huggingface.co`.

Why this change:
- Single endpoint: all Spaces route through the same proxy
- LLM observability: Langfuse auto-traces every LiteLLM call
- Cost tracking: per-model cost lines in Langfuse
- The canonical fallback chain (litellm/minimax, litellm/sonnet, etc.)
  is configured in `oideachais/foinse/litellm_config.yaml`

The hand-rolled chain (Qwen 7B -> Llama 8B -> Gemma 9b) is KEPT as
a per-Space fallback if the LiteLLM gateway is unreachable (so the
Spaces still work in offline / dev mode). The 3-tier chain is
preserved verbatim in `_HF_FALLBACK_CHAIN`.

For the canonical BAML extractions, use the 4 promoted functions
from sruth.oideachais + tuatha directly:
  - ExtractCircularMeta (oideachais/baml_src/circular_extraction.baml)
  - CompareCelticNations (tuatha/baml_src/celtic_curriculum.baml)
  - GenerateExitCardQuestions (tuatha/baml_src/player_assessment.baml)
  - GenerateNpcDialogue (tuatha/baml_src/mythology_extraction.baml)

These 4 give you schema validation + retries + Langfuse tracing
for free (see the canonical baml_src/clients.baml LitellmClient).
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Final

import urllib.error
import urllib.request


_log = logging.getLogger("baml_client")


# Canonical LiteLLM gateway (the KCG-default LLM endpoint).
# Mirrors oideachais/baml_src/clients.baml's LitellmClient.
LITELLM_BASE_URL: Final[str] = os.environ.get(
    "LITELLM_BASE_URL", "http://litellm:4000/v1"
)
# Default model: minimax-m3 (the KCG-canonical open-source model,
# aliased through LiteLLM). Override via the LITELLM_MODEL env var.
DEFAULT_MODEL: Final[str] = os.environ.get("LITELLM_MODEL", "minimax")
# Master key for the LiteLLM gateway. In production, this comes from
# the Infisical dev-baile vault via the Locket sidecar. In dev / HF
# Spaces, it can be set via the HF Space secrets.
LITELLM_MASTER_KEY: Final[str] = os.environ.get(
    "LITELLM_MASTER_KEY", os.environ.get("LITELLM_API_KEY", "")
)


# Hand-rolled HF Inference fallback chain (preserved verbatim from
# the 2026-06 hackathon). Used only when the LiteLLM gateway is
# unreachable. In the KCG production stack, the LiteLLM gateway
# always wins.
#
# The 3 chain entries are now resolved via MODEL_REGISTRY (the
# centralized-model-registry openspec change). They are explicitly
# marked as the "text_llm" family with the roles ``hackathon_primary``,
# ``hackathon_fallback_1`` and ``hackathon_fallback_2`` respectively.
# If MODEL_REGISTRY is unavailable (e.g. minimal container builds),
# the historical hardcoded HF IDs are preserved as the fallback
# string.
def _hackathon_model(role: str, fallback: str) -> str:
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY
        return MODEL_REGISTRY.resolve("text_llm", role)
    except Exception:  # noqa: BLE001 — registry unavailable in dev
        return fallback


HACKATHON_PRIMARY_MODEL: Final[str] = _hackathon_model(
    "hackathon_primary", "Qwen/Qwen2.5-7B-Instruct"
)
HACKATHON_FALLBACK_1_MODEL: Final[str] = _hackathon_model(
    "hackathon_fallback_1", "meta-llama/Llama-3.1-8B-Instruct"
)
HACKATHON_FALLBACK_2_MODEL: Final[str] = _hackathon_model(
    "hackathon_fallback_2", "google/gemma-2-9b-it"
)

HF_INFERENCE_BASE_URL: Final[str] = (
    os.environ.get("HF_INFERENCE_URL")
    or "https://api-inference.huggingface.co"
)
_OPENAI_CHAT_PATH: Final[str] = "/v1/chat/completions"

_HF_FALLBACK_CHAIN: Final[tuple[str, ...]] = (
    HACKATHON_PRIMARY_MODEL,
    HACKATHON_FALLBACK_1_MODEL,
    HACKATHON_FALLBACK_2_MODEL,
)


def get_hackathon_client_config() -> dict[str, Any]:
    """Return the resolved client config (for logging + UI display)."""
    return {
        "litellm": {
            "base_url": LITELLM_BASE_URL,
            "model": DEFAULT_MODEL,
            "master_key_set": bool(LITELLM_MASTER_KEY),
        },
        "fallback_chain": list(_HF_FALLBACK_CHAIN),
        "hf_token_set": bool(os.environ.get("HF_TOKEN")),
    }


def _build_payload(
    messages: list[dict[str, str]],
    model: str,
    max_tokens: int = 4096,
    temperature: float = 0.1,
    response_format_json: bool = True,
) -> dict[str, Any]:
    """Build the OpenAI-compatible request body."""
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if response_format_json:
        payload["response_format"] = {"type": "json_object"}
    return payload


def _post_json(url: str, payload: dict[str, Any], token: str, timeout: int) -> dict[str, Any]:
    """POST a JSON payload and return the parsed response."""
    headers: dict[str, str] = {
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def _extract_message(payload: dict[str, Any]) -> str:
    """Extract the assistant message text from a chat-completions response."""
    try:
        return str(payload["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(
            f"Malformed chat-completion response: {e}"
        ) from e


def _try_litellm(
    messages: list[dict[str, str]],
    *,
    max_tokens: int,
    temperature: float,
    timeout: int,
) -> tuple[str, str] | None:
    """Try the LiteLLM gateway. Return (text, model) on success, None on failure."""
    if not LITELLM_MASTER_KEY and not os.environ.get("LITELLM_API_KEY"):
        _log.info("LiteLLM key not set; skipping LiteLLM gateway")
        return None
    url = LITELLM_BASE_URL.rstrip("/") + _OPENAI_CHAT_PATH
    payload = _build_payload(messages, DEFAULT_MODEL, max_tokens, temperature)
    try:
        start = time.time()
        resp = _post_json(url, payload, LITELLM_MASTER_KEY, timeout)
        elapsed = time.time() - start
        _log.info(
            "LiteLLM OK: %s (%.2fs)", DEFAULT_MODEL, elapsed,
        )
        return _extract_message(resp), DEFAULT_MODEL
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        _log.warning("LiteLLM gateway failed: %s; falling back to HF", e)
        return None


def chat_complete(
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 4096,
    temperature: float = 0.1,
    timeout: int = 60,
    max_model_retries: int = 1,
) -> tuple[str, str]:
    """Call the canonical LLM with the 2-tier fallback chain.

    Tier 1: the KCG LiteLLM gateway (LitellmClient in oideachais/baml_src/clients.baml).
            Routes through Langfuse for cost + latency tracking.

    Tier 2: the 2026-06 hackathon HF Inference 3-model fallback chain
            (Qwen 7B -> Llama 8B -> Gemma 9b). Used when the LiteLLM
            gateway is unreachable (offline / dev / HF Space free tier).

    Args:
        messages: A list of {"role": ..., "content": ...} dicts in
            OpenAI chat-completions format.
        max_tokens: Max tokens in the response.
        temperature: Sampling temperature (0.0 - 1.0).
        timeout: Per-call timeout in seconds.
        max_model_retries: Number of times to retry the same model on
            transient failures (timeout, 5xx, 429) before falling back.

    Returns:
        (content, model_used) - the assistant's text and the name of
        the model that ultimately produced it.

    Raises:
        RuntimeError: If both tiers fail.
    """
    litellm_result = _try_litellm(
        messages,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout=timeout,
    )
    if litellm_result is not None:
        return litellm_result

    # Fall back to the HF Inference 3-tier chain (hackathon-preserved).
    if not os.environ.get("HF_TOKEN"):
        raise RuntimeError(
            "All LLM calls failed. LiteLLM gateway unreachable AND "
            "HF_TOKEN not set for the HF Inference fallback chain. "
            "Set HF_TOKEN in your HF Space secrets to enable the fallback."
        )

    url = HF_INFERENCE_BASE_URL.rstrip("/") + _OPENAI_CHAT_PATH
    last_err: Exception | None = None
    for model in _HF_FALLBACK_CHAIN:
        for attempt in range(max_model_retries + 1):
            try:
                payload = _build_payload(
                    messages, model, max_tokens, temperature,
                    response_format_json=False,  # HF Inference doesn't support json_object
                )
                start = time.time()
                resp = _post_json(url, payload, os.environ["HF_TOKEN"], timeout)
                elapsed = time.time() - start
                _log.info(
                    "HF Inference OK: %s (%.2fs, attempt %d)",
                    model, elapsed, attempt + 1,
                )
                return _extract_message(resp), model
            except urllib.error.HTTPError as e:
                last_err = e
                if e.code in (429, 500, 502, 503, 504):
                    _log.warning(
                        "HF Inference %d from %s, retry %d/%d",
                        e.code, model, attempt + 1, max_model_retries,
                    )
                    time.sleep(2 ** attempt)
                    continue
                _log.warning(
                    "HF Inference %d from %s, falling back", e.code, model,
                )
                break
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last_err = e
                _log.warning(
                    "HF Inference network error from %s: %s, retry %d/%d",
                    model, e, attempt + 1, max_model_retries,
                )
                time.sleep(2 ** attempt)
                continue
            except ValueError as e:
                last_err = e
                _log.warning(
                    "HF Inference malformed response from %s: %s", model, e,
                )
                break
    raise RuntimeError(
        f"All LLM calls failed (LiteLLM + 3 HF Inference models). Last error: {last_err}"
    )


def chat_complete_json(
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 4096,
    temperature: float = 0.1,
) -> tuple[dict[str, Any], str]:
    """Call chat_complete and parse the response as JSON.

    Returns:
        (parsed_dict, model_used). Raises ValueError if the response is
        not valid JSON.
    """
    text, model = chat_complete(
        messages, max_tokens=max_tokens, temperature=temperature
    )
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    try:
        return json.loads(text), model
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model {model} did not return valid JSON: {e}\n\n{text[:500]}"
        ) from e
