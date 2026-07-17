"""Academic History v1 CocoIndex App — embeds the academic-history
artefacts into a single LanceDB table.

Companion to
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.

Reads 7 DuckLake tables populated by the L2 BAML + L2 validation
assets and writes the embedded rows into a single LanceDB table
`cianfhoghlaim_academic_history` (BAAI/bge-m3, 1024-d).

The App follows the canonical v1 pattern documented in
`.agents/skills/cianfhoghlaim-cocoindex-v1/SKILL.md`:

- R1 — `from ._lifespan import shared_lifespan`
- R2 — uses the canonical ContextKeys (`LANCE_DB`, `EMBEDDER`)
- R3 — `coco.App(...)` at module scope
- R4 — `@coco.fn(memo=True)` on every expensive processor

The shared lifespan at `_lifespan.py` is the canonical home for the
3 ContextKeys + `LANCEDB_URI` + `EMBED_DIM` + `EMBED_MODEL`
(REFACTORING.md item 12).
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    import cocoindex as coco  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - defensive
    logger.warning("cocoindex_v1_not_available: %s", exc)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]

# Shared lifespan (REFACTORING.md item 12).
_EMBEDDER_FALLBACK: Any = None
_EMBED_DIM_FALLBACK: int = 1024
_EMBED_MODEL_FALLBACK: str = "BAAI/bge-m3"
_LANCEDB_URI_FALLBACK: str = os.environ.get("LANCEDB_URI", "rest://lakehouse-lance-namespace:8182")
_LANCE_DB_FALLBACK: Any = None

try:
    from ._lifespan import (
        EMBED_DIM as _LIFESPAN_EMBED_DIM,
    )
    from ._lifespan import (
        EMBED_MODEL as _LIFESPAN_EMBED_MODEL,
    )
    from ._lifespan import (  # type: ignore[import-not-found]
        EMBEDDER as _LIFESPAN_EMBEDDER,
    )
    from ._lifespan import (
        LANCE_DB as _LIFESPAN_LANCE_DB,
    )
    from ._lifespan import (
        LANCEDB_URI as _LIFESPAN_LANCEDB_URI,
    )
    from ._lifespan import (
        shared_lifespan as _LIFESPAN_SHARED_LIFESPAN,  # noqa: N812
    )

    _LIFESPAN_AVAILABLE = True
except ImportError:  # pragma: no cover - graceful degradation
    _LIFESPAN_AVAILABLE = False
    _LIFESPAN_EMBEDDER = _EMBEDDER_FALLBACK
    _LIFESPAN_EMBED_DIM = _EMBED_DIM_FALLBACK
    _LIFESPAN_EMBED_MODEL = _EMBED_MODEL_FALLBACK
    _LIFESPAN_LANCEDB_URI = _LANCEDB_URI_FALLBACK
    _LIFESPAN_LANCE_DB = _LANCE_DB_FALLBACK

    async def _LIFESPAN_SHARED_LIFESPAN(  # noqa: N802
        _builder: Any,
    ) -> AsyncIterator[None]:
        yield None


# Re-export the lifespan symbols under the canonical names (for the
# downstream @coco.fn decorator).
EMBEDDER = _LIFESPAN_EMBEDDER
EMBED_DIM = _LIFESPAN_EMBED_DIM
EMBED_MODEL = _LIFESPAN_EMBED_MODEL
LANCEDB_URI = _LIFESPAN_LANCEDB_URI
LANCE_DB = _LIFESPAN_LANCE_DB
shared_lifespan = _LIFESPAN_SHARED_LIFESPAN


# ---------------------------------------------------------------------------
# Source: 7 DuckLake tables (per the L2 / L3 split)
# ---------------------------------------------------------------------------

ACADEMIC_HISTORY_DUCKLAKE_TABLES: dict[str, str] = {
    "coursework": "cianfhoghlaim.education.ie.uog_math_coursework",
    "formulas": "cianfhoghlaim.education.ie.uog_formula_records",
    "theorems": "cianfhoghlaim.education.ie.uog_theorem_records",
    "stats": "cianfhoghlaim.education.ie.uog_statistical_procedure_records",
    "numerical": "cianfhoghlaim.education.ie.uog_numerical_method_records",
    "nonlinear": "cianfhoghlaim.education.ie.uog_nonlinear_system_records",
    "findings": "cianfhoghlaim_academic_history.validation_findings",
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    """Read rows from a DuckLake table via the local DuckDB destination.

    Returns an empty list when the destination is missing or the table
    is empty. The caller is responsible for the embedding loop.
    """
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_academic_history_embedding")
        return []

    db_path = os.environ.get("DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
    if not os.path.exists(db_path):
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(f"SELECT * FROM {table}").fetchall()
        columns = [d[0] for d in con.description]
        return [dict(zip(columns, r, strict=True)) for r in rows]
    except Exception as exc:
        logger.warning("ducklake_read_failed", table=table, error=str(exc))
        return []


# ---------------------------------------------------------------------------
# Row dataclass
# ---------------------------------------------------------------------------


@dataclass
class AcademicHistoryChunk:
    """One embedded row in the `cianfhoghlaim_academic_history` LanceDB table."""

    id: str
    source_table: str  # one of ACADEMIC_HISTORY_DUCKLAKE_TABLES
    source_id: str
    module_code: str
    document_kind: str
    language: str
    embedded_text: str
    embedding: Annotated[Any, SentenceTransformerEmbedder] = (
        (  # type: ignore[valid-type]
            SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
        )
        if COCOINDEX_AVAILABLE
        else None
    )  # type: ignore[assignment]


def _row_to_embedded_text(source_table: str, row: dict[str, Any]) -> str:
    """Pick the most informative fields per source table and join."""
    if source_table == "coursework":
        return " ".join(
            filter(
                None,
                [
                    str(row.get("module_code", "")),
                    str(row.get("module_title", "")),
                    " ".join(row.get("key_topics", []) or []),
                    " ".join(row.get("topic_areas", []) or []),
                    str(row.get("document_kind", "")),
                ],
            )
        ).strip()
    if source_table == "formulas":
        return " ".join(
            filter(
                None,
                [
                    str(row.get("name_en", "")),
                    str(row.get("latex", "")),
                    " ".join(row.get("applies_to_methods", []) or []),
                    str(row.get("module_code", "")),
                ],
            )
        ).strip()
    if source_table == "theorems":
        return " ".join(
            filter(
                None,
                [
                    str(row.get("name_en", "")),
                    str(row.get("statement_en", "")),
                    str(row.get("module_code", "")),
                ],
            )
        ).strip()
    if source_table in {"stats", "numerical", "nonlinear"}:
        return " ".join(
            filter(
                None,
                [
                    str(row.get("procedure", ""))
                    or str(row.get("method", ""))
                    or str(row.get("kind", "")),
                    str(row.get("system_string", "")) or "",
                    str(row.get("module_code", "")),
                ],
            )
        ).strip()
    if source_table == "findings":
        return " ".join(
            filter(
                None,
                [
                    str(row.get("code", "")),
                    str(row.get("message", "")),
                    str(row.get("target", "")) or "",
                ],
            )
        ).strip()
    return " ".join(str(v) for v in row.values() if v is not None)[:1024]


# ---------------------------------------------------------------------------
# v1 App
# ---------------------------------------------------------------------------


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_academic_history_chunk(
        row: dict[str, Any],
        source_table: str,
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Process one row from any of the 7 DuckLake source tables."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        embedded_text = _row_to_embedded_text(source_table, row)
        if not embedded_text.strip():
            return
        embedding = await embedder.embed(embedded_text)
        chunk_id = await id_gen.next_id(f"{source_table}::{embedded_text}")
        await table.declare_row(
            AcademicHistoryChunk(
                id=str(chunk_id),
                source_table=source_table,
                source_id=str(
                    row.get("file_hash") or row.get("formula_id") or row.get("id") or chunk_id
                ),
                module_code=str(row.get("module_code", "")),
                document_kind=str(row.get("document_kind") or row.get("kind") or source_table),
                language=str(row.get("language", "en") or "en"),
                embedded_text=embedded_text,
                embedding=embedding,
            )
        )

    @coco.fn
    async def academic_history_flow_app_main() -> None:
        """App entry point — called by `cocoindex update`."""
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="cianfhoghlaim_academic_history",
            table_schema=await lancedb.TableSchema.from_class(
                AcademicHistoryChunk,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")

        id_gen = IdGenerator()
        # 100-row batches (the canonical HNSW-DROP-THRESHOLD rule).
        for source_table, ducklake in ACADEMIC_HISTORY_DUCKLAKE_TABLES.items():
            rows = _read_ducklake_table(ducklake)
            logger.info(
                "academic_history_chunk_count",
                source_table=source_table,
                ducklake=ducklake,
                rows=len(rows),
            )
            for i in range(0, len(rows), 100):
                batch = rows[i : i + 100]
                await coco.map(
                    process_academic_history_chunk,
                    batch,
                    source_table,
                    id_gen,
                    target_table,
                )

    AcademicHistoryFlow = coco.App(
        coco.AppConfig(name="AcademicHistoryFlow"),
        academic_history_flow_app_main,
    )
else:
    AcademicHistoryFlow = None  # type: ignore[assignment]


__all__ = [
    "ACADEMIC_HISTORY_DUCKLAKE_TABLES",
    "COCOINDEX_AVAILABLE",
    "AcademicHistoryChunk",
    "AcademicHistoryFlow",
]
