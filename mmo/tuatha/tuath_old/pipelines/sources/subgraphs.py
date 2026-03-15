"""
The Graph subgraph sources for DeFi protocol data.

Provides GraphQL-based data ingestion for Aave, Pendle, and other protocols
with on-chain subgraph indexing.
"""

from datetime import datetime
from typing import Any, Iterator, Optional

import dlt


AAVE_V3_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/aave/protocol-v3"
PENDLE_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/pendle-finance/core-mainnet"


def _execute_graphql(
    endpoint: str,
    query: str,
    variables: Optional[dict] = None,
) -> dict[str, Any]:
    """Execute a GraphQL query."""
    import httpx

    response = httpx.post(
        endpoint,
        json={"query": query, "variables": variables or {}},
        timeout=60.0,
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
        priceInUsd
        priceInEth
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
        AAVE_V3_SUBGRAPH,
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
            # Prices
            "priceUSD": float(reserve.get("priceInUsd", 0)),
            "priceETH": float(reserve.get("priceInEth", 0)),
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
    primary_key=["user", "reserve"],
    write_disposition="merge",
)
def aave_user_positions(
    min_health_factor: Optional[float] = None,
    first: int = 1000,
) -> Iterator[dict[str, Any]]:
    """
    Fetch Aave user positions for liquidation risk analysis.

    Args:
        min_health_factor: Filter positions with health factor below threshold
        first: Max records

    Yields:
        User position records
    """
    # Build where clause
    where_clause = ""
    if min_health_factor:
        hf_ray = int(min_health_factor * 1e18)
        where_clause = f"where: {{ healthFactor_lt: \"{hf_ray}\" }}"

    query = f"""
    query UserPositions($first: Int!) {{
      users(first: $first, orderBy: healthFactor, orderDirection: asc, {where_clause}) {{
        id
        healthFactor
        totalCollateralUSD
        totalDebtUSD
        reserves {{
          reserve {{
            symbol
            name
          }}
          currentATokenBalance
          currentVariableDebt
          currentStableDebt
        }}
      }}
    }}
    """

    data = _execute_graphql(AAVE_V3_SUBGRAPH, query, {"first": first})

    for user in data.get("users", []):
        health_factor = int(user.get("healthFactor", 0))

        for position in user.get("reserves", []):
            yield {
                "user": user["id"],
                "reserve": position["reserve"]["symbol"],
                "healthFactor": health_factor / 1e18 if health_factor else None,
                "totalCollateralUSD": float(user.get("totalCollateralUSD", 0)),
                "totalDebtUSD": float(user.get("totalDebtUSD", 0)),
                "aTokenBalance": position.get("currentATokenBalance"),
                "variableDebt": position.get("currentVariableDebt"),
                "stableDebt": position.get("currentStableDebt"),
                "protocol": "aave_v3",
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
    yield aave_user_positions(min_health_factor=1.5)  # At-risk positions


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
    Fetch Pendle markets with PT/YT pricing and implied APY.

    Args:
        min_expiry: Minimum expiry timestamp (filter expired markets)
        first: Max records

    Yields:
        Market records with calculated implied APY
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
          priceUSD
        }
        yt {
          id
          symbol
          name
          priceUSD
        }
        sy {
          id
          symbol
          name
          priceUSD
        }
        totalPt
        totalSy
        impliedApy
        underlyingApy
        totalValueLockedUSD
        volumeUSD
      }
    }
    """

    data = _execute_graphql(
        PENDLE_SUBGRAPH,
        query,
        {"minExpiry": min_expiry, "first": first},
    )

    for market in data.get("markets", []):
        expiry = int(market.get("expiry", 0))
        expiry_dt = datetime.utcfromtimestamp(expiry)
        days_to_maturity = (expiry_dt - datetime.utcnow()).days

        # Calculate implied fixed APY from PT price
        pt_price = float(market.get("pt", {}).get("priceUSD", 0))
        implied_apy = 0
        if pt_price > 0 and days_to_maturity > 0:
            # Implied yield = (1 - PT price) / PT price * (365 / days to maturity)
            implied_apy = ((1 / pt_price) - 1) * (365 / days_to_maturity)

        yield {
            "id": market["id"],
            "expiry": expiry_dt,
            "daysToMaturity": max(0, days_to_maturity),
            # PT (Principal Token)
            "ptId": market.get("pt", {}).get("id"),
            "ptSymbol": market.get("pt", {}).get("symbol"),
            "ptPriceUSD": pt_price,
            # YT (Yield Token)
            "ytId": market.get("yt", {}).get("id"),
            "ytSymbol": market.get("yt", {}).get("symbol"),
            "ytPriceUSD": float(market.get("yt", {}).get("priceUSD", 0)),
            # SY (Standardized Yield)
            "syId": market.get("sy", {}).get("id"),
            "sySymbol": market.get("sy", {}).get("symbol"),
            # Liquidity
            "totalPt": market.get("totalPt"),
            "totalSy": market.get("totalSy"),
            "tvlUSD": float(market.get("totalValueLockedUSD", 0)),
            "volumeUSD": float(market.get("volumeUSD", 0)),
            # Yields
            "impliedAPY": implied_apy,
            "subgraphImpliedApy": float(market.get("impliedApy", 0)),
            "underlyingAPY": float(market.get("underlyingApy", 0)),
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

    data = _execute_graphql(PENDLE_SUBGRAPH, query, {"first": first})

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

    Yields:
        Pendle markets and swap data
    """
    yield pendle_markets()
    yield pendle_swaps(first=500)


def run_subgraph_pipeline(
    protocols: Optional[list[str]] = None,
    destination_type: str = "duckdb",
):
    """
    Run subgraph pipelines standalone.

    Args:
        protocols: List of protocols ("aave", "pendle")
        destination_type: Target destination
    """
    from pipelines.shared.duckdb_destination import create_pipeline

    if protocols is None:
        protocols = ["aave", "pendle"]

    pipeline, metadata = create_pipeline(
        pipeline_name="defi_subgraphs",
        destination_type=destination_type,
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
