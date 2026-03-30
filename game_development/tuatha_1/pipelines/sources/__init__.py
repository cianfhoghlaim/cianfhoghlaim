"""
DLT source modules for cryptocurrency data ingestion.

Each module provides a dlt.source for a specific data provider.
"""

from pipelines.sources.coingecko import coingecko_source
from pipelines.sources.defillama import defillama_source
from pipelines.sources.binance import binance_funding_source
from pipelines.sources.subgraphs import aave_subgraph_source, pendle_subgraph_source

__all__ = [
    "coingecko_source",
    "defillama_source",
    "binance_funding_source",
    "aave_subgraph_source",
    "pendle_subgraph_source",
]
