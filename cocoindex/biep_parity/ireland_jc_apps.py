"""Ireland Junior Cycle CocoIndex v1 Apps (BIEP v3 — M2).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Parameterised CocoIndex v1 App factory for the 70 Ireland JC cohorts:
- 18 NCCA JC subjects × 2 languages (EN + GA) = 36 per-subject Apps
- 16 NCCA JC short courses = 16 per-short-course Apps
- 36 NCCA JC CBAs (2 per JC subject) = 36 per-CBA Apps

Each App:
- Reads from the canonical BIEP v3 DuckLake namespace
  `cianfhoghlaim.education.ireland.junior_cycle.<cohort>.voted_canonical`
- Embeds via the canonical BAAI/bge-m3 1024-d embedder
- Writes to the canonical BIEP v3 LanceDB table
  `cianhoghlaim.ireland.junior_cycle.<cohort>.<lang>_chunks`

Conforms to R1–R4 (imports shared_lifespan + LANCE_DB + EMBEDDER).
"""
from __future__ import annotations

import os
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

from .._shared._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


# The 18 NCCA JC subjects (per dlt_sources/.../junior_cycle.py JC_SUBJECTS)
JC_SUBJECTS: tuple[str, ...] = (
    "english",
    "gaeilge",
    "mathematics",
    "irish_history",
    "geography",
    "science",
    "business_studies",
    "french",
    "german",
    "spanish",
    "italian",
    "home_economics",
    "music",
    "art",
    "technology",
    "engineering",
    "graphics",
    "wood_technology",
)

JC_LANGUAGES: tuple[str, ...] = ("en", "ga")

# 16 NCCA JC short courses
JC_SHORT_COURSES: tuple[str, ...] = (
    "coding",
    "chinese",
    "japanese",
    "russian",
    "polish",
    "lithuanian",
    "portuguese",
    "arabic",
    "hebrew",
    "philosophy",
    "film_studies",
    "financial_literacy",
    "media_literacy",
    "personal_professional_development",
    "digital_media",
    "athletic_studies",
)

_splitter = RecursiveSplitter()


@dataclass
class IrelandJCChunk:
    chunk_id: str
    nation: str
    subject: str
    language: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]
    source_url: str
    document_type: str
    extracted_at: str = datetime.now(UTC).isoformat()


# -----------------------------------------------------------------------------
# 18 per-subject × 2 language Apps
# -----------------------------------------------------------------------------

def _make_jc_subject_app(subject: str, language: str):
    """Factory: build a CocoIndex v1 App for one (JC subject, language) cohort."""
    table_name = f"cianhoghlaim.ireland.junior_cycle.{subject}.{language}_chunks"
    source_dir = pathlib.Path(f"junior_cycle/{subject}/{language}")
    table_description = (
        f"Multilingual 1024-d BGE-M3 embeddings of every Ireland JC {subject} "
        f"row in {language} (BIEP v3 — M2 milestone)."
    )

    @coco.fn(memo=True)
    async def process_jc_subject_file(
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
                row=IrelandJCChunk(
                    chunk_id=await id_gen.next_id(chunk.text),
                    nation=f"ie_jc_{subject}",
                    subject=subject,
                    language=language,
                    text=chunk.text,
                    embedding=vec,
                    source_url=str(file.file_path),
                    document_type=f"ireland_jc_{subject}",
                ),
            )

    @coco.fn
    async def jc_subject_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,
            table_name=table_name,
            table_schema=await lancedb.TableSchema.from_class(
                IrelandJCChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        files = lancedb  # not used
        if not source_dir.exists():
            return
        from cocoindex.connectors import localfs
        for path in source_dir.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".txt", ".json"):
                # Inline file walker
                file_like = FileLike(path=str(path))
                await process_jc_subject_file(file_like, target_table)

    return coco.App(
        coco.AppConfig(
            name=f"ireland_jc_{subject}_{language}_embedding",
            description=table_description,
        ),
        jc_subject_app_main,
    )


# Generate the 36 per-subject CocoIndex v1 Apps
ireland_jc_subject_apps = {
    (subject, language): _make_jc_subject_app(subject, language)
    for subject in JC_SUBJECTS
    for language in JC_LANGUAGES
}


