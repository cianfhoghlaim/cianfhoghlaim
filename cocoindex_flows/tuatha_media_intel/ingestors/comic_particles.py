"""Comic particle extractor — CocoIndex v1 App.

Watches s3://cianfhoghlaim-tuatha-raw/comic/<issue_id>/page-*.jpg
emitted by tuatha-comic-ingest. Extracts ComicParticleFrame via BAML,
embeds the motion description, writes the multimodal fat row.

shippable=false invariant: the row stores the description + thumb only;
the panel pixel and the issue URL are kept in private Pangolin volume.
"""
from __future__ import annotations

import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import cocoindex as coco
from cocoindex.connectors import lancedb
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from numpy.typing import NDArray

from .._shared import EMBEDDER, LANCE_DB, shared_lifespan

TABLE_NAME = "cianfhoghlaim.tuatha.comic.particles"
RAW_BUCKET = os.environ.get(
    "TUATHA_RAW_COMIC_BUCKET", "s3://cianfhoghlaim-tuatha-raw/comic"
)


@dataclass
class ComicParticleRow:
    panel_id: str
    issue_id: str
    page_number: int
    particle_form: str
    color_hex: str
    motion_description: str
    character_attribution: str
    source_page_url: str | None
    run_id: str
    frame_index: int
    captured_at: str
    embedding: Annotated[NDArray, EMBEDDER]
    thumb_blob: bytes


async def _downscale(raw: bytes, max_side: int = 768) -> bytes:
    from io import BytesIO

    from PIL import Image

    img = Image.open(BytesIO(raw))
    img.thumbnail((max_side, max_side))
    buf = BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=80)
    return buf.getvalue()


async def _baml_extract_comic_particle(
    thumb: bytes, issue_id: str, page_number: int
) -> dict[str, Any]:
    from baml_client.sync_client import b  # type: ignore[import-not-found]

    issue_context = f"Issue {issue_id}, page {page_number}"
    result = b.ExtractComicParticle(
        image=thumb, issue_context=issue_context
    )
    return {
        "panel_id": result.panel_id,
        "issue_id": result.issue_id,
        "page_number": result.page_number,
        "particle_form": (
            result.particle_form.value
            if hasattr(result.particle_form, "value")
            else str(result.particle_form)
        ),
        "color_hex": result.color_hex,
        "motion_description": result.motion_description,
        "character_attribution": result.character_attribution,
        "source_page_url": result.source_page_url,
        "run_id": result.run_id,
        "frame_index": result.frame_index,
        "captured_at": result.captured_at,
    }


def _panel_id_from_path(file_path: pathlib.PurePath) -> tuple[str, int]:
    """Derive issue_id + page_number from the file path."""
    # Convention: s3://.../comic/<issue_id>/page-<N>.jpg
    parts = file_path.parts
    issue_id = parts[-2]
    page_str = parts[-1].replace("page-", "").split(".")[0]
    return issue_id, int(page_str)


@coco.fn(memo=True)
async def process_comic_page(
    file: FileLike, table: lancedb.TableTarget
) -> None:
    raw = await file.read_bytes()
    issue_id, page_number = _panel_id_from_path(file.file_path.path)
    thumb = await _downscale(raw)
    frame = await _baml_extract_comic_particle(thumb, issue_id, page_number)
    desc = f"{frame['particle_form']} {frame['motion_description']} {frame['character_attribution']}"
    vec = await coco.use_context(EMBEDDER).embed(desc)
    table.declare_row(
        row=ComicParticleRow(
            panel_id=frame["panel_id"],
            issue_id=frame["issue_id"],
            page_number=frame["page_number"],
            particle_form=frame["particle_form"],
            color_hex=frame["color_hex"],
            motion_description=frame["motion_description"],
            character_attribution=frame["character_attribution"],
            source_page_url=frame.get("source_page_url"),
            run_id=frame["run_id"],
            frame_index=frame["frame_index"],
            captured_at=frame["captured_at"],
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
            ComicParticleRow, primary_key=["panel_id"]
        ),
    )
    table.declare_vector_index(column="embedding")
    table.declare_fts_index(
        column="motion_description", language="English", with_position=True
    )
    files = await lancedb.s3_walk_dir(
        RAW_BUCKET,
        path_matcher=PatternFilePathMatcher(
            included_patterns=["**/page-*.jpg"],
            excluded_patterns=["**/thumbs"],
        ),
        live=True,
    )
    await coco.mount_each(process_comic_page, files.items(), table)


comic_particles_app = coco.App(
    coco.AppConfig(name="tuatha_comic_particles"),
    app_main,
    lifespan=shared_lifespan,
)


if __name__ == "__main__":
    import cocoindex as _ci

    _ci.init()
    comic_particles_app.update()
