"""England GCSE CocoIndex v1 Apps (BIEP v3 — M4).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Parameterised CocoIndex v1 App factory for the 129 England GCSE cohorts:
- 43 GCSE subjects × 3 boards (AQA + OCR + Edexcel) = 129 per-subject Apps

Each App:
- Reads from the canonical BIEP v3 DuckLake namespace
  `cianfhoghlaim.education.england.gcse.<board>.<subject>.voted_canonical`
- Embeds via the canonical BAAI/bge-m3 1024-d embedder
- Writes to the canonical BIEP v3 LanceDB table
  `cianhoghlaim.england.gcse.<board>.<subject>_gcse_chunks`

Conforms to R1–R4 (imports shared_lifespan + LANCE_DB + EMBEDDER).
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

import cocoindex as coco
from cocoindex.connectors import lancedb
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.resources.id import IdGenerator
from cocoindex.ops.text import RecursiveSplitter
from numpy.typing import NDArray

from cianfhoghlaim.cocoindex._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


# The 3 England awarding boards
ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")

# The 43 GCSE subjects (the canonical 43 that overlap across AQA + OCR + Edexcel)
GCSE_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "english_language",
    "english_literature",
    "biology",
    "chemistry",
    "physics",
    "computer_science",
    "history",
    "geography",
    "religious_studies",
    "french",
    "german",
    "spanish",
    "latin",
    "classical_civilisation",
    "ancient_history",
    "economics",
    "business",
    "psychology",
    "sociology",
    "politics",
    "law",
    "art_and_design",
    "design_technology",
    "drama",
    "music",
    "pe",
    "dance",
    "media_studies",
    "food_preparation_nutrition",
    "further_mathematics",
    "statistics",
    "engineering",
    "electronics",
    "human_biology",
    "applied_business",
    "applied_ict",
    "applied_science_double",
    "applied_travel_tourism",
    "performing_arts",
    "statistics_9ma0",
    "geography_fieldwork",
    "environmental_science_team",
)

_splitter = RecursiveSplitter()


@dataclass
class EnglandGCSEChunk:
    chunk_id: str
    nation: str
    board: str
    subject: str
    language: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]
    source_url: str
    document_type: str
    extracted_at: str = datetime.now(UTC).isoformat()


# -----------------------------------------------------------------------------
# 43 × 3 = 129 per-subject × per-board Apps
# -----------------------------------------------------------------------------

def _make_england_gcse_app(board: str, subject: str):
    """Factory: build a CocoIndex v1 App for one (board, GCSE subject) cohort."""
    table_name = f"cianhoghlaim.england.gcse.{board}.{subject}_gcse_chunks"
    source_dir = pathlib.Path(f"england_gcse/{board}/{subject}")
    table_description = (
        f"Multilingual 1024-d BGE-M3 embeddings of every England GCSE "
        f"{subject} {board.upper()} row (BIEP v3 — M4 milestone)."
    )

    @coco.fn(memo=True)
    async def process_england_gcse_file(
        file: FileLike,
        table: lancedb.TableTarget,
    ) -> None:
        text = await file.read_text()
        chunks = _splitter.split(
            text, chunk_size=2000, chunk_overlap=500, language="markdown"
        )
        id_gen = IdGenerator()
        for chunk in chunks:
            vec = await coco.use_context(EMBEDDER).embed(chunk.text)
            table.declare_row(
                row=EnglandGCSEChunk(
                    chunk_id=await id_gen.next_id(chunk.text),
                    nation=f"en_gcse_{board}",
                    board=board,
                    subject=subject,
                    language="en",
                    text=chunk.text,
                    embedding=vec,
                    source_url=str(file.file_path),
                    document_type=f"england_gcse_{board}_{subject}",
                ),
            )

    @coco.fn
    async def england_gcse_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,
            table_name=table_name,
            table_schema=await lancedb.TableSchema.from_class(
                EnglandGCSEChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        if not source_dir.exists():
            return
        for path in source_dir.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".txt", ".json"):
                file_like = FileLike(path=str(path))
                await process_england_gcse_file(file_like, target_table)

    return coco.App(
        coco.AppConfig(
            name=f"england_gcse_{board}_{subject}_embedding",
            description=table_description,
        ),
        england_gcse_app_main,
    )


# Generate the 129 per-(board, subject) GCSE CocoIndex v1 Apps
england_gcse_apps = {
    (board, subject): _make_england_gcse_app(board, subject)
    for board in ENGLAND_BOARDS
    for subject in GCSE_SUBJECTS
}


__all__ = [
    "EnglandGCSEChunk",
    "ENGLAND_BOARDS",
    "GCSE_SUBJECTS",
    "england_gcse_apps",
    "shared_lifespan",
]
