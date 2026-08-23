"""NuiFederationApp — CocoIndex v1 App for the NUI federation.

Reads the `cianfhoghlaim.education.ie.nui_members` DuckLake table
(populated by `nui_federation_source`) and embeds the 4 NUI
constituents + the historical archive. BGE-M3 1024-d on
`{institution_name + wikipedia_title + nfq_min + nfq_max}`.
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
    logger.warning("cocoindex_v1_not_available_for_nui_federation: %s", exc)
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

NUI_MEMBERS_DUCKLAKE_TABLE = (
    "cianfhoghlaim.education.ie.nui_members"
)
LANCEDB_TABLE_NAME = "nui_members"


def _read_nui_members_ducklake() -> list[dict[str, Any]]:
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_nui_federation_embedding")
        return []
    db_path = os.environ.get("OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
    if not os.path.exists(db_path):
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(f"SELECT * FROM {NUI_MEMBERS_DUCKLAKE_TABLE}").fetchall()
        columns = [d[0] for d in con.description]
        return [dict(zip(columns, r, strict=False)) for r in rows]
    except Exception as exc:
        logger.warning(
            "nui_members_ducklake_read_failed",
            table=NUI_MEMBERS_DUCKLAKE_TABLE,
            error=str(exc),
        )
        return []


@dataclass
class NuiMemberChunk:
    """One row in the `nui_members` LanceDB table."""

    id: str
    member_id: str
    member_name: str
    member_kind: str
    home_url: str
    wikipedia_title: str
    joined_nui_year: int
    left_nui_year: int
    source_url: str
    scraped_at: str
    embedded_text: str
    embedding: Annotated[Any, "SentenceTransformerEmbedder"] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_nui_member_chunk(
        row: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        member_id = str(row.get("member_id", ""))
        if not member_id:
            return
        member_name = str(row.get("member_name", ""))
        embedded_text = " ".join(
            filter(
                None,
                [
                    member_name,
                    str(row.get("wikipedia_title", "") or ""),
                    str(row.get("kind", "") or ""),
                ],
            )
        )
        if not embedded_text.strip():
            return
        embedding = await embedder.embed(embedded_text)
        await table.declare_row(
            NuiMemberChunk(
                id=await id_gen.next_id(embedded_text),
                member_id=member_id,
                member_name=member_name,
                member_kind=str(row.get("kind", "") or ""),
                home_url=str(row.get("home_url", "") or ""),
                wikipedia_title=str(row.get("wikipedia_title", "") or ""),
                joined_nui_year=int(row.get("joined_nui_year", 0) or 0),
                left_nui_year=int(row.get("left_nui_year", 0) or 0),
                source_url=str(row.get("source_url", "") or ""),
                scraped_at=str(row.get("scraped_at", "") or ""),
                embedded_text=embedded_text,
                embedding=embedding,
            )
        )

    @coco.fn
    async def nui_federation_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE_NAME,
            table_schema=await lancedb.TableSchema.from_class(
                NuiMemberChunk,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_nui_members_ducklake()
        id_gen = IdGenerator()
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(process_nui_member_chunk, batch, id_gen, target_table)

    NuiFederationApp = coco.App(
        coco.AppConfig(name="NuiFederationApp"),
        nui_federation_app_main,
    )
else:
    NuiFederationApp = None  # type: ignore[assignment]


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCEDB_TABLE_NAME",
    "NUI_MEMBERS_DUCKLAKE_TABLE",
    "NuiFederationApp",
    "NuiMemberChunk",
]
