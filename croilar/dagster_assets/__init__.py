"""Dagster Assets for Croílár Pipeline.

Orchestrates DLT data ingestion, CocoIndex embedding,
and artwork processing workflows.

Assets are stream-driven: one (stream_id, source_type) asset per
entry in the Stream registry. See `croilar/_shared/streams.py` and
`croilar/dagster_assets/dlt_assets.py::build_stream_assets`.

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
    build_stream_assets,
    make_dlt_asset,
    motherduck_sync_asset,
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

# Re-export every stream-driven asset (e.g. `music__spotify`,
# `teaching__linkedin`, `cv__filesystem`) at module scope so they can
# be referenced directly by name. AssetDefinitions are not iterable as
# `__all__` entries, so we expose them via the dunder pattern used by
# dagster_assets.dlt_assets.

__all__ = [
    # Stream-driven asset factory
    "make_dlt_asset",
    "build_stream_assets",
    # Composer assets
    "artwork_processing_asset",
    "motherduck_sync_asset",
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
