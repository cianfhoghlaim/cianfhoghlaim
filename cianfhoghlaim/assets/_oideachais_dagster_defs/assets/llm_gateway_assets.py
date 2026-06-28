"""
LLM Gateway (LiteLLM) health asset + asset_check.

Tracks the health of the `minimax` alias in
`infrastructure/stacks/litellm/config/config.yaml` so the Dagster UI
shows whether the vendor-de-risking fallback chain is healthy.

Operational contract:
- This asset does NOT make any LLM calls (no credits burned).
- It hits the LiteLLM `/health/readiness` endpoint and the
  `/v1/models` endpoint and asserts the `minimax` alias resolves
  to at least one backing deployment.
- The companion asset_check (`minimax_alias_health`) returns
  AssetCheckResult(passed=...) for the Dagster UI badge.
- On failure the asset_check emits a structured metadata payload
  listing which backends are healthy and which are not.
- Wired into oideachais/dagster_defs/definitions.py via the
  `combined_assets` list (see task 5.3 of the
  litellm-minimax-vendor-derisking OpenSpec change).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx
from dagster import (
    AssetCheckExecutionContext,
    AssetCheckResult,
    AssetExecutionContext,
    MetadataValue,
    asset,
    asset_check,
)
from pydantic import BaseModel, Field

# ============================================================================
# Configuration
# ============================================================================


class GatewayHealthConfig(BaseModel):
    """LiteLLM gateway health-check configuration."""

    base_url: str = Field(
        default_factory=lambda: os.environ.get(
            "LITELLM_BASE_URL", "http://localhost:4000"
        )
    )
    master_key: str = Field(
        default_factory=lambda: os.environ.get("LITELLM_MASTER_KEY", "")
    )
    alias: str = "minimax"
    timeout_s: float = 5.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================================
# Health probes
# ============================================================================


def _probe_liveliness(client: httpx.Client, base_url: str) -> bool:
    """Hit /health/liveliness — returns True if the proxy is up."""
    try:
        r = client.get(f"{base_url}/health/liveliness", timeout=5.0)
        return r.status_code == 200
    except (httpx.HTTPError, httpx.RequestError):
        return False


def _probe_alias(
    client: httpx.Client, base_url: str, alias: str, master_key: str = ""
) -> dict[str, Any]:
    """Hit /v1/models and look up the alias. Returns the model_info if found.

    Per LiteLLM's contract, model_info for an alias includes the
    fallback_chain list. If the alias is missing, returns {"found": False}.
    Sends the master key as a Bearer token (the /v1/models endpoint
    requires auth when `store_model_in_db: true`).
    """
    headers = {"Authorization": f"Bearer {master_key}"} if master_key else {}
    try:
        r = client.get(f"{base_url}/v1/models", headers=headers, timeout=5.0)
        if r.status_code != 200:
            return {"found": False, "status": r.status_code}
    except (httpx.HTTPError, httpx.RequestError) as e:
        return {"found": False, "error": str(e)}

    try:
        models = r.json().get("data", [])
    except (ValueError, KeyError):
        return {"found": False, "error": "response not JSON"}

    for m in models:
        if m.get("id") == alias:
            return {"found": True, "model_info": m.get("model_info", {})}
    return {"found": False}


def _probe_chain_via_model_info(
    client: httpx.Client, base_url: str, alias: str, master_key: str = ""
) -> dict[str, Any]:
    """Hit /v1/model/info?model=<alias> to get the canonical
    fallback_chain. The /v1/models endpoint strips fallback_chain
    for some LiteLLM versions; the dedicated /v1/model/info
    endpoint preserves it.
    """
    headers = {"Authorization": f"Bearer {master_key}"} if master_key else {}
    try:
        r = client.get(
            f"{base_url}/v1/model/info", params={"model": alias}, headers=headers, timeout=5.0
        )
        if r.status_code != 200:
            return {"found": False, "status": r.status_code}
    except (httpx.HTTPError, httpx.RequestError) as e:
        return {"found": False, "error": str(e)}

    try:
        rows = r.json().get("data", [])
    except (ValueError, KeyError):
        return {"found": False, "error": "response not JSON"}

    for row in rows:
        if row.get("model_name") == alias:
            return {
                "found": True,
                "model_info": row.get("model_info", {}),
            }
    return {"found": False}


# ============================================================================
# Asset
# ============================================================================


@asset(
    group_name="llm_gateway",
    compute_kind="litellm",
    description=(
        "Health probe of the LiteLLM gateway + `minimax` alias. "
        "No LLM credits burned; this is a read-only check that emits "
        "structured metadata for the Dagster UI."
    ),
)
def minimax_alias_liveliness(context) -> None:
    """Run liveliness + alias-probe checks and emit metadata.

    The `context` parameter is intentionally untyped here so the
    module imports cleanly under Dagster 1.12.6 (which validates the
    type hint at decoration time and rejects the imported
    `AssetExecutionContext` symbol in some import-orderings).
    Dagster still injects the correct AssetExecutionContext
    instance at runtime — the type hint is purely documentary.
    """
    cfg = GatewayHealthConfig()

    with httpx.Client(timeout=cfg.timeout_s) as client:
        is_live = _probe_liveliness(client, cfg.base_url)
        # /v1/model/info preserves fallback_chain; /v1/models strips it.
        # We try /v1/model/info first; fall back to /v1/models for
        # presence detection.
        chain_info = _probe_chain_via_model_info(
            client, cfg.base_url, cfg.alias, cfg.master_key
        )
        if not chain_info.get("found"):
            chain_info = _probe_alias(client, cfg.base_url, cfg.alias, cfg.master_key)

    fallback_chain: list[str] = []
    if chain_info.get("found"):
        mi = chain_info["model_info"]
        fallback_chain = mi.get("fallback_chain", [])

    context.add_metadata(
        {
            "checked_at": MetadataValue.text(_now_iso()),
            "gateway_base_url": MetadataValue.text(cfg.base_url),
            "alias": MetadataValue.text(cfg.alias),
            "gateway_live": MetadataValue.bool(is_live),
            "alias_found": MetadataValue.bool(chain_info.get("found", False)),
            "fallback_chain_length": MetadataValue.int(len(fallback_chain)),
            "fallback_chain": MetadataValue.json(fallback_chain),
        }
    )

    if not is_live:
        context.log.warning(
            f"LiteLLM gateway at {cfg.base_url} is not live; the "
            "`minimax` alias will fail every request until the proxy "
            "recovers."
        )


# ============================================================================
# Asset check
# ============================================================================


@asset_check(
    asset=minimax_alias_liveliness,
    description=(
        "Passes iff the LiteLLM gateway is live AND the `minimax` "
        "alias is registered with a non-empty fallback_chain."
    ),
)
def minimax_alias_health(context) -> AssetCheckResult:
    """See note in `minimax_alias_liveliness` about the untyped
    `context` parameter (Dagster 1.12.6 import-ordering quirk)."""
    cfg = GatewayHealthConfig()
    if not cfg.master_key:
        return AssetCheckResult(
            passed=False,
            metadata={
                "error": MetadataValue.text(
                    "LITELLM_MASTER_KEY is not set; cannot authenticate "
                    "with the gateway"
                )
            },
        )

    with httpx.Client(timeout=cfg.timeout_s) as client:
        is_live = _probe_liveliness(client, cfg.base_url)
        chain_info = _probe_chain_via_model_info(
            client, cfg.base_url, cfg.alias, cfg.master_key
        )
        if not chain_info.get("found"):
            chain_info = _probe_alias(client, cfg.base_url, cfg.alias, cfg.master_key)

    if not is_live:
        return AssetCheckResult(
            passed=False,
            metadata={
                "error": MetadataValue.text(
                    f"LiteLLM gateway at {cfg.base_url} is not responding"
                )
            },
        )

    if not chain_info.get("found"):
        return AssetCheckResult(
            passed=False,
            metadata={
                "error": MetadataValue.text(
                    f"Alias `{cfg.alias}` is not registered in the "
                    "LiteLLM model registry. The `infrastructure/stacks/"
                    "litellm/config/config.yaml` is missing the entry."
                )
            },
        )

    fallback_chain: list[str] = chain_info["model_info"].get("fallback_chain", [])
    passed = len(fallback_chain) >= 1
    return AssetCheckResult(
        passed=passed,
        metadata={
            "fallback_chain_length": MetadataValue.int(len(fallback_chain)),
            "fallback_chain": MetadataValue.json(fallback_chain),
            "checked_at": MetadataValue.text(_now_iso()),
        },
    )
