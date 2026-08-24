"""CocoIndex v1 App for the Nigerian education pipeline.

Embeds every Nigerian federal + state education row into the shared
LanceDB table ``oideachais.commonwealth.nga.education_chunks`` using the
canonical ``BAAI/bge-m3`` 1024-d multilingual embedder.

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

from ..._shared._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)

TABLE_NAME = "oideachais.commonwealth.nga.education_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every Nigerian federal + "
    "state education row (37 sub-units × 5 domains = 195 sources)."
)
SOURCE_DIR = pathlib.Path("dlt/commonwealth/nga")

_splitter = RecursiveSplitter()


@dataclass
class NigeriaEducationChunk:
    chunk_id: str
    country: str
    state_code: str
    federal_institution: str
    language: str
    domain: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]
    source_url: str
    document_type: str
    extracted_at: str = datetime.now(UTC).isoformat()


@coco.fn(memo=True)
async def process_nigeria_education_file(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Process one Nigerian federal or state education file."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    parts = file.file_path.parts
    state_code = parts[3] if len(parts) >= 5 else "nga_federal"
    domain = parts[4] if len(parts) >= 5 else "education"
    language = parts[6] if len(parts) >= 7 else "en"
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=NigeriaEducationChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                country="nga",
                state_code=state_code,
                federal_institution=state_code if state_code.startswith("nga_federal_") else "",
                language=language,
                domain=domain,
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="nigeria_education",
            ),
        )


@coco.fn
async def app_main() -> None:
    """Wire the Nigerian education pipeline App."""
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            NigeriaEducationChunk, primary_key=["chunk_id"]
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
        process_nigeria_education_file, files.items(), target_table
    )


nigeria_education_embedding = coco.App(
    coco.AppConfig(
        name="nigeria_education_embedding",
    ),
    app_main,
)


__all__ = [
    "NigeriaEducationChunk",
    "TABLE_DESCRIPTION",
    "TABLE_NAME",
    "nigeria_education_embedding",
    "shared_lifespan",
]
