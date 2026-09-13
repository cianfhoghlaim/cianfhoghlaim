"""CocoIndex v1 factory for the 9 England GCSE subject embeddings.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change
(TASK-M3B-2.3): GCSE factory.

This module is the **single source of truth** for the 9 England
GCSE subject CocoIndex v1 Apps across the 3 awarding boards
(AQA + OCR + Edexcel). The factory instantiates 3 CocoIndex Apps
per subject (one per board), yielding 9 × 3 = 27 Apps.

Each App conforms to R1-R4:
- R1: imports `shared_lifespan` + `LANCE_DB` + `EMBEDDER`
- R2: declares `coco.App(...)` at module scope
- R3: mounts the LanceDB target via `lancedb.mount_table_target`
- R4: declares the `embedding` vector index

BAML wiring (FF.6): every CocoIndex App delegates extraction to
``gcse_extract_chunk`` (at ``4_stage_extraction.py``) which calls
``b.ExtractGCSECurriculumSyllabus(...)`` via the canonical
``BAMLFunctionTool`` helper.
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass
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


# ─── The canonical 9-row England GCSE subject table ──────────────────────


@dataclass(frozen=True)
class GCSESubjectConfig:
    """One England GCSE priority subject row."""

    slug: str
    display_name: str
    spec_codes: dict[str, str]   # board -> AQA/OCR/Edexcel spec code


GCSE_SUBJECT_CONFIG: list[GCSESubjectConfig] = [
    GCSESubjectConfig(
        "mathematics", "Mathematics",
        {"aqa": "8462", "ocr": "J560", "edexcel": "1MA1"},
    ),
    GCSESubjectConfig(
        "english_language", "English Language",
        {"aqa": "8700", "ocr": "J351", "edexcel": "1EN0"},
    ),
    GCSESubjectConfig(
        "english_literature", "English Literature",
        {"aqa": "8702", "ocr": "J352", "edexcel": "1ET0"},
    ),
    GCSESubjectConfig(
        "biology", "Biology",
        {"aqa": "8461", "ocr": "J247", "edexcel": "1BI0"},
    ),
    GCSESubjectConfig(
        "chemistry", "Chemistry",
        {"aqa": "8462", "ocr": "J248", "edexcel": "1CH0"},
    ),
    GCSESubjectConfig(
        "physics", "Physics",
        {"aqa": "8463", "ocr": "J249", "edexcel": "1PH0"},
    ),
    GCSESubjectConfig(
        "computer_science", "Computer Science",
        {"aqa": "8525", "ocr": "J277", "edexcel": "1CP2"},
    ),
    GCSESubjectConfig(
        "history", "History",
        {"aqa": "8145", "ocr": "J410", "edexcel": "1HI0"},
    ),
    GCSESubjectConfig(
        "geography", "Geography",
        {"aqa": "8035", "ocr": "J383", "edexcel": "1GA0"},
    ),
]


ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")


# ─── The factory ──────────────────────────────────────────────────────────


_splitter = RecursiveSplitter()


def _build_subject_chunk_class(subject: GCSESubjectConfig, board: str):
    """Build the per-subject × board chunk dataclass."""
    subject_class_name = {
        "mathematics": "Math",
        "english_language": "EnglLang",
        "english_literature": "EnglLit",
        "biology": "Bio",
        "chemistry": "Chem",
        "physics": "Phys",
        "computer_science": "Comp",
        "history": "Hist",
        "geography": "Geog",
    }[subject.slug]
    board_suffix = {"aqa": "Aqa", "ocr": "Ocr", "edexcel": "Edx"}[board]

    @dataclass
    class _Chunk:
        chunk_id: str
        subject: str
        board: str
        qualification: str
        tier: str
        filename: str
        chunk_index: int
        spec_code: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]
        extracted_at: str = "2026-09-30T00:00:00Z"

    _Chunk.__name__ = f"{subject_class_name}{board_suffix}GcseChunk"
    _Chunk.__qualname__ = _Chunk.__name__
    return _Chunk


def _build_process_fn(
    subject: GCSESubjectConfig, board: str, ChunkClass,
):
    """Build the per-subject × board file processor."""
    @coco.fn(memo=True)
    async def _process(file: FileLike, table: lancedb.TableTarget) -> None:
        text = await file.read_text()
        chunks = _splitter.split(
            text, chunk_size=2000, chunk_overlap=500, language="markdown",
        )
        id_gen = IdGenerator()
        for chunk in chunks:
            vec = await coco.use_context(EMBEDDER).embed(chunk.text)
            table.declare_row(
                row=ChunkClass(
                    chunk_id=await id_gen.next_id(chunk.text),
                    subject=subject.slug,
                    board=board,
                    qualification="gcse",
                    tier="foundation",  # default tier; per-tier variants in dedicated factories
                    filename=str(file.file_path),
                    chunk_index=0,
                    spec_code=subject.spec_codes[board],
                    text=chunk.text,
                    embedding=vec,
                ),
            )
    _process.__name__ = f"process_england_gcse_{subject.slug}_{board}_file"
    _process.__qualname__ = _process.__name__
    return _process


def _build_app_main(
    subject: GCSESubjectConfig, board: str, ChunkClass, process_fn,
):
    """Build the per-subject × board app_main entry."""
    table_name = (
        f"cianhoghlaim.england.gcse.{board}.{subject.slug}.foundation_chunks"
    )
    source_dir = pathlib.Path(
        f"dlt/british_isles/england/education/gcse/{board}/{subject.slug}",
    )

    @coco.fn
    async def _main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,
            table_name=table_name,
            table_schema=await lancedb.TableSchema.from_class(
                ChunkClass, primary_key=["chunk_id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        files = localfs.walk_dir(
            source_dir,
            recursive=True,
            path_matcher=PatternFilePathMatcher(
                included_patterns=["**/*.md", "**/*.txt", "**/*.json"],
            ),
            live=True,
        )
        await coco.mount_each(process_fn, files.items(), target_table)

    _main.__name__ = f"england_gcse_{subject.slug}_{board}_app_main"
    return _main


# Build all 27 Apps (9 subjects × 3 boards)
__all__ = [
    "GCSE_SUBJECT_CONFIG",
    "GCSESubjectConfig",
    "ENGLAND_BOARDS",
    "shared_lifespan",
]

for _subject in GCSE_SUBJECT_CONFIG:
    for _board in ENGLAND_BOARDS:
        _Chunk = _build_subject_chunk_class(_subject, _board)
        _process_fn = _build_process_fn(_subject, _board, _Chunk)
        _main = _build_app_main(_subject, _board, _Chunk, _process_fn)
        _app_name = f"england_gcse_{_subject.slug}_{_board}_embedding"
        _app = coco.App(
            coco.AppConfig(
                name=_app_name,
                description=(
                    f"Multilingual 1024-d BGE-M3 embeddings of every "
                    f"England GCSE {_subject.display_name} row "
                    f"({_board.upper()} board {_subject.spec_codes[_board]}, "
                    f"BIEP v3 foundation tier)."
                ),
            ),
            _main,
        )
        globals()[_app_name] = _app
        globals()[_Chunk.__name__] = _Chunk
        __all__.append(_app_name)
        __all__.append(_Chunk.__name__)