"""
Judgements v1 CocoIndex Embedding App (Pick-8 Ireland/law quadrant).

Embeds the BAML-extracted Judgement content from Judgements.ie into
LanceDB. The neutral citation + catchwords + holding + statutes_cited
fields are the canonical join keys against the ISB `acts` table.

R1-R4 v1 conformance contract (per the `oideachais-cocoindex-v1` skill):

- R1 — `from ._lifespan import shared_lifespan` (this module)
- R2 — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- R3 — `JudgementsEmbedding = coco.App(coco.AppConfig(name="JudgementsEmbedding"))`
        at module scope
- R4 — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

Embedder: `BAAI/bge-m3` (multilingual 1024-dim).
LanceDB table: `oideachais.law.ie.judgements_chunks`.

Source: `oideachais.law.ie.judgements` DuckLake table.

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


from ._lifespan import (  # noqa: E402, F401
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,  # R1 — required for cocoindex v1 conformance
)

JUDGEMENTS_DUCKLAKE_TABLES: dict[str, str] = {
    "judgements": "oideachais.law.ie.judgements",
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
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


@dataclass
class JudgementsChunk:
    """One row in the `judgements_chunks` LanceDB table."""

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


def _build_chunk_text(_source: str, row: dict[str, Any]) -> str:
    parts: list[str] = [
        row.get("neutral_citation", ""),
        row.get("case_name", ""),
        " | ".join(row.get("parties", []) or []),
        row.get("judge", ""),
        row.get("decision_date", ""),
        row.get("court_level", ""),
        " | ".join(row.get("catchwords", []) or []),
        row.get("holding", ""),
    ]
    text = " ".join(p for p in parts if p).strip()
    return text[:4096]


def _yield_judgements_chunks() -> Iterator[dict[str, Any]]:
    for source_key, table_name in JUDGEMENTS_DUCKLAKE_TABLES.items():
        rows = _read_ducklake_table(table_name)
        for row in rows:
            text = _build_chunk_text(source_key, row)
            if not text:
                continue
            yield {
                "source": "judgements",
                "entity_type": "judgement",
                "row": row,
                "text": text,
            }


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_judgements_chunk(
        item: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,
    ) -> None:
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        text = item["text"]
        if not text.strip():
            return
        embedding = await embedder.embed(text)  # type: ignore[attr-defined]
        row = item["row"]
        url = row.get("url") or row.get("source_url") or ""
        title = (
            row.get("case_name")
            or row.get("neutral_citation")
            or ""
        )
        extra_dict: dict[str, Any] = {
            k: v for k, v in row.items()
            if k not in {"url", "source_url", "case_name", "neutral_citation",
                         "summary", "holding"}
        }
        await table.declare_row(  # type: ignore[attr-defined]
            JudgementsChunk(
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
    async def judgements_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="oideachais.law.ie.judgements_chunks",
            table_schema=await lancedb.TableSchema.from_class(
                JudgementsChunk,
                primary_key=["chunk_id"],
            ),
        )
        items = list(_yield_judgements_chunks())
        id_gen = IdGenerator()
        for i in range(0, len(items), 100):
            batch = items[i : i + 100]
            await coco.map(  # type: ignore[attr-defined]
                process_judgements_chunk,
                batch,
                id_gen,
                target_table,
            )

    JudgementsEmbedding = coco.App(
        coco.AppConfig(name="JudgementsEmbedding"),
        judgements_app_main,
    )

else:

    def JudgementsEmbedding() -> None:  # type: ignore[no-redef]  # noqa: N802
        return None


async def search_judgements(
    query: str,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    if not COCOINDEX_AVAILABLE:
        return result
    try:
        from cianfhoghlaim.lancedb.search import semantic_search

        result = await semantic_search(
            table="oideachais.law.ie.judgements_chunks",
            query=query,
            top_k=limit,
        )
        return result
    except Exception as exc:
        logger.warning("search_judgements_failed", error=str(exc))
        return result


__all__ = [
    "COCOINDEX_AVAILABLE",
    "JUDGEMENTS_DUCKLAKE_TABLES",
    "JudgementsChunk",
    "JudgementsEmbedding",
    "search_judgements",
]
