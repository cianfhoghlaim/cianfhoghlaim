"""BIEP v3 canonical BAML clients.

Per the 2026-08-07-biep-v3-hardening-v1 change + the
2026-08-08-baml-clients-biep-v3-reconciliation-v1 follow-up + the
2026-07-29-complete-remaining-model-registry-migrations-v1 follow-up.

The 3 canonical clients are wired in `baml_src/clients.baml` and
all active BIEP v3 jurisdiction functions route through them.
The model strings here MUST match the `model` fields in
`clients.baml` — the Python module is the spec, the BAML clients
are the implementation.

Per the centralized-model-registry openspec change, the 3 model
strings below are resolved from MODEL_REGISTRY at import time:

  BIEPV3Extract        → text_llm/default (resolve)      → "minimax-m3"
  BIEPV3ExtractStrong  → text_llm/default (resolve)      → "minimax-m3"
  BIEPV3Vision         → ocr_vision, keyed lookup         → "local/vision/qwen3-vl-8b"

  Per the lakehouse-multi-subject-multi-model-rollout change:
  BIEPV3Vision now uses a direct MODEL_REGISTRY.get("qwen3-vl-8b") keyed
  lookup rather than resolve(family, role) -- ocr_vision entries no
  longer participate in role-based resolution at all (see
  model_registry.py::_ocr_vision_entries()'s docstring for why).

The historical hardcoded fallbacks are preserved for minimal
container builds where MODEL_REGISTRY (meaisinfhoghlaim) is
unavailable.

Historical note: an earlier version of this file declared
Gemma 3 4B + 27B + qwen3-vl-8b (per the 2026-07-13 Gemma 3 launch
announcement). The BAML clients were never updated to match;
they remained on `minimax-m3` (the coding-plan API). This file
was updated post-v8 to match the actual BAML wiring.
"""
from __future__ import annotations

# Historical hardcoded fallback chain — used when MODEL_REGISTRY is
# unavailable. Per the centralized-model-registry contract, the
# canonical source of truth is `meaisinfhoghlaim.models.MODEL_REGISTRY`.
_BIEPV3_EXTRACT_FALLBACK = "minimax-m3"
_BIEPV3_EXTRACT_STRONG_FALLBACK = "minimax-m3"
_BIEPV3_VISION_FALLBACK = "local/vision/qwen3-vl-8b"


def _resolve_text_llm_default() -> str:
    """Resolve text_llm/default from MODEL_REGISTRY (minimax-m3)."""
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY
        return MODEL_REGISTRY.resolve("text_llm", "default")
    except Exception:  # noqa: BLE001 — registry unavailable in dev
        return _BIEPV3_EXTRACT_FALLBACK


def _resolve_ocr_vision_qwen3_vl_default() -> str:
    """Resolve the default OCR vision client (qwen3-vl-8b) from MODEL_REGISTRY.

    Per the lakehouse-multi-subject-multi-model-rollout change: this
    used to call ``MODEL_REGISTRY.resolve("ocr_vision", "qwen3_vl_default")``,
    a role that never existed in the registry's role-map (confirmed
    live: always raised ``KeyError``, silently caught by the broad
    ``except Exception`` below, meaning this function's "resolve from
    the centralized registry" docstring claim never actually executed —
    it always fell through to the hardcoded ``_BIEPV3_VISION_FALLBACK``
    string, which happened to be correct by coincidence).

    `ocr_vision` entries no longer use `resolve(family, role)` at all
    (see `model_registry.py::_ocr_vision_entries()` for why) — a direct
    keyed lookup is the correct tool here for "give me the one specific
    default model this caller needs", and it actually executes/resolves
    for real, unlike the old dead code path.
    """
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY
        entry = MODEL_REGISTRY.get("qwen3-vl-8b")
        if entry is not None and entry.litellm_alias:
            return entry.litellm_alias
        return _BIEPV3_VISION_FALLBACK
    except Exception:  # noqa: BLE001 — registry unavailable in dev
        return _BIEPV3_VISION_FALLBACK


# BIEPV3Extract — the canonical light-weight text client.
# Routes through the minimax-m3 (coding-plan API).
BIEPV3Extract = _resolve_text_llm_default()

# BIEPV3ExtractStrong — the canonical detail-rich text client.
# Same model as BIEPV3Extract (both route through the same
# minimax-m3 instance); the Strong variant uses higher max_tokens
# + longer timeout per the CANONICAL_CLIENTS table below.
BIEPV3ExtractStrong = _resolve_text_llm_default()

# BIEPV3Vision — the canonical vision client for the 4-path OCR ensemble
# Routes through LiteLLM to the local qwen3-vl-8b server.
BIEPV3Vision = _resolve_ocr_vision_qwen3_vl_default()


# The 3 canonical clients, with documented retry + timeout + max_tokens.
# Per the 2026-08-07 hardening change.
CANONICAL_CLIENTS = {
    "BIEPV3Extract": {
        "model": BIEPV3Extract,
        "retries": 3,
        "timeout_s": 60,
        "max_tokens": 2048,
    },
    "BIEPV3ExtractStrong": {
        "model": BIEPV3ExtractStrong,
        "retries": 3,
        "timeout_s": 120,
        "max_tokens": 4096,
    },
    "BIEPV3Vision": {
        "model": BIEPV3Vision,
        "retries": 5,
        "timeout_s": 180,
        "max_tokens": 8192,
    },
}


__all__ = [
    "BIEPV3Extract",
    "BIEPV3ExtractStrong",
    "BIEPV3Vision",
    "CANONICAL_CLIENTS",
]
