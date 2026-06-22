"""
The Graph subgraph sources for DeFi protocol data.

Provides GraphQL-based data ingestion for Aave, Pendle, and other protocols
with on-chain subgraph indexing.

Note: The Graph hosted service was deprecated in 2024. These endpoints now use
the decentralized network which requires an API key (THEGRAPH_API_KEY).
"""

import os
from datetime import datetime
from typing import Any, Iterator, Optional

import dlt
import httpx


def _get_subgraph_url(subgraph_id: str) -> str:
    """Build subgraph URL using The Graph decentralized network."""
    api_key = os.environ.get("THEGRAPH_API_KEY", "")
    if api_key:
        # Use main gateway with API key in path
        return f"https://gateway.thegraph.com/api/{api_key}/subgraphs/id/{subgraph_id}"
    # No API key - queries will fail (decentralized network requires auth)
    return f"https://gateway.thegraph.com/api/subgraphs/id/{subgraph_id}"


# Subgraph IDs from The Graph decentralized network
# ETH Mainnet V3: https://thegraph.com/explorer/subgraphs/Cd2gEDVeqnjBn1hSeqFMitw8Q1iiyV9FYUZkLNRcL87g
AAVE_V3_SUBGRAPH_ID = "Cd2gEDVeqnjBn1hSeqFMitw8Q1iiyV9FYUZkLNRcL87g"
# Pendle V2 Mainnet: https://thegraph.com/explorer/subgraphs/ExXGU3ub2nrT5stPk5cH4hSk2qunJcMcP8eX5GAhrZhe
PENDLE_V2_SUBGRAPH_ID = "ExXGU3ub2nrT5stPk5cH4hSk2qunJcMcP8eX5GAhrZhe"


def get_aave_subgraph_url() -> str:
    """Get Aave V3 subgraph URL (computed at runtime to pick up env vars)."""
    return _get_subgraph_url(AAVE_V3_SUBGRAPH_ID)


def get_pendle_subgraph_url() -> str:
    """Get Pendle V2 subgraph URL (computed at runtime to pick up env vars)."""
    return _get_subgraph_url(PENDLE_V2_SUBGRAPH_ID)


# Legacy constants for backwards compatibility (computed at import time)
AAVE_V3_SUBGRAPH = _get_subgraph_url(AAVE_V3_SUBGRAPH_ID)
PENDLE_SUBGRAPH = _get_subgraph_url(PENDLE_V2_SUBGRAPH_ID)


def _get_graphql_client(endpoint: str) -> httpx.Client:
    """Get HTTP client for GraphQL endpoints."""
    return httpx.Client(
        base_url=endpoint,
        timeout=30.0,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "sruth-crypteolas/1.0",
        },
    )


def _execute_graphql(
    endpoint: str,
    query: str,
    variables: Optional[dict] = None,
) -> dict[str, Any]:
    """Execute a GraphQL query."""
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            endpoint,  # Use full URL directly (no base_url to avoid trailing slash issues)
            headers={
                "Content-Type": "application/json",
                "User-Agent": "sruth-crypteolas/1.0",
            },
            json={"query": query, "variables": variables or {}},
        )
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            raise ValueError(f"GraphQL errors: {data['errors']}")

        return data.get("data", {})


