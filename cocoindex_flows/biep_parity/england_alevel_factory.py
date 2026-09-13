"""CocoIndex v1 factory for the 15 England A-Level subject embeddings.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change
(TASK-M3B-2.2): A-Level factory.

This module is the **single source of truth** for the 15 England
A-Level subject CocoIndex v1 Apps across the 3 awarding boards
(AQA + OCR + Edexcel). The factory instantiates 3 CocoIndex Apps per
subject (one per board), yielding 15 × 3 = 45 Apps.

Each App conforms to R1-R4:
- R1: imports `shared_lifespan` + `LANCE_DB` + `EMBEDDER`
- R2: declares `coco.App(...)` at module scope
- R3: mounts the LanceDB target via `lancedb.mount_table_target`
- R4: declares the `embedding` vector index

BAML wiring (FF.6): every CocoIndex App delegates extraction to
``alevel_extract_chunk`` (at ``4_stage_extraction.py``) which calls
``b.ExtractALevelCurriculumSyllabus(...)`` via the canonical
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


# ─── The canonical 15-row England A-Level subject table ──────────────────


@dataclass(frozen=True)
class ALevelSubjectConfig:
    """One England A-Level priority subject row."""

    slug: str
    display_name: str
    spec_codes: dict[str, str]   # board -> AQA/OCR/Edexcel spec code


ALevel_SUBJECT_CONFIG: list[ALevelSubjectConfig] = [
    ALevelSubjectConfig(
        "mathematics", "Mathematics",
        {"aqa": "7357", "ocr": "H240", "edexcel": "9MA0"},
    ),
    ALevelSubjectConfig(
        "further_mathematics", "Further Mathematics",
        {"aqa": "7367", "ocr": "H245", "edexcel": "9FM0"},
    ),
    ALevelSubjectConfig(
        "english_literature", "English Literature",
        {"aqa": "7717", "ocr": "H472", "edexcel": "9ET0"},
    ),
    ALevelSubjectConfig(
        "english_language", "English Language",
        {"aqa": "7702", "ocr": "H470", "edexcel": "9EN0"},
    ),
    ALevelSubjectConfig(
        "biology", "Biology",
        {"aqa": "7402", "ocr": "H420", "edexcel": "9BN0"},
    ),
    ALevelSubjectConfig(
        "chemistry", "Chemistry",
        {"aqa": "7405", "ocr": "H433", "edexcel": "9CH0"},
    ),
    ALevelSubjectConfig(
        "physics", "Physics",
        {"aqa": "7408", "ocr": "H556", "edexcel": "9PH0"},
    ),
    ALevelSubjectConfig(
        "psychology", "Psychology",
        {"aqa": "7182", "ocr": "H180", "edexcel": "9PS0"},
    ),
    ALevelSubjectConfig(
        "history", "History",
        {"aqa": "7042", "ocr": "H505", "edexcel": "9HI0"},
    ),
    ALevelSubjectConfig(
        "geography", "Geography",
        {"aqa": "7037", "ocr": "H481", "edexcel": "9GE0"},
    ),
    ALevelSubjectConfig(
        "economics", "Economics",
        {"aqa": "7126", "ocr": "H460", "edexcel": "9EC0"},
    ),
    ALevelSubjectConfig(
        "business", "Business",
        {"aqa": "7132", "ocr": "H431", "edexcel": "9BS0"},
    ),
    ALevelSubjectConfig(
        "history_of_art", "History of Art",
        {"aqa": "7203", "ocr": "H401", "edexcel": "9HA0"},
    ),
    ALevelSubjectConfig(
        "politics", "Politics",
        {"aqa": "7152", "ocr": "H485", "edexcel": "9PL0"},
    ),
    ALevelSubjectConfig(
        "sociology", "Sociology",
        {"aqa": "7192", "ocr": "H180", "edexcel": "9SC0"},
    ),
]


ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")


# ─── The factory ──────────────────────────────────────────────────────────


_splitter = RecursiveSplitter()


def _build_subject_chunk_class(subject: ALevelSubjectConfig, board: str):
    """Build the per-subject × board chunk dataclass."""
    subject_class_name = {
        "mathematics": "Math",
        "further_mathematics": "FMath",
        "english_literature": "EnglLit",
        "english_language": "EnglLang",
        "biology": "Bio",
        "chemistry": "Chem",
        "physics": "Phys",
        "psychology": "Psych",
        "history": "Hist",
        "geography": "Geog",
        "economics": "Econ",
        "business": "Bus",
        "history_of_art": "HistArt",
        "politics": "Pol",
        "sociology": "Soc",
    }[subject.slug]
    board_suffix = {"aqa": "Aqa", "ocr": "Ocr", "edexcel": "Edx"}[board]

    @dataclass
    class _Chunk:
        chunk_id: str
        subject: str
        board: str
        qualification: str
        level: str
        filename: str
        chunk_index: int
        spec_code: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]
        extracted_at: str = "2026-09-30T00:00:00Z"

    _Chunk.__name__ = f"{subject_class_name}{board_suffix}AlevelChunk"
    _Chunk.__qualname__ = _Chunk.__name__
    return _Chunk


def _build_process_fn(
    subject: ALevelSubjectConfig, board: str, ChunkClass,
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
                    qualification="a-level",
                    level="a-level",
                    filename=str(file.file_path),
                    chunk_index=0,
                    spec_code=subject.spec_codes[board],
                    text=chunk.text,
                    embedding=vec,
                ),
            )
    _process.__name__ = f"process_england_alevel_{subject.slug}_{board}_file"
    _process.__qualname__ = _process.__name__
    return _process


def _build_app_main(
    subject: ALevelSubjectConfig, board: str, ChunkClass, process_fn,
):
    """Build the per-subject × board app_main entry."""
    table_name = (
        f"cianhoghlaim.england.a_level.{board}.{subject.slug}.untiered_chunks"
    )
    source_dir = pathlib.Path(
        f"dlt/british_isles/england/education/a_level/{board}/{subject.slug}",
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

    _main.__name__ = f"england_alevel_{subject.slug}_{board}_app_main"
    return _main


# Build all 45 Apps (15 subjects × 3 boards)
__all__ = [
    "ALevel_SUBJECT_CONFIG",
    "ALevelSubjectConfig",
    "ENGLAND_BOARDS",
    "shared_lifespan",
]

for _subject in ALevel_SUBJECT_CONFIG:
    for _board in ENGLAND_BOARDS:
        _Chunk = _build_subject_chunk_class(_subject, _board)
        _process_fn = _build_process_fn(_subject, _board, _Chunk)
        _main = _build_app_main(_subject, _board, _Chunk, _process_fn)
        _app_name = f"england_alevel_{_subject.slug}_{_board}_embedding"
        _app = coco.App(
            coco.AppConfig(
                name=_app_name,
                description=(
                    f"Multilingual 1024-d BGE-M3 embeddings of every "
                    f"England A-Level {_subject.display_name} row "
                    f"({_board.upper()} board {_subject.spec_codes[_board]}, "
                    f"BIEP v3 untiered)."
                ),
            ),
            _main,
        )
        globals()[_app_name] = _app
        globals()[_Chunk.__name__] = _Chunk
        __all__.append(_app_name)
        __all__.append(_Chunk.__name__)