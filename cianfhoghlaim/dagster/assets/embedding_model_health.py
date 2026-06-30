"""Embedding Model Health Dagster asset + asset check.

Added in the `2026-06-30-agent-platform-cluster-hermes-cocoindex` change.

Polls the `litellm` stack's `/health/liveliness` endpoint every
5 minutes and computes a rolling average of the last 100
completions' latency. Emits a Dagster `AssetCheck` that fails
when the rolling average > 500 ms.

The asset check is the canonical guardrail for the M3 chokepoint
— when LiteLLM is degraded, the 3 new agent surfaces
(OpenClaw-on-LiteLLM, OpenChamber-on-LiteLLM, Hermes-on-LiteLLM)
all degrade together.
"""
from __future__ import annotations

import os
import time
from collections import deque

import requests
import structlog
from dagster import (
    AssetCheckResult,
    AssetCheckSpec,
    MaterializeResult,
    asset,
    asset_check,
)

logger = structlog.get_logger(__name__)

# Rolling buffer of the last 100 completions' latencies
_LATENCY_BUFFER: deque[float] = deque(maxlen=100)
LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")
LATENCY_THRESHOLD_MS = 500.0


@asset(
    group_name="observability",
    compute_kind="monitor",
    description="Polls LiteLLM /health/liveliness + computes rolling avg completion latency.",
    check_specs=[
        AssetCheckSpec(
            name="latency_threshold_check",
            description="Fails when rolling avg > 500 ms (LiteLLM is degraded).",
        ),
    ],
)
def embedding_model_health(context) -> MaterializeResult:
    """Poll LiteLLM and update the rolling latency buffer."""
    try:
        t0 = time.perf_counter()
        response = requests.get(
            f"{LITELLM_URL}/health/liveliness",
            timeout=5,
        )
        t1 = time.perf_counter()
        health_latency_ms = (t1 - t0) * 1000.0
        alive = response.ok
    except Exception as e:
        logger.warning("litellm /health/liveliveness failed: %s", e)
        alive = False
        health_latency_ms = 0.0

    if alive:
        try:
            t0 = time.perf_counter()
            requests.post(
                f"{LITELLM_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('LITELLM_MASTER_KEY', '')}"
                },
                json={
                    "model": "minimax-m3",
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1,
                },
                timeout=10,
            )
            t1 = time.perf_counter()
            completion_latency_ms = (t1 - t0) * 1000.0
            _LATENCY_BUFFER.append(completion_latency_ms)
        except Exception as e:
            logger.warning("litellm /v1/chat/completions failed: %s", e)

    rolling_avg_ms = (
        sum(_LATENCY_BUFFER) / len(_LATENCY_BUFFER) if _LATENCY_BUFFER else 0.0
    )

    return MaterializeResult(
        metadata={
            "litellm_alive": alive,
            "health_latency_ms": health_latency_ms,
            "rolling_avg_completion_latency_ms": rolling_avg_ms,
            "rolling_buffer_size": len(_LATENCY_BUFFER),
            "latency_threshold_ms": LATENCY_THRESHOLD_MS,
        }
    )


@asset_check(
    asset=embedding_model_health,
    description="Fails when rolling avg > 500 ms.",
)
def latency_threshold_check(context, embedding_model_health: MaterializeResult) -> AssetCheckResult:
    """Asset check: rolling_avg > 500ms → fail."""
    metadata = embedding_model_health.metadata
    rolling_avg = metadata.get("rolling_avg_completion_latency_ms", 0.0)
    return AssetCheckResult(
        passed=rolling_avg <= LATENCY_THRESHOLD_MS,
        metadata={
            "rolling_avg_ms": rolling_avg,
            "threshold_ms": LATENCY_THRESHOLD_MS,
        },
    )
