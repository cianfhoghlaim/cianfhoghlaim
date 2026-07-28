"""England A-Level CocoIndex v1 Apps (BIEP v3 — M3).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Parameterised CocoIndex v1 App factory for the 147 England A-Level cohorts:
- 49 A-Level subjects × 3 boards (AQA + OCR + Edexcel) = 147 per-subject Apps

Each App:
- Reads from the canonical BIEP v3 DuckLake namespace
  `cianfhoghlaim.education.england.a_level.<board>.<subject>.voted_canonical`
- Embeds via the canonical BAAI/bge-m3 1024-d embedder
- Writes to the canonical BIEP v3 LanceDB table
  `cianhoghlaim.england.a_level.<board>.<subject>_a_level_chunks`

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

# The 49 A-Level subjects (per baml_src/.../england/education/subject_taxonomy.baml:ALevelAQASubject)
A_LEVEL_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "further_mathematics",
    "pure_mathematics",
    "statistics",
    "mechanics",
    "decision_maths",
    "english_literature",
    "english_language_and_literature",
    "biology",
    "chemistry",
    "physics",
    "geology",
    "human_biology",
    "environmental_science",
    "french",
    "german",
    "spanish",
    "latin",
    "italian",
    "classical_civilisation",
    "ancient_history",
    "history",
    "geography",
    "religious_studies",
    "philosophy",
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
    "applied_business",
    "applied_ict",
    "communication_and_culture",
    "critical_thinking",
    "general_studies",
    "performing_arts",
    "psychology_a2",
    "sociology_a2",
    "politics_a2",
    "law_a2",
    "other",
    "engineering",
)

_splitter = RecursiveSplitter()


@dataclass
class EnglandALevelChunk:
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
# 49 × 3 = 147 per-subject × per-board Apps
# -----------------------------------------------------------------------------

def _make_england_a_level_app(board: str, subject: str):
    """Factory: build a CocoIndex v1 App for one (board, A-Level subject) cohort."""
    table_name = f"cianhoghlaim.england.a_level.{board}.{subject}_a_level_chunks"
    source_dir = pathlib.Path(f"england_a_level/{board}/{subject}")
    table_description = (
        f"Multilingual 1024-d BGE-M3 embeddings of every England A-Level "
        f"{subject} {board.upper()} row (BIEP v3 — M3 milestone)."
    )

    @coco.fn(memo=True)
    async def process_england_a_level_file(
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
                row=EnglandALevelChunk(
                    chunk_id=await id_gen.next_id(chunk.text),
                    nation=f"en_a_level_{board}",
                    board=board,
                    subject=subject,
                    language="en",
                    text=chunk.text,
                    embedding=vec,
                    source_url=str(file.file_path),
                    document_type=f"england_a_level_{board}_{subject}",
                ),
            )

    @coco.fn
    async def england_a_level_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,
            table_name=table_name,
            table_schema=await lancedb.TableSchema.from_class(
                EnglandALevelChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        if not source_dir.exists():
            return
        for path in source_dir.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".txt", ".json"):
                file_like = FileLike(path=str(path))
                await process_england_a_level_file(file_like, target_table)

    return coco.App(
        coco.AppConfig(
            name=f"england_a_level_{board}_{subject}_embedding",
            description=table_description,
        ),
        england_a_level_app_main,
    )


# Generate the 147 per-(board, subject) A-Level CocoIndex v1 Apps
england_a_level_apps = {
    (board, subject): _make_england_a_level_app(board, subject)
    for board in ENGLAND_BOARDS
    for subject in A_LEVEL_SUBJECTS
}


__all__ = [
    "EnglandALevelChunk",
    "ENGLAND_BOARDS",
    "A_LEVEL_SUBJECTS",
    "england_a_level_apps",
    "shared_lifespan",
]
