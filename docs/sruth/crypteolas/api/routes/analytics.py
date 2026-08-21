"""
Analytics Routes for Crypteolas API.

Provides DeFi analytics endpoints.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
import structlog

from agents.tools.defi_metrics import (  # type: ignore
    get_protocol_tvl,
    get_yield_pools,
    get_funding_rates,
    get_token_price,
    get_protocol_comparison,
)

logger = structlog.get_logger()

router = APIRouter()


class TVLRequest(BaseModel):
    """TVL request model."""

    protocol: str | None = None
    chain: str | None = None
    top_n: int | None = None


class YieldsRequest(BaseModel):
    """Yields request model."""

    protocol: str | None = None
    chain: str | None = None
    min_tvl: float | None = None
    stablecoin_only: bool = False


class ComparisonRequest(BaseModel):
    """Protocol comparison request model."""

    protocols: list[str]
    metrics: list[str] | None = None


@router.post("/tvl")
async def get_tvl_endpoint(request: TVLRequest):
    """
    Get Total Value Locked (TVL) data.

    Filter by protocol, chain, or get top N protocols.
    """
    try:
        result = await get_protocol_tvl(
            protocol=request.protocol,
            chain=request.chain,
            top_n=request.top_n,
        )
        return {"data": result, "status": "success"}
    except Exception as e:
        logger.error("TVL fetch error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.get("/tvl")
async def get_tvl_get(
    protocol: str | None = Query(None, description="Protocol slug"),
    chain: str | None = Query(None, description="Chain filter"),
    top_n: int | None = Query(None, description="Top N protocols"),
):
    """GET endpoint for TVL data."""
    return await get_tvl_endpoint(TVLRequest(protocol=protocol, chain=chain, top_n=top_n))


@router.post("/yields")
async def get_yields_endpoint(request: YieldsRequest):
    """
    Get yield pool data.

    Filter by protocol, chain, minimum TVL, or stablecoins only.
    """
    try:
        result = await get_yield_pools(
            protocol=request.protocol,
            chain=request.chain,
            min_tvl=request.min_tvl,
            stablecoin_only=request.stablecoin_only,
        )
        return {"data": result, "count": len(result), "status": "success"}
    except Exception as e:
        logger.error("Yields fetch error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.get("/yields")
async def get_yields_get(
    protocol: str | None = Query(None, description="Protocol filter"),
    chain: str | None = Query(None, description="Chain filter"),
    min_tvl: float | None = Query(None, description="Minimum TVL"),
    stablecoin_only: bool = Query(False, description="Stablecoins only"),
):
    """GET endpoint for yields data."""
    return await get_yields_endpoint(
        YieldsRequest(
            protocol=protocol,
            chain=chain,
            min_tvl=min_tvl,
            stablecoin_only=stablecoin_only,
        )
    )


@router.get("/funding-rates")
async def get_funding_rates_endpoint(
    symbol: str | None = Query(None, description="Symbol filter (e.g., BTCUSDT)"),
):
    """
    Get perpetual futures funding rates.

    Data from Binance Futures.
    """
    try:
        result = await get_funding_rates(symbol=symbol)
        return {"data": result, "count": len(result), "status": "success"}
    except Exception as e:
        logger.error("Funding rates fetch error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.get("/price/{token_id}")
async def get_price_endpoint(token_id: str):
    """
    Get token price and market data.

    Data from CoinGecko.
    """
    try:
        result = await get_token_price(token_id)
        return {"data": result, "status": "success"}
    except Exception as e:
        logger.error("Price fetch error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.post("/compare")
async def compare_protocols_endpoint(request: ComparisonRequest):
    """
    Compare multiple protocols on various metrics.

    Compare TVL, volume, yields, and other metrics.
    """
    try:
        result = await get_protocol_comparison(
            protocols=request.protocols,
            metrics=request.metrics,
        )
        return {"data": result, "status": "success"}
    except Exception as e:
        logger.error("Comparison error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.get("/summary")
async def get_defi_summary():
    """
    Get DeFi market summary.

    Includes top protocols, yields, and key metrics.
    """
    try:
        # Get top protocols by TVL
        top_protocols = await get_protocol_tvl(top_n=10)

        # Get top yields
        top_yields = await get_yield_pools(min_tvl=1000000)

        # Get funding rates
        funding_rates = await get_funding_rates()

        return {
            "data": {
                "top_protocols": top_protocols.get("protocols", [])[:5]
                if isinstance(top_protocols, dict)
                else [],
                "top_yields": top_yields[:5] if isinstance(top_yields, list) else [],
                "funding_rates": funding_rates[:5] if isinstance(funding_rates, list) else [],
            },
            "status": "success",
        }
    except Exception as e:
        logger.error("Summary fetch error", error=str(e))
        return {"error": str(e), "status": "error"}
