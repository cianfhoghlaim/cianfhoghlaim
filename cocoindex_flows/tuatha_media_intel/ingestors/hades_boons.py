"""Hades boon extractor — CocoIndex v1 App.

Watches s3://cianfhoghlaim-tuatha-raw/hades/<run_id>/{keyframes,bursts}/
emitted by the Swift tuatha-capture daemon. Downscales frames to 1024px,
extracts typed HadesBoon via BAML, embeds the description, writes the
multimodal fat row to the Lance table.

Phase 1: manual capture (you play Hades; the daemon watches the window).
Phase 2 (stubbed): Hermes Agent computer-use controls the play; daemon
   is invoked via the same JSON-RPC socket.
"""
from __future__ import annotations

import json
import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

import cocoindex as coco
from cocoindex.connectors import lancedb
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.ops.text import RecursiveSplitter
from numpy.typing import NDArray

from .._shared import EMBEDDER, LANCE_DB, shared_lifespan

TABLE_NAME = "cianfhoghlaim.tuatha.hades.boons"
RAW_BUCKET = os.environ.get(
    "TUATHA_RAW_HADES_BUCKET", "s3://cianfhoghlaim-tuatha-raw/hades"
)


@dataclass
class HadesBoonRow:
    boon_id: str
    god: str
    tier: str
    slot: str
    effect_text: str
    color_hex: str
    particle_motion: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    run_id: str
    frame_index: int
    captured_at: str
    embedding: Annotated[NDArray, EMBEDDER]
    thumb_blob: bytes  # ≤1024px JPEG, stored in the Lance fat table


_splitter = RecursiveSplitter()


async def _downscale(raw: bytes, max_side: int = 1024) -> bytes:
    """Resize any image to ≤max_side and return as JPEG bytes."""
    from io import BytesIO

    from PIL import Image

    img = Image.open(BytesIO(raw))
    img.thumbnail((max_side, max_side))
    buf = BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=85)
    return buf.getvalue()


async def _baml_extract_hades_boon(thumb: bytes) -> dict[str, Any]:
    """Run the BAML ExtractHadesBoon function. Imported lazily so the
    CocoIndex build step doesn't require the baml_client to be installed
    in CI environments that only want to lint the graph."""
    from baml_client.sync_client import b  # type: ignore[import-not-found]

    result = b.ExtractHadesBoon(image=thumb)
    return {
        "boon_id": result.boon_id,
        "god": result.god.value if hasattr(result.god, "value") else str(result.god),
        "tier": result.tier.value
        if hasattr(result.tier, "value")
        else str(result.tier),
        "slot": result.slot.value
        if hasattr(result.slot, "value")
        else str(result.slot),
        "effect_text": result.effect_text,
        "color_hex": result.color_hex,
        "particle_motion": result.particle_motion,
        "x_min": result.ui_position.x_min,
        "y_min": result.ui_position.y_min,
        "x_max": result.ui_position.x_max,
        "y_max": result.ui_position.y_max,
        "run_id": result.run_id,
        "frame_index": result.frame_index,
        "captured_at": result.captured_at,
    }


@coco.fn(memo=True)
async def process_hades_keyframe(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Per-keyframe: downscale → BAML extract → embed → row."""
    raw = await file.read_bytes()
    thumb = await _downscale(raw)
    boon = await _baml_extract_hades_boon(thumb)
    desc_text = f"{boon['god']} {boon['tier']} {boon['slot']}: {boon['effect_text']} — {boon['particle_motion']}"
    vec = await coco.use_context(EMBEDDER).embed(desc_text)
    table.declare_row(
        row=HadesBoonRow(
            boon_id=boon["boon_id"],
            god=boon["god"],
            tier=boon["tier"],
            slot=boon["slot"],
            effect_text=boon["effect_text"],
            color_hex=boon["color_hex"],
            particle_motion=boon["particle_motion"],
            x_min=boon["x_min"],
            y_min=boon["y_min"],
            x_max=boon["x_max"],
            y_max=boon["y_max"],
            run_id=boon["run_id"],
            frame_index=boon["frame_index"],
            captured_at=boon["captured_at"],
            embedding=vec,
            thumb_blob=thumb,
        )
    )


@coco.fn
async def app_main() -> None:
    table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            HadesBoonRow, primary_key=["boon_id"]
        ),
    )
    table.declare_vector_index(column="embedding")
    table.declare_fts_index(
        column="effect_text", language="English", with_position=True
    )
    # Walk the raw capture bucket. Pattern matches both keyframes (jpegs)
    # and burst frame thumbs. The full-resolution blobs never enter the
    # CocoIndex state path — only the downsampled thumb_blob row.
    files = await lancedb.s3_walk_dir(
        RAW_BUCKET,
        path_matcher=PatternFilePathMatcher(
            included_patterns=["**/*.jpg", "**/*.jpeg"],
            excluded_patterns=["**/thumbs", "**/.tmp"],
        ),
        live=True,  # cocoindex update -L
    )
    await coco.mount_each(process_hades_keyframe, files.items(), table)


hades_boons_app = coco.App(
    coco.AppConfig(name="tuatha_hades_boons"),
    app_main,
    lifespan=shared_lifespan,
)


if __name__ == "__main__":
    import cocoindex as _ci

    _ci.init()
    hades_boons_app.update()
