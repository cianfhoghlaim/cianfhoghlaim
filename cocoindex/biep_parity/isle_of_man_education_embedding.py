"""CocoIndex v1 App for the Isle of Man Government education pipeline.

Embeds every per-island education row into the shared LanceDB table
``cianfhoghlaim.biep.crown.isle_of_man.education_chunks`` using the canonical
``BAAI/bge-m3`` 1024-d multilingual embedder.
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

TABLE_NAME = "cianfhoghlaim.biep.crown.isle_of_man.education_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every Isle of Man Government "
    "education row."
)
SOURCE_DIR = pathlib.Path("dlt/british_isles/isle_of_man/education/island")

_splitter = RecursiveSplitter()


@dataclass
class ISLE_OF_MANEducationChunk:
    chunk_id: str
    island: str
    language: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]
    source_url: str
    document_type: str
    extracted_at: str = datetime.now(UTC).isoformat()


@coco.fn(memo=True)
async def process_isle_of_man_education_file(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Process one Isle of Man Government education file."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    language = file.file_path.parent.name if len(file.file_path.parts) >= 2 else "en"
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=ISLE_OF_MANEducationChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                island="isle_of_man",
                language=language,
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="isle_of_man_education",
            ),
        )


@coco.fn
async def app_main() -> None:
    """Wire the Isle of Man Government education pipeline App."""
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            ISLE_OF_MANEducationChunk, primary_key=["chunk_id"]
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
        process_isle_of_man_education_file, files.items(), target_table
    )


isle_of_man_education_embedding = coco.App(
    coco.AppConfig(
        name="isle_of_man_education_embedding",
        description=TABLE_DESCRIPTION,
    ),
    app_main,
)


__all__ = [
    "ISLE_OF_MANEducationChunk",
    "TABLE_DESCRIPTION",
    "TABLE_NAME",
    "isle_of_man_education_embedding",
    "shared_lifespan",
]
