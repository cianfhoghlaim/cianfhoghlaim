"""Dagster Jobs, Schedules, and Sensors.

Orchestration configuration for the Aleyum pipeline.

Jobs:
    - daily_ingestion_job: Ingest from all sources
    - weekly_full_refresh_job: Full data refresh
    - artwork_embedding_job: Generate embeddings

Schedules:
    - daily_ingestion_schedule: Run ingestion daily at 6 AM
    - weekly_refresh_schedule: Full refresh on Sundays

Sensors:
    - new_artwork_sensor: Trigger embedding when new artwork arrives
"""

from dagster import (
    AssetSelection,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    sensor,
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
    AssetKey,
    DefaultSensorStatus,
)


# Asset selections for jobs
INGESTION_ASSETS = AssetSelection.groups("spotify", "soundcloud", "labels")
ARTWORK_ASSETS = AssetSelection.groups("artwork")
EMBEDDING_ASSETS = AssetSelection.groups("embeddings")
ALL_ASSETS = INGESTION_ASSETS | ARTWORK_ASSETS | EMBEDDING_ASSETS


# Jobs

daily_ingestion_job = define_asset_job(
    name="daily_ingestion_job",
    selection=INGESTION_ASSETS,
    description="Daily data ingestion from all music sources",
    tags={"type": "ingestion", "frequency": "daily"},
)

artwork_processing_job = define_asset_job(
    name="artwork_processing_job",
    selection=ARTWORK_ASSETS,
    description="Process and cache artwork images",
    tags={"type": "processing", "resource": "artwork"},
)

embedding_job = define_asset_job(
    name="embedding_job",
    selection=EMBEDDING_ASSETS,
    description="Generate CLIP embeddings for artwork",
    tags={"type": "embedding", "resource": "lancedb"},
)

weekly_full_refresh_job = define_asset_job(
    name="weekly_full_refresh_job",
    selection=ALL_ASSETS,
    description="Full pipeline refresh - all sources and processing",
    tags={"type": "full_refresh", "frequency": "weekly"},
)

full_pipeline_job = define_asset_job(
    name="full_pipeline_job",
    selection=ALL_ASSETS,
    description="Run complete pipeline: ingestion → processing → embedding",
    tags={"type": "full_pipeline"},
)


# Schedules

daily_ingestion_schedule = ScheduleDefinition(
    job=daily_ingestion_job,
    cron_schedule="0 6 * * *",  # 6 AM daily
    execution_timezone="UTC",
    description="Daily ingestion at 6 AM UTC",
)

weekly_refresh_schedule = ScheduleDefinition(
    job=weekly_full_refresh_job,
    cron_schedule="0 3 * * 0",  # 3 AM on Sundays
    execution_timezone="UTC",
    description="Weekly full refresh on Sundays at 3 AM UTC",
)


# Sensors


@sensor(
    name="new_artwork_sensor",
    job=embedding_job,
    minimum_interval_seconds=300,  # Check every 5 minutes
    default_status=DefaultSensorStatus.RUNNING,
    description="Trigger embedding when new artwork is detected",
)
def new_artwork_sensor(context: SensorEvaluationContext):
    """Sensor that triggers embedding when new artwork arrives.

    Monitors the artwork_data.images table for new entries
    that haven't been embedded yet.
    """
    import duckdb
    import os

    duckdb_path = os.environ.get("DUCKDB_PATH", "./aleyum.duckdb")
    lancedb_uri = os.environ.get("LANCEDB_URI", "./lancedb_data")

    try:
        conn = duckdb.connect(duckdb_path, read_only=True)

        # Count artwork in DuckDB
        artwork_count = conn.execute("""
            SELECT COUNT(*) FROM artwork_data.images
        """).fetchone()[0]

        conn.close()

        # Count embeddings in LanceDB
        try:
            import lancedb

            db = lancedb.connect(lancedb_uri)
            table = db.open_table("artwork_embeddings")
            embedding_count = len(table)
        except Exception:
            embedding_count = 0

        # Check if we have new artwork to embed
        new_count = artwork_count - embedding_count

        if new_count > 0:
            context.log.info(
                f"Found {new_count} new artwork images to embed "
                f"(artwork: {artwork_count}, embedded: {embedding_count})"
            )
            return RunRequest(
                run_key=f"new_artwork_{artwork_count}",
                run_config={},
                tags={"trigger": "sensor", "new_artwork_count": str(new_count)},
            )
        else:
            return SkipReason(
                f"No new artwork to embed (artwork: {artwork_count}, embedded: {embedding_count})"
            )

    except Exception as e:
        return SkipReason(f"Error checking for new artwork: {e}")


@sensor(
    name="source_update_sensor",
    job=artwork_processing_job,
    minimum_interval_seconds=600,  # Check every 10 minutes
    default_status=DefaultSensorStatus.STOPPED,  # Manual activation
    description="Trigger artwork processing when source data updates",
)
def source_update_sensor(context: SensorEvaluationContext):
    """Sensor that triggers artwork processing when source data updates.

    Monitors the label and Spotify tables for new releases
    with artwork URLs.
    """
    import duckdb
    import os

    duckdb_path = os.environ.get("DUCKDB_PATH", "./aleyum.duckdb")

    # Get cursor from previous run
    cursor = context.cursor or "0"
    last_count = int(cursor)

    try:
        conn = duckdb.connect(duckdb_path, read_only=True)

        # Count total artwork URLs across sources
        current_count = 0

        try:
            label_count = conn.execute("""
                SELECT COUNT(*) FROM label_data.artwork
            """).fetchone()[0]
            current_count += label_count
        except Exception:
            pass

        try:
            spotify_count = conn.execute("""
                SELECT COUNT(*) FROM spotify_data.cached_images
            """).fetchone()[0]
            current_count += spotify_count
        except Exception:
            pass

        conn.close()

        if current_count > last_count:
            new_count = current_count - last_count
            context.log.info(f"Found {new_count} new artwork URLs")

            # Update cursor
            context.update_cursor(str(current_count))

            return RunRequest(
                run_key=f"source_update_{current_count}",
                run_config={},
                tags={"trigger": "sensor", "new_urls": str(new_count)},
            )
        else:
            return SkipReason(f"No new artwork URLs (count: {current_count})")

    except Exception as e:
        return SkipReason(f"Error checking sources: {e}")


# List of all jobs for export
all_jobs = [
    daily_ingestion_job,
    artwork_processing_job,
    embedding_job,
    weekly_full_refresh_job,
    full_pipeline_job,
]

# List of all schedules for export
all_schedules = [
    daily_ingestion_schedule,
    weekly_refresh_schedule,
]

# List of all sensors for export
all_sensors = [
    new_artwork_sensor,
    source_update_sensor,
]
