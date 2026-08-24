"""CocoIndex v1 App for the Commonwealth of Nations education pipeline.

Embeds every Commonwealth per-nation education row (Australia / CAN / New Zealand /
India / South Africa + the 51 remaining Commonwealth members in the follow-on
change) into the shared LanceDB table
``oideachais.commonwealth.education_chunks`` using the canonical
``BAAI/bge-m3`` 1024-d multilingual embedder.

Conforms to the R1–R4 conformance contract (imports
``shared_lifespan`` + the canonical ContextKeys from ``_lifespan.py``;
the ``coco.App`` is at module scope; the module declares at least
one ``@coco.fn``).
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

TABLE_NAME = "oideachais.commonwealth.education_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every Commonwealth "
    "per-nation education row (Australia / CAN / New Zealand / India / South Africa + the 51 "
    "remaining Commonwealth members in the follow-on change)."
)
SOURCE_DIR = pathlib.Path("dlt/commonwealth")

_splitter = RecursiveSplitter()


@dataclass
class CommonwealthEducationChunk:
    chunk_id: str
    country_code: str
    language: str
    domain: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]
    source_url: str
    document_type: str
    extracted_at: str = datetime.now(UTC).isoformat()


@coco.fn(memo=True)
async def process_commonwealth_education_file(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Process one Commonwealth per-nation education file."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    country_code = file.file_path.parts[2] if len(file.file_path.parts) >= 3 else "commonwealth"
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=CommonwealthEducationChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                country_code=country_code,
                language=file.file_path.parent.name
                if len(file.file_path.parts) >= 2
                else "en",
                domain="education",
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="commonwealth_education",
            ),
        )


@coco.fn
async def app_main() -> None:
    """Wire the Commonwealth education pipeline App."""
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            CommonwealthEducationChunk, primary_key=["chunk_id"]
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
        process_commonwealth_education_file, files.items(), target_table
    )


commonwealth_education_embedding = coco.App(
    coco.AppConfig(
        name="commonwealth_education_embedding",
    ),
    app_main,
)


__all__ = [
    "CommonwealthEducationChunk",
    "TABLE_DESCRIPTION",
    "TABLE_NAME",
    "commonwealth_education_embedding",
    "shared_lifespan",
]
