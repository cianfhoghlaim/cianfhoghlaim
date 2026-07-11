"""CocoIndex v1 App for the Quebec + Montreal education pipeline.

Embeds every Quebec + Montreal education row (Ministry + 3 Montreal
school boards + 1 Montreal university cluster) into the shared
LanceDB table ``oideachais.commonwealth.can.qc.education_chunks``
using the canonical ``BAAI/bge-m3`` 1024-d multilingual embedder.

Conforms to the R1–R4 conformance contract (imports
``shared_lifespan`` + the canonical ContextKeys from ``_lifespan.py``).
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

TABLE_NAME = "oideachais.commonwealth.can.qc.education_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every Quebec + Montreal "
    "education row (MEES + 3 school boards + Montreal universities)."
)
SOURCE_DIR = pathlib.Path("dlt/commonwealth/can/qc/education")

_splitter = RecursiveSplitter()


@dataclass
class QuebecEducationChunk:
    chunk_id: str
    province: str
    language: str
    domain: str
    school_board: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]
    source_url: str
    document_type: str
    extracted_at: str = datetime.now(UTC).isoformat()


@coco.fn(memo=True)
async def process_quebec_education_file(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Process one Quebec + Montreal education file."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    parts = file.file_path.parts
    school_board = parts[5] if len(parts) >= 6 else "unknown"
    language = parts[6] if len(parts) >= 7 else "fr"
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=QuebecEducationChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                province="qc",
                language=language,
                domain="education",
                school_board=school_board,
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="quebec_education",
            ),
        )


@coco.fn
async def app_main() -> None:
    """Wire the Quebec + Montreal education pipeline App."""
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            QuebecEducationChunk, primary_key=["chunk_id"]
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
        process_quebec_education_file, files.items(), target_table
    )


quebec_montreal_education_embedding = coco.App(
    coco.AppConfig(
        name="quebec_montreal_education_embedding",
        description=TABLE_DESCRIPTION,
    ),
    app_main,
)


__all__ = [
    "QuebecEducationChunk",
    "TABLE_DESCRIPTION",
    "TABLE_NAME",
    "quebec_montreal_education_embedding",
    "shared_lifespan",
]
