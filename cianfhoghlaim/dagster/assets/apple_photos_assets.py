"""Apple Photos Dagster assets — the 5 assets in the `apple_photos` group.

Added in the `2026-06-30-agent-platform-cluster-hermes-cocoindex` change.
Companion to the 2 new v1 Apps (`apple_photos_metadata`,
`apple_photos_chunks`, `apple_photos_geospatial`).

1. `apple_photos_raw` — invokes the `apple_photos_source` dlt source
2. `apple_photos_captioning` — generates 1-2 sentence captions via
   `minimax-m3-vision` via LiteLLM for new photos
3. `apple_photos_cocoindex_metadata_update` — re-runs the
   `apple_photos_metadata` v1 App
4. `apple_photos_cocoindex_chunks_update` — re-runs the
   `apple_photos_chunks` v1 App
5. `apple_photos_cocoindex_geospatial_update` — re-runs the
   `apple_photos_geospatial` v1 App (emits the 2 GeoParquet files;
   gated by `LEABHARLANN_PHOTOS_INCLUDE_GPS=true`)

Plus the `apple_photos_weekly_recompute` schedule (Mondays 04:00 UTC).
"""
from __future__ import annotations

import os
import subprocess
from collections.abc import Iterator

import requests
import structlog
from dagster import AssetExecutionContext, ScheduleDefinition, asset

logger = structlog.get_logger(__name__)


@asset(
    group_name="apple_photos",
    compute_kind="dlt",
    description="Run the apple_photos dlt source to populate the apple_photos DuckLake table.",
)
def apple_photos_raw(context: AssetExecutionContext) -> Iterator[str]:
    """Run `dlt run apple_photos_source`."""
    context.log.info("[apple_photos_raw] starting")
    result = subprocess.run(
        ["uv", "run", "dlt", "run", "apple_photos_source"],
        capture_output=True,
        text=True,
        timeout=3600,
    )
    if result.returncode != 0:
        raise RuntimeError(f"dlt run apple_photos_source failed: {result.stderr}")
    context.log.info(f"[apple_photos_raw] done: {result.stdout[:200]}")
    yield result.stdout


@asset(
    group_name="apple_photos",
    compute_kind="vision",
    description="Generate 1-2 sentence captions for new photos via minimax-m3-vision via LiteLLM.",
)
def apple_photos_captioning(context: AssetExecutionContext) -> Iterator[str]:
    """Generate captions for new photos."""
    context.log.info("[apple_photos_captioning] starting")
    litellm_url = os.getenv("LITELLM_URL", "http://litellm:4000")
    master_key = os.getenv("LITELLM_MASTER_KEY", "")

    # Fetch the next 10 uncaptioned photos from DuckLake
    photos = _fetch_uncaptioned_photos(limit=10)
    captioned_count = 0
    for photo in photos:
        try:
            response = requests.post(
                f"{litellm_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {master_key}"},
                json={
                    "model": "minimax-m3-vision",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Generate a 1-2 sentence caption describing this photo.",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"file://{photo['file_path']}",
                                    },
                                },
                            ],
                        }
                    ],
                },
                timeout=60,
            )
            if response.ok:
                caption = response.json()["choices"][0]["message"]["content"]
                _update_photo_caption(photo["photo_id"], caption)
                captioned_count += 1
        except Exception as e:
            logger.warning(
                "[apple_photos_captioning] failed for %s: %s",
                photo["photo_id"], e,
            )
    context.log.info(f"[apple_photos_captioning] captioned {captioned_count} photos")
    yield f"captioned {captioned_count} photos"


@asset(
    group_name="apple_photos",
    compute_kind="embedding",
    description="Re-run the apple_photos_metadata v1 App.",
)
def apple_photos_cocoindex_metadata_update(
    context: AssetExecutionContext,
) -> Iterator[str]:
    """Run `mise run cocoindex:update apple_photos_metadata`."""
    context.log.info("[apple_photos_cocoindex_metadata_update] starting")
    result = subprocess.run(
        ["mise", "run", "cocoindex:update-apple_photos_metadata"],
        capture_output=True,
        text=True,
        timeout=3600,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cocoindex:update-apple_photos_metadata failed: {result.stderr}"
        )
    context.log.info(
        f"[apple_photos_cocoindex_metadata_update] done: {result.stdout[:200]}"
    )
    yield result.stdout


@asset(
    group_name="apple_photos",
    compute_kind="embedding",
    description="Re-run the apple_photos_chunks v1 App.",
)
def apple_photos_cocoindex_chunks_update(
    context: AssetExecutionContext,
) -> Iterator[str]:
    """Run `mise run cocoindex:update apple_photos_chunks`."""
    context.log.info("[apple_photos_cocoindex_chunks_update] starting")
    result = subprocess.run(
        ["mise", "run", "cocoindex:update-apple_photos_chunks"],
        capture_output=True,
        text=True,
        timeout=3600,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cocoindex:update-apple_photos_chunks failed: {result.stderr}"
        )
    context.log.info(
        f"[apple_photos_cocoindex_chunks_update] done: {result.stdout[:200]}"
    )
    yield result.stdout


@asset(
    group_name="apple_photos",
    compute_kind="embedding",
    description="Re-run the apple_photos_geospatial v1 App (emits the 2 GeoParquet files; gated by LEABHARLANN_PHOTOS_INCLUDE_GPS=true).",
)
def apple_photos_cocoindex_geospatial_update(
    context: AssetExecutionContext,
) -> Iterator[str]:
    """Run `mise run cocoindex:update apple_photos_geospatial` (gated by privacy env)."""
    include_gps = os.getenv("LEABHARLANN_PHOTOS_INCLUDE_GPS", "false").lower() == "true"
    if not include_gps:
        msg = "LEABHARLANN_PHOTOS_INCLUDE_GPS=false; skipping GeoParquet emission"
        context.log.info(f"[apple_photos_cocoindex_geospatial_update] {msg}")
        yield msg
        return
    context.log.info("[apple_photos_cocoindex_geospatial_update] starting")
    result = subprocess.run(
        ["mise", "run", "cocoindex:update-apple_photos_geospatial"],
        capture_output=True,
        text=True,
        timeout=3600,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cocoindex:update-apple_photos_geospatial failed: {result.stderr}"
        )
    context.log.info(
        f"[apple_photos_cocoindex_geospatial_update] done: {result.stdout[:200]}"
    )
    yield result.stdout


# Weekly schedule
apple_photos_weekly_recompute = ScheduleDefinition(
    name="apple_photos_weekly_recompute",
    job_name="apple_photos_assets_job",
    cron_schedule="0 4 * * 1",  # Mondays 04:00 UTC
    execution_timezone="UTC",
)


def _fetch_uncaptioned_photos(limit: int) -> list[dict]:
    """Fetch the next batch of uncaptioned photos from DuckLake.

    Returns a list of dicts with `photo_id` + `file_path`. The actual
    implementation uses the Dagster DuckLake resource; this stub
    returns an empty list to avoid blocking the build (the real
    implementation is wired in Phase 6 of the build agent's task plan).
    """
    return []


def _update_photo_caption(photo_id: str, caption: str) -> None:
    """Update the caption column for a photo in DuckLake.

    Real implementation: `UPDATE apple_photos SET caption=$caption
    WHERE photo_id=$photo_id`. Stub logs to stdout for now.
    """
    logger.info(
        f"[apple_photos_captioning] UPDATE apple_photos SET caption='{caption[:50]}...' WHERE photo_id='{photo_id}'"
    )
