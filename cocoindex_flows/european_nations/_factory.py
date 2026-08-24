"""CocoIndex v1 factory for the 40 European-nation education embeddings.

This module is the **single source of truth** for the 40
European-nation CocoIndex v1 Apps. It replaces the 40 files that
previously lived at
``cocoindex_flows/european_nations/<nation>/education_embedding.py``
(one per nation) with a single factory that parameterizes on
``NATION_CONFIG`` (the canonical 40-row ISO-3-table).

Each factory-built App conforms to R1+R2+R3+R4:
- R1: imports `shared_lifespan` + the canonical ContextKeys
  from `cocoindex_flows/_shared/_lifespan.py`
- R2: declares `coco.App(...)` at module scope (per-nation)
- R3: mounts the LanceDB target via `lancedb.mount_table_target`
- R4: declares the `embedding` vector index

The factory instantiates one `coco.App` per ISO-3 nation. Each
App is registered in `__all__` for backwards compatibility (the
pre-v8 callers imported `alb_education_embedding` etc. directly).

Per the `centralized-model-registry` + `centralized-schema-registry`
capabilities. See
``openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1``.
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, Any

import cocoindex as coco
from cocoindex.connectors import lancedb, localfs
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.resources.id import IdGenerator
from cocoindex.ops.text import RecursiveSplitter
from numpy.typing import NDArray

from .._shared._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)

# ─── The canonical 40-row ISO-3 table ──────────────────────────────────────


@dataclass(frozen=True)
class NationConfig:
    """One European nation row."""

    iso3: str              # 3-letter ISO code (e.g. "alb", "deu")
    iso2: str              # 2-letter ISO code (e.g. "al", "de")
    app_slug: str          # e.g. "alb" — used in function names
    display_name: str      # e.g. "Albania"
    table_suffix: str      # e.g. "alb.education_chunks"


NATION_CONFIG: list[NationConfig] = [
    NationConfig("alb", "al", "alb", "Albania",                    "alb.education_chunks"),
    NationConfig("aut", "at", "aut", "Austria",                    "aut.education_chunks"),
    NationConfig("bel", "be", "bel", "Belgium",                    "bel.education_chunks"),
    NationConfig("bih", "ba", "bih", "Bosnia and Herzegovina",     "bih.education_chunks"),
    NationConfig("bgr", "bg", "bgr", "Bulgaria",                   "bgr.education_chunks"),
    NationConfig("hrv", "hr", "hrv", "Croatia",                    "hrv.education_chunks"),
    NationConfig("cyp", "cy", "cyp", "Cyprus",                     "cyp.education_chunks"),
    NationConfig("cze", "cz", "cze", "Czechia",                    "cze.education_chunks"),
    NationConfig("dnk", "dk", "dnk", "Denmark",                    "dnk.education_chunks"),
    NationConfig("est", "ee", "est", "Estonia",                    "est.education_chunks"),
    NationConfig("fin", "fi", "fin", "Finland",                    "fin.education_chunks"),
    NationConfig("fra", "fr", "fra", "France",                     "fra.education_chunks"),
    NationConfig("geo", "ge", "geo", "Georgia",                    "geo.education_chunks"),
    NationConfig("deu", "de", "deu", "Germany",                    "deu.education_chunks"),
    NationConfig("grc", "gr", "grc", "Greece",                     "grc.education_chunks"),
    NationConfig("hun", "hu", "hun", "Hungary",                    "hun.education_chunks"),
    NationConfig("isl", "is", "isl", "Iceland",                    "isl.education_chunks"),
    NationConfig("ita", "it", "ita", "Italy",                      "ita.education_chunks"),
    NationConfig("xkx", "xk", "xkx", "Kosovo",                     "xkx.education_chunks"),
    NationConfig("lva", "lv", "lva", "Latvia",                     "lva.education_chunks"),
    NationConfig("lie", "li", "lie", "Liechtenstein",              "lie.education_chunks"),
    NationConfig("ltu", "lt", "ltu", "Lithuania",                  "ltu.education_chunks"),
    NationConfig("lux", "lu", "lux", "Luxembourg",                 "lux.education_chunks"),
    NationConfig("mlt", "mt", "mlt", "Malta",                      "mlt.education_chunks"),
    NationConfig("mda", "md", "mda", "Moldova",                    "mda.education_chunks"),
    NationConfig("mne", "me", "mne", "Montenegro",                 "mne.education_chunks"),
    NationConfig("nld", "nl", "nld", "Netherlands",                 "nld.education_chunks"),
    NationConfig("mkd", "mk", "mkd", "North Macedonia",            "mkd.education_chunks"),
    NationConfig("nor", "no", "nor", "Norway",                     "nor.education_chunks"),
    NationConfig("pol", "pl", "pol", "Poland",                     "pol.education_chunks"),
    NationConfig("prt", "pt", "prt", "Portugal",                   "prt.education_chunks"),
    NationConfig("rou", "ro", "rou", "Romania",                    "rou.education_chunks"),
    NationConfig("srb", "rs", "srb", "Serbia",                     "srb.education_chunks"),
    NationConfig("svk", "sk", "svk", "Slovakia",                   "svk.education_chunks"),
    NationConfig("svn", "si", "svn", "Slovenia",                   "svn.education_chunks"),
    NationConfig("esp", "es", "esp", "Spain",                      "esp.education_chunks"),
    NationConfig("swe", "se", "swe", "Sweden",                     "swe.education_chunks"),
    NationConfig("che", "ch", "che", "Switzerland",                "che.education_chunks"),
    NationConfig("tur", "tr", "tur", "Turkey",                     "tur.education_chunks"),
    NationConfig("ukr", "ua", "ukr", "Ukraine",                    "ukr.education_chunks"),
]


# ─── The factory ──────────────────────────────────────────────────────────


_splitter = RecursiveSplitter()


def _build_nation_education_chunk(nation: NationConfig) -> type:
    """Build the per-nation EducationChunk dataclass."""
    @dataclass
    class _Chunk:
        chunk_id: str
        nation: str
        subject: str
        language: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]
        source_url: str
        document_type: str
        extracted_at: str = datetime.now(UTC).isoformat()

    _Chunk.__name__ = f"{nation.app_slug.upper()}EducationChunk"
    _Chunk.__qualname__ = f"{nation.app_slug.upper()}EducationChunk"
    return _Chunk


def _build_process_fn(nation: NationConfig, ChunkClass: type):
    """Build the per-nation file processor."""
    @coco.fn(memo=True)
    async def _process(
        file: FileLike,
        table: lancedb.TableTarget,
    ) -> None:
        text = await file.read_text()
        chunks = _splitter.split(
            text, chunk_size=2000, chunk_overlap=500, language="markdown",
        )
        id_gen = IdGenerator()
        parts = file.file_path.parts
        subject = parts[5] if len(parts) >= 6 else "unknown"
        language = parts[6] if len(parts) >= 7 else "en"
        for chunk in chunks:
            vec = await coco.use_context(EMBEDDER).embed(chunk.text)
            table.declare_row(
                row=ChunkClass(
                    chunk_id=await id_gen.next_id(chunk.text),
                    nation=nation.iso3,
                    subject=subject,
                    language=language,
                    text=chunk.text,
                    embedding=vec,
                    source_url=str(file.file_path),
                    document_type=f"{nation.iso3}_education",
                ),
            )
    _process.__name__ = f"process_{nation.app_slug}_education_file"
    _process.__qualname__ = f"process_{nation.app_slug}_education_file"
    return _process


def _build_app_main(nation: NationConfig, ChunkClass: type, process_fn):
    """Build the per-nation app_main entry."""
    table_name = f"cianfhoghlaim.lc.european_nations.{nation.table_suffix}"
    source_dir = pathlib.Path(
        f"dlt/european_nations/{nation.iso3}/education/subjects",
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

    _main.__name__ = f"{nation.app_slug}_education_app_main"
    return _main


# Build all 40 Apps
# Each entry in module namespace is `<iso>_education_embedding: coco.App`
__all__ = ["NATION_CONFIG", "NationConfig", "shared_lifespan"]

for _nation in NATION_CONFIG:
    _Chunk = _build_nation_education_chunk(_nation)
    _process_fn = _build_process_fn(_nation, _Chunk)
    _main = _build_app_main(_nation, _Chunk, _process_fn)
    _app_name = f"{_nation.app_slug}_education_embedding"
    _app = coco.App(
        coco.AppConfig(name=_app_name),
        _main,
    )
    # Inject into module namespace
    globals()[_app_name] = _app
    _Chunk.__name__ = f"{_nation.app_slug.upper()}EducationChunk"
    globals()[_Chunk.__name__] = _Chunk
    __all__.append(_app_name)
    __all__.append(_Chunk.__name__)

# Note: the pre-v8 callers that did `from cocoindex_flows.european_nations.<nation>.education_embedding import <app>`
# can be migrated via the 1-line shim files at
# cocoindex_flows/european_nations/<nation>/education_embedding.py — each
# is now a 1-line re-export:
#     from cocoindex_flows.european_nations._factory import <app_slug>_education_embedding
