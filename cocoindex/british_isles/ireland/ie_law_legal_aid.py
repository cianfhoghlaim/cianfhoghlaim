"""
Legal Aid Board v1 CocoIndex Embedding App (Pick-8 Ireland/law quadrant).

Embeds the BAML-extracted LegalAidPage + LegalAidForm content from the
Legal Aid Board (legalaidboard.ie) into LanceDB.

R1-R4 v1 conformance contract (per the `cianfhoghlaim-cocoindex-v1` skill):

- R1 — `from ._lifespan import shared_lifespan` (this module)
- R2 — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- R3 — `LegalAidEmbedding = coco.App(coco.AppConfig(name="LegalAidEmbedding"))`
        at module scope
- R4 — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

Embedder: `BAAI/bge-m3` (multilingual 1024-dim).
LanceDB table: `cianfhoghlaim.law.ie.legal_aid_chunks`.

Source: `cianfhoghlaim.law.ie.legal_aid_pages` + `cianfhoghlaim.law.ie.legal_aid_forms`
DuckLake tables.

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

LEGAL_AID_DUCKLAKE_TABLES: dict[str, str] = {
    "legal_aid_pages": "cianfhoghlaim.law.ie.legal_aid_pages",
    "legal_aid_forms": "cianfhoghlaim.law.ie.legal_aid_forms",
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
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


@dataclass
class LegalAidChunk:
    """One row in the `legal_aid_chunks` LanceDB table."""

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
    parts: list[str] = []
    if source == "legal_aid_pages":
        parts.extend([
            row.get("title", ""),
            row.get("page_kind", ""),
            " | ".join(row.get("eligibility_criteria", []) or []),
            " | ".join(row.get("services_offered", []) or []),
            " | ".join(row.get("application_steps", []) or []),
            row.get("summary", ""),
        ])
    elif source == "legal_aid_forms":
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


def _yield_legal_aid_chunks() -> Iterator[dict[str, Any]]:
    for source_key, table_name in LEGAL_AID_DUCKLAKE_TABLES.items():
        rows = _read_ducklake_table(table_name)
        for row in rows:
            text = _build_chunk_text(source_key, row)
            if not text:
                continue
            entity_type = "page" if source_key == "legal_aid_pages" else "form"
            yield {
                "source": "legal_aid",
                "entity_type": entity_type,
                "row": row,
                "text": text,
            }


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_legal_aid_chunk(
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
            row.get("title")
            or row.get("form_title")
            or row.get("form_number")
            or ""
        )
        extra_dict: dict[str, Any] = {
            k: v for k, v in row.items()
            if k not in {"url", "source_url", "title", "form_title",
                         "form_number", "summary"}
        }
        await table.declare_row(  # type: ignore[attr-defined]
            LegalAidChunk(
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
    async def legal_aid_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="cianfhoghlaim.law.ie.legal_aid_chunks",
            table_schema=await lancedb.TableSchema.from_class(
                LegalAidChunk,
                primary_key=["chunk_id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")  # R4
        items = list(_yield_legal_aid_chunks())
        id_gen = IdGenerator()
        for i in range(0, len(items), 100):
            batch = items[i : i + 100]
            await coco.map(  # type: ignore[attr-defined]
                process_legal_aid_chunk,
                batch,
                id_gen,
                target_table,
            )

    LegalAidEmbedding = coco.App(
        coco.AppConfig(name="LegalAidEmbedding"),
        legal_aid_app_main,
    )

else:

    def LegalAidEmbedding() -> None:  # type: ignore[no-redef]  # noqa: N802
        return None


async def search_legal_aid(
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
            table="cianfhoghlaim.law.ie.legal_aid_chunks",
            query=query,
            top_k=limit,
        )
        return result
    except Exception as exc:
        logger.warning("search_legal_aid_failed", error=str(exc))
        return result


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LEGAL_AID_DUCKLAKE_TABLES",
    "LegalAidChunk",
    "LegalAidEmbedding",
    "search_legal_aid",
]
