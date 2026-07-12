"""CocoIndex v1 App for EU bilingual (en + ga) alignment embeddings.

Embeds every EU institutional document (in en or ga) into a shared
LanceDB table for cross-jurisdiction alignment with the British Isles
Ireland + Northern Ireland corpus.

Conforms to the R1–R4 conformance contract (imports shared_lifespan +
EMBEDDER + LANCE_DB).
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

TABLE_NAME = "oideachais.eu.multilingual_alignment_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every EU institutional "
    "document (en + ga) for cross-jurisdiction alignment with the "
    "British Isles Ireland + Northern Ireland corpus."
)
SOURCE_DIR = pathlib.Path("stedding/ingest_queue/eu")

_splitter = RecursiveSplitter()


@dataclass
class EUMultilingualAlignmentChunk:
    chunk_id: str
    institution: str
    language: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]
    source_url: str
    document_type: str
    extracted_at: str = datetime.now(UTC).isoformat()


@coco.fn(memo=True)
async def process_eu_multilingual_file(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Process one EU institutional document for bilingual alignment."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    parts = file.file_path.parts
    institution = parts[3] if len(parts) >= 5 else "unknown"
    language = parts[5] if len(parts) >= 6 else "en"
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=EUMultilingualAlignmentChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                institution=institution,
                language=language,
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="eu_multilingual_alignment",
            ),
        )


@coco.fn
async def app_main() -> None:
    """Wire the EU multilingual alignment App."""
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            EUMultilingualAlignmentChunk, primary_key=["chunk_id"]
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
        process_eu_multilingual_file, files.items(), target_table
    )


eu_multilingual_alignment_embedding = coco.App(
    coco.AppConfig(
        name="eu_multilingual_alignment_embedding",
        description=TABLE_DESCRIPTION,
    ),
    app_main,
)


__all__ = [
    "EUMultilingualAlignmentChunk",
    "TABLE_DESCRIPTION",
    "TABLE_NAME",
    "eu_multilingual_alignment_embedding",
    "shared_lifespan",
]
