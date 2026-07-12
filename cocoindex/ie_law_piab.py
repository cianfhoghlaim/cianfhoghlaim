"""
PIAB v1 CocoIndex Embedding App (Pick-8 Ireland/law quadrant).

Embeds the BAML-extracted content from the 5 Ireland/law sources into
LanceDB. This is the PIAB-specific app — one v1-conformant App per
source (vs the absorbed `ireland_legal_embedding.py` which unifies all
5 into one table).

R1-R4 v1 conformance contract (per the `oideachais-cocoindex-v1` skill):

- R1 — `from ._lifespan import shared_lifespan` (this module)
- R2 — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- R3 — `PIABEmbedding = coco.App(coco.AppConfig(name="PIABEmbedding"))`
        at module scope
- R4 — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

Embedder: `BAAI/bge-m3` (multilingual 1024-dim) per the BIEP v1 spec.
LanceDB table: `oideachais.law.ie.piab_chunks`.

Source: `oideachais.law.ie.piab_pages` + `oideachais.law.ie.piab_forms`
DuckLake tables (read via the canonical `duckdb.connect(...)` pattern).

Reference: openspec/changes/archive/2026-07-07-finalize-v4-landing/
           absorbed/2026-07-06-ireland-legal-pipeline/proposal.md
"""
from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    import cocoindex as coco  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - defensive
    logger.warning("cocoindex_v1_not_available: %s", exc)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


# R1 — Shared lifespan
from ._lifespan import (  # noqa: E402, F401
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,  # R1 — required for cocoindex v1 conformance
)

# R2 — ContextKeys imported above

# Source DuckLake tables (the 2 PIAB-mirrored extraction tables)
PIAB_DUCKLAKE_TABLES: dict[str, str] = {
    "piab_pages": "oideachais.law.ie.piab_pages",
    "piab_forms": "oideachais.law.ie.piab_forms",
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    """Read rows from a DuckLake table via the local DuckDB destination.

    Returns an empty list when the destination is missing (CI without
    Dagster resources) or when the table is empty.
    """
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_piab_embedding")
        return []

    db_path = os.environ.get("DUCKDB_PATH", "/tmp/oideachais.duckdb")
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


# Data model — 1 chunk dataclass (1 LanceDB table per source)
@dataclass
class PIABChunk:
    """One row in the `piab_chunks` LanceDB table."""

    chunk_id: str
    source: str
    entity_type: str
    url: str
    title: str
    text: str
    extra: str
    embedded_text: str
    embedding: Annotated[Any, EMBEDDER] = (  # type: ignore[valid-type]
        EMBEDDER  # type: ignore[valid-type]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


def _build_chunk_text(source: str, row: dict[str, Any]) -> str:
    """Build the text-to-embed from one DuckLake row."""
    parts: list[str] = []
    if source == "piab_pages":
        parts.extend([
            row.get("title", ""),
            row.get("page_kind", ""),
            " | ".join(row.get("process_steps", []) or []),
            " | ".join(row.get("forms_mentioned", []) or []),
            " | ".join(row.get("statutory_deadlines", []) or []),
            row.get("summary", ""),
        ])
    elif source == "piab_forms":
        parts.extend([
            row.get("title", ""),
            row.get("form_number", ""),
            row.get("form_title", ""),
            row.get("purpose", ""),
            " | ".join(row.get("fillable_fields", []) or []),
            row.get("summary", ""),
        ])
    else:
        for _k, v in row.items():
            if isinstance(v, str):
                parts.append(v)
    text = " ".join(p for p in parts if p).strip()
    return text[:4096]


def _yield_piab_chunks() -> Iterator[dict[str, Any]]:
    """Yield one (source, row) dict per row across the 2 PIAB tables."""
    for source_key, table_name in PIAB_DUCKLAKE_TABLES.items():
        rows = _read_ducklake_table(table_name)
        for row in rows:
            text = _build_chunk_text(source_key, row)
            if not text:
                continue
            entity_type = "page" if source_key == "piab_pages" else "form"
            yield {
                "source": "piab",
                "entity_type": entity_type,
                "row": row,
                "text": text,
            }


# R3 — module-scope App + R4 — @coco.fn + lancedb.mount_table_target
if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_piab_chunk(
        item: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Process one (source, row, text) tuple into a LanceDB row."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        text = item["text"]
        if not text.strip():
            return
        embedding = await embedder.embed(text)  # type: ignore[attr-defined]
        row = item["row"]
        url = row.get("url") or row.get("source_url") or ""
        title = row.get("title") or row.get("form_title") or ""
        extra_dict: dict[str, Any] = {
            k: v for k, v in row.items()
            if k not in {"url", "source_url", "title", "form_title", "summary"}
        }
        await table.declare_row(  # type: ignore[attr-defined]
            PIABChunk(
                chunk_id=await id_gen.next_id(text),
                source=item["source"],
                entity_type=item["entity_type"],
                url=str(url),
                title=str(title),
                text=text,
                extra=str(extra_dict)[:4000],
                embedded_text=text,
                embedding=embedding,
            )
        )

    @coco.fn
    async def piab_app_main() -> None:
        """App entry point — called by `cocoindex update`."""
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="oideachais.law.ie.piab_chunks",
            table_schema=await lancedb.TableSchema.from_class(
                PIABChunk,
                primary_key=["chunk_id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")  # R4
        items = list(_yield_piab_chunks())
        id_gen = IdGenerator()
        for i in range(0, len(items), 100):
            batch = items[i : i + 100]
            await coco.map(  # type: ignore[attr-defined]
                process_piab_chunk,
                batch,
                id_gen,
                target_table,
            )

    PIABEmbedding = coco.App(
        coco.AppConfig(name="PIABEmbedding"),
        piab_app_main,
    )

else:
    # Stub when CocoIndex is not installed — keeps the symbol import-safe.
    def PIABEmbedding() -> None:  # type: ignore[no-redef]  # noqa: N802
        """Stub when CocoIndex is not installed."""
        return None


async def search_piab(
    query: str,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Semantic search over the `piab_chunks` LanceDB table."""
    result: list[dict[str, Any]] = []
    if not COCOINDEX_AVAILABLE:
        logger.warning("search_piab_cocoindex_unavailable")
        return result
    try:
        from cianfhoghlaim.lancedb.search import semantic_search

        result = await semantic_search(
            table="oideachais.law.ie.piab_chunks",
            query=query,
            top_k=limit,
        )
        return result
    except Exception as exc:
        logger.warning("search_piab_failed", error=str(exc))
        return result


__all__ = [
    "COCOINDEX_AVAILABLE",
    "PIAB_DUCKLAKE_TABLES",
    "PIABChunk",
    "PIABEmbedding",
    "search_piab",
]
