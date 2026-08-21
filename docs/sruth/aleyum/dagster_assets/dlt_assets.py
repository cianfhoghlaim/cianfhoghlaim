"""DLT Assets for Aleyum Pipeline.

Wraps DLT pipelines as Dagster assets for orchestration.
Uses dagster-dlt integration for automatic asset tracking.

Assets:
    - spotify_assets: Ingest from Spotify Web API
    - label_assets: Scrape record label websites
    - artwork_assets: Download and process artwork

Note:
    SoundCloud uses Crawl4AI scraper, not a DLT source - see manual asset below.

Reference:
    https://docs.dagster.io/integrations/libraries/dlt/dlt-pythonic
"""

import os
from typing import Any

from dagster import (
    AssetExecutionContext,
    AssetKey,
    asset,
    MaterializeResult,
)
# Note: DagsterDltResource and dlt_assets would be used for full dagster-dlt integration,
# but we use manual @asset definitions to avoid DLT config init at import time.


# =============================================================================
# Manual @asset definitions for DLT pipelines
# =============================================================================
# Using manual @asset instead of @dlt_assets decorator to avoid
# DLT configuration initialization issues at module import time.


@asset(
    name="spotify_ingestion",
    group_name="spotify_manual",
    description="Ingest Spotify artist data via API (manual asset)",
    compute_kind="dlt",
)
def spotify_ingestion_asset(context: AssetExecutionContext) -> MaterializeResult:
    """Run Spotify DLT pipeline."""
    from pipelines.spotify import run_spotify_pipeline

    load_info = run_spotify_pipeline(
        artist_id="2vLlk2CcC4NnN7yoNSTmX2",
        cache_images=False,
        fetch_audio_features=True,
    )

    return MaterializeResult(
        metadata={
            "load_ids": str(load_info.loads_ids),
            "loads_count": len(load_info.loads_ids) if load_info.loads_ids else 0,
        }
    )


@asset(
    name="soundcloud_ingestion",
    group_name="soundcloud_manual",
    description="Scrape SoundCloud profile data (manual asset)",
    compute_kind="dlt",
)
def soundcloud_ingestion_asset(context: AssetExecutionContext) -> MaterializeResult:
    """Run SoundCloud DLT pipeline."""
    from pipelines.soundcloud import run_soundcloud_pipeline

    load_info = run_soundcloud_pipeline(
        username="aleyummusic",
    )

    return MaterializeResult(
        metadata={
            "load_ids": str(load_info.loads_ids),
        }
    )


@asset(
    name="label_ingestion",
    group_name="labels_manual",
    description="Scrape record label websites (manual asset)",
    compute_kind="dlt",
)
def label_ingestion_asset(context: AssetExecutionContext) -> MaterializeResult:
    """Run labels DLT pipeline."""
    from pipelines.labels import run_labels_pipeline

    load_info = run_labels_pipeline(
        artist_slug="aleyum",
        labels=["monstercat", "lemongrass"],
    )

    return MaterializeResult(
        metadata={
            "load_ids": str(load_info.loads_ids),
        }
    )


@asset(
    name="artwork_processing",
    group_name="artwork",
    description="Download and process artwork images",
    deps=[
        AssetKey(["spotify_ingestion"]),
        AssetKey(["soundcloud_ingestion"]),
        AssetKey(["label_ingestion"]),
    ],
    compute_kind="dlt",
)
def artwork_processing_asset(context: AssetExecutionContext) -> MaterializeResult:
    """Run artwork processing pipeline."""
    from pipelines.artwork import run_artwork_pipeline
    import duckdb

    conn = duckdb.connect("./aleyum.duckdb")
    urls = []

    try:
        spotify_urls = conn.execute("""
            SELECT url, id as entity_id, 'album' as entity_type, 'spotify' as label
            FROM spotify_data.cached_images
        """).fetchall()
        for row in spotify_urls:
            urls.append(
                {
                    "url": row[0],
                    "entity_id": row[1],
                    "entity_type": row[2],
                    "label": row[3],
                }
            )
    except Exception:
        pass

    try:
        label_urls = conn.execute("""
            SELECT url, entity_id, entity_type, label
            FROM label_data.artwork
        """).fetchall()
        for row in label_urls:
            urls.append(
                {
                    "url": row[0],
                    "entity_id": row[1],
                    "entity_type": row[2],
                    "label": row[3],
                }
            )
    except Exception:
        pass

    conn.close()

    context.log.info(f"Processing {len(urls)} artwork images")

    load_info = run_artwork_pipeline(
        artwork_urls=urls,
    )

    return MaterializeResult(
        metadata={
            "load_ids": str(load_info.loads_ids),
            "images_processed": len(urls),
        }
    )
