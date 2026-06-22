"""
Dagster Definitions for Crypteolas.

Orchestrates GitHub data ingestion, DeFi metrics, and embedding pipelines.
"""

from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from dagster import (
    AssetSelection,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_modules,
)

from . import defi_assets, embedding_assets, github_assets
from .schedules import (
    daily_defi_schedule,
    daily_embedding_schedule,
    hourly_github_schedule,
)

# Load all assets from modules
github_asset_list = load_assets_from_modules([github_assets])
defi_asset_list = load_assets_from_modules([defi_assets])
embedding_asset_list = load_assets_from_modules([embedding_assets])

# Define jobs - split defi into separate jobs by partition type
github_job = define_asset_job(
    name="github_sync_job",
    selection=github_asset_list,
    description="Sync GitHub repositories, issues, PRs, and commits",
)

# Non-partitioned DeFi assets (token prices, funding rates, staking, subgraphs)
defi_non_partitioned_job = define_asset_job(
    name="defi_metrics_job",
    selection=AssetSelection.assets(
        "token_prices",
        "token_price_history",
        "binance_funding_rates",
        "bybit_funding_rates",
        "okx_funding_rates",
        "eth_staking_data",
        "aave_subgraph_data",
        "pendle_subgraph_data",
        "defi_aggregate_stats",
        "defi_analytics_views",
    ),
    description="Fetch non-partitioned DeFi metrics (prices, funding, staking)",
)

# Protocol-partitioned assets
defi_protocol_job = define_asset_job(
    name="defi_protocol_job",
    selection=AssetSelection.assets("protocol_tvl", "protocol_yields"),
    description="Fetch protocol-specific TVL and yields (partitioned by protocol)",
)

# Chain-partitioned assets
defi_chain_job = define_asset_job(
    name="defi_chain_job",
    selection=AssetSelection.assets("chain_tvl"),
    description="Fetch chain-specific TVL (partitioned by chain)",
)

# Code embeddings (partitioned by github_repos)
code_embedding_job = define_asset_job(
    name="code_embedding_job",
    selection=AssetSelection.assets("code_embeddings"),
    description="Generate code embeddings (partitioned by repo)",
)

# Document embeddings (partitioned by defi_protocols)
doc_embedding_job = define_asset_job(
    name="doc_embedding_job",
    selection=AssetSelection.assets("document_embeddings"),
    description="Generate document embeddings (partitioned by protocol)",
)

# Embedding stats (non-partitioned)
embedding_stats_job = define_asset_job(
    name="embedding_stats_job",
    selection=AssetSelection.assets("embedding_stats"),
    description="Compute embedding statistics",
)

# Combine all definitions
defs = Definitions(
    assets=github_asset_list + defi_asset_list + embedding_asset_list,
    jobs=[
        github_job,
        defi_non_partitioned_job,
        defi_protocol_job,
        defi_chain_job,
        code_embedding_job,
        doc_embedding_job,
        embedding_stats_job,
    ],
    schedules=[
        hourly_github_schedule,
        daily_defi_schedule,
        daily_embedding_schedule,
    ],
)
