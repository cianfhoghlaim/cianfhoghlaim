"""Ireland LC English CocoIndex v1 App (BIEP v3).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Mirrors the pattern of `ireland_lc_mathematics_embedding.py` for the
Ireland LC English subject. Declares 2 CocoIndex v1 Apps (one per
language):
- ireland_lc_english_untiered_en_embedding
- ireland_lc_english_untiered_ga_embedding
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

from cianfhoghlaim.cocoindex._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


TABLE_NAME_EN = "cianhoghlaim.ireland.leaving_cycle.english.untiered_en_chunks"
TABLE_NAME_GA = "cianhoghlaim.ireland.leaving_cycle.english.untiered_ga_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every Ireland LC English "
    "row in EN + GA (BIEP v3 — M1 milestone)."
)
SOURCE_DIR = pathlib.Path("leaving_certificate/english")

_splitter = RecursiveSplitter()


@dataclass
class IrelandLCEnglishChunk:
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
async def process_ireland_lc_english_file(
    file: FileLike,
    table: lancedb.TableTarget,
    language: str,
) -> None:
    """Process one Ireland LC English file."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=IrelandLCEnglishChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                nation="ie_english",
                subject="english",
                language=language,
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="ireland_lc_english",
            ),
        )


@coco.fn
async def ireland_lc_english_app_main() -> None:
    """Wire the Ireland LC English pipeline App (EN + GA)."""
    for table_name, language in (
        (TABLE_NAME_EN, "en"),
        (TABLE_NAME_GA, "ga"),
    ):
        target_table = await lancedb.mount_table_target(
            LANCE_DB,
            table_name=table_name,
            table_schema=await lancedb.TableSchema.from_class(
                IrelandLCEnglishChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        files = localfs.walk_dir(
            SOURCE_DIR / language,
            recursive=True,
            path_matcher=PatternFilePathMatcher(
                included_patterns=["**/*.md", "**/*.txt", "**/*.json"],
            ),
            live=True,
        )
        await coco.mount_each(
            process_ireland_lc_english_file, files.items(), target_table, language
        )


ireland_lc_english_embedding = coco.App(
    coco.AppConfig(
        name="ireland_lc_english_embedding",
        description=TABLE_DESCRIPTION,
    ),
    ireland_lc_english_app_main,
)


__all__ = [
    "IrelandLCEnglishChunk",
    "TABLE_NAME_EN",
    "TABLE_NAME_GA",
    "ireland_lc_english_embedding",
    "shared_lifespan",
]