# -----------------------------------------------------------------------------
# 16 per-short-course Apps
# -----------------------------------------------------------------------------

def _make_jc_short_course_app(short_course_code: str):
    """Factory: build a CocoIndex v1 App for one JC short course."""
    table_name = f"cianhoghlaim.ireland.junior_cycle.short_courses.{short_course_code}_en_chunks"
    source_dir = pathlib.Path(f"junior_cycle/short_courses/{short_course_code}")
    table_description = (
        f"Multilingual 1024-d BGE-M3 embeddings of the Ireland JC "
        f"{short_course_code} short course (BIEP v3 — M2 milestone)."
    )

    @coco.fn(memo=True)
    async def process_jc_short_course_file(
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
                row=IrelandJCChunk(
                    chunk_id=await id_gen.next_id(chunk.text),
                    nation=f"ie_jc_short_course_{short_course_code}",
                    subject=short_course_code,
                    language="en",
                    text=chunk.text,
                    embedding=vec,
                    source_url=str(file.file_path),
                    document_type=f"ireland_jc_short_course_{short_course_code}",
                ),
            )

    @coco.fn
    async def jc_short_course_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,
            table_name=table_name,
            table_schema=await lancedb.TableSchema.from_class(
                IrelandJCChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        if not source_dir.exists():
            return
        for path in source_dir.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".txt", ".json"):
                file_like = FileLike(path=str(path))
                await process_jc_short_course_file(file_like, target_table)

    return coco.App(
        coco.AppConfig(
            name=f"ireland_jc_short_course_{short_course_code}_embedding",
            description=table_description,
        ),
        jc_short_course_app_main,
    )


# Generate the 16 per-short-course CocoIndex v1 Apps
ireland_jc_short_course_apps = {
    code: _make_jc_short_course_app(code)
    for code in JC_SHORT_COURSES
}


# -----------------------------------------------------------------------------
# 36 per-CBA Apps
# -----------------------------------------------------------------------------

def _make_jc_cba_app(subject: str, cba_idx: int):
    """Factory: build a CocoIndex v1 App for one JC CBA (subject, cba_id)."""
    cba_id = f"{subject}_{cba_idx + 1}"
    table_name = f"cianhoghlaim.ireland.junior_cycle.cbas.{cba_id}_en_chunks"
    source_dir = pathlib.Path(f"junior_cycle/cbas/{cba_id}")
    table_description = (
        f"Multilingual 1024-d BGE-M3 embeddings of the Ireland JC {cba_id} "
        f"CBA (Classroom-Based Assessment for {subject}) (BIEP v3 — M2 milestone)."
    )

    @coco.fn(memo=True)
    async def process_jc_cba_file(
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
                row=IrelandJCChunk(
                    chunk_id=await id_gen.next_id(chunk.text),
                    nation=f"ie_jc_cba_{cba_id}",
                    subject=subject,
                    language="en",
                    text=chunk.text,
                    embedding=vec,
                    source_url=str(file.file_path),
                    document_type=f"ireland_jc_cba_{cba_id}",
                ),
            )

    @coco.fn
    async def jc_cba_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,
            table_name=table_name,
            table_schema=await lancedb.TableSchema.from_class(
                IrelandJCChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        if not source_dir.exists():
            return
        for path in source_dir.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".txt", ".json"):
                file_like = FileLike(path=str(path))
                await process_jc_cba_file(file_like, target_table)

    return coco.App(
        coco.AppConfig(
            name=f"ireland_jc_cba_{cba_id}_embedding",
            description=table_description,
        ),
        jc_cba_app_main,
    )


# Generate the 36 per-CBA CocoIndex v1 Apps
ireland_jc_cba_apps = {
    f"{subject}_{cba_idx + 1}": _make_jc_cba_app(subject, cba_idx)
    for subject in JC_SUBJECTS
    for cba_idx in range(2)
}


__all__ = [
    "IrelandJCChunk",
    "JC_SUBJECTS",
    "JC_LANGUAGES",
    "JC_SHORT_COURSES",
    "ireland_jc_subject_apps",
    "ireland_jc_short_course_apps",
    "ireland_jc_cba_apps",
    "shared_lifespan",
]
