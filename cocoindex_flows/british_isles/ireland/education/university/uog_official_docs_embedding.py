"""UoGOfficialDocsApp — CocoIndex v1 App for UoG official documents.

Reads the `cianfhoghlaim.education.ie.uog_official_documents`
DuckLake table (populated by `uog_official_docs_source`) and
embeds the `{title + body + tags}` chunk into a LanceDB table
(`uog_official_documents`) using BGE-M3 1024-d.

Mirrors the canonical v1 App pattern from
`openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md`:
- `from .._shared._lifespan import shared_lifespan, EMBEDDER, LANCE_DB`
- `@coco.fn(memo=True)` for the processor
- `lancedb.mount_table_target(LANCE_DB, table_name=...)`
- `IdGenerator` for stable IDs
- BGE-M3 1024-d

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-tertiary-embeddings/spec.md
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco
    from cocoindex.connectors import lancedb
    from cocoindex.ops.sentence_transformers import (
        SentenceTransformerEmbedder,
    )
    from cocoindex.resources.id import IdGenerator

    COCOINDEX_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - defensive
    logger.warning("cocoindex_v1_not_available_for_uog_official_docs: %s", exc)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


from .._shared._lifespan import (  # noqa: E402
    EMBED_MODEL,
    EMBEDDER,
    LANCE_DB,
)

UOG_OFFICIAL_DOCS_DUCKLAKE_TABLE = (
    "cianfhoghlaim.education.ie.uog_official_documents"
)
LANCEDB_TABLE_NAME = "uog_official_documents"


def _read_uog_official_docs_ducklake() -> list[dict[str, Any]]:
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_uog_official_docs_embedding")
        return []
    db_path = os.environ.get("OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
    if not os.path.exists(db_path):
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(f"SELECT * FROM {UOG_OFFICIAL_DOCS_DUCKLAKE_TABLE}").fetchall()
        columns = [d[0] for d in con.description]
        return [dict(zip(columns, r, strict=False)) for r in rows]
    except Exception as exc:
        logger.warning(
            "uog_official_docs_ducklake_read_failed",
            table=UOG_OFFICIAL_DOCS_DUCKLAKE_TABLE,
            error=str(exc),
        )
        return []


@dataclass
class UoGOfficialDocPage:
    """One row in the `uog_official_documents` LanceDB table."""

    id: str
    document_id: str
    title: str
    body: str
    document_type: str
    source_kind: str
    source_url: str
    school_slug: str
    tags: str
    scraped_at: str
    embedded_text: str
    embedding: Annotated[Any, "SentenceTransformerEmbedder"] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_uog_official_doc_page(
        row: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        document_id = str(row.get("document_id", ""))
        if not document_id:
            return
        title = str(row.get("title", ""))
        body = str(row.get("body", "") or "")[:8000]
        tags = row.get("tags") or []
        tags_str = ", ".join(t for t in tags if isinstance(t, str))
        embedded_text = " ".join(filter(None, [title, body, tags_str]))
        if not embedded_text.strip():
            return
        embedding = await embedder.embed(embedded_text)
        await table.declare_row(
            UoGOfficialDocPage(
                id=await id_gen.next_id(embedded_text),
                document_id=document_id,
                title=title,
                body=body[:1000],
                document_type=str(row.get("document_type", "OTHER") or "OTHER"),
                source_kind=str(row.get("source_kind", "PUBLIC_WEB") or "PUBLIC_WEB"),
                source_url=str(row.get("url", "") or row.get("source_url", "")),
                school_slug=str(row.get("school_slug", "") or ""),
                tags=tags_str,
                scraped_at=str(row.get("scraped_at", "") or ""),
                embedded_text=embedded_text,
                embedding=embedding,
            )
        )

    @coco.fn
    async def uog_official_docs_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE_NAME,
            table_schema=await lancedb.TableSchema.from_class(
                UoGOfficialDocPage,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_uog_official_docs_ducklake()
        id_gen = IdGenerator()
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(process_uog_official_doc_page, batch, id_gen, target_table)

    UoGOfficialDocsApp = coco.App(
        coco.AppConfig(name="UoGOfficialDocsApp"),
        uog_official_docs_app_main,
    )
else:
    UoGOfficialDocsApp = None  # type: ignore[assignment]


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCEDB_TABLE_NAME",
    "UOG_OFFICIAL_DOCS_DUCKLAKE_TABLE",
    "UoGOfficialDocPage",
    "UoGOfficialDocsApp",
]
