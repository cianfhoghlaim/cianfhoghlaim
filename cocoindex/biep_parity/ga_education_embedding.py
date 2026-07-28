"""Gaeilge (Irish) education CocoIndex v1 App (BIEP v3 parity).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The `ga_education_embedding.py` CocoIndex app was missing in the
BIEP v1 parity set (which already had `en/ni/sct/wls/guernsey/jersey/
isle_of_man_education_embedding.py`). This is the BIEP v3 entry that
fills the gap.

Embeds every Ireland Gaeilge-language row into the canonical
LanceDB table `cianhoghlaim.biep.ga.education_chunks` using the canonical
`BAAI/bge-m3` 1024-d multilingual embedder.

Conforms to the R1–R4 conformance contract.
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


TABLE_NAME = "cianhoghlaim.biep.ga.education_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every Ireland Gaeilge (Irish) "
    "education row. BIEP v3 parity entry — fills the gap left by the "
    "BIEP v1 parity set (which had en/ni/sct/wls/guernsey/jersey/"
    "isle_of_man but not ga)."
)
SOURCE_DIR = pathlib.Path("dlt/british_isles/ga/education")

_splitter = RecursiveSplitter()


@dataclass
class GAEducationChunk:
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
async def process_ga_education_file(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Process one Gaeilge education file."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    parts = file.file_path.parts
    subject = parts[5] if len(parts) >= 6 else "unknown"
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=GAEducationChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                nation="ga",
                subject=subject,
                language="ga",
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="ga_education",
            ),
        )


@coco.fn
async def ga_education_app_main() -> None:
    """Wire the Gaeilge education pipeline App."""
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            GAEducationChunk, primary_key=["chunk_id"]
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
        process_ga_education_file, files.items(), target_table
    )


ga_education_embedding = coco.App(
    coco.AppConfig(
        name="ga_education_embedding",
        description=TABLE_DESCRIPTION,
    ),
    ga_education_app_main,
)


__all__ = [
    "GAEducationChunk",
    "TABLE_NAME",
    "ga_education_embedding",
    "shared_lifespan",
]
