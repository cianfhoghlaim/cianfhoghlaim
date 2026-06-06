"""Dagster Assets for Croílár Pipeline.

Orchestrates DLT data ingestion, CocoIndex embedding,
and artwork processing workflows.

Assets:
    - spotify_data: Ingest from Spotify API
    - soundcloud_data: Scrape from SoundCloud
    - label_releases: Scrape from record labels
    - artwork_images: Download and cache artwork
    - artwork_embeddings: CLIP embeddings in LanceDB
    - artwork_analysis: Vision model analysis

Usage:
    from dagster_assets import defs

    # Run in development
    defs.get_job_def("daily_music_job").execute_in_process()
"""

# Add project root to path for pipelines package
import sys
from pathlib import Path

_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from dagster_assets.cocoindex_assets import (
    artwork_embedding_asset,
    run_cocoindex_flow,
)
from dagster_assets.dlt_assets import (
    artwork_processing_asset,
    label_ingestion_asset,
    soundcloud_ingestion_asset,
    # Manual DLT assets (avoiding dlt_assets decorator due to import-time issues)
    spotify_ingestion_asset,
)
from dagster_assets.schedules import (
    all_jobs,
    all_schedules,
    all_sensors,
    daily_music_job,
    daily_music_schedule,
    new_artwork_sensor,
    weekly_full_refresh_job,
)

__all__ = [
    # DLT Assets (manual @asset definitions)
    "spotify_ingestion_asset",
    "soundcloud_ingestion_asset",
    "label_ingestion_asset",
    "artwork_processing_asset",
    # CocoIndex Assets
    "artwork_embedding_asset",
    "run_cocoindex_flow",
    # Jobs & Schedules
    "all_jobs",
    "all_schedules",
    "all_sensors",
    "daily_music_job",
    "daily_music_schedule",
    "weekly_full_refresh_job",
    "new_artwork_sensor",
]
