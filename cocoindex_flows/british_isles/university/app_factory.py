"""cocoindex_flows.british_isles.university — British Isles tertiary CocoIndex apps.

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-british-isles-tertiary-factory/spec.md

The `bitertiary_universities_app_factory(config)` emits one
CocoIndex v1 App per `BITertiaryDeepExtractionConfig`. Off by
default — the `[tool.dlt.sources.bitertiary_universities]` block
must be added to `pyproject.toml` for the factory to load.
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
    logger.warning("cocoindex_v1_not_available_for_bitertiary: %s", exc)
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


@dataclass
class BITertiaryAppConfig:
    """Per-institution CocoIndex app configuration."""

    university_id: str
    institution_name: str
    base_url: str
    nation: str  # BINation.value


@dataclass
class BITertiaryDocPage:
    id: str
    url: str
    title: str
    resource_kind: str
    university_id: str
    embedded_text: str
    embedding: Annotated[Any, "SentenceTransformerEmbedder"] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


def _read_bitertiary_ducklake(university_id: str, table: str) -> list[dict[str, Any]]:
    try:
        import duckdb
    except ImportError:
        return []
    db_path = os.environ.get("OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
    if not os.path.exists(db_path):
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(
            f"SELECT * FROM {table} WHERE university_id = ?",
            [university_id],
        ).fetchall()
        columns = [d[0] for d in con.description]
        return [dict(zip(columns, r, strict=False)) for r in rows]
    except Exception:
        return []


def bitertiary_universities_app_factory(config: BITertiaryAppConfig) -> Any:
    """Build one CocoIndex v1 App per BITertiaryDeepExtractionConfig.

    Off by default: the caller must register the App only when
    the corresponding `pyproject.toml :: [tool.dlt.sources.bitertiary_universities]`
    block contains the entry.
    """
    if not COCOINDEX_AVAILABLE:
        return None

    table_name = f"bitertiary_universities_{config.university_id}".replace("-", "_")

    @coco.fn(memo=True)
    async def process_bitertiary_page(
        row: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,
    ) -> None:
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        url = str(row.get("url", ""))
        title = str(row.get("title", "") or "")
        resource_kind = str(row.get("resource_kind", "OTHER") or "OTHER")
        embedded_text = " ".join(filter(None, [title, url, resource_kind]))
        if not embedded_text.strip():
            return
        embedding = await embedder.embed(embedded_text)
        await table.declare_row(
            BITertiaryDocPage(
                id=await id_gen.next_id(embedded_text),
                url=url,
                title=title,
                resource_kind=resource_kind,
                university_id=config.university_id,
                embedded_text=embedded_text,
                embedding=embedding,
            )
        )

    @coco.fn
    async def bitertiary_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=table_name,
            table_schema=await lancedb.TableSchema.from_class(
                BITertiaryDocPage,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_bitertiary_ducklake(
            config.university_id, "cianfhoghlaim.education.ie.uog_official_documents"
        )
        id_gen = IdGenerator()
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(process_bitertiary_page, batch, id_gen, target_table)

    return coco.App(
        coco.AppConfig(name=f"BITertiaryApp_{config.university_id}"),
        bitertiary_app_main,
    )


__all__ = [
    "COCOINDEX_AVAILABLE",
    "BITertiaryAppConfig",
    "BITertiaryDocPage",
    "bitertiary_universities_app_factory",
]