@dlt.resource(
    name="aave_reserves",
    primary_key="id",
    write_disposition="merge",
)
def aave_reserves(
    last_updated: Optional[int] = None,
    first: int = 1000,
) -> Iterator[dict[str, Any]]:
    """
    Fetch Aave V3 reserve data with lending rates and utilization.

    Args:
        last_updated: Filter by lastUpdateTimestamp (Unix timestamp)
        first: Max records to fetch

    Yields:
        Reserve records with calculated APR/APY
    """
    if last_updated is None:
        # Default to 24 hours ago
        last_updated = int(datetime.utcnow().timestamp()) - 86400

    query = """
    query Reserves($lastUpdated: Int!, $first: Int!) {
      reserves(
        first: $first
        orderBy: lastUpdateTimestamp
        orderDirection: asc
        where: { lastUpdateTimestamp_gte: $lastUpdated }
      ) {
        id
        name
        symbol
        decimals
        lastUpdateTimestamp
        liquidityRate
        variableBorrowRate
        stableBorrowRate
        totalATokenSupply
        totalCurrentVariableDebt
        totalPrincipalStableDebt
        utilizationRate
        availableLiquidity
        isActive
        isFrozen
        borrowingEnabled
        stableBorrowRateEnabled
        reserveFactor
        baseLTVasCollateral
        reserveLiquidationThreshold
        reserveLiquidationBonus
      }
    }
    """

    data = _execute_graphql(
        get_aave_subgraph_url(),
        query,
        {"lastUpdated": last_updated, "first": first},
    )

    for reserve in data.get("reserves", []):
        # Convert ray values (1e27) to decimal APR
        liquidity_rate = int(reserve.get("liquidityRate", 0))
        borrow_rate = int(reserve.get("variableBorrowRate", 0))

        yield {
            "id": reserve["id"],
            "name": reserve["name"],
            "symbol": reserve["symbol"],
            "decimals": int(reserve.get("decimals", 18)),
            "lastUpdateTimestamp": datetime.utcfromtimestamp(
                int(reserve["lastUpdateTimestamp"])
            ),
            # APR calculations (ray = 1e27)
            "supplyAPR": liquidity_rate / 1e27,
            "borrowAPR": borrow_rate / 1e27,
            "stableBorrowRate": int(reserve.get("stableBorrowRate", 0)) / 1e27,
            # Supply/borrow totals
            "totalSupply": reserve.get("totalATokenSupply"),
            "totalVariableDebt": reserve.get("totalCurrentVariableDebt"),
            "totalStableDebt": reserve.get("totalPrincipalStableDebt"),
            "availableLiquidity": reserve.get("availableLiquidity"),
            # Utilization
            "utilizationRate": float(reserve.get("utilizationRate", 0)) / 1e27,
            # Risk parameters
            "ltv": float(reserve.get("baseLTVasCollateral", 0)) / 10000,
            "liquidationThreshold": float(
                reserve.get("reserveLiquidationThreshold", 0)
            )
            / 10000,
            "liquidationBonus": float(reserve.get("reserveLiquidationBonus", 0))
            / 10000,
            "reserveFactor": float(reserve.get("reserveFactor", 0)) / 10000,
            # Status
            "isActive": reserve.get("isActive", False),
            "isFrozen": reserve.get("isFrozen", False),
            "borrowingEnabled": reserve.get("borrowingEnabled", False),
            "protocol": "aave_v3",
            "chain": "ethereum",
            "fetched_at": datetime.utcnow(),
        }


@dlt.resource(
    name="aave_user_positions",
    primary_key=["id"],
    write_disposition="merge",
)
def aave_user_positions(
    first: int = 1000,
) -> Iterator[dict[str, Any]]:
    """
    Fetch Aave user reserve positions.

    Note: The Aave V3 subgraph schema changed - healthFactor, totalCollateralUSD,
    totalDebtUSD are no longer on the User entity. We now query userReserves directly.

    Args:
        first: Max records

    Yields:
        User reserve position records
    """
    query = """
    query UserReserves($first: Int!) {
      userReserves(first: $first, orderBy: currentATokenBalance, orderDirection: desc) {
        id
        user {
          id
        }
        reserve {
          symbol
          name
          decimals
        }
        currentATokenBalance
        currentVariableDebt
        currentStableDebt
        scaledATokenBalance
        scaledVariableDebt
        usageAsCollateralEnabledOnUser
      }
    }
    """

    data = _execute_graphql(get_aave_subgraph_url(), query, {"first": first})

    for position in data.get("userReserves", []):
        yield {
            "id": position["id"],
            "user": position["user"]["id"],
            "reserve": position["reserve"]["symbol"],
            "reserveName": position["reserve"]["name"],
            "decimals": int(position["reserve"].get("decimals", 18)),
            "aTokenBalance": position.get("currentATokenBalance"),
            "variableDebt": position.get("currentVariableDebt"),
            "stableDebt": position.get("currentStableDebt"),
            "scaledATokenBalance": position.get("scaledATokenBalance"),
            "scaledVariableDebt": position.get("scaledVariableDebt"),
            "usageAsCollateralEnabled": position.get("usageAsCollateralEnabledOnUser"),
            "protocol": "aave_v3",
            "chain": "ethereum",
            "fetched_at": datetime.utcnow(),
        }


@dlt.source(name="aave_subgraph")
def aave_subgraph_source(
    last_updated: Optional[int] = None,
) -> Iterator[dlt.resource]:
    """
    Aave V3 subgraph data source.

    Args:
        last_updated: Filter reserves updated after timestamp

    Yields:
        Aave data resources
    """
    yield aave_reserves(last_updated=last_updated)
    yield aave_user_positions()


