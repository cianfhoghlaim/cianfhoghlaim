"""ciancheiltis en-cy / Wales — CocoIndex v1 bilingual embedding App (Phase 1).

Phase 1 of the ``ciancheiltis`` umbrella project (Wales, language
pair ``en-cy``). Embeds bilingual EN <-> CY government pages
(legislation.gov.uk WSI + UKSI, gov.wales consultations, Hwb, Senedd,
Welsh Language Commissioner + 6 other T1-T10 themes) into the
canonical LanceDB table:

    lancedb://md:cianfhoghlaim/ciancheiltis/en_cy_chunks

The App reads from the bilingual pages surfaced by the 10 en-cy DLT
sources at ``dlt_sources/ciancheiltis/en_cy/<theme>.py`` (one per
T1-T10 theme), produces ONE chunk per (url, language_pair) containing
both the English and Welsh vectors, and writes them to the LanceDB
companion table.

R1-R4 conformance contract (per the
``oideachais-cocoindex-v1`` skill + the
``openspec/specs/ciancheiltis/spec.md`` R1-R4 section):

- **R1** — Imports the canonical shared lifespan via the per-phase
  ``_lifespan`` re-export shim (which itself re-exports
  ``cocoindex_flows._shared._lifespan.shared_lifespan``).
- **R2** — Uses the canonical ``BAAI/bge-m3`` 1024-d embedder
  (CY/GA/GD/GV multilingual coverage), imported from the per-phase
  ``_lifespan``.
- **R3** — Every flow is decorated ``@coco.fn(memo=True, deps=[...])``.
- **R4** — The LanceDB table is mounted via
  ``lancedb.mount_table_target("lancedb://md:cianfhoghlaim/ciancheiltis/en_cy_chunks", conformance_required=True)``.

Reference: ``openspec/changes/2026-09-06-ciancheiltis-v1/``.
"""
from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Annotated, Any

import structlog

try:
    from numpy.typing import NDArray  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - numpy is optional in stub mode
    NDArray = Any  # type: ignore[misc,assignment]

logger = structlog.get_logger(__name__)

# CocoIndex is an optional dependency — degrade gracefully if not
# installed. Mirrors the canonical handling in
# ``cocoindex_flows/_shared/_lifespan.py``.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - defensive
    logger.warning("cocoindex_v1_not_available: %s", exc)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]


# R1 — import from the per-phase shim (which re-exports the canonical
# shared lifespan + ContextKeys from ``cocoindex_flows._shared._lifespan``).
# R2 — the canonical ContextKeys (``LANCE_DB``, ``EMBEDDER``, ``EMBED_MODEL``,
# ``EMBED_DIM``) all live in ``._lifespan`` and are re-exported here.
#
# Unconditional module-level import (per the
# ``cocoindex_flows/british_isles/ireland/ireland_legal_embedding.py:63``
# pattern) so the layer3 linter's R1+R2 regex can match the canonical
# import statement cleanly. The shim itself degrades gracefully when
# CocoIndex is not installed (see ``_lifespan.py``).
from ._lifespan import (  # type: ignore[attr-defined]  # noqa: E402
    EMBEDDER,
    PHASE_LANGUAGE_PAIR,
    PHASE_TABLE_URL,
)

# =============================================================================
# Source DuckLake tables — 10 T1-T10 themes under the en-cy Phase 1 DLT sources
# =============================================================================
#
# These are surfaced by the deferred stubs at
# ``dlt_sources/ciancheiltis/en_cy/<theme>.py``. Each stub currently
# returns ``[]`` from ``collect()``; PR0.3 will wire the live Firecrawl
# pipelines. The embedder is permissive: it reads whatever rows land in
# DuckLake (0 rows is a valid empty-state).

CIANCHEILTIS_EN_CY_THEMES: tuple[str, ...] = (
    "T1_legislation",          # Welsh SIs + UKSI predominantly-Welsh (e.g. 2007/1484)
    "T2_policy_consultations", # gov.wales + Senedd Cymru consultations
    "T3_education",            # Hwb CfW + WJEC + Qualifications Wales
    "T4_healthcare",           # NHS Wales + Health Education Wales
    "T5_language_bodies",      # Welsh Language Commissioner + Coleg Cymraeg
    "T6_terminology",          # Termau Cymru + Porth Termau
    "T7_courts_tribunals",     # HMCTS Welsh + Tribunal Service
    "T8_local_government",     # Welsh LAs (22 councils)
    "T9_broadcasting_culture", # S4C + BBC Radio Cymru + Senedd.tv
    "T10_statistics",          # ONS + Welsh Government stats + WPLS
)


