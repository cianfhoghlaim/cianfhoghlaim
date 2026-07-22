"""
Junior Cycle CocoIndex v1 Embedding App (BIEP v2 canonical).

Embeds the NCCA Junior Cycle subject specifications, exam papers, and
CBAs into LanceDB for semantic search.

Follows the canonical v1 pattern (R1–R4 conformance contract):

- **R1** — `from .._shared._lifespan import shared_lifespan` (delegates to the
  shared lifespan in `_lifespan.py`)
- **R2** — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- **R3** — `app = coco.App(coco.AppConfig(name=...))` at module scope
- **R4** — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

Embedder: `BAAI/bge-m3` (multilingual 1024-dim) per the BIEP v1 spec.
LanceDB tables: `cianfhoghlaim.jc.<subject>.<year>_<lang>` for each of the
18 NCCA JC subjects × 3 years × 2 languages = 108 tables.

Driven by Dagster assets in
`cianfhoghlaim/orchestration/defs/2_materials/junior_cycle/`.

Reference: openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/
"""

from __future__ import annotations

import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog
from numpy.typing import NDArray

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.connectors import localfs  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]


# R1 — Re-export the shared lifespan from the canonical _lifespan.py.
# Falls back to a stub if cocoindex is unavailable so the module is still
# importable (needed for the dagster `dg check yaml` and lint steps).
if COCOINDEX_AVAILABLE:
    from cocoindex._shared._lifespan import (  # type: ignore[attr-defined]  # noqa: E402
        EMBEDDER,
        LANCE_DB,
        shared_lifespan,
    )
else:
    EMBEDDER = None  # type: ignore[assignment]
    LANCE_DB = None  # type: ignore[assignment]

    @dataclass
    class _StubLifespan:
        async def __aenter__(self) -> "_StubLifespan":
            return self

        async def __aexit__(self, *_args: Any) -> None:
            pass

    async def shared_lifespan() -> AsyncIterator[Any]:  # type: ignore[no-redef]
        yield _StubLifespan()


# The 18 NCCA JC subjects (kept in sync with `JC_SUBJECTS` in
# `dlt/british_isles/ireland/education/junior_cycle.py`).
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

# The 3 years × 2 languages = 6 LanceDB tables per subject.
JC_YEARS: tuple[str, ...] = ("year_1", "year_2", "year_3")
JC_LANGUAGES: tuple[str, ...] = ("en", "ga")


@dataclass
class JCChunk:
    """One chunked + embedded Junior Cycle row (per subject / year / language)."""

    chunk_id: str
    subject: str
    year: int
    language: str
    topic: str
    strand: str
    learning_outcome_id: str
    learning_outcome_text: str
    source_pdf: str
    content_hash: str
    chunk_text: str
    embedding: Annotated[NDArray[Any], EMBEDDER] if COCOINDEX_AVAILABLE else NDArray[Any]  # type: ignore[misc]


# R3 — `app = coco.App(coco.AppConfig(name=...))` at module scope.
if COCOINDEX_AVAILABLE:
    app = coco.App(coco.AppConfig(name="junior_cycle_embedding"))
else:
    app = None  # type: ignore[assignment]


def _table_name(subject: str, year: str, language: str) -> str:
    """Return the canonical LanceDB table name for one (subject, year, language) tuple."""
    return f"cianfhoghlaim.jc.{subject}.{year}_{language}"


def _lc_table_count() -> int:
    """Total LanceDB tables produced by this App: 18 subjects × 3 years × 2 langs = 108."""
    return len(JC_SUBJECTS) * len(JC_YEARS) * len(JC_LANGUAGES)


if COCOINDEX_AVAILABLE:
    # R4 — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`.
    @coco.function(
        lifespan=shared_lifespan,
    )
    async def jc_subject_embedding_flow(
        subject: str,
        year: int,
        language: str,
        source_pdf: pathlib.Path,
        chunk_text: str,
        topic: str = "",
        strand: str = "",
        lo_id: str = "",
        lo_text: str = "",
        content_hash: str = "",
    ) -> AsyncIterator[JCChunk]:
        """Embed one Junior Cycle specification into the per-subject per-year per-language LanceDB table.

        The DAG materialisation calls this function once per BAML-extracted
        `JCCurriculumSpec` row from
        `orchestration/defs/2_materials/junior_cycle/`.
        """
        # Mount the per-subject per-year per-language LanceDB table.
        table_name = _table_name(subject, f"year_{year}", language)
        target = lancedb.mount_table_target(  # type: ignore[union-attr]
            LANCE_DB,
            table_name,
            schema=JCChunk,
        )

        chunk_id = f"{subject}/year_{year}/{language}/{content_hash[:16]}/{lo_id}"
        embedding = await EMBEDDER.embed(chunk_text)  # type: ignore[union-attr]
        yield JCChunk(
            chunk_id=chunk_id,
            subject=subject,
            year=year,
            language=language,
            topic=topic,
            strand=strand,
            learning_outcome_id=lo_id,
            learning_outcome_text=lo_text,
            source_pdf=str(source_pdf),
            content_hash=content_hash,
            chunk_text=chunk_text,
            embedding=embedding,
        )

else:
    async def jc_subject_embedding_flow(*args: Any, **kwargs: Any) -> AsyncIterator[JCChunk]:
        """Stub when cocoindex is unavailable."""
        if False:  # pragma: no cover - no-op for type checker
            yield JCChunk(  # type: ignore[call-arg]
                chunk_id="", subject="", year=0, language="",
                topic="", strand="", learning_outcome_id="",
                learning_outcome_text="", source_pdf="", content_hash="",
                chunk_text="", embedding=None,  # type: ignore[arg-type]
            )


__all__: list[str] = [
    "JC_SUBJECTS",
    "JC_YEARS",
    "JC_LANGUAGES",
    "JCChunk",
    "jc_subject_embedding_flow",
    "app",
]


def table_count() -> int:
    """Return the total number of LanceDB tables produced (108 = 18 × 3 × 2)."""
    return _lc_table_count()
