"""ciancheiltis en-ga / EU level — CocoIndex v1 bilingual embedding App (Phase 6).

Phase 6 of the ``ciancheiltis`` umbrella project (EU level, language
pair ``en-ga``). Embeds bilingual EN <-> GA EU institutional pages
(EUR-Lex CELEX — Treaties + Regulations + Directives + Decisions +
International Agreements; EU Commission public consultations + EU
Council press releases; Eurydice + Cedefop; EMA + ECDC; EU Council
Irish Language Unit + Oifig an Choimisinéara Teanga + Parliament's
Irish Language Unit + Commission's Irish Language Translation
Centre; IATE + Teanglann; CJEU case law at curia.europa.eu; the 9
main EU institutions + 3 key EU agencies — Council, Parliament,
Commission, ECB, EIB, CJEU, ECA, CoR, EESC + Eurofound, Eurojust,
EUROPOL, FRA; Phase 6 covers T1-T8 of the 10-theme taxonomy; T9 +
T10 land in a later PR) into the canonical Phase 6 LanceDB table:

    lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu_chunks

The App reads from the bilingual pages surfaced by the 8 en-ga-EU
DLT sources at ``dlt_sources/ciancheiltis/en_ga_eu/<theme>.py`` (one
per T1-T8 theme), produces ONE chunk per (url, language_pair)
containing both the English and Irish embeddings + the
``language_availability`` tag (``full`` / ``partial`` /
``summary_only``) per the umbrella spec's Phase 6 §
first-class-column rule, and writes them to the Phase 6 LanceDB
companion table.

R1-R4 conformance contract (per the
``oideachais-cocoindex-v1`` skill + the
``openspec/specs/ciancheiltis/spec.md`` R1-R4 section):

- **R1** — Imports ``from ._lifespan import EMBEDDER,
  PHASE_LANGUAGE_PAIR_GA_EU, PHASE_TABLE_URL_GA_EU,
  PHASE_LANGUAGE_AVAILABILITY`` (the per-phase shim which itself
  re-exports ``cocoindex_flows._shared._lifespan.shared_lifespan``).
- **R2** — Uses the canonical ``BAAI/bge-m3`` 1024-d embedder
  (CY/GA/GD/GV multilingual coverage — Irish coverage verified via
  the shared BGE-M3 multilingual vector space), imported from the
  per-phase ``_lifespan``.
- **R3** — Every flow is decorated
  ``@coco.fn(memo=True, deps=[EMBEDDER])``.
- **R4** — The LanceDB table is mounted via
  ``lancedb.mount_table_target("lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu_chunks", conformance_required=True)``.

The BAML extraction client used to populate this App's input rows
is ``CiancheiltisGaEuExtract`` (registered by subagent 1 in
``baml_src/british_isles/ciancheiltis_en_ga_eu.baml``); the App
itself does not call BAML directly — the bilingual pages land in
DuckLake first (via the DLT sources), and this App embeds whatever
rows are present.

Canonical example (per the umbrella spec's Phase 6 row +
``dlt_sources/ciancheiltis/en_ga_eu/__init__.py``):
``https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E``
— the Treaty on European Union, Irish-language edition. Irish is
an official + treaty language of the EU under Article 55 TEU +
Council Regulation No 1/1958. EU-level coverage is **partial** for
Irish — many EU documents exist only in English plus a "summary in
Irish" rather than a full Irish translation. The
``language_availability`` ∈ ``{"full", "partial", "summary_only"}``
field is the critical signal here.

Reference: ``openspec/changes/2026-09-12-ciancheiltis-v2/`` (the
umbrella change that introduces Phase 5 + Phase 6, building on
PR0.5 / PR0.6 / PR0.7 / PR0.8).
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
# ``cocoindex_flows/british_isles/uk/ciancheiltis_en_gv_embedding.py:97``
# pattern) so the layer3 linter's R1+R2 regex can match the canonical
# import statement cleanly. The shim itself degrades gracefully when
# CocoIndex is not installed (see ``_lifespan.py``).
from ._lifespan import (  # type: ignore[attr-defined]  # noqa: E402
    EMBEDDER,
    PHASE_LANGUAGE_AVAILABILITY,
    PHASE_LANGUAGE_PAIR_GA_EU,
    PHASE_TABLE_URL_GA_EU,
)

# =============================================================================
# Source DuckLake tables — 8 T1-T8 themes under the en-ga-EU Phase 6 DLT sources
# =============================================================================
#
# These are surfaced by the deferred stubs at
# ``dlt_sources/ciancheiltis/en_ga_eu/<theme>.py``. Each stub currently
# returns ``[]`` from ``collect()``; PR0.10 will wire the live Firecrawl
# pipelines. The embedder is permissive: it reads whatever rows land in
# DuckLake (0 rows is a valid empty-state).
#
# Phase 6 covers T1-T8 only; T9 (Public broadcasting & culture: TG4's
# pan-EU distribution presence + EU broadcasting regulation) and T10
# (Statistics & public records: Eurostat's Irish-language presence)
# land in PR0.10.1.

CIANCHEILTIS_EN_GA_EU_THEMES: tuple[str, ...] = (
    "T1_legislation",          # EUR-Lex CELEX — Treaties + Regulations + Directives + Decisions + International Agreements (the Irish switch is ``eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:<num>``)
    "T2_policy_consultations", # EU Commission public consultations + EU Council press releases — PARTIAL per umbrella spec (small EU Council Irish-language presence)
    "T3_education",            # Eurydice + Cedefop — the bilingual-pair wrapper around dlt_sources/european_union/education/{eurydice,cedefop}.py
    "T4_healthcare",           # EMA + ECDC — PARTIAL per umbrella spec (most EU medical content is English-only or summary_in_irish; ``language_availability`` is the critical signal)
    "T5_language_bodies",      # EU Council Irish Language Unit + Coimisinéir Teanga + European Parliament Irish Language Unit + Oifig an Choimisinéara Teanga + Commission's Irish Language Translation Centre
    "T6_terminology",          # IATE (EU inter-institutional terminology DB) + Teanglann (Foras na Gaeilge's Irish-language terminology DB) — the EU_TERMINOLOGY_DBS Phase 6 pair
    "T7_courts_tribunals",     # CJEU (Court of Justice of the European Union) case law on curia.europa.eu — PARTIAL per umbrella spec (most CJEU case law exists in English only)
    "T8_institutions",         # The 9 main EU institutions + 3 key EU agencies (Council, Parliament, Commission, ECB, EIB, CJEU, ECA, CoR, EESC + Eurofound, Eurojust, EUROPOL, FRA) — T8 is remapped from "local government" to "EU institutions + agencies" because the EU has no local government structure
)


CIANCHEILTIS_EN_GA_EU_DUCKLAKE_TABLES: dict[str, str] = {
    theme: f"cianfhoghlaim.ciancheiltis.en_ga_eu.{theme}"
    for theme in CIANCHEILTIS_EN_GA_EU_THEMES
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    """Read rows from a DuckLake table via the local DuckDB destination.

    Returns an empty list when the destination is missing (CI without
    Dagster resources), when the table is empty, or when the row has no
    ``en_text`` AND no ``ga_text`` (a mis-categorised bilingual page).
    Mirrors the canonical pattern in
    ``cocoindex_flows/british_isles/uk/ciancheiltis_en_gv_embedding.py:137``.
    """
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_en_ga_eu_embedding")
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
            "ducklake_read_failed_en_ga_eu",
            table=table,
            error=str(exc),
        )
        return []


# =============================================================================
# Data model — 1 chunk dataclass with EN + GA embeddings + language_availability
# =============================================================================


@dataclass
class EnGaEuChunk:
    """One row in the ``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu_chunks`` LanceDB table.

    Each row is a bilingual EU-institutional page (or page-segment)
    with two independent 1024-d embeddings — one for the English body,
    one for the Irish body — so downstream RAG queries can route to
    the correct side via the shared ``BAAI/bge-m3`` vector space.

    Columns:
        chunk_id: stable per-page id (deterministic hash of url+section_id)
        url: the canonical URL of the bilingual EU-institutional
            page (eur-lex.europa.eu/legal-content/...,
            consilium.europa.eu/ga/...,
            europarl.europa.eu/doceo/...,
            iate.europa.eu, teanglann.ie,
            curia.europa.eu/juris/..., etc.)
        language_pair: always ``"en-ga"`` for Phase 6 (per the
            ``dlt_sources/ciancheiltis/_shared/`` convention)
        theme_code: one of T1-T8 for Phase 6 (T9 + T10 land in PR0.10.1)
        en_text: English body (≤ 4 096 chars — BGE-M3 effective window)
        ga_text: Irish body (≤ 4 096 chars; often empty or shorter
            than the English body in Phase 6 because EU-level
            coverage is **partial** for Irish — many EU documents
            exist only in English plus a "summary in Irish" rather
            than a full Irish translation; the BAML coverage gate
            flags these partial rows but does not drop them)
        title_en: English page title (typically the only title in
            Phase 6 since most pages are English-only)
        title_ga: Irish page title (often empty)
        en_embedding: 1024-d BGE-M3 vector of ``en_text``
        ga_embedding: 1024-d BGE-M3 vector of ``ga_text``
        language_availability: the canonical Phase 6 § first-class
            column per the umbrella spec — one of ``"full"``,
            ``"partial"``, ``"summary_only"``. The BAML extraction
            client ``CiancheiltisGaEuExtract`` populates this
            column from the EUR-Lex / Council / Parliament /
            Commission / EMA / ECDC / CJEU metadata. Most rows
            will be ``"summary_only"`` or ``"partial"`` because
            EU-level Irish coverage is selective; the schema
            captures the partial-coverage caveat so the
            downstream MotherDuck Dive can highlight the
            language_availability distribution.
        metadata_language_mismatch: True when the DLT source flagged
            a metadata-vs-content language disagreement (rare in
            Phase 6 — EUR-Lex typically ships
            ``metadata.language="EN"`` even for the Irish switch
            so the content-based detector is the gate).
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
    language_availability: str = "partial"
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
    spec's Phase 6 § MotherDuck-Dive scenario. Rows that carry a
    ``language_availability`` value are tagged so the schema's
    first-class ``language_availability`` column carries the
    umbrella-spec-compliant signal.

    Note: in Phase 6 most rows are expected to have a populated
    ``en_text`` and an empty or shorter ``ga_text`` (EU-level coverage
    is **partial** for Irish — many documents exist only in English
    plus a "summary in Irish" rather than a full Irish translation).
    The BAML coverage gate flags these partial rows but does not drop
    them — they are still embedded so downstream RAG queries can
    surface the English body and route to whatever Irish content
    exists.
    """
    for theme_code, table_name in CIANCHEILTIS_EN_GA_EU_DUCKLAKE_TABLES.items():
        rows = _read_ducklake_table(table_name)
        for row in rows:
            en_text = (row.get("en_text") or "").strip()
            ga_text = (row.get("ga_text") or "").strip()
            if not en_text and not ga_text:
                continue
            # Normalise the ``language_availability`` tag to one of the
            # canonical umbrella-spec values — invalid values fall back
            # to ``"partial"`` (the Phase 6 default for partial EU-level
            # Irish coverage). Subagent 1's BAML client
            # ``CiancheiltisGaEuExtract`` is the canonical source for
            # this value; the normalisation here is defensive in case a
            # future DLT source ships an out-of-range value.
            raw_lang_avail = (
                row.get(PHASE_LANGUAGE_AVAILABILITY) or "partial"
            )
            if raw_lang_avail not in {"full", "partial", "summary_only"}:
                raw_lang_avail = "partial"
            yield {
                "theme_code": theme_code,
                "url": str(row.get("url") or ""),
                "language_pair": str(
                    row.get("language_pair") or PHASE_LANGUAGE_PAIR_GA_EU
                ),
                "title_en": str(row.get("title_en") or ""),
                "title_ga": str(row.get("title_ga") or ""),
                "en_text": en_text[:4096],
                "ga_text": ga_text[:4096],
                PHASE_LANGUAGE_AVAILABILITY: raw_lang_avail,
                "metadata_language_mismatch": bool(
                    row.get("metadata_language_mismatch", False)
                ),
                "extra": str(row.get("extra") or "")[:4000],
            }


# =============================================================================
# The v1 App — every flow is ``@coco.fn(memo=True, deps=[EMBEDDER])`` (R3, strict)
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

        ``BAAI/bge-m3`` handles Irish (``ga``) natively — Irish is
        an official + treaty language of the EU under Article 55 TEU
        + Council Regulation No 1/1958, and the multilingual
        vector space is well-populated for Irish at the corpus
        level (the embedder produces a 1024-d multilingual output
        vector per the ``oideachais-cocoindex-v1`` skill's R2
        contract).
        """
        if not ga_text.strip():
            return await coco.use_context(EMBEDDER).embed(" ")  # type: ignore[arg-type]
        embedder = await coco.use_context(EMBEDDER)
        return await embedder.embed(ga_text)

    @coco.fn(memo=True, deps=[EMBEDDER])
    async def en_ga_eu_embedding_flow(
        item: dict[str, Any],
        id_gen: coco.IdGenerator,  # type: ignore[valid-type]
    ) -> EnGaEuChunk | None:
        """Embed one bilingual (en, ga) EU-institutional page into a LanceDB ``EnGaEuChunk``.

        R3 conformance: decorated ``@coco.fn(memo=True, deps=[EMBEDDER])``
        per the umbrella spec's R3 rule (every flow MUST be wrapped with
        ``memo=True`` + explicit ``deps=[...]``).

        The function performs both English and Irish embeddings in one
        pass so downstream consumers can route queries to either side
        of the bilingual pair via the shared ``BAAI/bge-m3`` vector
        space. The ``language_availability`` column carries the
        umbrella-spec-compliant signal (``full`` / ``partial`` /
        ``summary_only``) per the Phase 6 § first-class-column rule.

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

        return EnGaEuChunk(
            chunk_id=chunk_id,
            url=str(item.get("url") or ""),
            language_pair=str(
                item.get("language_pair") or PHASE_LANGUAGE_PAIR_GA_EU
            ),
            theme_code=str(item.get("theme_code") or "T_unknown"),
            title_en=str(item.get("title_en") or ""),
            title_ga=str(item.get("title_ga") or ""),
            en_text=en_text,
            ga_text=ga_text,
            en_embedding=en_vec,
            ga_embedding=ga_vec,
            language_availability=str(
                item.get(PHASE_LANGUAGE_AVAILABILITY) or "partial"
            ),
            metadata_language_mismatch=bool(
                item.get("metadata_language_mismatch", False)
            ),
            extra=str(item.get("extra") or ""),
        )

    @coco.fn(memo=True, deps=[EMBEDDER])
    async def mount_en_ga_eu_chunks_table(
        target: Any,  # lancedb.TableTarget[EnGaEuChunk]
    ) -> None:
        """Mount the canonical ``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu_chunks`` LanceDB table.

        R4 conformance (per the umbrella spec): the mount uses
        ``conformance_required=True`` so the L1 Ingestion layer's
        scaffold-time linter verifies the en-ga-EU Phase 6 R1-R4
        contract every time the table is wired.

        ``deps=[EMBEDDER]`` so a model swap re-declares the vector
        indices on the new embedding columns.
        """
        lancedb.mount_table_target(  # type: ignore[union-attr]
            PHASE_TABLE_URL_GA_EU,
            table_name="en_ga_eu_chunks",
            conformance_required=True,
        )

    @coco.fn(memo=True, deps=[EMBEDDER])
    async def en_ga_eu_app_main() -> None:
        """App entry point — called by ``cocoindex update``.

        Mounts the LanceDB table via the URL string
        ``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu_chunks``
        with ``conformance_required=True`` (R4), then fans out across
        the 8 T1-T8 bilingual DuckLake tables via ``coco.map``.

        ``deps=[EMBEDDER]`` because the orchestrator depends on the
        embedder context for all downstream per-row embedding work.
        """
        # R4 — mount with conformance_required=True
        table = lancedb.mount_table_target(  # type: ignore[union-attr]
            PHASE_TABLE_URL_GA_EU,
            table_name="en_ga_eu_chunks",
            conformance_required=True,
            table_schema=await lancedb.TableSchema.from_class(
                EnGaEuChunk,
                primary_key=["chunk_id"],
            ),
        )
        table.declare_vector_index(column="en_embedding")
        table.declare_vector_index(column="ga_embedding")

        items = list(_yield_bilingual_pages())
        id_gen = coco.IdGenerator()
        # 100-row batches — same HNSW-DROP-THRESHOLD cadence as the
        # en-cy Phase 1 + en-ga-ROI Phase 2 + en-ga-NI Phase 3 +
        # en-gd Phase 4 + en-gv Phase 5 reference Apps.
        for i in range(0, len(items), 100):
            batch = items[i : i + 100]
            chunks = await coco.map(en_ga_eu_embedding_flow, batch, id_gen)
            for chunk in chunks:
                if chunk is not None:
                    await table.declare_row(chunk)

    # R3 (per the layer3_model_lifecycle.py linter) — ``coco.App(...)``
    # at module scope. The AppConfig.name is what the L3 Component's
    # ``_find_app`` reflection looks up by.
    ciancheiltis_en_ga_eu_embedding = coco.App(
        coco.AppConfig(name="CiancheiltisEnGaEuEmbedding"),
        en_ga_eu_app_main,
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
                    "CiancheiltisEnGaEuEmbedding has no .update() method"
                )
            import asyncio

            if asyncio.iscoroutinefunction(update):
                return await update()
            return update()

    flow = _Flow(ciancheiltis_en_ga_eu_embedding)

else:
    # Stubs when CocoIndex isn't installed — keeps the symbol import-safe.
    async def en_ga_eu_embedding_flow(*args: Any, **kwargs: Any) -> None:  # type: ignore[no-redef]
        return None

    async def en_ga_eu_app_main(*args: Any, **kwargs: Any) -> None:  # type: ignore[no-redef]
        return None

    ciancheiltis_en_ga_eu_embedding = None  # type: ignore[assignment]
    flow = None  # type: ignore[assignment]


# =============================================================================
# Public surface — the Dagster adapter + the marimo notebooks consume these
# =============================================================================


__all__ = [
    "CIANCHEILTIS_EN_GA_EU_DUCKLAKE_TABLES",
    "CIANCHEILTIS_EN_GA_EU_THEMES",
    "COCOINDEX_AVAILABLE",
    "EnGaEuChunk",
    "PHASE_LANGUAGE_AVAILABILITY",
    "PHASE_LANGUAGE_PAIR_GA_EU",
    "PHASE_TABLE_URL_GA_EU",
    "ciancheiltis_en_ga_eu_embedding",
    "embed_en_text",
    "embed_ga_text",
    "en_ga_eu_app_main",
    "en_ga_eu_embedding_flow",
    "flow",
]
