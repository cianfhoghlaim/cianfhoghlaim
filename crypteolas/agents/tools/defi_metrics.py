"""
DeFi Metrics Tools for Crypteolas agents.

Provides real-time DeFi data access.
"""

import os
from datetime import datetime, timezone
from typing import Any

import httpx


# DeFiLlama API
DEFILLAMA_API = "https://api.llama.fi"
COINGECKO_API = "https://api.coingecko.com/api/v3"
BINANCE_FUTURES_API = "https://fapi.binance.com/fapi/v1"


async def get_protocol_tvl(
    protocol: str | None = None,
    chain: str | None = None,
    top_n: int | None = None,
) -> dict[str, Any]:
    """Fetch TVL data from DeFiLlama."""
    async with httpx.AsyncClient() as client:
        try:
            if protocol:
                response = await client.get(f"{DEFILLAMA_API}/protocol/{protocol}")
                response.raise_for_status()
                data = response.json()
                return {
                    "protocol": protocol,
                    "tvl": data.get("tvl"),
                    "chain_tvls": data.get("chainTvls", {}),
                    "change_1d": data.get("change_1d"),
                    "change_7d": data.get("change_7d"),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }
            else:
                response = await client.get(f"{DEFILLAMA_API}/protocols")
                response.raise_for_status()
                protocols = response.json()

                # Filter by chain if specified
                if chain:
                    protocols = [
                        p for p in protocols if chain.lower() in [c.lower() for c in p.get("chains", [])]
                    ]

                # Sort by TVL and limit
                protocols.sort(key=lambda x: x.get("tvl", 0) or 0, reverse=True)
                if top_n:
                    protocols = protocols[:top_n]

                return {
                    "protocols": [
                        {
                            "name": p.get("name"),
                            "slug": p.get("slug"),
                            "tvl": p.get("tvl"),
                            "chains": p.get("chains"),
                            "change_1d": p.get("change_1d"),
                        }
                        for p in protocols
                    ],
                    "count": len(protocols),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            return {"error": str(e)}


async def get_yield_pools(
    protocol: str | None = None,
    chain: str | None = None,
    min_tvl: float | None = None,
    stablecoin_only: bool = False,
) -> list[dict[str, Any]]:
    """Fetch yield pool data from DeFiLlama."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://yields.llama.fi/pools")
            response.raise_for_status()
            pools = response.json().get("data", [])

            # Apply filters
            if protocol:
                pools = [p for p in pools if p.get("project", "").lower() == protocol.lower()]
            if chain:
                pools = [p for p in pools if p.get("chain", "").lower() == chain.lower()]
            if min_tvl:
                pools = [p for p in pools if (p.get("tvlUsd") or 0) >= min_tvl]
            if stablecoin_only:
                pools = [p for p in pools if p.get("stablecoin")]

            # Sort by APY and limit
            pools.sort(key=lambda x: x.get("apy", 0) or 0, reverse=True)

            return [
                {
                    "pool": p.get("pool"),
                    "project": p.get("project"),
                    "chain": p.get("chain"),
                    "symbol": p.get("symbol"),
                    "tvl_usd": p.get("tvlUsd"),
                    "apy": p.get("apy"),
                    "apy_base": p.get("apyBase"),
                    "apy_reward": p.get("apyReward"),
                    "stablecoin": p.get("stablecoin"),
                }
                for p in pools[:50]
            ]

        except Exception:
            return []


async def get_funding_rates(
    symbol: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch perpetual funding rates from Binance."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BINANCE_FUTURES_API}/premiumIndex")
            response.raise_for_status()
            rates = response.json()

            if symbol:
                rates = [r for r in rates if r.get("symbol") == symbol]

            # Sort by absolute funding rate
            rates.sort(key=lambda x: abs(float(x.get("lastFundingRate", 0))), reverse=True)

            return [
                {
                    "symbol": r.get("symbol"),
                    "mark_price": float(r.get("markPrice", 0)),
                    "funding_rate": float(r.get("lastFundingRate", 0)),
                    "funding_rate_annualized": float(r.get("lastFundingRate", 0)) * 3 * 365 * 100,
                    "next_funding_time": r.get("nextFundingTime"),
                }
                for r in rates[:30]
            ]

        except Exception:
            return []


async def get_token_price(
    token_id: str,
) -> dict[str, Any]:
    """Fetch token price from CoinGecko."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{COINGECKO_API}/simple/price",
                params={
                    "ids": token_id,
                    "vs_currencies": "usd,eth",
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                },
            )
            response.raise_for_status()
            data = response.json().get(token_id, {})

            return {
                "token_id": token_id,
                "price_usd": data.get("usd"),
                "price_eth": data.get("eth"),
                "change_24h": data.get("usd_24h_change"),
                "market_cap": data.get("usd_market_cap"),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}


async def get_protocol_comparison(
    protocols: list[str],
    metrics: list[str] | None = None,
) -> dict[str, Any]:
    """Compare multiple protocols on metrics."""
    results = {"protocols": {}, "metrics": metrics or ["tvl", "change_1d"]}

    for protocol in protocols:
        data = await get_protocol_tvl(protocol=protocol)
        if "error" not in data:
            results["protocols"][protocol] = {
                "tvl": data.get("tvl"),
                "change_1d": data.get("change_1d"),
                "change_7d": data.get("change_7d"),
            }

    return results


__all__ = [
    "get_protocol_tvl",
    "get_yield_pools",
    "get_funding_rates",
    "get_token_price",
    "get_protocol_comparison",
]
