"""BIEP v3 canonical BAML clients.

Per the 2026-08-07-biep-v3-hardening-v1 change.

Replaces the fragmented client setup (ExtractEn, ExtractEnStrong,
LlamaSwapClient, LocalVision, etc.) with 3 canonical clients that
all active BIEP v3 jurisdiction functions route through.
"""
from __future__ import annotations

# BIEPV3Extract — the canonical light-weight client (Gemma 3 4B)
# Per the 2026-08-07 hardening change. Replaces ExtractEn.
BIEPV3Extract = "gemma-3-4b-it"

# BIEPV3ExtractStrong — the canonical detail-rich client (Qwen 3-VL 8B)
# Replaces ExtractEnStrong.
BIEPV3ExtractStrong = "qwen3-vl-8b-it"

# BIEPV3Vision — the canonical vision client for the 4-path OCR ensemble
# Routes through llama-swap with qwen3-vl-8b.
BIEPV3Vision = "qwen3-vl-8b-it-via-llama-swap"


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
