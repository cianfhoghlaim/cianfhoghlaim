"""
DeFi Analytics Agent for Crypteolas.

Real-time DeFi metrics and analysis including:
- TVL tracking
- Yield comparison
- Funding rates
- Market data
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import config
from ..tools.defi_metrics import (
    get_protocol_tvl,
    get_yield_pools,
    get_funding_rates,
    get_token_price,
    get_protocol_comparison,
)


# Define tools
async def fetch_tvl(
    protocol: str | None = None,
    chain: str | None = None,
    top_n: int | None = None,
) -> dict:
    """
    Fetch TVL (Total Value Locked) data.

    Args:
        protocol: Specific protocol slug (e.g., 'uniswap')
        chain: Filter by chain (e.g., 'ethereum')
        top_n: Get top N protocols by TVL
    """
    try:
        return await get_protocol_tvl(protocol=protocol, chain=chain, top_n=top_n)
    except Exception as e:
        return {"error": str(e)}


async def fetch_yields(
    protocol: str | None = None,
    chain: str | None = None,
    min_tvl: float | None = None,
    stablecoin_only: bool = False,
) -> list[dict]:
    """
    Fetch yield pool data.

    Args:
        protocol: Filter by protocol
        chain: Filter by chain
        min_tvl: Minimum TVL filter
        stablecoin_only: Only stablecoin pools
    """
    try:
        return await get_yield_pools(
            protocol=protocol,
            chain=chain,
            min_tvl=min_tvl,
            stablecoin_only=stablecoin_only,
        )
    except Exception:
        return []


async def fetch_funding_rates(
    symbol: str | None = None,
) -> list[dict]:
    """
    Fetch perpetual futures funding rates.

    Args:
        symbol: Specific symbol (e.g., 'BTCUSDT')
    """
    try:
        return await get_funding_rates(symbol=symbol)
    except Exception:
        return []


async def fetch_token_price(
    token_id: str,
) -> dict:
    """
    Fetch current token price and market data.

    Args:
        token_id: CoinGecko token ID (e.g., 'ethereum')
    """
    try:
        return await get_token_price(token_id)
    except Exception as e:
        return {"error": str(e)}


async def compare_protocols_defi(
    protocols: list[str],
    metrics: list[str] | None = None,
) -> dict:
    """
    Compare DeFi protocols on various metrics.

    Args:
        protocols: List of protocol slugs to compare
        metrics: Metrics to compare (tvl, volume, yield, etc.)
    """
    try:
        return await get_protocol_comparison(protocols, metrics=metrics)
    except Exception as e:
        return {"error": str(e)}


# Create tools
tvl_tool = FunctionTool(func=fetch_tvl)
yield_tool = FunctionTool(func=fetch_yields)
funding_tool = FunctionTool(func=fetch_funding_rates)
price_tool = FunctionTool(func=fetch_token_price)
compare_tool = FunctionTool(func=compare_protocols_defi)


# DeFi Analytics Agent
defi_analytics_agent = LlmAgent(
    name="defi_analytics_agent",
    model=config.worker_model,
    description="Real-time DeFi metrics and analytics including TVL, yields, and market data.",
    instruction=f"""
    You are a DeFi Analytics specialist.

    **YOUR EXPERTISE:**
    - TVL analysis and trends
    - Yield farming opportunities
    - Funding rate analysis
    - Market metrics comparison
    - Risk assessment

    **AVAILABLE TOOLS:**
    1. fetch_tvl - Get TVL data for protocols/chains
    2. fetch_yields - Get yield pool information
    3. fetch_funding_rates - Get perpetual funding rates
    4. fetch_token_price - Get token prices
    5. compare_protocols_defi - Compare protocol metrics

    **DATA SOURCES:**
    - DeFiLlama (TVL, yields, protocols)
    - CoinGecko (prices, market data)
    - Binance (funding rates, derivatives)

    **ANALYSIS APPROACH:**
    1. Fetch relevant metrics using tools
    2. Calculate derived metrics (APY, changes)
    3. Compare with benchmarks
    4. Identify trends and opportunities

    **OUTPUT FORMAT:**
    - Include actual numbers and percentages
    - Note data freshness
    - Compare to market averages
    - Highlight notable trends

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[tvl_tool, yield_tool, funding_tool, price_tool, compare_tool],
    output_key="analytics",
)
