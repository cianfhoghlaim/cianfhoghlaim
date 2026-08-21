"""
DeFi Assets for Crypteolas.

Ingests protocol metrics, token prices, and funding rates using DLT.
Uses DuckLake destination for concurrency-safe parallel writes.
"""

import os
from pathlib import Path

import yaml
from dagster import (
    AssetExecutionContext,
    MetadataValue,
    StaticPartitionsDefinition,
    asset,
)

from dlt_utils import get_dlt_destination, create_pipeline


def load_protocol_config() -> list[dict]:
    """Load protocol configuration from YAML."""
    config_path = Path(__file__).parent.parent / "config" / "protocols.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config.get("protocols", [])
    return []


def load_token_config() -> list[dict]:
    """Load token configuration from YAML."""
    config_path = Path(__file__).parent.parent / "config" / "tokens.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            tokens_config = config.get("tokens", {})
            # Flatten nested categories (major, defi_governance, etc.) into a single list
            all_tokens = []
            for category_tokens in tokens_config.values():
                if isinstance(category_tokens, list):
                    all_tokens.extend(category_tokens)
            return all_tokens
    return []


def _get_protocol_slugs() -> list[str]:
    """Extract protocol slugs from config for static partitions."""
    config_path = Path(__file__).parent.parent / "config" / "protocols.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            protocols_config = config.get("protocols", {})
            # Flatten nested categories (dexes, lending, etc.) into slugs
            slugs = []
            for category_protocols in protocols_config.values():
                if isinstance(category_protocols, list):
                    for protocol in category_protocols:
                        if isinstance(protocol, dict) and "slug" in protocol:
                            slugs.append(protocol["slug"])
            if slugs:
                return slugs
    # Fallback defaults
    return [
        "uniswap",
        "curve-dex",
        "sushiswap",
        "aave",
        "compound",
        "morpho",
        "lido",
        "rocket-pool",
        "gmx",
        "synthetix",
        "stargate",
        "across",
    ]


def _get_chain_keys() -> list[str]:
    """Extract unique chains from protocol config for static partitions."""
    config_path = Path(__file__).parent.parent / "config" / "protocols.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            protocols_config = config.get("protocols", {})
            # Extract chains from all protocols across categories
            chains = set()
            for category_protocols in protocols_config.values():
                if isinstance(category_protocols, list):
                    for protocol in category_protocols:
                        if isinstance(protocol, dict) and "chains" in protocol:
                            chains.update(protocol["chains"])
            if chains:
                return sorted(chains)
    # Fallback defaults
    return ["arbitrum", "avalanche", "base", "bsc", "ethereum", "optimism", "polygon"]


# Static partitions from config
protocol_partitions = StaticPartitionsDefinition(_get_protocol_slugs())
chain_partitions = StaticPartitionsDefinition(_get_chain_keys())


@asset(
    partitions_def=protocol_partitions,
    group_name="defi",
    description="Protocol TVL data from DeFiLlama",
)
def protocol_tvl(context: AssetExecutionContext) -> dict:
    """Fetch TVL for a protocol from DeFiLlama."""
    from dlt_sources.defi.defillama import defillama_source

    protocol_slug = context.partition_key

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="defillama_tvl",
        dataset_name="defi",
    )

    source = defillama_source(
        protocol_slugs=[protocol_slug],
        include_protocols=True,
        include_chains=False,
        include_yields=False,
        include_stablecoins=False,
    )

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "protocol": protocol_slug,
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {
        "protocol": protocol_slug,
        "status": "success",
    }


@asset(
    partitions_def=protocol_partitions,
    group_name="defi",
    description="Protocol yield/pool data from DeFiLlama",
)
def protocol_yields(context: AssetExecutionContext) -> dict:
    """Fetch yield opportunities for a protocol."""
    from dlt_sources.defi.defillama import defillama_source

    protocol_slug = context.partition_key

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="defillama_yields",
        dataset_name="defi",
    )

    source = defillama_source(
        include_yields=True,
        include_protocols=False,
        include_chains=False,
        include_stablecoins=False,
    )

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "protocol": protocol_slug,
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {
        "protocol": protocol_slug,
        "status": "success",
    }


