"""
spaces/_common/baml_client.py
Lightweight Python wrapper around the HF Inference API for the 4 Spaces.

This module bypasses the BAML compiler (which requires a Rust toolchain
and is too heavy for a Gradio Space container) and implements the same
3-tier fallback chain in pure Python. The BAML function signatures
remain the source of truth in `spaces/_common/baml/*.baml` for the
Gradio apps to reference; this module does the HTTP work.

The 3-tier chain:
  1. Qwen2.5-7B-Instruct    (primary, fast JSON)
  2. Llama-3.1-8B-Instruct  (fallback 1, broad)
  3. Gemma-2-9b-it          (fallback 2, safety-tuned)

Triggers for fallback:
  - HTTP timeout (default 60s)
  - 5xx response
  - 429 rate limit (after 1 retry)
  - JSON schema parse failure on the response
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


# Model configuration (mirror of clients_hackathon.baml)
HACKATHON_PRIMARY_MODEL: Final[str] = "Qwen/Qwen2.5-7B-Instruct"
HACKATHON_FALLBACK_1_MODEL: Final[str] = "meta-llama/Llama-3.1-8B-Instruct"
HACKATHON_FALLBACK_2_MODEL: Final[str] = "google/gemma-2-9b-it"

HF_INFERENCE_BASE_URL: Final[str] = (
    os.environ.get("HF_INFERENCE_URL")
    or "https://api-inference.huggingface.co"
)

# The HF Inference API exposes an OpenAI-compatible /v1/chat/completions
# endpoint when the model supports it. Qwen2.5-7B-Instruct, Llama-3.1-8B-
# Instruct, and Gemma-2-9b-it all do.
_OPENAI_CHAT_PATH: Final[str] = "/v1/chat/completions"


_MODEL_CHAIN: Final[tuple[str, ...]] = (
    HACKATHON_PRIMARY_MODEL,
    HACKATHON_FALLBACK_1_MODEL,
    HACKATHON_FALLBACK_2_MODEL,
)


def get_hackathon_client_config() -> dict[str, Any]:
    """Return the resolved client config (for logging + UI display)."""
    return {
        "primary": HACKATHON_PRIMARY_MODEL,
        "fallback_1": HACKATHON_FALLBACK_1_MODEL,
        "fallback_2": HACKATHON_FALLBACK_2_MODEL,
        "base_url": HF_INFERENCE_BASE_URL,
        "hf_token_set": bool(os.environ.get("HF_TOKEN")),
    }


def _build_payload(
    messages: list[dict[str, str]],
    model: str,
    max_tokens: int = 4096,
    temperature: float = 0.1,
) -> dict[str, Any]:
    """Build the OpenAI-compatible request body."""
    return {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }


def _post_json(
    url: str, payload: dict[str, Any], timeout: int = 60
) -> dict[str, Any]:
    """POST a JSON payload and return the parsed response."""
    token = os.environ.get("HF_TOKEN", "")
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
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


def chat_complete(
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 4096,
    temperature: float = 0.1,
    timeout: int = 60,
    max_model_retries: int = 1,
) -> tuple[str, str]:
    """Call HF Inference with the 3-tier fallback chain.

    Args:
        messages: A list of {"role": ..., "content": ...} dicts in
            OpenAI chat-completions format.
        max_tokens: Max tokens in the response.
        temperature: Sampling temperature (0.0 - 1.0).
        timeout: Per-model timeout in seconds.
        max_model_retries: Number of times to retry the same model on
            transient failures (timeout, 5xx, 429) before falling back.

    Returns:
        (content, model_used) - the assistant's text and the name of
        the model that ultimately produced it.

    Raises:
        RuntimeError: If all 3 models fail.
        ValueError: If HF_TOKEN is unset.
    """
    if not os.environ.get("HF_TOKEN"):
        raise ValueError(
            "HF_TOKEN is not set. Add it to your HF Space secrets."
        )

    url = HF_INFERENCE_BASE_URL.rstrip("/") + _OPENAI_CHAT_PATH
    last_err: Exception | None = None

    for model in _MODEL_CHAIN:
        for attempt in range(max_model_retries + 1):
            try:
                payload = _build_payload(
                    messages, model, max_tokens, temperature
                )
                start = time.time()
                resp = _post_json(url, payload, timeout=timeout)
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
        f"All 3 hackathon models failed. Last error: {last_err}"
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