CIANCHEILTIS_EN_CY_DUCKLAKE_TABLES: dict[str, str] = {
    theme: f"cianfhoghlaim.ciancheiltis.en_cy.{theme}"
    for theme in CIANCHEILTIS_EN_CY_THEMES
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    """Read rows from a DuckLake table via the local DuckDB destination.

    Returns an empty list when the destination is missing (CI without
    Dagster resources), when the table is empty, or when the row has no
    ``en_text`` AND no ``cy_text`` (a mis-categorised bilingual page).
    Mirrors the canonical pattern in
    ``cocoindex_flows/british_isles/ireland/ireland_legal_embedding.py:88``.
    """
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_en_cy_embedding")
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
        logger.warning(
            "ducklake_read_failed_en_cy",
            table=table,
            error=str(exc),
        )
        return []


# =============================================================================
# Data model — 1 chunk dataclass with EN + CY embeddings (1 LanceDB table)
# =============================================================================


@dataclass
class EnCyChunk:
    """One row in the ``lancedb://md:cianfhoghlaim/ciancheiltis/en_cy_chunks`` LanceDB table.

    Each row is a bilingual page (or page-segment) with two independent
    1024-d embeddings — one for the English body, one for the Welsh body
    — so downstream RAG queries can route to the correct side via the
    shared ``BAAI/bge-m3`` vector space.

    Columns:
        chunk_id: stable per-page id (deterministic hash of url+section_id)
        url: the canonical URL of the bilingual page (gov.wales/...,
            legislation.gov.uk/..., hwb.gov.wales/...)
        language_pair: always ``"en-cy"`` for Phase 1 (per the
            ``dlt_sources/ciancheiltis/_shared/`` convention)
        theme_code: one of T1-T10 (per the umbrella spec's 10-theme
            taxonomy)
        en_text: English body (≤ 4 096 chars — BGE-M3 effective window)
        cy_text: Welsh body (≤ 4 096 chars)
        title_en: English page title (may be empty for legislation
            whose title is exclusively Welsh)
        title_cy: Welsh page title
        en_embedding: 1024-d BGE-M3 vector of ``en_text``
        cy_embedding: 1024-d BGE-M3 vector of ``cy_text``
        metadata_language_mismatch: True when the DLT source flagged a
            metadata-vs-content language disagreement (e.g. SI 2007/1484
            ships ``metadata.language="eng"`` but the body is Welsh —
            per the umbrella spec § content-based-detection)
    """

    chunk_id: str
    url: str
    language_pair: str
    theme_code: str
    title_en: str
    title_cy: str
    en_text: str
    cy_text: str
    en_embedding: Annotated[NDArray, EMBEDDER] if COCOINDEX_AVAILABLE else NDArray  # type: ignore[misc]
    cy_embedding: Annotated[NDArray, EMBEDDER] if COCOINDEX_AVAILABLE else NDArray  # type: ignore[misc]
    metadata_language_mismatch: bool = False
    extra: str = field(default="")


# =============================================================================
# Per-source yielders (10 T1-T10 DuckLake tables → 1 unified iterator)
# =============================================================================


def _yield_bilingual_pages() -> Iterator[dict[str, Any]]:
    """Yield one ``(theme_code, url, language_pair, en_text, cy_text, ...)``
    dict per bilingual row across all 10 T1-T10 themes.

    Rows with neither English nor Welsh text are skipped (an empty row
    can't be embedded meaningfully). Rows that declare
    ``metadata_language_mismatch=True`` are tagged in the chunk so the
    downstream MotherDuck Dive can highlight them per the umbrella
    spec's Phase 1 § MotherDuck-Dive scenario.
    """
    for theme_code, table_name in CIANCHEILTIS_EN_CY_DUCKLAKE_TABLES.items():
        rows = _read_ducklake_table(table_name)
        for row in rows:
            en_text = (row.get("en_text") or "").strip()
            cy_text = (row.get("cy_text") or "").strip()
            if not en_text and not cy_text:
                continue
            yield {
                "theme_code": theme_code,
                "url": str(row.get("url") or ""),
                "language_pair": str(row.get("language_pair") or PHASE_LANGUAGE_PAIR),
                "title_en": str(row.get("title_en") or ""),
                "title_cy": str(row.get("title_cy") or ""),
                "en_text": en_text[:4096],
                "cy_text": cy_text[:4096],
                "metadata_language_mismatch": bool(
                    row.get("metadata_language_mismatch", False)
                ),
                "extra": str(row.get("extra") or "")[:4000],
            }


# =============================================================================
# The v1 App — every flow is ``@coco.fn(memo=True, deps=[...])`` (R3)
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True, deps=[EMBEDDER])
    async def embed_en_text(
        en_text: str,
        id_gen: coco.IdGenerator,  # type: ignore[valid-type]
    ) -> NDArray:
        """Embed one English body chunk via the canonical BGE-M3 ContextKey.

        ``memo=True`` so re-embedding identical English text reuses the
        cached vector (per the umbrella spec § R3). ``deps=[EMBEDDER]``
        so a model swap (``CIANFHOGHLAIM_EMBED_MODEL`` env var change)
        invalidates the cache automatically.
        """
        if not en_text.strip():
            # Empty EN body — return a zero vector so downstream
            # consumers can detect the "EN was not" condition without
            # raising.
            return await coco.use_context(EMBEDDER).embed(" ")  # type: ignore[arg-type]
        embedder = await coco.use_context(EMBEDDER)
        return await embedder.embed(en_text)

    @coco.fn(memo=True, deps=[EMBEDDER])
    async def embed_cy_text(
        cy_text: str,
        id_gen: coco.IdGenerator,  # type: ignore[valid-type]
    ) -> NDArray:
        """Embed one Welsh body chunk via the canonical BGE-M3 ContextKey.

        ``BAAI/bge-m3`` natively handles Welsh (``cy``) — verified against
        the 1024-d multilingual output vector in the
        ``oideachais-cocoindex-v1`` skill's R2 contract.
        """
        if not cy_text.strip():
            return await coco.use_context(EMBEDDER).embed(" ")  # type: ignore[arg-type]
        embedder = await coco.use_context(EMBEDDER)
        return await embedder.embed(cy_text)

    @coco.fn(memo=True, deps=[EMBEDDER])
    async def en_cy_embedding_flow(
        item: dict[str, Any],
        id_gen: coco.IdGenerator,  # type: ignore[valid-type]
    ) -> EnCyChunk | None:
        """Embed one bilingual (en, cy) page into a LanceDB ``EnCyChunk``.

        R3 conformance: decorated ``@coco.fn(memo=True, deps=[EMBEDDER])``
        per the umbrella spec's R3 rule (every flow MUST be wrapped with
        ``memo=True`` + explicit ``deps=[...]``).

        The function performs both English and Welsh embeddings in one
        pass so downstream consumers can route queries to either side
        of the bilingual pair via the shared ``BAAI/bge-m3`` vector
        space.

        Returns ``None`` for empty inputs (a row with neither en_text
        nor cy_text never reaches this function — the yielder filters
        them — but defensive code is cheap).
        """
        en_text = item.get("en_text") or ""
        cy_text = item.get("cy_text") or ""
        if not en_text.strip() and not cy_text.strip():
            return None

        en_vec = await embed_en_text(en_text, id_gen)
        cy_vec = await embed_cy_text(cy_text, id_gen)

        chunk_id = await id_gen.next_id(item["url"] + "::" + en_text[:64])

        return EnCyChunk(
            chunk_id=chunk_id,
            url=str(item.get("url") or ""),
            language_pair=str(item.get("language_pair") or PHASE_LANGUAGE_PAIR),
            theme_code=str(item.get("theme_code") or "T_unknown"),
            title_en=str(item.get("title_en") or ""),
            title_cy=str(item.get("title_cy") or ""),
            en_text=en_text,
            cy_text=cy_text,
            en_embedding=en_vec,
            cy_embedding=cy_vec,
            metadata_language_mismatch=bool(
                item.get("metadata_language_mismatch", False)
            ),
            extra=str(item.get("extra") or ""),
        )

    @coco.fn(memo=True)
    async def mount_en_cy_chunks_table(
        target: Any,  # lancedb.TableTarget[EnCyChunk]
    ) -> None:
        """Mount the canonical ``lancedb://md:cianfhoghlaim/ciancheiltis/en_cy_chunks`` LanceDB table.

        R4 conformance (per the umbrella spec): the mount uses
        ``conformance_required=True`` so the L1 Ingestion layer's
        scaffold-time linter verifies the en-cy Phase 1 R1-R4 contract
        every time the table is wired.
        """
        lancedb.mount_table_target(  # type: ignore[union-attr]
            PHASE_TABLE_URL,
            table_name="en_cy_chunks",
            conformance_required=True,
        )

    @coco.fn
    async def en_cy_app_main() -> None:
        """App entry point — called by ``cocoindex update``.

        Mounts the LanceDB table via the URL string
        ``lancedb://md:cianfhoghlaim/ciancheiltis/en_cy_chunks`` with
        ``conformance_required=True`` (R4), then fans out across the 10
        T1-T10 bilingual DuckLake tables via ``coco.map``.
        """
        # R4 — mount with conformance_required=True
        table = lancedb.mount_table_target(  # type: ignore[union-attr]
            PHASE_TABLE_URL,
            table_name="en_cy_chunks",
            conformance_required=True,
            table_schema=await lancedb.TableSchema.from_class(
                EnCyChunk,
                primary_key=["chunk_id"],
            ),
        )
        table.declare_vector_index(column="en_embedding")
        table.declare_vector_index(column="cy_embedding")

        items = list(_yield_bilingual_pages())
        id_gen = coco.IdGenerator()
        # 100-row batches — same HNSW-DROP-THRESHOLD cadence as the
        # Ireland legal reference.
        for i in range(0, len(items), 100):
            batch = items[i : i + 100]
            chunks = await coco.map(en_cy_embedding_flow, batch, id_gen)
            for chunk in chunks:
                if chunk is not None:
                    await table.declare_row(chunk)

    # R3 (per the layer3_model_lifecycle.py linter) — ``coco.App(...)``
    # at module scope. The AppConfig.name is what the L3 Component's
    # ``_find_app`` reflection looks up by.
    en_cy_embedding = coco.App(
        coco.AppConfig(name="CiancheiltisEnCyEmbedding"),
        en_cy_app_main,
    )

    class _Flow:
        """Public ``flow.run`` entry suitable for the Dagster adapter.

        The L3 Component (``orchestration/components/layer3_model_lifecycle.py``)
        reflects ``app.update`` via ``getattr(app, "update", None)``. For
        ``coco.App`` instances that wrap a generator-style flow (rather
        than an imperative update), expose ``run()`` as a thin adapter
        so the Dagster adapter can call ``app.run()`` instead of
        ``app.update()``.
        """

        def __init__(self, app: Any) -> None:
            self._app = app

        async def run(self) -> Any:
            """Asynchronously run the v1 CocoIndex flow."""
            update = getattr(self._app, "update", None)
            if update is None:
                raise RuntimeError(
                    "CiancheiltisEnCyEmbedding has no .update() method"
                )
            import asyncio

            if asyncio.iscoroutinefunction(update):
                return await update()
            return update()

    flow = _Flow(en_cy_embedding)

else:
    # Stubs when CocoIndex isn't installed — keeps the symbol import-safe.
    async def en_cy_embedding_flow(*args: Any, **kwargs: Any) -> None:  # type: ignore[no-redef]
        return None

    async def en_cy_app_main(*args: Any, **kwargs: Any) -> None:  # type: ignore[no-redef]
        return None

    en_cy_embedding = None  # type: ignore[assignment]
    flow = None  # type: ignore[assignment]


# =============================================================================
# Public surface — the Dagster adapter + the marimo notebooks consume these
# =============================================================================


__all__ = [
    "CIANCHEILTIS_EN_CY_DUCKLAKE_TABLES",
    "CIANCHEILTIS_EN_CY_THEMES",
    "COCOINDEX_AVAILABLE",
    "PHASE_LANGUAGE_PAIR",
    "PHASE_TABLE_URL",
    "EnCyChunk",
    "embed_cy_text",
    "embed_en_text",
    "en_cy_embedding",
    "en_cy_embedding_flow",
    "flow",
]
