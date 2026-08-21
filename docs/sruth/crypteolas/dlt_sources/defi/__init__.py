"""
DeFi data sources for crypteolas.

Provides DLT sources for:
- Price data (CoinGecko)
- TVL and yields (DeFiLlama)
- Funding rates (Binance, Bybit, OKX)
- Ethereum staking (Beaconchain)
- On-chain DeFi data (Aave, Pendle subgraphs)
"""

from .binance import binance_source
from .bybit import (
    bybit_source,
    bybit_funding_history,
    bybit_open_interest,
    bybit_tickers,
)
from .coingecko import coingecko_source
from .defillama import defillama_source
from .okx import (
    okx_source,
    okx_funding_history,
    okx_current_funding,
    okx_open_interest,
    okx_mark_price,
)
from .beaconchain import (
    beaconchain_source,
    eth_staking_apr,
    eth_network_stats,
    eth_validator_queue,
    eth_rewards_chart,
)
from .subgraphs import (
    aave_subgraph_source,
    aave_reserves,
    aave_user_positions,
    pendle_subgraph_source,
    pendle_markets,
    pendle_swaps,
)

__all__ = [
    # Binance
    "binance_source",
    # Bybit
    "bybit_source",
    "bybit_funding_history",
    "bybit_open_interest",
    "bybit_tickers",
    # CoinGecko
    "coingecko_source",
    # DeFiLlama
    "defillama_source",
    # OKX
    "okx_source",
    "okx_funding_history",
    "okx_current_funding",
    "okx_open_interest",
    "okx_mark_price",
    # Beaconchain
    "beaconchain_source",
    "eth_staking_apr",
    "eth_network_stats",
    "eth_validator_queue",
    "eth_rewards_chart",
    # Subgraphs
    "aave_subgraph_source",
    "aave_reserves",
    "aave_user_positions",
    "pendle_subgraph_source",
    "pendle_markets",
    "pendle_swaps",
]
