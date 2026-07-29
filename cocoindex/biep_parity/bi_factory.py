"""CocoIndex v1 factory for the 8 British Isles parity education embeddings (BIEP v3).

This module is the **single source of truth** for the 8 BI
parity CocoIndex v1 Apps. It replaces the 8 hand-written files that
previously lived at
``cocoindex/biep_parity/{ga,en,ni,sct,wls,isle_of_man,jersey,guernsey}_education_embedding.py``
(one per jurisdiction) with a single factory parameterized on
``JURISDICTION_CONFIG`` (the canonical 8-row BI-jurisdiction table).

The factory instantiates 1 CocoIndex App per jurisdiction.

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

from ..._shared._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)

# ─── The canonical 8-row BI jurisdiction table ────────────────────────────


@dataclass(frozen=True)
class BIJurisdictionConfig:
    """One British Isles jurisdiction row."""

    slug: str               # e.g. "ireland" — used in function names
    iso3: str               # 3-letter code (e.g. "ire", "eng")
    display_name: str       # e.g. "Ireland"
    iso3_long: str          # 6-letter BIEP code (e.g. "ire", "eng", "sct_wls_ni")


JURISDICTION_CONFIG: list[BIJurisdictionConfig] = [
    BIJurisdictionConfig("ga",            "ga",  "Gaeilge (Ireland)",   "ga"),
    BIJurisdictionConfig("en",            "eng", "England",             "eng"),
    BIJurisdictionConfig("ni",            "nir", "Northern Ireland",   "ni"),
    BIJurisdictionConfig("sct",           "sct", "Scotland",            "sct"),
    BIJurisdictionConfig("wls",           "wls", "Wales",              "wls"),
    BIJurisdictionConfig("isle_of_man",   "iom", "Isle of Man",        "iom"),
    BIJurisdictionConfig("jersey",        "jey", "Jersey",             "jey"),
    BIJurisdictionConfig("guernsey",      "ggy", "Guernsey",           "ggy"),
]


# ─── The factory ──────────────────────────────────────────────────────────


_splitter = RecursiveSplitter()


def _build_chunk_class(jurisdiction: BIJurisdictionConfig):
    """Build the per-jurisdiction chunk dataclass."""
    chunk_class_name = {
        "ga": "GaeilgeEducationChunk",
        "en": "EnglandEducationChunk",
        "ni": "NorthernIrelandEducationChunk",
        "sct": "ScotlandEducationChunk",
        "wls": "WalesEducationChunk",
        "isle_of_man": "IsleOfManEducationChunk",
        "jersey": "JerseyEducationChunk",
        "guernsey": "GuernseyEducationChunk",
    }[jurisdiction.slug]

    @dataclass
    class _Chunk:
        chunk_id: str
        jurisdiction: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]
        source_url: str
        document_type: str
        extracted_at: str = "2026-08-15T00:00:00Z"

    _Chunk.__name__ = chunk_class_name
    _Chunk.__qualname__ = chunk_class_name
    return _Chunk


def _build_process_fn(jurisdiction: BIJurisdictionConfig, ChunkClass):
    """Build the per-jurisdiction file processor."""
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
                    jurisdiction=jurisdiction.iso3,
                    text=chunk.text,
                    embedding=vec,
                    source_url=str(file.file_path),
                    document_type=f"{jurisdiction.iso3}_education",
                ),
            )
    _process.__name__ = f"process_{jurisdiction.slug}_education_file"
    _process.__qualname__ = _process.__name__
    return _process


def _build_app_main(jurisdiction: BIJurisdictionConfig, ChunkClass, process_fn):
    """Build the per-jurisdiction app_main entry."""
    table_name = f"cianhoghlaim.biep.{jurisdiction.slug}.education_chunks"
    source_dir = pathlib.Path(
        f"dlt/british_isles/{jurisdiction.slug}/education",
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

    _main.__name__ = f"{jurisdiction.slug}_education_app_main"
    return _main


# Build all 8 Apps
__all__ = ["JURISDICTION_CONFIG", "BIJurisdictionConfig", "shared_lifespan"]

for _jurisdiction in JURISDICTION_CONFIG:
    _Chunk = _build_chunk_class(_jurisdiction)
    _process_fn = _build_process_fn(_jurisdiction, _Chunk)
    _main = _build_app_main(_jurisdiction, _Chunk, _process_fn)
    _app_name = f"{_jurisdiction.slug}_education_embedding"
    _app = coco.App(
        coco.AppConfig(
            name=_app_name,
            description=(
                f"Multilingual 1024-d BGE-M3 embeddings of every "
                f"{_jurisdiction.display_name} education row (BIEP v3 parity)."
            ),
        ),
        _main,
    )
    globals()[_app_name] = _app
    globals()[_Chunk.__name__] = _Chunk
    __all__.append(_app_name)
    __all__.append(_Chunk.__name__)