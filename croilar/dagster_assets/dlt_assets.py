"""DLT Assets for Croílár Pipeline.

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


from dagster import (
    AssetExecutionContext,
    AssetKey,
    MaterializeResult,
    asset,
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
    import duckdb

    from pipelines.artwork import run_artwork_pipeline

    conn = duckdb.connect("./croilar.duckdb")
    urls = []

    try:
        spotify_urls = conn.execute("""
            SELECT url, id as entity_id, 'album' as entity_type, 'spotify' as label
            FROM spotify_data.cached_images
        """).fetchall()
        for row in spotify_urls:
            urls.append({
                "url": row[0],
                "entity_id": row[1],
                "entity_type": row[2],
                "label": row[3],
            })
    except Exception:
        pass

    try:
        label_urls = conn.execute("""
            SELECT url, entity_id, entity_type, label
            FROM label_data.artwork
        """).fetchall()
        for row in label_urls:
            urls.append({
                "url": row[0],
                "entity_id": row[1],
                "entity_type": row[2],
                "label": row[3],
            })
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


@asset(
    name="motherduck_sync",
    group_name="cross_link",
    description="Sync DuckDB tables to MotherDuck cloud for Dive embedding",
    compute_kind="motherduck",
    deps=[
        AssetKey(["spotify_ingestion"]),
        AssetKey(["soundcloud_ingestion"]),
        AssetKey(["cv_pdf_ingestion"]),
        AssetKey(["placement_ingestion"]),
    ],
)
def motherduck_sync_asset(context: AssetExecutionContext) -> MaterializeResult:
    """Copy all DuckDB tables to MotherDuck cloud.

    MotherDuck provides a cloud-hosted DuckDB with the Dive UI for
    self-service SQL exploration by collaborators.

    The MotherDuck token comes from env var MOTHERDUCK_TOKEN (set via
    Infisical dev-baile/croilar/motherduck/).

    Runs after all upstream DLT ingestion assets to keep Dive in sync.
    """
    import os
    import duckdb

    token = os.environ.get("MOTHERDUCK_TOKEN")
    if not token:
        context.log.warning("MOTHERDUCK_TOKEN not set — MotherDuck sync skipped")
        return MaterializeResult(
            metadata={"synced_tables": 0, "reason": "missing_token"},
        )

    local = duckdb.connect("./data/croilar.duckdb", read_only=True)
    md = duckdb.connect(f"md:?motherduck_token={token}")
    synced = 0

    tables = [
        ("spotify_data", "tracks"),
        ("spotify_data", "artists"),
        ("spotify_data", "albums"),
        ("github_data", "repos"),
        ("cv_data", "cv_raw"),
        ("teaching_data", "cv_raw"),
    ]

    for schema, table in tables:
        try:
            full_name = f"{schema}.{table}"
            count = local.execute(f"SELECT COUNT(*) FROM {full_name}").fetchone()[0]
            if count > 0:
                md.execute(f"CREATE OR REPLACE TABLE {schema}.{table} AS SELECT * FROM local.{full_name}")
                synced += 1
                context.log.info(f"Synced {full_name} ({count} rows) to MotherDuck")
        except Exception as e:
            context.log.warning(f"Failed to sync {schema}.{table}: {e}")

    local.close()
    md.close()

    return MaterializeResult(
        metadata={
            "synced_tables": synced,
            "total_tables": len(tables),
        }
    )