@dlt.resource(
    name="pendle_markets",
    primary_key="id",
    write_disposition="merge",
)
def pendle_markets(
    min_expiry: Optional[int] = None,
    first: int = 100,
) -> Iterator[dict[str, Any]]:
    """
    Fetch Pendle markets with PT/YT token info.

    Note: The Pendle V2 subgraph schema changed - priceUSD, totalPt, totalSy,
    impliedApy, underlyingApy, totalValueLockedUSD, volumeUSD are no longer available.

    Args:
        min_expiry: Minimum expiry timestamp (filter expired markets)
        first: Max records

    Yields:
        Market records with basic token info
    """
    if min_expiry is None:
        min_expiry = int(datetime.utcnow().timestamp())

    query = """
    query Markets($minExpiry: Int!, $first: Int!) {
      markets(
        first: $first
        where: { expiry_gt: $minExpiry }
        orderBy: expiry
        orderDirection: asc
      ) {
        id
        expiry
        pt {
          id
          symbol
          name
          decimals
        }
        yt {
          id
          symbol
          name
          decimals
        }
        sy {
          id
          symbol
          name
          decimals
        }
      }
    }
    """

    data = _execute_graphql(
        get_pendle_subgraph_url(),
        query,
        {"minExpiry": min_expiry, "first": first},
    )

    for market in data.get("markets", []):
        expiry = int(market.get("expiry", 0))
        expiry_dt = datetime.utcfromtimestamp(expiry)
        days_to_maturity = (expiry_dt - datetime.utcnow()).days

        yield {
            "id": market["id"],
            "expiry": expiry_dt,
            "daysToMaturity": max(0, days_to_maturity),
            # PT (Principal Token)
            "ptId": market.get("pt", {}).get("id"),
            "ptSymbol": market.get("pt", {}).get("symbol"),
            "ptName": market.get("pt", {}).get("name"),
            "ptDecimals": market.get("pt", {}).get("decimals"),
            # YT (Yield Token)
            "ytId": market.get("yt", {}).get("id"),
            "ytSymbol": market.get("yt", {}).get("symbol"),
            "ytName": market.get("yt", {}).get("name"),
            "ytDecimals": market.get("yt", {}).get("decimals"),
            # SY (Standardized Yield)
            "syId": market.get("sy", {}).get("id"),
            "sySymbol": market.get("sy", {}).get("symbol"),
            "syName": market.get("sy", {}).get("name"),
            "syDecimals": market.get("sy", {}).get("decimals"),
            "protocol": "pendle",
            "chain": "ethereum",
            "fetched_at": datetime.utcnow(),
        }


@dlt.resource(
    name="pendle_swaps",
    primary_key=["id"],
    write_disposition="merge",
)
def pendle_swaps(
    market_id: Optional[str] = None,
    first: int = 1000,
) -> Iterator[dict[str, Any]]:
    """
    Fetch Pendle swap transactions for volume analysis.

    Args:
        market_id: Optional filter by market
        first: Max records

    Yields:
        Swap transaction records
    """
    where_clause = ""
    if market_id:
        where_clause = f'where: {{ market: "{market_id}" }}'

    query = f"""
    query Swaps($first: Int!) {{
      swaps(first: $first, orderBy: timestamp, orderDirection: desc, {where_clause}) {{
        id
        timestamp
        market {{
          id
        }}
        caller
        netPtOut
        netSyOut
        amountUSD
      }}
    }}
    """

    data = _execute_graphql(get_pendle_subgraph_url(), query, {"first": first})

    for swap in data.get("swaps", []):
        yield {
            "id": swap["id"],
            "timestamp": datetime.utcfromtimestamp(int(swap["timestamp"])),
            "marketId": swap.get("market", {}).get("id"),
            "caller": swap.get("caller"),
            "netPtOut": swap.get("netPtOut"),
            "netSyOut": swap.get("netSyOut"),
            "amountUSD": float(swap.get("amountUSD", 0)),
            "protocol": "pendle",
            "fetched_at": datetime.utcnow(),
        }


@dlt.source(name="pendle_subgraph")
def pendle_subgraph_source() -> Iterator[dlt.resource]:
    """
    Pendle subgraph data source.

    Note: The Pendle V2 subgraph schema changed significantly.
    The 'swaps' query is no longer available.

    Yields:
        Pendle markets data
    """
    yield pendle_markets()
    # pendle_swaps removed - 'swaps' query no longer exists in schema


def run_subgraph_pipeline(
    protocols: Optional[list[str]] = None,
    destination: str = "duckdb",
    dataset_name: str = "defi_raw",
):
    """
    Run subgraph pipelines standalone.

    Args:
        protocols: List of protocols ("aave", "pendle")
        destination: Target destination type
        dataset_name: Dataset name for DuckDB
    """
    if protocols is None:
        protocols = ["aave", "pendle"]

    pipeline = dlt.pipeline(
        pipeline_name="defi_subgraphs",
        destination=destination,
        dataset_name=dataset_name,
    )

    sources = []
    if "aave" in protocols:
        sources.append(aave_subgraph_source())
    if "pendle" in protocols:
        sources.append(pendle_subgraph_source())

    for source in sources:
        load_info = pipeline.run(source)
        print(f"Subgraph pipeline completed: {load_info}")

    return pipeline


if __name__ == "__main__":
    run_subgraph_pipeline()