@asset(
    group_name="defi",
    description="Token prices from CoinGecko",
)
def token_prices(context: AssetExecutionContext) -> dict:
    """Fetch token prices from CoinGecko."""
    from dlt_sources.defi.coingecko import coingecko_source

    tokens = load_token_config()
    token_ids = [t.get("coingecko_id") for t in tokens if t.get("coingecko_id")]

    if not token_ids:
        context.log.warning("No tokens configured for price fetching")
        return {"status": "skipped", "reason": "no tokens configured"}

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="coingecko_prices",
        dataset_name="defi",
    )

    source = coingecko_source(
        coin_ids=token_ids,
        include_coins=True,
        include_exchanges=False,
        include_trending=False,
    )

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "tokens_fetched": len(token_ids),
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {
        "status": "success",
        "tokens": len(token_ids),
    }


@asset(
    group_name="defi",
    description="Historical token prices for trend analysis",
)
def token_price_history(context: AssetExecutionContext) -> dict:
    """Fetch historical token prices."""
    from dlt_sources.defi.coingecko import coingecko_source

    tokens = load_token_config()
    priority_tokens = [t.get("coingecko_id") for t in tokens if t.get("priority", False)]

    if not priority_tokens:
        priority_tokens = [t.get("coingecko_id") for t in tokens[:10]]

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="coingecko_history",
        dataset_name="defi",
    )

    source = coingecko_source(
        coin_ids=priority_tokens,
        price_history_days=30,
        include_coins=False,
        include_exchanges=False,
        include_trending=False,
    )

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "tokens_fetched": len(priority_tokens),
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {
        "status": "success",
        "tokens": len(priority_tokens),
    }


@asset(
    group_name="defi",
    description="Perpetual funding rates from Binance",
)
def binance_funding_rates(context: AssetExecutionContext) -> dict:
    """Fetch funding rates from Binance."""
    from dlt_sources.defi.binance import binance_source

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="binance_funding",
        dataset_name="defi",
    )

    source = binance_source(
        include_spot=False,  # Skip spot data
        include_futures=True,  # Fetch futures funding rates
    )

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "exchange": "binance",
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {"status": "success", "exchange": "binance"}


@asset(
    group_name="defi",
    description="Perpetual funding rates from Bybit",
)
def bybit_funding_rates(context: AssetExecutionContext) -> dict:
    """Fetch funding rates from Bybit."""
    from dlt_sources.defi.bybit import bybit_source

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="bybit_funding",
        dataset_name="defi",
    )

    source = bybit_source(
        include_tickers=True,
        include_funding=True,
        include_oi=True,
    )

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "exchange": "bybit",
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {"status": "success", "exchange": "bybit"}


@asset(
    group_name="defi",
    description="Perpetual funding rates from OKX",
)
def okx_funding_rates(context: AssetExecutionContext) -> dict:
    """Fetch funding rates from OKX."""
    from dlt_sources.defi.okx import okx_source

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="okx_funding",
        dataset_name="defi",
    )

    source = okx_source(
        include_funding_history=True,
        include_current_funding=True,
        include_oi=True,
        include_mark_price=True,
    )

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "exchange": "okx",
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {"status": "success", "exchange": "okx"}


@asset(
    group_name="defi",
    description="Ethereum staking APR from Beaconchain",
)
def eth_staking_data(context: AssetExecutionContext) -> dict:
    """Fetch Ethereum staking data from Beaconchain."""
    from dlt_sources.defi.beaconchain import beaconchain_source

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="beaconchain_data",
        dataset_name="defi",
    )

    source = beaconchain_source(
        include_apr=True,
        include_network_stats=True,
        include_queue=True,
        include_rewards_chart=True,
        days=30,
    )

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "source": "beaconchain",
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {"status": "success", "source": "beaconchain"}


@asset(
    group_name="defi",
    description="Aave V3 reserve and position data from The Graph",
)
def aave_subgraph_data(context: AssetExecutionContext) -> dict:
    """Fetch Aave V3 data from subgraph."""
    from dlt_sources.defi.subgraphs import aave_subgraph_source

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="aave_subgraph",
        dataset_name="defi",
    )

    source = aave_subgraph_source()

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "protocol": "aave_v3",
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {"status": "success", "protocol": "aave_v3"}


@asset(
    group_name="defi",
    description="Pendle market and swap data from The Graph",
)
def pendle_subgraph_data(context: AssetExecutionContext) -> dict:
    """Fetch Pendle data from subgraph."""
    from dlt_sources.defi.subgraphs import pendle_subgraph_source

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="pendle_subgraph",
        dataset_name="defi",
    )

    source = pendle_subgraph_source()

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "protocol": "pendle",
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {"status": "success", "protocol": "pendle"}


