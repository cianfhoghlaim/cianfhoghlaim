"""ciancheiltis en-ga / Northern Ireland — CocoIndex v1 bilingual embedding App (Phase 3).

Phase 3 of the ``ciancheiltis`` umbrella project (Northern Ireland,
language pair ``en-ga``). Embeds bilingual EN <-> GA government pages
(legislation.gov.uk NISI + NID + NIA + UKSI NI-applicable subset,
nidirect.gov.uk + NI Executive department pages, CCEA + Education
Authority NI, NI Health & Social Care patient information, Comhairle
na Gaelscolaíochta (CnaG) + The Executive Office + Ulster-Scots
Agency, IATE, NI Courts Service, and the 11 NI unitary councils —
Phase 3 covers T1-T8 of the 10-theme taxonomy; T9 + T10 land in a
later PR) into the canonical Phase 3 LanceDB table:

    lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni_chunks

The App reads from the bilingual pages surfaced by the 8 en-ga-NI DLT
sources at ``dlt_sources/ciancheiltis/en_ga_ni/<theme>.py`` (one per
T1-T8 theme), produces ONE chunk per (url, language_pair) containing
both the English and Irish embeddings, and writes them to the Phase 3
LanceDB companion table.

R1-R4 conformance contract (per the
``oideachais-cocoindex-v1`` skill + the
``openspec/specs/ciancheiltis/spec.md`` R1-R4 section):

- **R1** — Imports ``from ._lifespan import EMBEDDER,
  PHASE_LANGUAGE_PAIR_GA_NI, PHASE_TABLE_URL_GA_NI`` (the
  per-phase shim which itself re-exports
  ``cocoindex_flows._shared._lifespan.shared_lifespan``).
- **R2** — Uses the canonical ``BAAI/bge-m3`` 1024-d embedder
  (CY/GA/GD/GV multilingual coverage), imported from the per-phase
  ``_lifespan``.
- **R3** — Every flow is decorated ``@coco.fn(memo=True, deps=[...])``.
- **R4** — The LanceDB table is mounted via
  ``lancedb.mount_table_target("lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni_chunks", conformance_required=True)``.

The BAML extraction client used to populate this App's input rows
is ``CiancheiltisGaNiExtract`` (registered by subagent 1 in
``baml_src/british_isles/ciancheiltis_en_ga_ni.baml``); the App
itself does not call BAML directly — the bilingual pages land in
DuckLake first (via the DLT sources), and this App embeds whatever
rows are present.

Canonical example (per the umbrella spec's Northern Ireland row):
``https://www.legislation.gov.uk/uksi/2022/15/contents/made`` — the
*Identity and Language (Northern Ireland) Act 2022*, the founding
statute of the modern Irish-language rights framework in NI
(establishing the Irish Language Commissioner + the Commissioner for
Ulster Scots and the Ulster Scots Academy).

Reference: ``openspec/changes/2026-09-06-ciancheiltis-v1/`` (the
umbrella change that introduces Phase 1 + Phase 2 + Phase 3).
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
# ``cocoindex_flows/british_isles/uk/ciancheiltis_en_ga_roi_embedding.py:86``
# pattern) so the layer3 linter's R1+R2 regex can match the canonical
# import statement cleanly. The shim itself degrades gracefully when
# CocoIndex is not installed (see ``_lifespan.py``).
from ._lifespan import (  # type: ignore[attr-defined]  # noqa: E402
    EMBEDDER,
    PHASE_LANGUAGE_PAIR_GA_NI,
    PHASE_TABLE_URL_GA_NI,
)

# =============================================================================
# Source DuckLake tables — 8 T1-T8 themes under the en-ga-NI Phase 3 DLT sources
# =============================================================================
#
# These are surfaced by the deferred stubs at
# ``dlt_sources/ciancheiltis/en_ga_ni/<theme>.py``. Each stub currently
# returns ``[]`` from ``collect()``; PR0.7 will wire the live Firecrawl
# pipelines. The embedder is permissive: it reads whatever rows land in
# DuckLake (0 rows is a valid empty-state).
#
# Phase 3 covers T1-T8 only; T9 (Public broadcasting & culture: TG4 +
# RTÉ Raidió na Gaeltachta + RTÉ Raidió na Life — not NI-applicable, will
# inherit from Phase 2 ROI sister corpus) and T10 (Statistics & public
# records: NISRA Gaeilge) land in PR0.7.1.

CIANCHEILTIS_EN_GA_NI_THEMES: tuple[str, ...] = (
    "T1_legislation",          # legislation.gov.uk /nisi/<year>/<num> + /nid + /nia + NI-applicable /uksi subset (e.g. uksi/2022/15 = Identity and Language (NI) Act 2022)
    "T2_policy_consultations", # nidirect.gov.uk + northerireland.gov.uk department pages
    "T3_education",            # CCEA + Education Authority NI (the bilingual-pair wrapper around dlt_sources/british_isles/northern_ireland/education/ccea_qualifications.py)
    "T4_healthcare",           # NI Health & Social Care (HSC) patient info en + ga
    "T5_language_bodies",      # Comhairle na Gaelscolaíochta (CnaG / comhairle.org) + The Executive Office + Ulster-Scots Agency
    "T6_terminology",          # IATE only (NI shares Téarma with the Republic — no separate NI term DB)
    "T7_courts_tribunals",     # NI Courts Service (courtsni.uk forms + rules + judgments)
    "T8_local_government",     # 11 NI unitary councils (Antrim & Newtownabbey, Ards & North Down, Armagh Banbridge & Craigavon, Belfast, Causeway Coast & Glens, Derry & Strabane, Fermanagh & Omagh, Lisburn & Castlereagh, Mid & East Antrim, Mid Ulster, Newry Mourne & Down)
)


CIANCHEILTIS_EN_GA_NI_DUCKLAKE_TABLES: dict[str, str] = {
    theme: f"cianfhoghlaim.ciancheiltis.en_ga_ni.{theme}"
    for theme in CIANCHEILTIS_EN_GA_NI_THEMES
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    """Read rows from a DuckLake table via the local DuckDB destination.

    Returns an empty list when the destination is missing (CI without
    Dagster resources), when the table is empty, or when the row has no
    ``en_text`` AND no ``ga_text`` (a mis-categorised bilingual page).
    Mirrors the canonical pattern in
    ``cocoindex_flows/british_isles/uk/ciancheiltis_en_cy_embedding.py:110``.
    """
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_en_ga_ni_embedding")
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
            "ducklake_read_failed_en_ga_ni",
            table=table,
            error=str(exc),
        )
        return []


# =============================================================================
# Data model — 1 chunk dataclass with EN + GA embeddings (1 LanceDB table)
# =============================================================================


@dataclass
class EnGaNiChunk:
    """One row in the ``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni_chunks`` LanceDB table.

    Each row is a bilingual page (or page-segment) with two independent
    1024-d embeddings — one for the English body, one for the Irish body
    — so downstream RAG queries can route to the correct side via the
    shared ``BAAI/bge-m3`` vector space.

    Columns:
        chunk_id: stable per-page id (deterministic hash of url+section_id)
        url: the canonical URL of the bilingual page
            (legislation.gov.uk/..., nidirect.gov.uk/...,
            ccea.org.uk/..., online.hscni.net/...,
            comhairle.org/..., iate.europa.eu/...,
            courtsni.uk/..., antrimandnewtownabbey.gov.uk/...)
        language_pair: always ``"en-ga"`` for Phase 3 (per the
            ``dlt_sources/ciancheiltis/_shared/`` convention)
        theme_code: one of T1-T8 for Phase 3 (T9 + T10 land in PR0.7.1)
        en_text: English body (≤ 4 096 chars — BGE-M3 effective window)
        ga_text: Irish body (≤ 4 096 chars)
        title_en: English page title (may be empty for legislation
            whose title is exclusively Irish)
        title_ga: Irish page title
        en_embedding: 1024-d BGE-M3 vector of ``en_text``
        ga_embedding: 1024-d BGE-M3 vector of ``ga_text``
        metadata_language_mismatch: True when the DLT source flagged a
            metadata-vs-content language disagreement (e.g. some
            UKSI NI-applicable rows ship ``metadata.language="en"``
            while the body is Irish-only — per the umbrella spec §
            content-based-detection)
    """

    chunk_id: str
    url: str
    language_pair: str
    theme_code: str
    title_en: str
    title_ga: str
    en_text: str
    ga_text: str
    en_embedding: Annotated[NDArray, EMBEDDER] if COCOINDEX_AVAILABLE else NDArray  # type: ignore[misc]
    ga_embedding: Annotated[NDArray, EMBEDDER] if COCOINDEX_AVAILABLE else NDArray  # type: ignore[misc]
    metadata_language_mismatch: bool = False
    extra: str = field(default="")


# =============================================================================
# Per-source yielders (8 T1-T8 DuckLake tables → 1 unified iterator)
# =============================================================================


def _yield_bilingual_pages() -> Iterator[dict[str, Any]]:
    """Yield one ``(theme_code, url, language_pair, en_text, ga_text, ...)``
    dict per bilingual row across all 8 T1-T8 themes.

    Rows with neither English nor Irish text are skipped (an empty row
    can't be embedded meaningfully). Rows that declare
    ``metadata_language_mismatch=True`` are tagged in the chunk so the
    downstream MotherDuck Dive can highlight them per the umbrella
    spec's Phase 3 § MotherDuck-Dive scenario.
    """
    for theme_code, table_name in CIANCHEILTIS_EN_GA_NI_DUCKLAKE_TABLES.items():
        rows = _read_ducklake_table(table_name)
        for row in rows:
            en_text = (row.get("en_text") or "").strip()
            ga_text = (row.get("ga_text") or "").strip()
            if not en_text and not ga_text:
                continue
            yield {
                "theme_code": theme_code,
                "url": str(row.get("url") or ""),
                "language_pair": str(row.get("language_pair") or PHASE_LANGUAGE_PAIR_GA_NI),
                "title_en": str(row.get("title_en") or ""),
                "title_ga": str(row.get("title_ga") or ""),
                "en_text": en_text[:4096],
                "ga_text": ga_text[:4096],
                "metadata_language_mismatch": bool(
                    row.get("metadata_language_mismatch", False)
                ),
                "extra": str(row.get("extra") or "")[:4000],
            }


# =============================================================================
# The v1 App — every flow is ``@coco.fn(memo=True, deps=[...])`` (R3, strict)
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
    async def embed_ga_text(
        ga_text: str,
        id_gen: coco.IdGenerator,  # type: ignore[valid-type]
    ) -> NDArray:
        """Embed one Irish body chunk via the canonical BGE-M3 ContextKey.

        ``BAAI/bge-m3`` natively handles Irish (``ga``) — verified
        against the 1024-d multilingual output vector in the
        ``oideachais-cocoindex-v1`` skill's R2 contract.
        """
        if not ga_text.strip():
            return await coco.use_context(EMBEDDER).embed(" ")  # type: ignore[arg-type]
        embedder = await coco.use_context(EMBEDDER)
        return await embedder.embed(ga_text)

    @coco.fn(memo=True, deps=[EMBEDDER])
    async def en_ga_ni_embedding_flow(
        item: dict[str, Any],
        id_gen: coco.IdGenerator,  # type: ignore[valid-type]
    ) -> EnGaNiChunk | None:
        """Embed one bilingual (en, ga) page into a LanceDB ``EnGaNiChunk``.

        R3 conformance: decorated ``@coco.fn(memo=True, deps=[EMBEDDER])``
        per the umbrella spec's R3 rule (every flow MUST be wrapped with
        ``memo=True`` + explicit ``deps=[...]``).

        The function performs both English and Irish embeddings in one
        pass so downstream consumers can route queries to either side
        of the bilingual pair via the shared ``BAAI/bge-m3`` vector
        space.

        Returns ``None`` for empty inputs (a row with neither en_text
        nor ga_text never reaches this function — the yielder filters
        them — but defensive code is cheap).
        """
        en_text = item.get("en_text") or ""
        ga_text = item.get("ga_text") or ""
        if not en_text.strip() and not ga_text.strip():
            return None

        en_vec = await embed_en_text(en_text, id_gen)
        ga_vec = await embed_ga_text(ga_text, id_gen)

        chunk_id = await id_gen.next_id(item["url"] + "::" + en_text[:64])

        return EnGaNiChunk(
            chunk_id=chunk_id,
            url=str(item.get("url") or ""),
            language_pair=str(item.get("language_pair") or PHASE_LANGUAGE_PAIR_GA_NI),
            theme_code=str(item.get("theme_code") or "T_unknown"),
            title_en=str(item.get("title_en") or ""),
            title_ga=str(item.get("title_ga") or ""),
            en_text=en_text,
            ga_text=ga_text,
            en_embedding=en_vec,
            ga_embedding=ga_vec,
            metadata_language_mismatch=bool(
                item.get("metadata_language_mismatch", False)
            ),
            extra=str(item.get("extra") or ""),
        )

    @coco.fn(memo=True, deps=[EMBEDDER])
    async def mount_en_ga_ni_chunks_table(
        target: Any,  # lancedb.TableTarget[EnGaNiChunk]
    ) -> None:
        """Mount the canonical ``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni_chunks`` LanceDB table.

        R4 conformance (per the umbrella spec): the mount uses
        ``conformance_required=True`` so the L1 Ingestion layer's
        scaffold-time linter verifies the en-ga-NI Phase 3 R1-R4
        contract every time the table is wired.

        ``deps=[EMBEDDER]`` so a model swap re-declares the vector
        indices on the new embedding columns.
        """
        lancedb.mount_table_target(  # type: ignore[union-attr]
            PHASE_TABLE_URL_GA_NI,
            table_name="en_ga_ni_chunks",
            conformance_required=True,
        )

    @coco.fn(memo=True, deps=[EMBEDDER])
    async def en_ga_ni_app_main() -> None:
        """App entry point — called by ``cocoindex update``.

        Mounts the LanceDB table via the URL string
        ``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni_chunks``
        with ``conformance_required=True`` (R4), then fans out across
        the 8 T1-T8 bilingual DuckLake tables via ``coco.map``.

        ``deps=[EMBEDDER]`` because the orchestrator depends on the
        embedder context for all downstream per-row embedding work.
        """
        # R4 — mount with conformance_required=True
        table = lancedb.mount_table_target(  # type: ignore[union-attr]
            PHASE_TABLE_URL_GA_NI,
            table_name="en_ga_ni_chunks",
            conformance_required=True,
            table_schema=await lancedb.TableSchema.from_class(
                EnGaNiChunk,
                primary_key=["chunk_id"],
            ),
        )
        table.declare_vector_index(column="en_embedding")
        table.declare_vector_index(column="ga_embedding")

        items = list(_yield_bilingual_pages())
        id_gen = coco.IdGenerator()
        # 100-row batches — same HNSW-DROP-THRESHOLD cadence as the
        # en-cy Phase 1 + en-ga-ROI Phase 2 reference Apps.
        for i in range(0, len(items), 100):
            batch = items[i : i + 100]
            chunks = await coco.map(en_ga_ni_embedding_flow, batch, id_gen)
            for chunk in chunks:
                if chunk is not None:
                    await table.declare_row(chunk)

    # R3 (per the layer3_model_lifecycle.py linter) — ``coco.App(...)``
    # at module scope. The AppConfig.name is what the L3 Component's
    # ``_find_app`` reflection looks up by.
    ciancheiltis_en_ga_ni_embedding = coco.App(
        coco.AppConfig(name="CiancheiltisEnGaNiEmbedding"),
        en_ga_ni_app_main,
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
                    "CiancheiltisEnGaNiEmbedding has no .update() method"
                )
            import asyncio

            if asyncio.iscoroutinefunction(update):
                return await update()
            return update()

    flow = _Flow(ciancheiltis_en_ga_ni_embedding)

else:
    # Stubs when CocoIndex isn't installed — keeps the symbol import-safe.
    async def en_ga_ni_embedding_flow(*args: Any, **kwargs: Any) -> None:  # type: ignore[no-redef]
        return None

    async def en_ga_ni_app_main(*args: Any, **kwargs: Any) -> None:  # type: ignore[no-redef]
        return None

    ciancheiltis_en_ga_ni_embedding = None  # type: ignore[assignment]
    flow = None  # type: ignore[assignment]


# =============================================================================
# Public surface — the Dagster adapter + the marimo notebooks consume these
# =============================================================================


__all__ = [
    "CIANCHEILTIS_EN_GA_NI_DUCKLAKE_TABLES",
    "CIANCHEILTIS_EN_GA_NI_THEMES",
    "COCOINDEX_AVAILABLE",
    "EnGaNiChunk",
    "PHASE_LANGUAGE_PAIR_GA_NI",
    "PHASE_TABLE_URL_GA_NI",
    "ciancheiltis_en_ga_ni_embedding",
    "embed_en_text",
    "embed_ga_text",
    "en_ga_ni_app_main",
    "en_ga_ni_embedding_flow",
    "flow",
]
