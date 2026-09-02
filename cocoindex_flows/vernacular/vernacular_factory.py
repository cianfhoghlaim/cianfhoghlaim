"""CocoIndex v1 factory for the 7 vernacular language embeddings (Phase 14).

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Adds the
embedding layer for the 7 British Isles vernacular languages
(beyond the canonical EN + GA pair):

  1. Welsh (CY)              — Ireland_LC factory sibling
  2. Scottish Gaelic (GD)    — Ireland_LC factory sibling
  3. Breton (BR)             — sister-repo lift target
  4. Cornish (KW)            — sister-repo lift target
  5. Manx (GV)               — sister-repo lift target (with PDF corpus)
  6. Jersey French (FR_JE)   — Channel Islands
  7. Guernsey French (FR_GG) — Channel Islands

Each vernacular is a single CocoIndex App (one language, one
jurisdiction) per the Phase 14 spec. Following the
``ireland_lc_factory.py`` pattern, this module constructs 7
CocoIndex Apps at module import time.

The shared ``EMBEDDER`` (``BAAI/bge-m3``, 1024-d) and ``LANCE_DB``
context keys live at
``cocoindex_flows._shared._lifespan``. Reuses them per the
2026-08-15-centralized-schema-registry-and-deployment-control-panel-v1
change.
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

try:
    from baml_client.baml_client import b  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - baml_client ships with the repo
    b = None  # type: ignore[assignment]

from .._shared._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


# ─── The canonical 7-vernacular table ────────────────────────────────────────


@dataclass(frozen=True)
class VernacularConfig:
    """One vernacular row.

    The 7 British Isles vernaculars (beyond EN + GA). Each maps to
    a single CocoIndex v1 App + a single BAML extraction function.
    """

    slug: str               # e.g. "cy" — directory + table suffix
    display_name: str       # e.g. "Welsh"
    language_code: str      # ISO code, e.g. "cy"
    baml_function: str      # b.Extract<Vernacular>SubjectSpec
    jurisdiction: str       # WL/SC/IM/JE/GG/BR/KW/CORN/NI
    nation_dir: str         # path segment under dlt/british_isles/...


# ─── 7 vernacular config rows ────────────────────────────────────────────────

VERNACULAR_CONFIG: list[VernacularConfig] = [
    VernacularConfig(
        slug="welsh",
        display_name="Welsh (Cymraeg)",
        language_code="cy",
        baml_function="ExtractWelshSubjectSpec",
        jurisdiction="WL",
        nation_dir="wales",
    ),
    VernacularConfig(
        slug="scottish_gaelic",
        display_name="Scottish Gaelic (Gàidhlig)",
        language_code="gd",
        baml_function="ExtractScottishGaelicSubjectSpec",
        jurisdiction="SC",
        nation_dir="scotland",
    ),
    VernacularConfig(
        slug="manx",
        display_name="Manx (Gaelg)",
        language_code="gv",
        baml_function="ExtractManxSubjectSpec",
        jurisdiction="IM",
        nation_dir="isle_of_man",
    ),
    VernacularConfig(
        slug="breton",
        display_name="Breton (Brezhoneg)",
        language_code="br",
        baml_function="ExtractBretonSubjectSpec",
        jurisdiction="BR",
        nation_dir="breton_cornish",
    ),
    VernacularConfig(
        slug="cornish",
        display_name="Cornish (Kernewek)",
        language_code="kw",
        baml_function="ExtractCornishSubjectSpec",
        jurisdiction="KW",
        nation_dir="breton_cornish",
    ),
    VernacularConfig(
        slug="jersey_french",
        display_name="Jersey French (Jèrriais)",
        language_code="fr-je",
        baml_function="ExtractJerseyFrenchSubjectSpec",
        jurisdiction="JE",
        nation_dir="jersey",
    ),
    VernacularConfig(
        slug="guernsey_french",
        display_name="Guernsey French (Guernésiais)",
        language_code="fr-gg",
        baml_function="ExtractGuernseyFrenchSubjectSpec",
        jurisdiction="GG",
        nation_dir="guernsey",
    ),
]


# ─── The factory ─────────────────────────────────────────────────────────────

_splitter = RecursiveSplitter()


def _build_vernacular_chunk_class(vernacular: VernacularConfig):
    """Build the per-vernacular chunk dataclass."""

    @dataclass
    class VernacularChunk:
        chunk_id: str
        vernacular: str
        jurisdiction: str
        subject_slug: str
        stage: str
        language: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]
        source_url: str
        document_type: str
        extracted_at: str = "2026-09-01T00:00:00Z"

    VernacularChunk.__name__ = f"{vernacular.slug.capitalize()}Chunk"
    VernacularChunk.__qualname__ = VernacularChunk.__name__
    return VernacularChunk


def _build_vernacular_process_fn(vernacular: VernacularConfig, ChunkClass):
    """Build the per-vernacular file processor.

    For each chunk, the BAML function ``vernacular.baml_function``
    is invoked with the chunk text. The extracted VernacularSubjectSpec
    carries per-jurisdiction display names.
    """
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
                    vernacular=vernacular.slug,
                    jurisdiction=vernacular.jurisdiction,
                    subject_slug="mathematics",  # default; overridden by BAML
                    stage="gcse",  # default; overridden by BAML
                    language=vernacular.language_code,
                    text=chunk.text,
                    embedding=vec,
                    source_url=str(file.file_path),
                    document_type=f"vernacular_{vernacular.slug}",
                ),
            )
    _process.__name__ = f"process_vernacular_{vernacular.slug}_file"
    _process.__qualname__ = _process.__name__
    return _process


def _build_vernacular_app_main(
    vernacular: VernacularConfig, ChunkClass, process_fn
):
    """Build the per-vernacular app_main entry.

    Writes to the canonical LanceDB table
    ``cianfhoghlaim.british_isles.<jurisdiction>.<vernacular>.<vernacular>_chunks``.
    """
    table_name = (
        f"cianhoghlaim.british_isles.{vernacular.jurisdiction.lower()}"
        f".{vernacular.slug}.chunks"
    )
    # Source dir follows the DLT output convention.
    source_dir = pathlib.Path(
        f"dlt/british_isles/{vernacular.nation_dir}/education/"
        f"{vernacular.slug}_vernacular"
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
        # FTS index for hybrid search (BM25 + vector). Gracefully
        # degrades on older LanceDB versions.
        try:
            target_table.declare_full_text_search_index(column="text")
        except Exception:  # noqa: BLE001
            pass
        files = localfs.walk_dir(
            source_dir,
            recursive=True,
            path_matcher=PatternFilePathMatcher(
                included_patterns=["**/*.md", "**/*.txt", "**/*.json"],
            ),
            live=True,
        )
        await coco.mount_each(process_fn, files.items(), target_table)

    _main.__name__ = f"vernacular_{vernacular.slug}_app_main"
    return _main


# Build all 7 Apps (one per vernacular).
__all__ = ["VERNACULAR_CONFIG", "VernacularConfig", "shared_lifespan"]

for _vern in VERNACULAR_CONFIG:
    _Chunk = _build_vernacular_chunk_class(_vern)
    _process_fn = _build_vernacular_process_fn(_vern, _Chunk)
    _main = _build_vernacular_app_main(_vern, _Chunk, _process_fn)
    _app_name = f"vernacular_{_vern.slug}_embedding"
    _app = coco.App(
        coco.AppConfig(name=_app_name),
        _main,
    )
    globals()[_app_name] = _app
    globals()[_Chunk.__name__] = _Chunk
    __all__.append(_app_name)
    # Note: Chunk class names get namespaced as module-level globals
    # above. The 7 sibling per-vernacular files import them by name.
