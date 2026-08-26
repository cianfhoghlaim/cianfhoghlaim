"""Golden Sun (GBA) magic extractor — CocoIndex v1 App.

Watches s3://cianfhoghlaim-tuatha-raw/gba/<run_id>/frame-*.png
emitted by tuatha-gba-shim (the mGBA headless controller). Extracts
GbaMagicSystem via BAML, embeds the sprite description, writes the row.

shippable=false invariant: the frame blobs are from the user's own save
states; they stay in the private Pangolin volume. The Lance fat table
holds only a small thumb + the BAML-extracted structured description.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Annotated, Any

import cocoindex as coco
from cocoindex.connectors import lancedb
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from numpy.typing import NDArray

from .._shared import EMBEDDER, LANCE_DB, shared_lifespan

TABLE_NAME = "cianfhoghlaim.tuatha.gba.magic"
RAW_BUCKET = os.environ.get(
    "TUATHA_RAW_GBA_BUCKET", "s3://cianfhoghlaim-tuatha-raw/gba"
)


@dataclass
class GbaMagicRow:
    psynergy_name: str
    game: str
    room_id: str
    djinn_name: str | None
    element: str
    effect_text: str
    color_hex: str
    sprite_description: str
    run_id: str
    frame_index: int
    captured_at: str
    embedding: Annotated[NDArray, EMBEDDER]
    thumb_blob: bytes


async def _downscale(raw: bytes, max_side: int = 480) -> bytes:
    from io import BytesIO

    from PIL import Image

    img = Image.open(BytesIO(raw))
    img.thumbnail((max_side, max_side))
    buf = BytesIO()
    # GBA frames are 240x160 — keep them recognizable at 480px max.
    img.convert("RGB").save(buf, "PNG", optimize=True)
    return buf.getvalue()


async def _baml_extract_gba_magic(frame: bytes) -> dict[str, Any]:
    from baml_client.sync_client import b  # type: ignore[import-not-found]

    result = b.ExtractGbaMagic(frame=frame)
    return {
        "psynergy_name": result.psynergy_name,
        "game": (
            result.game.value
            if hasattr(result.game, "value")
            else str(result.game)
        ),
        "room_id": result.room_id,
        "djinn_name": result.djinn_name,
        "element": (
            result.element.value
            if hasattr(result.element, "value")
            else str(result.element)
        ),
        "effect_text": result.effect_text,
        "color_hex": result.color_hex,
        "sprite_description": result.sprite_description,
        "run_id": result.run_id,
        "frame_index": result.frame_index,
        "captured_at": result.captured_at,
    }


@coco.fn(memo=True)
async def process_gba_frame(
    file: FileLike, table: lancedb.TableTarget
) -> None:
    raw = await file.read_bytes()
    thumb = await _downscale(raw)
    magic = await _baml_extract_gba_magic(thumb)
    desc = f"{magic['element']} {magic['psynergy_name']} {magic['sprite_description']}"
    vec = await coco.use_context(EMBEDDER).embed(desc)
    table.declare_row(
        row=GbaMagicRow(
            psynergy_name=magic["psynergy_name"],
            game=magic["game"],
            room_id=magic["room_id"],
            djinn_name=magic.get("djinn_name"),
            element=magic["element"],
            effect_text=magic["effect_text"],
            color_hex=magic["color_hex"],
            sprite_description=magic["sprite_description"],
            run_id=magic["run_id"],
            frame_index=magic["frame_index"],
            captured_at=magic["captured_at"],
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
            GbaMagicRow, primary_key=["psynergy_name"]
        ),
    )
    table.declare_vector_index(column="embedding")
    table.declare_fts_index(
        column="sprite_description", language="English", with_position=True
    )
    files = await lancedb.s3_walk_dir(
        RAW_BUCKET,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/frame-*.png"]),
        live=True,
    )
    await coco.mount_each(process_gba_frame, files.items(), table)


gba_magic_app = coco.App(
    coco.AppConfig(name="tuatha_gba_magic"),
    app_main,
    lifespan=shared_lifespan,
)


if __name__ == "__main__":
    import cocoindex as _ci

    _ci.init()
    gba_magic_app.update()
