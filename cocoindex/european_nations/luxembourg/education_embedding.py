"""CocoIndex v1 App for the Luxembourg (Luxembourg) education pipeline.

Embeds every Luxembourg per-subject education row into the
shared LanceDB table ``cianfhoghlaim.lc.european_nations.lux.education_chunks`` using the canonical
``BAAI/bge-m3`` 1024-d multilingual embedder.

Conforms to the R1-R4 conformance contract (imports
``shared_lifespan`` + the canonical ContextKeys from
``_lifespan.py``; the ``coco.App`` is at module scope; the module
declares at least one ``@coco.fn``).
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

TABLE_NAME = "cianfhoghlaim.lc.european_nations.lux.education_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every Luxembourg "
    "per-subject education row (EU full-depth expansion change)."
)
SOURCE_DIR = pathlib.Path("dlt/european_nations/lux/education/subjects")

_splitter = RecursiveSplitter()


@dataclass
class LuxembourgEducationChunk:
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
async def process_lux_education_file(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Process one Luxembourg per-subject education file."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    parts = file.file_path.parts
    subject = parts[5] if len(parts) >= 6 else "unknown"
    language = parts[6] if len(parts) >= 7 else "lb"
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=LUXEducationChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                nation="lux",
                subject=subject,
                language=language,
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="lux_education",
            ),
        )


@coco.fn
async def app_main() -> None:
    """Wire the Luxembourg education pipeline App."""
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            LUXEducationChunk, primary_key=["chunk_id"]
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
        process_lux_education_file, files.items(), target_table
    )


lux_education_embedding = coco.App(
    coco.AppConfig(
        name="lux_education_embedding",
        description=TABLE_DESCRIPTION,
    ),
    app_main,
)


__all__ = [
    "LUXEducationChunk",
    "TABLE_DESCRIPTION",
    "TABLE_NAME",
    "lux_education_embedding",
    "shared_lifespan",
]
