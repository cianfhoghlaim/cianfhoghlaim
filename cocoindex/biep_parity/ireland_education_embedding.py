"""Ireland education CocoIndex v1 App (BIEP v3).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The Ireland (BIEP v3) CocoIndex app. The BIEP v1 parity set has
`en/ni/sct/wls/guernsey/jersey/isle_of_man_education_embedding.py` but
NO `ireland_education_embedding.py`. This file fills the gap.

Embeds every Ireland education row (LC + JC, EN + GA) into the canonical
LanceDB table `cianhoghlaim.biep.ireland.education_chunks` using the
canonical `BAAI/bge-m3` 1024-d multilingual embedder.

The per-cohort CocoIndex apps (e.g. `ireland_lc_mathematics_embedding.py`)
are the canonical home for the M1 milestone; this `ireland_education.py`
app is the parity-shorthand that covers the full 544-cohort matrix in a
single table.
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

import cocoindex as coco
from cocoindex.connectors import lancedb, localfs
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.resources.id import IdGenerator
from cocoindex.ops.text import RecursiveSplitter
from numpy.typing import NDArray

from .._shared._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


TABLE_NAME = "cianhoghlaim.biep.ireland.education_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every Ireland education "
    "row (LC + JC, EN + GA). The BIEP v3 Ireland parity entry — fills the "
    "gap left by the BIEP v1 parity set."
)
SOURCE_DIR = pathlib.Path("dlt/british_isles/ireland/education")

_splitter = RecursiveSplitter()


@dataclass
class IrelandEducationChunk:
    chunk_id: str
    nation: str
    subject: str
    language: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]
    source_url: str
    document_type: str
    extracted_at: str = datetime.now(UTC).isoformat()


@coco.fn(memo=True)
async def process_ireland_education_file(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Process one Ireland education file."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    parts = file.file_path.parts
    subject = parts[5] if len(parts) >= 6 else "unknown"
    language = parts[6] if len(parts) >= 7 else "en"
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=IrelandEducationChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                nation="ie",
                subject=subject,
                language=language,
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="ireland_education",
            ),
        )


@coco.fn
async def ireland_education_app_main() -> None:
    """Wire the Ireland education pipeline App."""
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            IrelandEducationChunk, primary_key=["chunk_id"]
        ),
    )
    target_table.declare_vector_index(column="embedding")
    files = localfs.walk_dir(
        SOURCE_DIR,
        recursive=True,
        path_matcher=PatternFilePathMatcher(
            included_patterns=["**/*.md", "**/*.txt", "**/*.json"],
        ),
        live=True,
    )
    await coco.mount_each(
        process_ireland_education_file, files.items(), target_table
    )


ireland_education_embedding = coco.App(
    coco.AppConfig(
        name="ireland_education_embedding",
        description=TABLE_DESCRIPTION,
    ),
    ireland_education_app_main,
)


__all__ = [
    "IrelandEducationChunk",
    "TABLE_NAME",
    "ireland_education_embedding",
    "shared_lifespan",
]
