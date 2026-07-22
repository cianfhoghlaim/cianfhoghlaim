"""CocoIndex v1 App for the EU nations + Ukraine medicine pipeline.

Embeds every per-nation medicine row into the shared
``cianfhoghlaim.eu_nations.medicine_chunks`` LanceDB table using the
canonical ``BAAI/bge-m3`` 1024-d multilingual embedder.

Conforms to the R1–R4 conformance contract (imports
``shared_lifespan`` + the canonical ContextKeys from ``_lifespan.py``;
the ``coco.App`` is at module scope; the module declares at least
one ``@coco.fn``).
"""
from __future__ import annotations

import pathlib
from collections.abc import AsyncIterator
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

TABLE_NAME = "cianfhoghlaim.eu_nations.medicine_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every EU nations "
    "+ Ukraine per-nation {domain} row (Ukraine / France / Germany / Poland / "
    "Spain / Italy + the 21 remaining EU member states + EEA/EFTA)."
)
SOURCE_DIR = pathlib.Path("dlt/european_nations")

_splitter = RecursiveSplitter()


@dataclass
class MedicineChunk:
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
async def process_medicine_file(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Process one per-nation {domain} file into the shared LanceDB table."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    country_code = file.file_path.parts[2] if len(file.file_path.parts) >= 3 else "eu"
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=MedicineChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                country_code=country_code,
                language=file.file_path.parent.name
                if len(file.file_path.parts) >= 2
                else "en",
                domain="medicine",
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="eu_nation_medicine",
            ),
        )


@coco.fn
async def app_main() -> None:
    """Wire the EU nations + Ukraine {domain} pipeline App."""
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            MedicineChunk, primary_key=["chunk_id"]
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
    await coco.mount_each(process_medicine_file, files.items(), target_table)


european_nations_medicine_embedding = coco.App(
    coco.AppConfig(
        name="european_nations_medicine_embedding",
        description=TABLE_DESCRIPTION,
    ),
    app_main,
)


__all__ = [
    "MedicineChunk",
    "TABLE_DESCRIPTION",
    "TABLE_NAME",
    "european_nations_medicine_embedding",
    "shared_lifespan",
]
