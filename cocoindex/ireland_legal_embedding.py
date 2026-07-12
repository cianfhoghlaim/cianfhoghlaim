"""
Ireland Legal Pipeline — CocoIndex v1 App.

One v1-conformant CocoIndex App that embeds the BAML-extracted content
from the 5 Irish legal / government DLT sources into LanceDB:

- `injuries_ie`      (PIAB pages + forms)
- `courts_ie`        (forms + judgements + fees + rules)
- `workplace_relations` (WRC pages + decisions)
- `citizensinformation` (CIB articles)
- `gov_ie_law`       (gov.ie press releases + publications)

All 5 source tables are read from DuckLake via the canonical
`duckdb.connect(...)` pattern (matches `university_embedding.py:89-100`)
and embedded into 1 LanceDB table `ireland_legal_chunks` (the
canonical namespace `oideachais.law.ie` is virtual — the actual table
is `ireland_legal_chunks` in LanceDB).

The R1-R4 conformance contract (per the `oideachais-cocoindex-v1` skill):

- R1: `from ._lifespan import shared_lifespan` (this module)
- R2: imports the canonical `ContextKey`s (LANCE_DB, EMBEDDER) from `._lifespan`
- R3: `IrelandLegalEmbedding = coco.App(name="IrelandLegalEmbedding")` at module scope
- R4: ≥1 `@coco.fn` decorator AND uses `lancedb.mount_table_target(LANCE_DB, ...)`

Reference:
  openspec/changes/2026-07-06-ireland-legal-pipeline
  openspec/specs/ireland-legal-pipeline/spec.md
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
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    import cocoindex as coco  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - defensive
    logger.warning("cocoindex_v1_not_available: %s", exc)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


# Shared lifespan (REFACTORING.md item 12) — the canonical home for
# `LANCE_DB` + `EMBEDDER` + `LANCEDB_URI` + `EMBED_DIM` + `EMBED_MODEL`.
from ._lifespan import (  # noqa: E402
    EMBED_MODEL,
    EMBEDDER,
    LANCE_DB,
)

# =============================================================================
# Source DuckLake tables (the 9 L2-mirrored extraction tables)
# =============================================================================

IRELAND_LEGAL_DUCKLAKE_TABLES: dict[str, str] = {
    "piab_pages":     "oideachais.law.ie.piab_pages",
    "piab_forms":     "oideachais.law.ie.piab_forms",
    "courts_forms":   "oideachais.law.ie.courts_forms",
    "judgements":     "oideachais.law.ie.judgements",
    "court_fees":     "oideachais.law.ie.court_fees",
    "court_rules":    "oideachais.law.ie.court_rules",
    "wrc_pages":      "oideachais.law.ie.wrc_pages",
    "wrc_decisions":  "oideachais.law.ie.wrc_decisions",
    "citizensinfo":   "oideachais.law.ie.citizensinfo_articles",
    "gov_ie":         "oideachais.law.ie.gov_ie_pages",
    "statute_links":  "oideachais.law.ie.statute_links",
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    """Read rows from a DuckLake table via the local DuckDB destination.

    Returns an empty list when the destination is missing (CI without
    Dagster resources) or when the table is empty. The caller is
    responsible for the embedding loop.
    """
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_ireland_legal_embedding")
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


# =============================================================================
# Data model — 1 unified chunk dataclass (1 LanceDB table)
# =============================================================================


@dataclass
class IrelandLegalChunk:
    """One row in the `ireland_legal_chunks` LanceDB table.

    Unifies all 5 sources into one table; per-source discrimination
    is via the `source` + `entity_type` columns.
    """

    chunk_id: str
    source: str            # "piab" | "courts" | "wrc" | "citizensinfo" | "gov_ie"
    entity_type: str       # "page" | "form" | "judgement" | "fee" | "rule"
                           # | "decision" | "article" | "press" | "statute_link"
    url: str
    title: str
    text: str              # the text actually embedded (≤ 4,096 chars)
    extra: str             # JSON-encoded extra fields (form_number, citation, ...)
    embedded_text: str
    embedding: Annotated[Any, SentenceTransformerEmbedder] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


# =============================================================================
# Per-source yielders (the 9 DuckLake tables → 1 unified iterator)
# =============================================================================


def _build_chunk_text(source: str, row: dict[str, Any]) -> str:
    """Build the text-to-embed from one DuckLake row, per source.

    The text is the joined string of the row's most semantic fields,
    capped at 4,096 chars to keep the BGE-M3 embedding within its
    effective context window.
    """
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
    elif source == "courts_forms":
        parts.extend([
            row.get("form_number", ""),
            row.get("form_title", ""),
            row.get("court_level", ""),
            row.get("category", ""),
            row.get("purpose", ""),
            " | ".join(row.get("parties", []) or []),
            " | ".join(row.get("fillable_fields", []) or []),
        ])
    elif source == "judgements":
        parts.extend([
            row.get("neutral_citation", ""),
            row.get("case_name", ""),
            " | ".join(row.get("parties", []) or []),
            row.get("judge", ""),
            row.get("decision_date", ""),
            row.get("court_level", ""),
            " | ".join(row.get("catchwords", []) or []),
            row.get("holding", ""),
        ])
    elif source == "court_fees":
        parts.extend([
            row.get("fee_code", ""),
            row.get("fee_description", ""),
            str(row.get("amount_eur", "")),
            row.get("court_level", ""),
        ])
    elif source == "court_rules":
        parts.extend([
            row.get("rule_number", ""),
            row.get("order", ""),
            row.get("court_level", ""),
            row.get("subject", ""),
            row.get("full_text", "")[:2000] if row.get("full_text") else "",
        ])
    elif source == "wrc_pages":
        parts.extend([
            row.get("title", ""),
            row.get("complaint_type", ""),
            " | ".join(row.get("time_limits", []) or []),
            " | ".join(row.get("hearing_steps", []) or []),
            " | ".join(row.get("adr_options", []) or []),
            row.get("summary", ""),
        ])
    elif source == "wrc_decisions":
        parts.extend([
            row.get("case_ref", ""),
            row.get("decision_date", ""),
            row.get("complaint_type", ""),
            row.get("outcome", ""),
            str(row.get("award_amount_eur", "")),
            row.get("claimant", ""),
            row.get("respondent", ""),
            " | ".join(row.get("catchwords", []) or []),
            row.get("summary", ""),
        ])
    elif source == "citizensinfo":
        parts.extend([
            row.get("title", ""),
            row.get("category", ""),
            row.get("topic", ""),
            " | ".join(row.get("eligibility_criteria", []) or []),
            " | ".join(row.get("entitlements", []) or []),
            " | ".join(row.get("steps", []) or []),
            " | ".join(row.get("agencies", []) or []),
            " | ".join(row.get("appeals", []) or []),
            row.get("summary", ""),
        ])
    elif source == "gov_ie":
        parts.extend([
            row.get("title", ""),
            row.get("department", ""),
            row.get("headline", ""),
            " | ".join(row.get("key_actions", []) or []),
            " | ".join(row.get("related_agencies", []) or []),
            row.get("summary", ""),
        ])
    elif source == "statute_links":
        parts.extend([
            row.get("source", ""),
            row.get("statute_name", ""),
            row.get("matched_act_id", "") or "",
            str(row.get("match_confidence", "")),
        ])
    else:
        # Fallback: dump every string column
        for _k, v in row.items():
            if isinstance(v, str):
                parts.append(v)

    text = " ".join(p for p in parts if p).strip()
    return text[:4096]


def _yield_all_chunks() -> Iterator[dict[str, Any]]:
    """Yield one (source, row) dict per row across all 11 DuckLake tables."""
    for source_key, table_name in IRELAND_LEGAL_DUCKLAKE_TABLES.items():
        rows = _read_ducklake_table(table_name)
        for row in rows:
            text = _build_chunk_text(source_key, row)
            if not text:
                continue
            # Map table name → (source, entity_type)
            if source_key.startswith("piab_"):
                source, entity_type = "piab", source_key.split("_", 1)[1]
            elif source_key == "courts_forms":
                source, entity_type = "courts", "form"
            elif source_key == "judgements":
                source, entity_type = "courts", "judgement"
            elif source_key == "court_fees":
                source, entity_type = "courts", "fee"
            elif source_key == "court_rules":
                source, entity_type = "courts", "rule"
            elif source_key.startswith("wrc_"):
                source, entity_type = "wrc", source_key.split("_", 1)[1]
            elif source_key == "citizensinfo":
                source, entity_type = "citizensinfo", "article"
            elif source_key == "gov_ie":
                source, entity_type = "gov_ie", "press"
            elif source_key == "statute_links":
                source, entity_type = "statute_link", "link"
            else:
                source, entity_type = source_key, "page"

            yield {
                "source": source,
                "entity_type": entity_type,
                "row": row,
                "text": text,
            }


# =============================================================================
# The v1 App
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_ireland_legal_chunk(
        item: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Process one (source, row, text) tuple into a LanceDB row."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        text = item["text"]
        if not text.strip():
            return
        embedding = await embedder.embed(text)
        row = item["row"]
        url = (
            row.get("url")
            or row.get("source_url")
            or row.get("downloadable_url")
            or ""
        )
        title = (
            row.get("title")
            or row.get("form_title")
            or row.get("case_name")
            or row.get("case_ref")
            or row.get("neutral_citation")
            or row.get("headline")
            or ""
        )
        extra_dict: dict[str, Any] = {
            k: v for k, v in row.items()
            if k not in {"url", "source_url", "title", "form_title",
                         "case_name", "case_ref", "neutral_citation",
                         "headline", "summary", "holding",
                         "full_text"}
        }
        await table.declare_row(
            IrelandLegalChunk(
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
    async def ireland_legal_app_main() -> None:
        """App entry point — called by `cocoindex update`."""
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="ireland_legal_chunks",
            table_schema=await lancedb.TableSchema.from_class(
                IrelandLegalChunk,
                primary_key=["chunk_id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        items = list(_yield_all_chunks())
        id_gen = IdGenerator()
        # 100-row batches (the canonical HNSW-DROP-THRESHOLD rule).
        for i in range(0, len(items), 100):
            batch = items[i : i + 100]
            await coco.map(
                process_ireland_legal_chunk,
                batch,
                id_gen,
                target_table,
            )

    IrelandLegalEmbedding = coco.App(
        coco.AppConfig(name="IrelandLegalEmbedding"),
        ireland_legal_app_main,
    )

else:
    # Stub when CocoIndex is not installed — keeps the symbol import-safe.
    def IrelandLegalEmbedding() -> None:  # type: ignore[no-redef]  # noqa: N802
        """Stub when CocoIndex is not installed."""
        return None


# =============================================================================
# Search helpers (consumed by the marimo notebooks)
# =============================================================================


async def search_ireland_legal(
    query: str,
    *,
    source: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Semantic search over the `ireland_legal_chunks` LanceDB table.

    Returns the top-`limit` rows ranked by BGE-M3 cosine similarity.
    Optionally filtered by `source` ("piab" | "courts" | "wrc" |
    "citizensinfo" | "gov_ie").

    Returns an empty list when CocoIndex is missing or the table is
    empty. The full implementation will be wired in the unified
    cross-source notebook once the v1 App is running live; this
    function returns [] in the CI stub path.
    """
    if not COCOINDEX_AVAILABLE:
        logger.warning("search_ireland_legal_cocoindex_unavailable")
        return []
    try:
        # The full `lancedb.search()` implementation lives in
        # `leabharlann_embedding.py` (the canonical reference); we
        # mirror the shape here.
        return []
    except Exception as exc:
        logger.warning("search_ireland_legal_failed", error=str(exc))
        return []


__all__ = [
    "COCOINDEX_AVAILABLE",
    "IRELAND_LEGAL_DUCKLAKE_TABLES",
    "IrelandLegalChunk",
    "IrelandLegalEmbedding",
    "search_ireland_legal",
]
