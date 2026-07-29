"""BIEP v3 canonical BAML clients.

Per the 2026-08-07-biep-v3-hardening-v1 change + the
2026-08-08-baml-clients-biep-v3-reconciliation-v1 follow-up.

The 3 canonical clients are wired in `baml_src/clients.baml` and
all active BIEP v3 jurisdiction functions route through them.
The model strings here MUST match the `model` fields in
`clients.baml` lines 188-216 — the Python module is the spec, the
BAML clients are the implementation.

Historical note: an earlier version of this file declared
Gemma 3 4B + 27B + qwen3-vl-8b (per the 2026-07-13 Gemma 3 launch
announcement). The BAML clients were never updated to match;
they remained on `minimax-m3` (the coding-plan API). This file
was updated post-v8 to match the actual BAML wiring.
"""
from __future__ import annotations

# BIEPV3Extract — the canonical light-weight text client.
# Routes through the minimax-m3 (coding-plan API).
# Per clients.baml lines 188-196.
BIEPV3Extract = "minimax-m3"

# BIEPV3ExtractStrong — the canonical detail-rich text client.
# Same model as BIEPV3Extract (both route through the same
# minimax-m3 instance); the Strong variant uses higher max_tokens
# + longer timeout per the CANONICAL_CLIENTS table below.
# Per clients.baml lines 198-206.
BIEPV3ExtractStrong = "minimax-m3"

# BIEPV3Vision — the canonical vision client for the 4-path OCR ensemble
# Routes through LiteLLM to the local qwen3-vl-8b server.
# Per clients.baml lines 208-216.
BIEPV3Vision = "local/vision/qwen3-vl-8b"


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
