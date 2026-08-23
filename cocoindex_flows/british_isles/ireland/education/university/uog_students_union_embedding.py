"""UoGStudentsUnionApp — CocoIndex v1 App for the UoG SU corpus.

Reads the `cianfhoghlaim.education.ie.uog_students_union_documents`
DuckLake table (populated by `uog_students_union_source`) and
embeds the SU documents into a LanceDB table using BGE-M3 1024-d.
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
except ImportError as exc:  # pragma: no cover
    logger.warning("cocoindex_v1_not_available_for_uog_students_union: %s", exc)
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

UOG_SU_DUCKLAKE_TABLE = (
    "cianfhoghlaim.education.ie.uog_students_union_documents"
)
LANCEDB_TABLE_NAME = "uog_students_union_documents"


def _read_uog_su_ducklake() -> list[dict[str, Any]]:
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_uog_students_union_embedding")
        return []
    db_path = os.environ.get("OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
    if not os.path.exists(db_path):
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(f"SELECT * FROM {UOG_SU_DUCKLAKE_TABLE}").fetchall()
        columns = [d[0] for d in con.description]
        return [dict(zip(columns, r, strict=False)) for r in rows]
    except Exception as exc:
        logger.warning(
            "uog_su_ducklake_read_failed",
            table=UOG_SU_DUCKLAKE_TABLE,
            error=str(exc),
        )
        return []


@dataclass
class UoGStudentsUnionPage:
    """One row in the `uog_students_union_documents` LanceDB table."""

    id: str
    document_id: str
    title: str
    body: str
    resource_kind: str
    is_constitution: bool
    elected_officer: str
    officer_role: str
    tags: str
    source_url: str
    scraped_at: str
    embedded_text: str
    embedding: Annotated[Any, "SentenceTransformerEmbedder"] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_uog_su_page(
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
        embedded_text = " ".join(
            filter(
                None,
                [
                    title,
                    body,
                    ", ".join(t for t in tags if isinstance(t, str)),
                    str(row.get("resource_kind", "") or ""),
                ],
            )
        )
        if not embedded_text.strip():
            return
        embedding = await embedder.embed(embedded_text)
        await table.declare_row(
            UoGStudentsUnionPage(
                id=await id_gen.next_id(embedded_text),
                document_id=document_id,
                title=title,
                body=body[:1000],
                resource_kind=str(row.get("resource_kind", "OTHER") or "OTHER"),
                is_constitution=bool(row.get("is_constitution", False)),
                elected_officer=str(row.get("elected_officer", "") or ""),
                officer_role=str(row.get("officer_role", "") or ""),
                tags=", ".join(t for t in tags if isinstance(t, str)),
                source_url=str(row.get("source_url", "") or ""),
                scraped_at=str(row.get("scraped_at", "") or ""),
                embedded_text=embedded_text,
                embedding=embedding,
            )
        )

    @coco.fn
    async def uog_students_union_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE_NAME,
            table_schema=await lancedb.TableSchema.from_class(
                UoGStudentsUnionPage,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_uog_su_ducklake()
        id_gen = IdGenerator()
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(process_uog_su_page, batch, id_gen, target_table)

    UoGStudentsUnionApp = coco.App(
        coco.AppConfig(name="UoGStudentsUnionApp"),
        uog_students_union_app_main,
    )
else:
    UoGStudentsUnionApp = None  # type: ignore[assignment]


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCEDB_TABLE_NAME",
    "UOG_SU_DUCKLAKE_TABLE",
    "UoGStudentsUnionApp",
    "UoGStudentsUnionPage",
]
