"""
API source assets for crypto data ingestion.

Ingests data from:
- CoinGecko (token prices)
- DeFiLlama (TVL and yields)
- Binance (funding rates - hourly partitioned)
- Aave V3 subgraph (reserves and positions)
- Pendle subgraph (markets and swaps)
"""

from datetime import datetime
from typing import Any

import dlt
from dagster import (
    asset,
    AssetExecutionContext,
    Definitions,
    MetadataValue,
    Output,
)

from crypteolas.defs._partitions import hourly_partitions
from crypteolas.defs._helpers import get_duckdb_path


@asset(
    group_name="api_sources",
    metadata={
        "description": "CoinGecko price data for crypto tokens",
    },
)
def coingecko_assets(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    """CoinGecko price data assets."""
    from crypteolas.pipelines.sources.coingecko import coingecko_prices

    tokens = ["ethena-usde", "ethena-staked-usde", "ethereum"]

    pipeline = dlt.pipeline(
        pipeline_name="coingecko_prices",
        destination=dlt.destinations.duckdb(get_duckdb_path()),
        dataset_name="crypto_prices",
    )

    context.log.info(f"Fetching CoinGecko data for {tokens}")

    load_info = pipeline.run(
        coingecko_prices(token_ids=tokens, days=30),
    )

    return Output(
        value={"load_info": str(load_info), "tokens": tokens},
        metadata={
            "tokens_fetched": MetadataValue.int(len(tokens)),
            "pipeline": "coingecko_prices",
        },
    )


@asset(
    group_name="api_sources",
    metadata={
        "description": "DeFiLlama TVL and yield data",
    },
)
def defillama_assets(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    """DeFiLlama TVL and yield assets."""
    from crypteolas.pipelines.sources.defillama import defillama_yields, defillama_protocol_tvl

    protocols = ["ethena", "aave", "pendle", "lido"]

    pipeline = dlt.pipeline(
        pipeline_name="defillama",
        destination=dlt.destinations.duckdb(get_duckdb_path()),
        dataset_name="defi_metrics",
    )

    context.log.info(f"Fetching DeFiLlama data for {protocols}")

    # Run yields
    load_info_yields = pipeline.run(defillama_yields(projects=protocols))

    # Run TVL
    load_info_tvl = pipeline.run(defillama_protocol_tvl(protocols=protocols))

    return Output(
        value={
            "yields_load_info": str(load_info_yields),
            "tvl_load_info": str(load_info_tvl),
            "protocols": protocols,
        },
        metadata={
            "protocols_fetched": MetadataValue.int(len(protocols)),
            "pipeline": "defillama",
        },
    )


@asset(
    group_name="api_sources",
    partitions_def=hourly_partitions,
    metadata={
        "description": "Binance funding rate data (hourly)",
    },
)
def binance_funding_assets(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    """Binance funding rate assets (hourly incremental)."""
    from crypteolas.pipelines.sources.binance import binance_funding_rates

    # Get partition time window
    partition_key = context.partition_key
    start_dt = datetime.fromisoformat(partition_key)
    start_ms = int(start_dt.timestamp() * 1000)

    symbols = ["ETHUSDT", "BTCUSDT"]

    pipeline = dlt.pipeline(
        pipeline_name="binance_funding",
        destination=dlt.destinations.duckdb(get_duckdb_path()),
        dataset_name="funding_rates",
    )

    context.log.info(f"Fetching Binance funding rates for {symbols} from {partition_key}")

    load_info = pipeline.run(
        binance_funding_rates(symbols=symbols, start_time=start_ms),
    )

    return Output(
        value={"load_info": str(load_info), "symbols": symbols, "partition": partition_key},
        metadata={
            "symbols_fetched": MetadataValue.int(len(symbols)),
            "partition_key": partition_key,
        },
    )


@asset(
    group_name="api_sources",
    metadata={
        "description": "Aave V3 subgraph data (reserves and positions)",
    },
)
def aave_subgraph_assets(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    """Aave V3 subgraph assets."""
    from crypteolas.pipelines.sources.subgraphs import aave_reserves, aave_user_positions

    pipeline = dlt.pipeline(
        pipeline_name="subgraphs",
        destination=dlt.destinations.duckdb(get_duckdb_path()),
        dataset_name="subgraph_data",
    )

    context.log.info("Fetching Aave V3 subgraph data")

    load_info_reserves = pipeline.run(aave_reserves())
    load_info_positions = pipeline.run(aave_user_positions(min_health_factor=1.5))

    return Output(
        value={
            "reserves_load_info": str(load_info_reserves),
            "positions_load_info": str(load_info_positions),
        },
        metadata={
            "source": "aave_v3_subgraph",
        },
    )


@asset(
    group_name="api_sources",
    metadata={
        "description": "Pendle subgraph data (markets and swaps)",
    },
)
def pendle_subgraph_assets(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    """Pendle subgraph assets."""
    from crypteolas.pipelines.sources.subgraphs import pendle_markets, pendle_swaps

    pipeline = dlt.pipeline(
        pipeline_name="subgraphs",
        destination=dlt.destinations.duckdb(get_duckdb_path()),
        dataset_name="subgraph_data",
    )

    context.log.info("Fetching Pendle subgraph data")

    load_info_markets = pipeline.run(pendle_markets())
    load_info_swaps = pipeline.run(pendle_swaps(first=500))

    return Output(
        value={
            "markets_load_info": str(load_info_markets),
            "swaps_load_info": str(load_info_swaps),
        },
        metadata={
            "source": "pendle_subgraph",
        },
    )


# Export definitions for load_from_defs_folder
defs = Definitions(
    assets=[
        coingecko_assets,
        defillama_assets,
        binance_funding_assets,
        aave_subgraph_assets,
        pendle_subgraph_assets,
    ],
)
