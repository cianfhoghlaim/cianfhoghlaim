"""CocoIndex v1 factory for the 8 Irish Junior Cycle (JC) subject embeddings.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change
(TASK-M3B-2.1): Junior Cycle factory.

This module is the **single source of truth** for the 8 NCCA JC
subject CocoIndex v1 Apps. It replaces the per-subject hand-written
files with a single factory parameterised on ``JC_SUBJECT_CONFIG``
(the canonical 8-row NCCA JC subject table).

The factory instantiates 1-2 CocoIndex Apps per subject (English +
Gaeilge variants; Gaeilge is ga-only).

Each App conforms to R1-R4:
- R1: imports `shared_lifespan` + `LANCE_DB` + `EMBEDDER`
- R2: declares `coco.App(...)` at module scope
- R3: mounts the LanceDB target via `lancedb.mount_table_target`
- R4: declares the `embedding` vector index

BAML wiring (FF.6): every CocoIndex App delegates extraction to
``jc_extract_chunk`` (at ``4_stage_extraction.py``) which calls
``b.ExtractJuniorCycleCurriculum(...)`` via the canonical
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


# ─── The canonical 8-row NCCA JC subject table ───────────────────────────


@dataclass(frozen=True)
class JCSubjectConfig:
    """One NCCA Junior Cycle subject row."""

    slug: str
    display_name: str
    languages: tuple[str, ...]


JC_SUBJECT_CONFIG: list[JCSubjectConfig] = [
    JCSubjectConfig("mathematics", "Mathematics", ("en", "ga")),
    JCSubjectConfig("english",     "English",     ("en", "ga")),
    JCSubjectConfig("gaeilge",     "Gaeilge",     ("ga",)),
    JCSubjectConfig("science",     "Science",     ("en", "ga")),
    JCSubjectConfig("history",     "History",     ("en", "ga")),
    JCSubjectConfig("geography",   "Geography",   ("en", "ga")),
    JCSubjectConfig("french",      "French",      ("en", "ga")),
    JCSubjectConfig("business",    "Business",    ("en", "ga")),
]


# ─── The factory ──────────────────────────────────────────────────────────


_splitter = RecursiveSplitter()


def _build_subject_chunk_class(subject: JCSubjectConfig, language: str):
    """Build the per-subject chunk dataclass."""
    subject_class_name = {
        "mathematics": "Math",
        "english": "Engl",
        "gaeilge": "Gael",
        "science": "Sci",
        "history": "Hist",
        "geography": "Geog",
        "french": "Fren",
        "business": "Bus",
    }[subject.slug]
    language_suffix = "EnChunk" if language == "en" else "GaChunk"

    @dataclass
    class _Chunk:
        chunk_id: str
        subject: str
        language: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]
        source_url: str
        document_type: str
        extracted_at: str = "2026-09-30T00:00:00Z"

    _Chunk.__name__ = f"{subject_class_name}{language_suffix}"
    _Chunk.__qualname__ = _Chunk.__name__
    return _Chunk


def _build_process_fn(subject: JCSubjectConfig, language: str, ChunkClass):
    """Build the per-subject file processor."""
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
                    language=language,
                    text=chunk.text,
                    embedding=vec,
                    source_url=str(file.file_path),
                    document_type=f"ireland_jc_{subject.slug}",
                ),
            )
    _process.__name__ = f"process_ireland_jc_{subject.slug}_{language}_file"
    _process.__qualname__ = _process.__name__
    return _process


def _build_app_main(subject: JCSubjectConfig, language: str, ChunkClass, process_fn):
    """Build the per-subject app_main entry."""
    table_name = (
        f"cianhoghlaim.ireland.junior_cycle.{subject.slug}"
        f".untiered_{language}_chunks"
    )
    source_dir = pathlib.Path(
        f"dlt/british_isles/ireland/education/jc/{subject.slug}/untiered/{language}",
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

    _main.__name__ = f"ireland_jc_{subject.slug}_{language}_app_main"
    return _main


# Build all 15 Apps (8 subjects × 2 langs, minus 1 for Gaeilge which is ga-only)
__all__ = ["JC_SUBJECT_CONFIG", "JCSubjectConfig", "shared_lifespan"]

for _subject in JC_SUBJECT_CONFIG:
    for _language in _subject.languages:
        _Chunk = _build_subject_chunk_class(_subject, _language)
        _process_fn = _build_process_fn(_subject, _language, _Chunk)
        _main = _build_app_main(_subject, _language, _Chunk, _process_fn)
        _app_name = f"ireland_jc_{_subject.slug}_untiered_{_language}_embedding"
        _app = coco.App(
            coco.AppConfig(
                name=_app_name,
                description=(
                    f"Multilingual 1024-d BGE-M3 embeddings of every "
                    f"Ireland JC {_subject.display_name} row "
                    f"({_language.upper()}, BIEP v3 untiered)."
                ),
            ),
            _main,
        )
        globals()[_app_name] = _app
        globals()[_Chunk.__name__] = _Chunk
        __all__.append(_app_name)
        __all__.append(_Chunk.__name__)