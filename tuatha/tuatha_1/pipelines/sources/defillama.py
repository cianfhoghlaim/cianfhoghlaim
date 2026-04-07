"""
DeFiLlama API source for TVL, yields, and protocol data.

Provides comprehensive DeFi protocol metrics without authentication.
"""

from datetime import datetime
from typing import Any, Iterator, Optional

import dlt
from dlt.sources.rest_api import rest_api_source, RESTAPIConfig


@dlt.source(name="defillama")
def defillama_source(
    protocols: Optional[list[str]] = None,
    include_yields: bool = True,
    include_stablecoins: bool = True,
) -> Iterator[dlt.resource]:
    """
    DeFiLlama API source for DeFi protocol data.

    Args:
        protocols: List of protocol slugs to fetch. Defaults to Ethena ecosystem.
        include_yields: Include yield/APY data
        include_stablecoins: Include stablecoin supply data

    Yields:
        DLT resources for protocols, yields, and stablecoins
    """
    if protocols is None:
        protocols = ["ethena", "aave", "lido", "pendle", "curve-dex"]

    # Protocol TVL resources
    resources = []

    for protocol in protocols:
        resources.append(
            {
                "name": f"protocol_{protocol.replace('-', '_')}",
                "endpoint": {
                    "path": f"/protocol/{protocol}",
                },
                "primary_key": "id",
                "write_disposition": "replace",  # Full refresh for protocol data
            }
        )

    # Add TVL history for each protocol
    for protocol in protocols:
        resources.append(
            {
                "name": f"tvl_{protocol.replace('-', '_')}",
                "endpoint": {
                    "path": f"/protocol/{protocol}",
                },
                "data_selector": "tvl",
                "primary_key": "date",
                "write_disposition": "merge",
            }
        )

    yield from rest_api_source(
        RESTAPIConfig(
            client={"base_url": "https://api.llama.fi"},
            resources=resources,
        )
    )

    # Yields data (separate base URL)
    if include_yields:
        yield defillama_yields()

    # Stablecoin data
    if include_stablecoins:
        yield defillama_stablecoins()


@dlt.resource(
    name="defillama_yields",
    primary_key=["pool", "chain", "project"],
    write_disposition="merge",
)
def defillama_yields(
    min_tvl: float = 100000,
    projects: Optional[list[str]] = None,
) -> Iterator[dict[str, Any]]:
    """
    Fetch DeFiLlama yield pools with filtering.

    Args:
        min_tvl: Minimum TVL filter (default $100k)
        projects: Optional project filter

    Yields:
        Yield pool records
    """
    import httpx

    client = httpx.Client(timeout=60.0)

    response = client.get("https://yields.llama.fi/pools")
    response.raise_for_status()
    data = response.json()

    for pool in data.get("data", []):
        # Apply filters
        if pool.get("tvlUsd", 0) < min_tvl:
            continue

        if projects and pool.get("project") not in projects:
            continue

        yield {
            "pool": pool.get("pool"),
            "chain": pool.get("chain"),
            "project": pool.get("project"),
            "symbol": pool.get("symbol"),
            "tvl_usd": pool.get("tvlUsd"),
            "apy": pool.get("apy"),
            "apy_base": pool.get("apyBase"),
            "apy_reward": pool.get("apyReward"),
            "apy_pct_1d": pool.get("apyPct1D"),
            "apy_pct_7d": pool.get("apyPct7D"),
            "apy_pct_30d": pool.get("apyPct30D"),
            "stablecoin": pool.get("stablecoin", False),
            "il_risk": pool.get("ilRisk"),
            "exposure": pool.get("exposure"),
            "pool_meta": pool.get("poolMeta"),
            "underlying_tokens": pool.get("underlyingTokens"),
            "reward_tokens": pool.get("rewardTokens"),
            "fetched_at": datetime.utcnow(),
        }

    client.close()


@dlt.resource(
    name="defillama_yield_history",
    primary_key=["pool_id", "timestamp"],
    write_disposition="merge",
)
def defillama_yield_history(
    pool_ids: list[str],
) -> Iterator[dict[str, Any]]:
    """
    Fetch historical yield data for specific pools.

    Args:
        pool_ids: List of DeFiLlama pool UUIDs

    Yields:
        Historical yield records
    """
    import httpx

    client = httpx.Client(timeout=60.0)

    for pool_id in pool_ids:
        try:
            response = client.get(f"https://yields.llama.fi/chart/{pool_id}")
            response.raise_for_status()
            data = response.json()

            for point in data.get("data", []):
                yield {
                    "pool_id": pool_id,
                    "timestamp": datetime.fromisoformat(
                        point.get("timestamp").replace("Z", "+00:00")
                    ),
                    "tvl_usd": point.get("tvlUsd"),
                    "apy": point.get("apy"),
                    "apy_base": point.get("apyBase"),
                    "apy_reward": point.get("apyReward"),
                }

        except httpx.HTTPError as e:
            print(f"Error fetching pool {pool_id}: {e}")
            continue

    client.close()


