"""Stub: x402 pricing types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PricingTier:
    """Stub pricing tier."""

    name: str
    free_per_day: int
    price_per_call: str
    asset: str = "USDC"


__all__ = ["PricingTier"]
