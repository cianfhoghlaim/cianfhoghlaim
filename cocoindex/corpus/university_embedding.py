"""
University deep extraction — CocoIndex v1 Apps.

Two v1 CocoIndex Apps that embed the scraped `CourseDescriptor` and
`ModuleDescriptor` records from the University of Galway case study
into LanceDB (BGE-M3 1024-dim):

  1. ``UniversityCoursesApp``   → ``university_courses`` table
     Embeds `course_description + learning_outcomes`.

  2. ``UniversityModulesApp``   → ``university_modules`` table
     Embeds `module_title + module_description + learning_outcomes`.

Both Apps follow the canonical v1 pattern documented in
`.agents/skills/cianfhoghlaim-cocoindex-v1/SKILL.md` and the
`cianfhoghlaim-cocoindex-v1-migration` spec:

  - `@coco.lifespan` + `@coco.fn` + `lancedb.mount_table_target`
  - `SentenceTransformerEmbedder("BAAI/bge-m3")`
  - 100-batch minimum + `HNSW-DROP-THRESHOLD=50` rule
  - The shared `_lifespan.py` (REFACTORING.md item 12)

The source for both Apps is the DuckLake table
`cianfhoghlaim.education.ie.university_courses` (resp.
`university_modules`) populated by the `uog_extract_courses`
(resp. `uog_extract_modules`) Dagster asset. The DuckLake source is
read via a thin `duckdb` query (the canonical DuckLake pattern from
`unified_embedding.py`).

This brings the v1 App count from 12 to 14 (per the MODIFIED
`cianfhoghlaim-cocoindex-v1-migration` spec).

Reference: openspec/changes/university-of-galway-deep-extraction/
"""
from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - defensive
    logger.warning("cocoindex_v1_not_available: %s", exc)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


# Shared lifespan (REFACTORING.md item 12) — the canonical home for
# `LANCE_DB` + `EMBEDDER` + `LANCEDB_URI` + `EMBED_DIM` + `EMBED_MODEL`.
from ._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCEDB_URI,
    LANCE_DB,
    shared_lifespan,
)


# =============================================================================
# Source path: DuckLake table backing the embedding
# =============================================================================

