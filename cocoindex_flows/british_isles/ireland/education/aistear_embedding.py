"""
Aistear (Early Years) CocoIndex embedding flow.

Per the 2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1
change (Step 2 of the cianfhoghlaim-nua v6 era plan). Consumes
the ~70 Aistear PDFs from stedding/site_scrape_samples/aistear/
and writes embeddings to LanceDB.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Annotated

import cocoindex as coco
from cocoindex.connectors import lancedb, localfs
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from numpy.typing import NDArray

from ..._shared._lifespan import EMBEDDER, LANCE_DB, shared_lifespan

# Source directory (the Aistear PDFs from the stedding scrape)
AISTEAR_RAW_ROOT: pathlib.Path = pathlib.Path(
    __import__("os").environ.get(
        "BI_EP_AISTEAR_RAW_ROOT",
        pathlib.Path.cwd() / "stedding" / "site_scrape_samples" / "aistear",
    )
)


@dataclass(frozen=True)
class AistearChunk:
    chunk_id: str
    subject: str
    ga_term: str
    ga_definition: str
    text_en: str
    text_ga: str
    age_band: str  # "infant" / "toddler" / "preschool"
    pedagogy_theme: str  # "wellbeing" / "identity_belonging" / "communicating" / "exploring_thinking"
    source_pdf: str
    page: int
    embedding: Annotated[NDArray, EMBEDDER]


_splitter = coco.SentenceSplitter()


@coco.AppConfig(name="ireland_aistear_embedding")
@coco.fn
def aistear_app() -> None:
    source_dir = AISTEAR_RAW_ROOT
    table_name = "cianhfhoghlaim.ireland.education.aistear"

    @coco.fn
    async def process_file(file: FileLike) -> None:
        text = file.content.decode("utf-8", errors="replace")
        chunks = _splitter.split(text)
        for i, chunk in enumerate(chunks):
            await LANCE_DB.upsert(
                table_name,
                coco.Row(
                    chunk_id=f"{file.path.name}::{i}",
                    subject="aistear",
                    ga_term="",
                    ga_definition="",
                    text_en=chunk,
                    text_ga="",
                    age_band="",
                    pedagogy_theme="",
                    source_pdf=file.path.name,
                    page=0,
                ),
                embedding=await EMBEDDER.embed(chunk),
            )

    files = localfs.walk_dir(
        source_dir,
        recursive=True,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/*.pdf", "**/*.txt", "**/*.md"]),
        live=True,
    )
    await coco.mount_each(process_file, files.items())


__all__ = ["aistear_app", "AistearChunk", "AISTEAR_RAW_ROOT"]
