"""Stub: pricing config (re-exports from crypteolas.api.services.* when needed)."""

from __future__ import annotations

PRICING_CONFIG: dict[str, dict] = {
    "copilot_chat": {"free_per_day": 5, "price_per_call": "0.01", "asset": "USDC"},
    "yield_analytics": {"free_per_day": 3, "price_per_call": "0.05", "asset": "USDC"},
    "risk_analysis": {"free_per_day": 3, "price_per_call": "0.05", "asset": "USDC"},
    "knowledge_graph": {"free_per_day": 3, "price_per_call": "0.02", "asset": "USDC"},
}


__all__ = ["PRICING_CONFIG"]