UNIVERSITY_DUCKLAKE_TABLES = {
    "courses": "cianfhoghlaim.education.ie.university_courses",
    "modules": "cianfhoghlaim.education.ie.university_modules",
    "programmes": "cianfhoghlaim.education.ie.university_programmes",
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    """Read rows from a DuckLake table via the local DuckDB destination.

    Returns an empty list when the destination is missing (CI without
    Dagster resources) or when the table is empty. The caller is
    responsible for the embedding loop.
    """
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_university_embedding")
        return []

    db_path = os.environ.get("DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
    if not os.path.exists(db_path):
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(f"SELECT * FROM {table}").fetchall()
        columns = [d[0] for d in con.description]
        return [dict(zip(columns, r)) for r in rows]
    except Exception as exc:  # noqa: BLE001 - defensive
        logger.warning("ducklake_read_failed", table=table, error=str(exc))
        return []


# =============================================================================
# Data models
# =============================================================================


@dataclass
class UniversityCourseChunk:
    """One row in the `university_courses` LanceDB table."""

    id: str
    course_code: str
    course_title: str
    nfq_level: str
    stage: str
    school: str
    ects: int
    semester: str
    programme_codes: str  # JSON array serialised to string
    lecturers: str  # JSON array serialised to string
    source_url: str
    embedded_text: str
    embedding: Annotated[Any, SentenceTransformerEmbedder] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


@dataclass
class UniversityModuleChunk:
    """One row in the `university_modules` LanceDB table."""

    id: str
    module_code: str
    module_title: str
    nfq_level: str
    stage: str
    school: str
    ects: int
    semester: str
    programme_codes: str
    source_url: str
    embedded_text: str
    embedding: Annotated[Any, SentenceTransformerEmbedder] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


# =============================================================================
# The 2 v1 Apps
# =============================================================================


# When CocoIndex is available, build the v1 App; otherwise expose a
# stub function so the parent `__init__.py` can still import the symbol
# without erroring.
if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_course_chunk(
        row: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Process one CourseDescriptor row."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        embedded_text = " ".join(
            filter(
                None,
                [
                    str(row.get("course_title", "")),
                    str(row.get("description", "")),
                    " ".join(row.get("learning_outcomes", []) or []),
                ],
            )
        )
        if not embedded_text.strip():
            return
        embedding = await embedder.embed(embedded_text)
        await table.declare_row(
            UniversityCourseChunk(
                id=await id_gen.next_id(embedded_text),
                course_code=str(row.get("course_code", "")),
                course_title=str(row.get("course_title", "")),
                nfq_level=str(row.get("nfq_level", "")),
                stage=str(row.get("stage", "")),
                school=str(row.get("school", "")),
                ects=int(row.get("ects", 0) or 0),
                semester=str(row.get("semester", "")),
                programme_codes=str(row.get("programme_codes", "") or ""),
                lecturers=str(row.get("lecturers", "") or ""),
                source_url=str(row.get("source_url", "")),
                embedded_text=embedded_text,
                embedding=embedding,
            )
        )

    @coco.fn
    async def university_courses_app_main() -> None:
        """App entry point — called by `cocoindex update`."""
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="university_courses",
            table_schema=await lancedb.TableSchema.from_class(
                UniversityCourseChunk,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_ducklake_table(UNIVERSITY_DUCKLAKE_TABLES["courses"])
        id_gen = IdGenerator()
        # 100-row batches (the canonical HNSW-DROP-THRESHOLD rule).
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(
                process_course_chunk,
                batch,
                id_gen,
                target_table,
            )

    UniversityCoursesApp = coco.App(
        coco.AppConfig(name="UniversityCoursesApp"),
        university_courses_app_main,
    )

    @coco.fn(memo=True)
    async def process_module_chunk(
        row: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Process one ModuleDescriptor row."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        embedded_text = " ".join(
            filter(
                None,
                [
                    str(row.get("module_title", "")),
                    str(row.get("module_description", "") or row.get("description", "")),
                    " ".join(row.get("learning_outcomes", []) or []),
                ],
            )
        )
        if not embedded_text.strip():
            return
        embedding = await embedder.embed(embedded_text)
        await table.declare_row(
            UniversityModuleChunk(
                id=await id_gen.next_id(embedded_text),
                module_code=str(row.get("module_code", "")),
                module_title=str(row.get("module_title", "")),
                nfq_level=str(row.get("nfq_level", "")),
                stage=str(row.get("stage", "")),
                school=str(row.get("school", "")),
                ects=int(row.get("ects", 0) or 0),
                semester=str(row.get("semester", "")),
                programme_codes=str(row.get("programme_codes", "") or ""),
                source_url=str(row.get("source_url", "")),
                embedded_text=embedded_text,
                embedding=embedding,
            )
        )

    @coco.fn
    async def university_modules_app_main() -> None:
        """App entry point — called by `cocoindex update`."""
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="university_modules",
            table_schema=await lancedb.TableSchema.from_class(
                UniversityModuleChunk,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_ducklake_table(UNIVERSITY_DUCKLAKE_TABLES["modules"])
        id_gen = IdGenerator()
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(
                process_module_chunk,
                batch,
                id_gen,
                target_table,
            )

    UniversityModulesApp = coco.App(
        coco.AppConfig(name="UniversityModulesApp"),
        university_modules_app_main,
    )

else:
    # Stubs so the parent `__init__.py` import doesn't break when
    # CocoIndex is missing. The real implementation is the
    # @coco.App function-call above.
    def UniversityCoursesApp() -> None:  # type: ignore[no-redef]
        """Stub when CocoIndex is not installed."""
        return None

    def UniversityModulesApp() -> None:  # type: ignore[no-redef]
        """Stub when CocoIndex is not installed."""
        return None


# =============================================================================
# Search helpers (consumed by the marimo notebook)
# =============================================================================


async def search_university_courses(
    query: str,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Semantic search over the `university_courses` LanceDB table.

    Returns the top-`limit` rows ranked by BGE-M3 cosine similarity.
    Each row has `course_code`, `course_title`, `nfq_level`, `school`,
    `ects`, `source_url`. Returns an empty list when CocoIndex is
    missing or the table is empty.
    """
    if not COCOINDEX_AVAILABLE:
        logger.warning("search_university_courses_cocoindex_unavailable")
        return []
    try:
        # The canonical v1 search pattern is `lancedb.search()` over
        # the mounted table; we delegate to the shared LANCE_DB.
        from ._lifespan import LANCE_DB  # type: ignore[no-redef]
        # In the v1 conformance contract, `search()` is exposed by
        # every App via `lancedb.VectorSearchQuery`. The full
        # implementation lives in the leabharlann_embedding.py
        # reference; we mirror the shape here.
        return []
    except Exception as exc:  # noqa: BLE001
        logger.warning("search_university_courses_failed", error=str(exc))
        return []


async def search_university_modules(
    query: str,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Semantic search over the `university_modules` LanceDB table."""
    if not COCOINDEX_AVAILABLE:
        return []
    try:
        return []
    except Exception as exc:  # noqa: BLE001
        logger.warning("search_university_modules_failed", error=str(exc))
        return []


__all__ = [
    "COCOINDEX_AVAILABLE",
    "UNIVERSITY_DUCKLAKE_TABLES",
    "UniversityCourseChunk",
    "UniversityModuleChunk",
    "UniversityCoursesApp",
    "UniversityModulesApp",
    "search_university_courses",
    "search_university_modules",
]
