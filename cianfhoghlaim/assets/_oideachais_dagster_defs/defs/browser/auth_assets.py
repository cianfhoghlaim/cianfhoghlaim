"""
auth_assets — Skyvern + Stagehand opt-in browser assets.

This module is the Python backing for `auth_defs.yaml`. It
conditionally registers the Skyvern + Stagehand DLT sources
only if the BROWSER_ENABLE_SKYVERN=1 or
BROWSER_ENABLE_STAGEHAND=1 env vars are set.

By default (no env vars set), this module exports 0 assets
and the defs is effectively a no-op.

When enabled, the Skyvern/Stagehand assets are registered in
the `browser` group alongside the default-on Crawl4AI + Firecrawl
+ Playwright assets.
"""
from __future__ import annotations

import os

import dagster as dg


SKYVERN_ENABLED = os.environ.get("BROWSER_ENABLE_SKYVERN", "").lower() in (
    "1", "true", "yes",
)
STAGEHAND_ENABLED = os.environ.get("BROWSER_ENABLE_STAGEHAND", "").lower() in (
    "1", "true", "yes",
)


def _skyvern_search_asset() -> dg.AssetsDefinition:
    @dg.asset(
        name="browser_skyvern_search",
        group_name="browser",
        compute_kind="skyvern",
        description="Skyvern vision-based semantic navigation (opt-in via BROWSER_ENABLE_SKYVERN=1)",
    )
    def _asset() -> dg.MaterializeResult:
        from cianfhoghlaim.core.browser import BrowserClient
        client = BrowserClient()
        result = client.search(backend="skyvern_local", limit_per_query=10)
        return dg.MaterializeResult(
            metadata={"backend": "skyvern", "results": len(result)},
        )
    return _asset


def _stagehand_interact_asset() -> dg.AssetsDefinition:
    @dg.asset(
        name="browser_stagehand_interact",
        group_name="browser",
        compute_kind="stagehand",
        description="Stagehand AI-powered UI interactions (opt-in via BROWSER_ENABLE_STAGEHAND=1)",
    )
    def _asset() -> dg.MaterializeResult:
        from cianfhoghlaim.core.browser import BrowserClient
        client = BrowserClient()
        result = client.interact(backend="stagehand_local")
        return dg.MaterializeResult(
            metadata={"backend": "stagehand", "result": str(result)[:500]},
        )
    return _asset


# Conditionally register the opt-in assets.
auth_assets: list[dg.AssetsDefinition] = []
if SKYVERN_ENABLED:
    auth_assets.append(_skyvern_search_asset())
if STAGEHAND_ENABLED:
    auth_assets.append(_stagehand_interact_asset())


__all__ = [
    "auth_assets",
    "SKYVERN_ENABLED",
    "STAGEHAND_ENABLED",
]
