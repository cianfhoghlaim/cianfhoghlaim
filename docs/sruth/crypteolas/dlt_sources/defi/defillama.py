"""
DLT source for DeFiLlama API - Protocol TVL, yields, stablecoins.

API Reference: https://defillama.com/docs/api

Provides access to:
- Protocol TVL and metrics
- DeFi yields and APYs
- Stablecoin market data
- Historical TVL data
"""

from datetime import datetime, timezone
from typing import Any, Iterator

import dlt
import httpx

# DeFiLlama API base URLs
DEFILLAMA_API_URL = "https://api.llama.fi"
DEFILLAMA_YIELDS_URL = "https://yields.llama.fi"
DEFILLAMA_STABLECOINS_URL = "https://stablecoins.llama.fi"


def _get_main_client() -> httpx.Client:
    """Get HTTP client for main DeFiLlama API."""
    return httpx.Client(base_url=DEFILLAMA_API_URL, timeout=30.0)


def _get_yields_client() -> httpx.Client:
    """Get HTTP client for DeFiLlama Yields API."""
    return httpx.Client(base_url=DEFILLAMA_YIELDS_URL, timeout=30.0)


def _get_stablecoins_client() -> httpx.Client:
    """Get HTTP client for DeFiLlama Stablecoins API."""
    return httpx.Client(base_url=DEFILLAMA_STABLECOINS_URL, timeout=30.0)


def _list_protocols() -> Iterator[dict[str, Any]]:
    """List all DeFi protocols with TVL data."""
    with _get_main_client() as client:
        try:
            response = client.get("/protocols")
            response.raise_for_status()
            protocols = response.json()

            for protocol in protocols:
                yield {
                    "id": protocol.get("id"),
                    "name": protocol.get("name"),
                    "slug": protocol.get("slug"),
                    "symbol": protocol.get("symbol"),
                    "logo": protocol.get("logo"),
                    "chain": protocol.get("chain"),
                    "chains": protocol.get("chains", []),
                    "category": protocol.get("category"),
                    "tvl": protocol.get("tvl"),
                    "tvl_change_1h": protocol.get("change_1h"),
                    "tvl_change_1d": protocol.get("change_1d"),
                    "tvl_change_7d": protocol.get("change_7d"),
                    "mcap": protocol.get("mcap"),
                    "fdv": protocol.get("fdv"),
                    "staking": protocol.get("staking"),
                    "pool2": protocol.get("pool2"),
                    "governance_id": protocol.get("governanceID"),
                    "treasury": protocol.get("treasury"),
                    "twitter": protocol.get("twitter"),
                    "url": protocol.get("url"),
                    "description": protocol.get("description"),
                    "audits": protocol.get("audits"),
                    "audit_links": protocol.get("audit_links"),
                    "oracle": protocol.get("oracles", []),
                    "forked_from": protocol.get("forkedFrom"),
                    "listed_at": protocol.get("listedAt"),
                    "status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            yield {
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }


def _get_protocol_tvl_history(slug: str) -> Iterator[dict[str, Any]]:
    """Get historical TVL data for a protocol."""
    with _get_main_client() as client:
        try:
            response = client.get(f"/protocol/{slug}")
            response.raise_for_status()
            data = response.json()

            # Get chain TVL breakdown
            chain_tvls = data.get("chainTvls", {})
            for chain, chain_data in chain_tvls.items():
                tvl_history = chain_data.get("tvl", [])
                for entry in tvl_history:
                    yield {
                        "protocol_slug": slug,
                        "chain": chain,
                        "date": datetime.fromtimestamp(entry.get("date", 0), tz=timezone.utc)
                        .date()
                        .isoformat(),
                        "timestamp": entry.get("date"),
                        "tvl": entry.get("totalLiquidityUSD"),
                        "status": "success",
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    }

        except Exception as e:
            yield {
                "protocol_slug": slug,
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }


def _list_chains() -> Iterator[dict[str, Any]]:
    """List all chains with TVL data."""
    with _get_main_client() as client:
        try:
            response = client.get("/v2/chains")
            response.raise_for_status()
            chains = response.json()

            for chain in chains:
                yield {
                    "name": chain.get("name"),
                    "gecko_id": chain.get("gecko_id"),
                    "cmc_id": chain.get("cmcId"),
                    "chain_id": chain.get("chainId"),
                    "tvl": chain.get("tvl"),
                    "token_symbol": chain.get("tokenSymbol"),
                    "status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            yield {
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }


