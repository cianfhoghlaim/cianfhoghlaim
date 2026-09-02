"""
Primary CocoIndex embedding flow.

Per the 2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1
change (Step 2 of the cianfhoghlaim-nua v6 era plan). Consumes
the ~137 Primary PDFs from stedding/site_scrape_samples/primary/
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

PRIMARY_RAW_ROOT: pathlib.Path = pathlib.Path(
    __import__("os").environ.get(
        "BI_EP_PRIMARY_RAW_ROOT",
        pathlib.Path.cwd() / "stedding" / "site_scrape_samples" / "primary",
    )
)


@dataclass(frozen=True)
class PrimaryChunk:
    chunk_id: str
    subject: str
    ga_term: str
    ga_definition: str
    text_en: str
    text_ga: str
    curriculum_area: str  # "language" / "mathematics" / "sese" / "sphe" / "pe" / "art" / "music"
    class_level: str  # "junior_infants" / "senior_infants" / "1st_class" / "2nd_class" / "3rd_class" / "4th_class" / "5th_class" / "6th_class"
    source_pdf: str
    page: int
    embedding: Annotated[NDArray, EMBEDDER]


_splitter = coco.SentenceSplitter()


@coco.AppConfig(name="ireland_primary_embedding")
@coco.fn
def primary_app() -> None:
    source_dir = PRIMARY_RAW_ROOT
    table_name = "cianhfhoghlaim.ireland.education.primary"

    @coco.fn
    async def process_file(file: FileLike) -> None:
        text = file.content.decode("utf-8", errors="replace")
        chunks = _splitter.split(text)
        for i, chunk in enumerate(chunks):
            await LANCE_DB.upsert(
                table_name,
                coco.Row(
                    chunk_id=f"{file.path.name}::{i}",
                    subject="primary",
                    ga_term="",
                    ga_definition="",
                    text_en=chunk,
                    text_ga="",
                    curriculum_area="",
                    class_level="",
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


__all__ = ["primary_app", "PrimaryChunk", "PRIMARY_RAW_ROOT"]
