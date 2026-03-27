"""
Job definitions for crypto data pipeline.

Defines jobs that group assets for coordinated execution.
"""

from dagster import (
    AssetSelection,
    define_asset_job,
    Definitions,
)

from crypteolas.defs._partitions import hourly_partitions


# Non-partitioned API sources job (excludes partitioned assets)
api_ingestion_job = define_asset_job(
    name="crypto_api_ingestion",
    selection=(
        AssetSelection.groups("api_sources")
        - AssetSelection.keys("binance_funding_assets")
    ),
    description="Ingest data from non-partitioned API sources",
)

# Document processing only
document_job = define_asset_job(
    name="crypto_document_processing",
    selection=AssetSelection.groups("document_scraping", "processing"),
    description="Scrape and process documentation",
)

# Analytics only (non-partitioned)
analytics_job = define_asset_job(
    name="crypto_analytics",
    selection=(
        AssetSelection.groups("analytics")
        - AssetSelection.keys("funding_rate_metrics")  # Depends on partitioned asset
    ),
    description="Run analytics transformations (non-partitioned)",
)

# Funding rate focused job (partitioned)
funding_job = define_asset_job(
    name="funding_rate_pipeline",
    selection=AssetSelection.keys("binance_funding_assets"),
    partitions_def=hourly_partitions,
    description="Funding rate data pipeline (hourly partitioned)",
)


# Export definitions for load_from_defs_folder
defs = Definitions(
    jobs=[
        api_ingestion_job,
        document_job,
        analytics_job,
        funding_job,
    ],
)