def _list_yields() -> Iterator[dict[str, Any]]:
    """List all yield pools."""
    with _get_yields_client() as client:
        try:
            response = client.get("/pools")
            response.raise_for_status()
            data = response.json()

            for pool in data.get("data", []):
                yield {
                    "pool_id": pool.get("pool"),
                    "chain": pool.get("chain"),
                    "project": pool.get("project"),
                    "symbol": pool.get("symbol"),
                    "tvl_usd": pool.get("tvlUsd"),
                    "apy": pool.get("apy"),
                    "apy_base": pool.get("apyBase"),
                    "apy_reward": pool.get("apyReward"),
                    "apy_7d": pool.get("apyMean7d"),
                    "apy_30d": pool.get("apyMean30d"),
                    "il_risk": pool.get("ilRisk"),
                    "stablecoin": pool.get("stablecoin"),
                    "reward_tokens": pool.get("rewardTokens"),
                    "underlying_tokens": pool.get("underlyingTokens"),
                    "pool_meta": pool.get("poolMeta"),
                    "exposure": pool.get("exposure"),
                    "predictions": pool.get("predictions"),
                    "status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            yield {
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }


def _list_stablecoins() -> Iterator[dict[str, Any]]:
    """List all stablecoins with market data."""
    with _get_stablecoins_client() as client:
        try:
            response = client.get("/stablecoins")
            response.raise_for_status()
            data = response.json()

            for stablecoin in data.get("peggedAssets", []):
                yield {
                    "id": stablecoin.get("id"),
                    "name": stablecoin.get("name"),
                    "symbol": stablecoin.get("symbol"),
                    "gecko_id": stablecoin.get("gecko_id"),
                    "peg_type": stablecoin.get("pegType"),
                    "peg_mechanism": stablecoin.get("pegMechanism"),
                    "circulating": stablecoin.get("circulating", {}).get("peggedUSD"),
                    "circulating_prev_day": stablecoin.get("circulatingPrevDay", {}).get(
                        "peggedUSD"
                    ),
                    "circulating_prev_week": stablecoin.get("circulatingPrevWeek", {}).get(
                        "peggedUSD"
                    ),
                    "circulating_prev_month": stablecoin.get("circulatingPrevMonth", {}).get(
                        "peggedUSD"
                    ),
                    "chains": stablecoin.get("chains", []),
                    "price": stablecoin.get("price"),
                    "status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            yield {
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }


@dlt.source(name="defillama")
def defillama_source(
    include_protocols: bool = True,
    include_chains: bool = True,
    include_yields: bool = True,
    include_stablecoins: bool = True,
    protocol_slugs: list[str] | None = None,
):
    """
    DLT source for DeFiLlama data.

    Args:
        include_protocols: Include protocol TVL data
        include_chains: Include chain TVL data
        include_yields: Include yield pool data
        include_stablecoins: Include stablecoin data
        protocol_slugs: Optional list of protocol slugs for historical TVL

    Returns:
        DLT source with protocols, chains, yields, stablecoins resources
    """

    @dlt.resource(
        name="protocols",
        write_disposition="merge",
        primary_key=["id"],
    )
    def protocols():
        """DeFi protocols with TVL."""
        if not include_protocols:
            return
        yield from _list_protocols()

    @dlt.resource(
        name="chains",
        write_disposition="merge",
        primary_key=["name"],
    )
    def chains():
        """Blockchain chains with TVL."""
        if not include_chains:
            return
        yield from _list_chains()

    @dlt.resource(
        name="yields",
        write_disposition="replace",
        primary_key=["pool_id"],
    )
    def yields():
        """DeFi yield pools."""
        if not include_yields:
            return
        yield from _list_yields()

    @dlt.resource(
        name="stablecoins",
        write_disposition="merge",
        primary_key=["id"],
    )
    def stablecoins():
        """Stablecoins market data."""
        if not include_stablecoins:
            return
        yield from _list_stablecoins()

    @dlt.resource(
        name="protocol_tvl_history",
        write_disposition="merge",
        primary_key=["protocol_slug", "chain", "date"],
    )
    def protocol_tvl_history():
        """Historical TVL by protocol and chain."""
        if not protocol_slugs:
            return
        for slug in protocol_slugs:
            yield from _get_protocol_tvl_history(slug)

    return protocols, chains, yields, stablecoins, protocol_tvl_history
