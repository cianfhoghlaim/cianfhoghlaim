"""Dagster Jobs, Schedules, and Sensors.

Orchestration configuration for the Croílár pipeline.

Jobs:
    - daily_ingestion_job: Ingest from all sources (music + CV)
    - weekly_cv_refresh_job: Full CV refresh
    - weekly_full_refresh_job: Full data refresh (all assets)
    - artwork_embedding_job: Generate CLIP embeddings
    - monthly_identity_job: Identity document verification

Schedules:
    - daily_ingestion_schedule: Run music ingestion daily at 3 AM UTC
    - weekly_cv_refresh_schedule: CV refresh Sundays at 4 AM UTC
    - weekly_full_refresh_schedule: Full pipeline Sundays at 3 AM UTC
    - monthly_identity_schedule: Identity check on 1st of month at 5 AM UTC

Sensors:
    - new_artwork_sensor: Trigger embedding when new artwork arrives
    - source_update_sensor: Trigger artwork processing when source data updates
"""

from dagster import (
    AssetSelection,
    ScheduleDefinition,
    define_asset_job,
    sensor,
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
    DefaultSensorStatus,
)


# Asset selections
MUSIC_INGESTION = AssetSelection.groups("spotify_manual", "soundcloud_manual", "labels_manual")
ARTWORK = AssetSelection.groups("artwork")
EMBEDDINGS = AssetSelection.groups("embeddings")
CV_PIPELINE = AssetSelection.groups("cv_pipeline")
TEACHING_PIPELINE = AssetSelection.groups("teaching_pipeline")
CROSS_LINK = AssetSelection.groups("cross_link")
IDENTITY = AssetSelection.groups("identity_pipeline")

ALL_CV = CV_PIPELINE | TEACHING_PIPELINE | CROSS_LINK | IDENTITY
ALL_MUSIC = MUSIC_INGESTION | ARTWORK | EMBEDDINGS


# Jobs

daily_music_job = define_asset_job(
    name="daily_music_job",
    selection=MUSIC_INGESTION,
    description="Daily music ingestion from Spotify, SoundCloud, and labels",
    tags={"type": "ingestion", "frequency": "daily", "domain": "music"},
)

weekly_cv_refresh_job = define_asset_job(
    name="weekly_cv_refresh_job",
    selection=CV_PIPELINE | TEACHING_PIPELINE,
    description="Weekly CV and teaching data refresh from scanned PDFs",
    tags={"type": "extraction", "frequency": "weekly", "domain": "cv"},
)

weekly_full_refresh_job = define_asset_job(
    name="weekly_full_refresh_job",
    selection=ALL_MUSIC | ALL_CV,
    description="Full pipeline refresh — all sources and processing",
    tags={"type": "full_refresh", "frequency": "weekly"},
)

monthly_identity_job = define_asset_job(
    name="monthly_identity_job",
    selection=IDENTITY,
    description="Monthly identity document verification and expiry check",
    tags={"type": "verification", "frequency": "monthly", "domain": "identity"},
)


# Schedules (per spec: music at 03:00, CV at 04:00 Sun, identity at 05:00 1st)

daily_music_schedule = ScheduleDefinition(
    job=daily_music_job,
    cron_schedule="0 3 * * *",
    execution_timezone="Europe/Dublin",
    description="Daily music ingestion at 3 AM Dublin time",
)

weekly_cv_refresh_schedule = ScheduleDefinition(
    job=weekly_cv_refresh_job,
    cron_schedule="0 4 * * 0",
    execution_timezone="Europe/Dublin",
    description="Weekly CV and teaching refresh on Sundays at 4 AM Dublin time",
)

weekly_full_refresh_schedule = ScheduleDefinition(
    job=weekly_full_refresh_job,
    cron_schedule="0 3 * * 0",
    execution_timezone="Europe/Dublin",
    description="Weekly full pipeline refresh on Sundays at 3 AM Dublin time",
)

monthly_identity_schedule = ScheduleDefinition(
    job=monthly_identity_job,
    cron_schedule="0 5 1 * *",
    execution_timezone="Europe/Dublin",
    description="Monthly identity document verification on the 1st at 5 AM Dublin time",
)


# Sensors

@sensor(
    name="new_artwork_sensor",
    job=weekly_full_refresh_job,
    minimum_interval_seconds=300,
    default_status=DefaultSensorStatus.RUNNING,
    description="Trigger pipeline refresh when new artwork is detected",
)
def new_artwork_sensor(context: SensorEvaluationContext):
    """Trigger pipeline when new artwork arrives in the DuckDB store."""
    import duckdb
    import os

    duckdb_path = os.environ.get("DUCKDB_PATH", "./croilar.duckdb")

    try:
        conn = duckdb.connect(duckdb_path, read_only=True)
        artwork_count = conn.execute(
            "SELECT COUNT(*) FROM artwork_data.images"
        ).fetchone()[0]
        conn.close()
    except Exception:
        return SkipReason("Artwork data not available yet")

    cursor = int(context.cursor or "0")
    if artwork_count > cursor:
        context.update_cursor(str(artwork_count))
        return RunRequest(
            run_key=f"artwork_{artwork_count}",
            tags={"trigger": "sensor", "new_artwork_count": str(artwork_count - cursor)},
        )
    return SkipReason(f"No new artwork (count: {artwork_count})")


@sensor(
    name="cv_document_sensor",
    job=weekly_cv_refresh_job,
    minimum_interval_seconds=3600,
    default_status=DefaultSensorStatus.RUNNING,
    description="Trigger CV refresh when new PDFs are detected in the author directory",
)
def cv_document_sensor(context: SensorEvaluationContext):
    """Trigger CV pipeline when new PDFs appear in the author directory."""
    from pathlib import Path

    author_dir = Path(__file__).parent.parent.parent.parent.parent / (
        "author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin"
    )
    pdf_count = len(list(author_dir.rglob("*.pdf")))

    cursor = int(context.cursor or "0")
    if pdf_count > cursor:
        context.update_cursor(str(pdf_count))
        return RunRequest(
            run_key=f"cv_pdfs_{pdf_count}",
            tags={"trigger": "sensor", "new_pdf_count": str(pdf_count - cursor)},
        )
    return SkipReason(f"No new author PDFs (count: {pdf_count})")


# Export lists

all_jobs = [
    daily_music_job,
    weekly_cv_refresh_job,
    weekly_full_refresh_job,
    monthly_identity_job,
]

all_schedules = [
    daily_music_schedule,
    weekly_cv_refresh_schedule,
    weekly_full_refresh_schedule,
    monthly_identity_schedule,
]

all_sensors = [
    new_artwork_sensor,
    cv_document_sensor,
]