@dlt.resource(
    name="defillama_stablecoins",
    primary_key="id",
    write_disposition="merge",
)
def defillama_stablecoins(
    symbols: Optional[list[str]] = None,
) -> Iterator[dict[str, Any]]:
    """
    Fetch stablecoin data including supply and peg info.

    Args:
        symbols: Optional filter for specific stablecoins

    Yields:
        Stablecoin records
    """
    import httpx

    if symbols is None:
        symbols = ["USDe", "USDC", "USDT", "DAI", "FRAX"]

    client = httpx.Client(timeout=60.0)

    response = client.get("https://stablecoins.llama.fi/stablecoins")
    response.raise_for_status()
    data = response.json()

    for stablecoin in data.get("peggedAssets", []):
        if symbols and stablecoin.get("symbol") not in symbols:
            continue

        yield {
            "id": stablecoin.get("id"),
            "name": stablecoin.get("name"),
            "symbol": stablecoin.get("symbol"),
            "gecko_id": stablecoin.get("gecko_id"),
            "peg_type": stablecoin.get("pegType"),
            "peg_mechanism": stablecoin.get("pegMechanism"),
            "circulating": stablecoin.get("circulating", {}).get("peggedUSD"),
            "price": stablecoin.get("price"),
            "chains": stablecoin.get("chains", []),
            "fetched_at": datetime.utcnow(),
        }

    client.close()


@dlt.resource(
    name="defillama_stablecoin_history",
    primary_key=["stablecoin_id", "timestamp"],
    write_disposition="merge",
)
def defillama_stablecoin_history(
    stablecoin_id: str,
) -> Iterator[dict[str, Any]]:
    """
    Fetch historical supply data for a stablecoin.

    Args:
        stablecoin_id: DeFiLlama stablecoin ID (e.g., "USDe")

    Yields:
        Historical supply records
    """
    import httpx

    client = httpx.Client(timeout=60.0)

    try:
        response = client.get(
            f"https://stablecoins.llama.fi/stablecoin/{stablecoin_id}",
            params={"includeChains": "true"},
        )
        response.raise_for_status()
        data = response.json()

        for point in data.get("peggedSeries", {}).get("usd_mcap", []):
            yield {
                "stablecoin_id": stablecoin_id,
                "timestamp": datetime.utcfromtimestamp(point.get("date")),
                "circulating_usd": point.get("total"),
            }

    except httpx.HTTPError as e:
        print(f"Error fetching stablecoin history for {stablecoin_id}: {e}")

    client.close()


@dlt.resource(
    name="defillama_protocol_tvl",
    primary_key=["protocol", "timestamp"],
    write_disposition="merge",
)
def defillama_protocol_tvl(
    protocols: list[str],
) -> Iterator[dict[str, Any]]:
    """
    Fetch TVL history for protocols.

    Args:
        protocols: List of protocol slugs

    Yields:
        TVL history records
    """
    import httpx

    client = httpx.Client(timeout=60.0)

    for protocol in protocols:
        try:
            response = client.get(f"https://api.llama.fi/protocol/{protocol}")
            response.raise_for_status()
            data = response.json()

            for point in data.get("tvl", []):
                yield {
                    "protocol": protocol,
                    "timestamp": datetime.utcfromtimestamp(point.get("date")),
                    "tvl_usd": point.get("totalLiquidityUSD"),
                }

            # Also yield chain breakdown if available
            for chain, chain_tvl in data.get("chainTvls", {}).items():
                for point in chain_tvl.get("tvl", []):
                    yield {
                        "protocol": protocol,
                        "chain": chain,
                        "timestamp": datetime.utcfromtimestamp(point.get("date")),
                        "tvl_usd": point.get("totalLiquidityUSD"),
                    }

        except httpx.HTTPError as e:
            print(f"Error fetching TVL for {protocol}: {e}")
            continue

    client.close()


# Well-known pool IDs for tracking
KNOWN_POOLS = {
    "susde_ethena": "66985a81-9c51-46ca-9977-42b4fe7bc6df",
    "usde_curve": "7ec46bb7-fbb7-4f40-8e55-cfa9bf0fd867",
    "pendle_susde_mar25": "f4e74e13-c6a5-4aa2-b3d2-2b3dc8e83e71",
}


def run_defillama_pipeline(
    protocols: Optional[list[str]] = None,
    destination_type: str = "duckdb",
):
    """
    Run the DeFiLlama pipeline standalone.

    Args:
        protocols: Protocol slugs to fetch
        destination_type: Target destination
    """
    from pipelines.shared.duckdb_destination import create_pipeline

    if protocols is None:
        protocols = ["ethena", "aave", "lido", "pendle"]

    pipeline, metadata = create_pipeline(
        pipeline_name="defillama",
        destination_type=destination_type,
    )

    # Run all resources
    load_info = pipeline.run(
        [
            defillama_yields(projects=protocols),
            defillama_stablecoins(),
            defillama_protocol_tvl(protocols=protocols),
            defillama_yield_history(pool_ids=list(KNOWN_POOLS.values())),
        ]
    )

    print(f"DeFiLlama pipeline completed: {load_info}")
    return load_info


if __name__ == "__main__":
    run_defillama_pipeline()
