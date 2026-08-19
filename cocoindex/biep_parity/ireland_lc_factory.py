"""CocoIndex v1 factory for the 6 Irish-LC subject embeddings (BIEP v3).

This module is the **single source of truth** for the 6 Irish LC
subject CocoIndex v1 Apps. It replaces the 6 hand-written files that
previously lived at
``cocoindex/biep_parity/ireland_lc_<subject>_embedding.py`` (one per
subject) with a single factory parameterized on ``LC_SUBJECT_CONFIG``
(the canonical 6-row NCCA-subject table).

The factory instantiates 1-2 CocoIndex Apps per subject (English +
Gaeilge variants; Gaeilge has only the `ga` variant since it's
Irish-only).

Per the `centralized-schema-registry` capability. See
``openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1``.
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

from baml_client.baml_client import b  # BAML → CocoIndex wire-up (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)
from ..._shared._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)

# ─── The canonical 6-row NCCA LC subject table ────────────────────────────


@dataclass(frozen=True)
class LCSubjectConfig:
    """One NCCA LC subject row."""

    slug: str               # e.g. "mathematics" — used in function names + table suffixes
    display_name: str       # e.g. "Mathematics"
    languages: tuple[str, ...]  # which languages to build Apps for (e.g. ("en", "ga"))


LC_SUBJECT_CONFIG: list[LCSubjectConfig] = [
    LCSubjectConfig("mathematics",      "Mathematics",       ("en", "ga")),
    LCSubjectConfig("chemistry",        "Chemistry",         ("en", "ga")),
    LCSubjectConfig("computer_science", "Computer Science",  ("en", "ga")),
    LCSubjectConfig("gaeilge",          "Gaeilge",           ("ga",)),
    LCSubjectConfig("english",          "English",           ("en", "ga")),
    LCSubjectConfig("geography",        "Geography",         ("en", "ga")),
]


# ─── The factory ──────────────────────────────────────────────────────────


_splitter = RecursiveSplitter()


def _build_subject_chunk_class(subject: LCSubjectConfig, language: str):
    """Build the per-subject chunk dataclass."""
    subject_class_name = {
        "mathematics": "Math",
        "chemistry": "Chem",
        "computer_science": "Comp",
        "gaeilge": "Gael",
        "english": "Engl",
        "geography": "Geog",
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
        extracted_at: str = "2026-08-15T00:00:00Z"

    _Chunk.__name__ = f"{subject_class_name}{language_suffix}"
    _Chunk.__qualname__ = _Chunk.__name__
    return _Chunk


def _build_process_fn(subject: LCSubjectConfig, language: str, ChunkClass):
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
                    document_type=f"ireland_lc_{subject.slug}",
                ),
            )
    _process.__name__ = f"process_ireland_lc_{subject.slug}_{language}_file"
    _process.__qualname__ = _process.__name__
    return _process


def _build_app_main(subject: LCSubjectConfig, language: str, ChunkClass, process_fn):
    """Build the per-subject app_main entry."""
    table_name = (
        f"cianhoghlaim.ireland.leaving_cycle.{subject.slug}"
        f".untiered_{language}_chunks"
    )
    source_dir = pathlib.Path(
        f"dlt/british_isles/ireland/education/{subject.slug}/untiered/{language}",
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

    _main.__name__ = f"ireland_lc_{subject.slug}_{language}_app_main"
    return _main


# Build all 11 Apps (6 subjects × 2 langs, minus 1 for Gaeilge which is ga-only)
__all__ = ["LC_SUBJECT_CONFIG", "LCSubjectConfig", "shared_lifespan"]

for _subject in LC_SUBJECT_CONFIG:
    for _language in _subject.languages:
        _Chunk = _build_subject_chunk_class(_subject, _language)
        _process_fn = _build_process_fn(_subject, _language, _Chunk)
        _main = _build_app_main(_subject, _language, _Chunk, _process_fn)
        _app_name = f"ireland_lc_{_subject.slug}_untiered_{_language}_embedding"
        _app = coco.App(
            coco.AppConfig(
                name=_app_name,
                description=(
                    f"Multilingual 1024-d BGE-M3 embeddings of every "
                    f"Ireland LC {_subject.display_name} row "
                    f"({_language.upper()}, BIEP v3 untiered)."
                ),
            ),
            _main,
        )
        globals()[_app_name] = _app
        _Chunk.__name__ = f"{_Chunk.__name__}"
        globals()[_Chunk.__name__] = _Chunk
        __all__.append(_app_name)
        __all__.append(_Chunk.__name__)