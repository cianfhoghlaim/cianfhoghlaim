"""Ireland LC Mathematics CocoIndex v1 App (BIEP v3).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Embeds every Ireland LC mathematics row into the canonical
LanceDB table `cianhoghlaim.<jurisdiction>.<stage>.<subject>.<level>_<lang>_chunks`
using the canonical `BAAI/bge-m3` 1024-d multilingual embedder.

This file declares 2 CocoIndex v1 Apps (one per language):
- ireland_lc_mathematics_untiered_en_embedding (English)
- ireland_lc_mathematics_untiered_ga_embedding (Gaeilge)

Conforms to the R1–R4 conformance contract (imports
`shared_lifespan` + the canonical ContextKeys from
`_lifespan.py`; the `coco.App` is at module scope; the module
declares at least one `@coco.fn`).
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


TABLE_NAME_EN = "cianhoghlaim.ireland.leaving_cycle.mathematics.untiered_en_chunks"
TABLE_NAME_GA = "cianhoghlaim.ireland.leaving_cycle.mathematics.untiered_ga_chunks"
TABLE_DESCRIPTION = (
    "Multilingual 1024-d BGE-M3 embeddings of every Ireland LC mathematics "
    "row in EN + GA (BIEP v3 — M1 milestone)."
)
SOURCE_DIR = pathlib.Path("leaving_certificate/mathematics")

_splitter = RecursiveSplitter()


@dataclass
class IrelandLCMathematicsChunk:
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
async def process_ireland_lc_mathematics_file(
    file: FileLike,
    table: lancedb.TableTarget,
    language: str,
) -> None:
    """Process one Ireland LC mathematics file."""
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=2000, chunk_overlap=500, language="markdown"
    )
    id_gen = IdGenerator()
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=IrelandLCMathematicsChunk(
                chunk_id=await id_gen.next_id(chunk.text),
                nation="ie_mathematics",
                subject="mathematics",
                language=language,
                text=chunk.text,
                embedding=vec,
                source_url=str(file.file_path),
                document_type="ireland_lc_mathematics",
            ),
        )


@coco.fn
async def ireland_lc_mathematics_app_main() -> None:
    """Wire the Ireland LC mathematics pipeline App (EN + GA)."""
    for table_name, language in (
        (TABLE_NAME_EN, "en"),
        (TABLE_NAME_GA, "ga"),
    ):
        target_table = await lancedb.mount_table_target(
            LANCE_DB,
            table_name=table_name,
            table_schema=await lancedb.TableSchema.from_class(
                IrelandLCMathematicsChunk, primary_key=["chunk_id"]
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
            process_ireland_lc_mathematics_file, files.items(), target_table, language
        )


ireland_lc_mathematics_embedding = coco.App(
    coco.AppConfig(
        name="ireland_lc_mathematics_embedding",
        description=TABLE_DESCRIPTION,
    ),
    ireland_lc_mathematics_app_main,
)


__all__ = [
    "IrelandLCMathematicsChunk",
    "TABLE_DESCRIPTION",
    "TABLE_NAME_EN",
    "TABLE_NAME_GA",
    "ireland_lc_mathematics_embedding",
    "shared_lifespan",
]
