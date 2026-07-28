"""Ireland LC Gaeilge CocoIndex v1 App (BIEP v3).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Gaeilge is taught through Irish (no English sibling). The canonical
table is `cianhoghlaim.ireland.leaving_cycle.gaeilge.untiered_ga_chunks`.
The English version is intentionally absent (per the BIEP v3 spec).

The `cross_linguistic` BAML function (ExtractCrossLinguisticConcept)
maps the GA content to the EN content for the 5 other LC subjects.
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


TABLE_NAME_GA = "cianhoghlaim.ireland.leaving_cycle.gaeilge.untiered_ga_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every Ireland LC Gaeilge "
    "row in GA (BIEP v3 — M1 milestone). Gaeilge is Irish-only; the English "
    "sibling is intentionally absent."
)
SOURCE_DIR = pathlib.Path("leaving_certificate/gaeilge")

_splitter = RecursiveSplitter()


@dataclass
class IrelandLCGaeilgeChunk:
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
async def process_ireland_lc_gaeilge_file(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Process one Ireland LC Gaeilge file."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=IrelandLCGaeilgeChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                nation="ie_gaeilge",
                subject="gaeilge",
                language="ga",
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="ireland_lc_gaeilge",
            ),
        )


@coco.fn
async def ireland_lc_gaeilge_app_main() -> None:
    """Wire the Ireland LC Gaeilge pipeline App (GA only)."""
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME_GA,
        table_schema=await lancedb.TableSchema.from_class(
            IrelandLCGaeilgeChunk, primary_key=["chunk_id"]
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
        process_ireland_lc_gaeilge_file, files.items(), target_table
    )


ireland_lc_gaeilge_embedding = coco.App(
    coco.AppConfig(
        name="ireland_lc_gaeilge_embedding",
        description=TABLE_DESCRIPTION,
    ),
    ireland_lc_gaeilge_app_main,
)


__all__ = [
    "IrelandLCGaeilgeChunk",
    "TABLE_NAME_GA",
    "ireland_lc_gaeilge_embedding",
    "shared_lifespan",
]