@asset(
    partitions_def=chain_partitions,
    group_name="defi",
    description="Chain-specific TVL breakdown",
)
def chain_tvl(context: AssetExecutionContext) -> dict:
    """Fetch TVL breakdown by chain."""
    from dlt_sources.defi.defillama import defillama_source

    chain = context.partition_key

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="defillama_chains",
        dataset_name="defi",
    )

    source = defillama_source(
        include_chains=True,
        include_protocols=False,
        include_yields=False,
        include_stablecoins=False,
    )

    info = pipeline.run(source)

    context.add_output_metadata(
        {
            "chain": chain,
            "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        }
    )

    return {
        "chain": chain,
        "status": "success",
    }


@asset(
    group_name="defi",
    deps=[
        "protocol_tvl",
        "token_prices",
        "binance_funding_rates",
        "bybit_funding_rates",
        "okx_funding_rates",
        "eth_staking_data",
        "aave_subgraph_data",
        "pendle_subgraph_data",
    ],
    description="Aggregate DeFi statistics",
)
def defi_aggregate_stats(context: AssetExecutionContext) -> dict:
    """Compute aggregate DeFi statistics."""
    import duckdb

    # Get project root directory (crypteolas/)
    project_root = Path(__file__).parent.parent
    default_db_path = str(project_root / "storage" / "duckdb" / "crypteolas.duckdb")
    db_path = os.environ.get("DUCKDB_PATH", default_db_path)

    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(db_path)

    try:
        stats = {}

        # TVL stats
        try:
            total_tvl = conn.execute("SELECT SUM(tvl_usd) FROM defi.protocol_tvl").fetchone()
            stats["total_tvl_usd"] = total_tvl[0] if total_tvl else 0

            protocol_count = conn.execute(
                "SELECT COUNT(DISTINCT protocol) FROM defi.protocol_tvl"
            ).fetchone()
            stats["protocols_tracked"] = protocol_count[0] if protocol_count else 0
        except Exception:
            stats["total_tvl_usd"] = 0
            stats["protocols_tracked"] = 0

        # Token stats
        try:
            token_count = conn.execute(
                "SELECT COUNT(DISTINCT symbol) FROM defi.token_prices"
            ).fetchone()
            stats["tokens_tracked"] = token_count[0] if token_count else 0
        except Exception:
            stats["tokens_tracked"] = 0

        # Exchange funding data stats
        try:
            exchange_count = conn.execute("""
                SELECT
                    'binance' as exchange,
                    COUNT(*) as records
                FROM defi.binance_funding_rates
                UNION ALL
                SELECT
                    'bybit' as exchange,
                    COUNT(*) as records
                FROM defi.bybit_funding_history
                UNION ALL
                SELECT
                    'okx' as exchange,
                    COUNT(*) as records
                FROM defi.okx_funding_history
            """).fetchall()
            stats["exchange_funding_records"] = {row[0]: row[1] for row in exchange_count}
        except Exception:
            stats["exchange_funding_records"] = {}

        # ETH staking stats
        try:
            staking = conn.execute(
                "SELECT apr_percent FROM defi.eth_staking_apr ORDER BY day DESC LIMIT 1"
            ).fetchone()
            stats["eth_staking_apr"] = staking[0] if staking else 0
        except Exception:
            stats["eth_staking_apr"] = 0

        context.add_output_metadata(
            {
                "total_tvl_usd": MetadataValue.float(stats["total_tvl_usd"] or 0),
                "protocols_tracked": stats["protocols_tracked"],
                "tokens_tracked": stats["tokens_tracked"],
                "eth_staking_apr": MetadataValue.float(stats["eth_staking_apr"] or 0),
            }
        )

        return stats
    finally:
        conn.close()


@asset(
    group_name="defi",
    deps=["defi_aggregate_stats"],
    description="Create Ibis analytics views for dashboards",
)
def defi_analytics_views(context: AssetExecutionContext) -> dict:
    """Create analytics views using Ibis transformations."""
    from transformations.crypto_analytics import create_analytics_views, get_connection

    # Get project root directory (crypteolas/)
    project_root = Path(__file__).parent.parent
    default_db_path = str(project_root / "storage" / "duckdb" / "crypteolas.duckdb")
    db_path = os.environ.get("DUCKDB_PATH", default_db_path)

    try:
        con = get_connection(db_path)
        create_analytics_views(con)

        context.add_output_metadata(
            {
                "views_created": MetadataValue.text(
                    "v_funding_daily, v_yield_rankings, v_stablecoin_comparison, "
                    "v_eth_staking_apr, v_exchange_funding_comparison"
                ),
            }
        )

        return {"status": "success", "views_created": 5}
    except Exception as e:
        context.log.error(f"Failed to create analytics views: {e}")
        return {"status": "error", "error": str(e)}
