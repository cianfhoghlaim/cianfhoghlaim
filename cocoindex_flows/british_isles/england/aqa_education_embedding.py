"""
England AQA CocoIndex v1 Embedding App (BIEP v2 canonical).

Embeds the AQA GCSE + A-Level qualifications into LanceDB for semantic
search + downstream retrieval-augmented generation.

Follows the canonical v1 pattern (R1–R4 conformance contract):

- **R1** — `from cocoindex_flows._shared._lifespan import shared_lifespan`
- **R2** — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- **R3** — `app = coco.App(coco.AppConfig(name="england_aqa_education_embedding"))`
  at module scope
- **R4** — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

Embedder: `BAAI/bge-m3` (multilingual 1024-dim) per the BIEP v1 spec.
LanceDB table: `cianfhoghlaim.england.aqa.<subject>.<level>` (one per
AQA subject × qualification level = 18 tables).

Driven by Dagster assets in
`cianfhoghlaim/orchestration/defs/2_materials/england_education/aqa/`.

Reference: openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/
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

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]


# R1 — Re-export the shared lifespan from the canonical _lifespan.py.
if COCOINDEX_AVAILABLE:
    from cocoindex_flows._shared._lifespan import (  # type: ignore[attr-defined]  # noqa: E402
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


# The 9 AQA priority subjects (per the BIEP v2 plan).
AQA_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "english_language",
    "english_literature",
    "chemistry",
    "biology",
    "physics",
    "computer_science",
    "history",
    "geography",
)
AQA_LEVELS: tuple[str, ...] = ("gcse", "a_level")


@dataclass
class AQAChunk:
    """One chunked + embedded AQA qualification row."""

    chunk_id: str
    board: str
    subject: str
    qualification_level: str
    topic: str
    assessment_objective_id: str
    text: str
    source_pdf: str
    content_hash: str
    embedding: Annotated[NDArray[Any], EMBEDDER] if COCOINDEX_AVAILABLE else NDArray[Any]  # type: ignore[misc]


# R3 — `app = coco.App(coco.AppConfig(name=...))` at module scope.
# NOTE: The actual `app = coco.App(...)` assignment is at the END of this
# file (after `aqa_qualification_embedding_flow` is defined). This forward
# reference avoids the "name not defined" error at module-import time.
if COCOINDEX_AVAILABLE:
    pass  # placeholder
else:
    app = None  # type: ignore[assignment]


def _table_name(subject: str, level: str) -> str:
    return f"cianfhoghlaim.england.aqa.{subject}.{level}"


if COCOINDEX_AVAILABLE:
    # R4 — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`.
    @coco.fn()
    async def aqa_qualification_embedding_flow(
        subject: str,
        qualification_level: str,
        source_pdf: pathlib.Path,
        chunk_text: str,
        topic: str = "",
        ao_id: str = "",
        content_hash: str = "",
    ) -> AsyncIterator[AQAChunk]:
        """Embed one AQA qualification row into the per-(subject, level) LanceDB table."""
        table_name = _table_name(subject, qualification_level)
        target = lancedb.mount_table_target(  # type: ignore[union-attr]
            LANCE_DB,
            table_name,
            schema=AQAChunk,
        )

        chunk_id = f"aqa/{subject}/{qualification_level}/{content_hash[:16]}/{ao_id}"
        embedding = await EMBEDDER.embed(chunk_text)  # type: ignore[union-attr]
        yield AQAChunk(
            chunk_id=chunk_id,
            board="aqa",
            subject=subject,
            qualification_level=qualification_level,
            topic=topic,
            assessment_objective_id=ao_id,
            text=chunk_text,
            source_pdf=str(source_pdf),
            content_hash=content_hash,
            embedding=embedding,
        )
else:
    async def aqa_qualification_embedding_flow(*args: Any, **kwargs: Any) -> AsyncIterator[AQAChunk]:
        if False:  # pragma: no cover - no-op
            yield AQAChunk(  # type: ignore[call-arg]
                chunk_id="", board="", subject="", qualification_level="",
                topic="", assessment_objective_id="", text="", source_pdf="",
                content_hash="", embedding=None,  # type: ignore[arg-type]
            )


__all__: list[str] = [
    "AQA_SUBJECTS",
    "AQA_LEVELS",
    "AQAChunk",
    "aqa_qualification_embedding_flow",
    "app",
]


def aqa_table_count() -> int:
    """Total AQA LanceDB tables (9 subjects × 2 levels = 18)."""
    return len(AQA_SUBJECTS) * len(AQA_LEVELS)

# [Wave 3 fix] Imperative coco.App() registration (the App is declared
# at module scope per the R3 conformance contract, but the App can only
# be instantiated AFTER `aqa_qualification_embedding_flow` is defined).
if COCOINDEX_AVAILABLE:
    try:
        app = coco.App(  # type: ignore[call-arg]
            coco.AppConfig(name="england_aqa_education_embedding"),
            aqa_qualification_embedding_flow,  # type: ignore[arg-type]
            shared_lifespan=shared_lifespan,  # type: ignore[arg-type]
        )
    except Exception as _exc:
        app = None  # type: ignore[assignment]
        import structlog as _slog
        _slog.get_logger().warning(
            "wave_3_aqa_app_registration_failed err=%s", str(_exc)
        )
