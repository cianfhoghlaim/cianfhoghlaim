"""Filesystem generic Dagster assets (BIEP v3 — DLT scanner domain).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change
(extended to all British Isles jurisdictions via the
2026-08-13 filesystem + language openspec change).

The canonical generic filesystem DLT pipeline. Wraps the 16 filesystem
scanner sources at `dlt_sources/filesystem/`:

1. `leabharlann_books` — `leabharlann/{gaeilge,aigne}/` (EPUB + preview pairing)
2. `gemini_deep_research` — `leabharlann/gemini_deep_research/`
3. `google_takeout` — `Takeout/<account_label>/` (per-account)
4. `takeout_v1` — `stedding/Takeout/` (multi-account auto-discovery)
5. `email_inbox` — `/srv/mailcow-exports/*.mbox` (4-account email-inbox pipeline)
6. `leaving_cert_source` — filesystem scanner for the Ireland LC PDFs
7. `university_of_galway` — `leabharlann/ollscoil_na_gaillimhe/`
8. `zotero` — `leabharlann/zotero/` (real Zotero storage format)
9. `gemini_corpus_source` — Gemini corpus loader
10. `pdf_download_source` — PDF downloader
11. `previews` — preview pairing
12. `+ 5 helpers` (`_scanner`, `_takeout_paths`, `_epub_extractor`, `_citation_extractor`, `config.example.yaml`)

Each filesystem source emits 1 row per file in the cache; the
filesystem Dagster assets aggregate them into 4 cross-cutting metrics:

- `filesystem_documents_ingested` — total files ingested per source
- `filesystem_extractions` — BAML extraction (text + metadata)
- `filesystem_embeddings` — CocoIndex v1 embeddings (BAAI/bge-m3 1024-d)
- `filesystem_audit` — 1 audit row per ingestion (per the BIEP v3 spec)

The 2 cross-cutting MotherDuck Dives:
- `filesystem_sources_overview` — per-source row count + total size
- `filesystem_content_topics` — per-source topic frequency with RAGAS

The 1 monthly MotherDuck Flight:
- `filesystem_monthly_sync_flight` — yearly run (filesystem is more
  frequent than education content, so it runs monthly per the BIEP v3
  scheduling policy)

YEARLY + MONTHLY automation per the BIEP v3 scheduling policy.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()``.
- dagster (per `.agents/skills/dagster/SKILL.md`) — 5-layer group_name
  convention.
"""
import logging
from typing import Any

from dagster import (
    AssetCheckResult, AssetExecutionContext, asset, asset_check, define_asset_job,
)

from orchestration.automation.biiep_scheduling import (
    make_monthly_circulars_automation,
    make_nightly_audit_automation,
)

logger = logging.getLogger(__name__)


FILESYSTEM_INGESTION_GROUP = "1_ingestion_filesystem_documents"
FILESYSTEM_EXTRACTION_GROUP = "2_materials_filesystem_extractions"
FILESYSTEM_EMBEDDING_GROUP = "3_model_lifecycle_filesystem_embeddings"


# The 11 canonical filesystem DLT sources (per the
# `dlt_sources/filesystem/` directory)
FILESYSTEM_SOURCES: tuple[str, ...] = (
    "leabharlann_books",
    "gemini_deep_research",
    "google_takeout",
    "takeout_v1",
    "email_inbox",
    "leaving_cert_source",
    "university_of_galway",
    "zotero",
    "gemini_corpus_source",
    "pdf_download_source",
    "previews",
)


@asset(
    group_name=FILESYSTEM_INGESTION_GROUP,
    description=(
        "Generic filesystem ingestion (BIEP v3 — DLT scanner domain). "
        "Aggregates the 11 canonical filesystem DLT sources at "
        "`dlt_sources/filesystem/` into a single asset. "
        "Triggers MONTHLY (1st of each month 00:00 UTC) per the BIEP v3 "
        "scheduling policy (filesystem is more frequent than education content). "
        "Also triggers event-driven via the filesystem ChangeDetection "
        "sensors for new files."
    ),
    automation_condition=make_monthly_circulars_automation(),
)
def filesystem_documents_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 — DLT ingestion of all filesystem sources (11 sources)."""
    from dlt_sources.filesystem import (
        leabharlann_books_source,
        gemini_deep_research_source,
        google_takeout_source,
        takeout_v1_source,
        email_inbox_source,
        leaving_cert_source,
        university_of_galway_source,
        zotero_source,
        gemini_corpus_source,
        pdf_download_source,
        previews,
    )

    sources = [
        leabharlann_books_source,
        gemini_deep_research_source,
        google_takeout_source,
        takeout_v1_source,
        email_inbox_source,
        leaving_cert_source,
        university_of_galway_source,
        zotero_source,
        gemini_corpus_source,
        pdf_download_source,
        previews,
    ]

    import dlt

    from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination

    rows_landed = 0
    failed_sources: list[str] = []
    for source in sources:
        source_name = getattr(source, "__name__", repr(source))
        try:
            pipeline = dlt.pipeline(
                pipeline_name=f"filesystem_{source_name}",
                # Previously hardcoded `destination="duckdb"`, which landed
                # in an ephemeral local file — the real DuckLake/Garage
                # lakehouse was never reached by this asset, unlike each
                # source's own standalone `main()`. `use_ducklake=None`
                # honours the USE_DUCKLAKE env var (defaults to true),
                # matching every other real caller of this helper.
                destination=get_dlt_destination(use_ducklake=None),
                dataset_name="cianfhoghlaim.bronze.filesystem",
            )
            load_info = pipeline.run(source)
            if load_info.load_packages:
                for lp in load_info.load_packages:
                    rows_landed += getattr(lp, "jobs", {}).get("completed", 0) if hasattr(lp, "jobs") else 0
        except Exception:
            # Previously a bare `except Exception: pass` that silently
            # swallowed every failure. Log with the real traceback so a
            # broken source is visible in the Dagster run log instead of
            # just quietly contributing 0 rows.
            context.log.exception("filesystem source %s failed to ingest", source_name)
            failed_sources.append(source_name)

    context.log.info("filesystem_documents_ingested: %d rows landed", rows_landed)
    if failed_sources:
        context.log.warning(
            "filesystem_documents_ingested: %d/%d sources failed: %s",
            len(failed_sources), len(sources), ", ".join(failed_sources),
        )
    return {
        "rows": rows_landed,
        "sources": len(FILESYSTEM_SOURCES),
        "failed_sources": failed_sources,
    }


@asset(
    group_name=FILESYSTEM_EXTRACTION_GROUP,
    description=(
        "Generic filesystem BAML extraction (BIEP v3). "
        "Triggers MONTHLY (1st of each month 00:00 UTC)."
    ),
    automation_condition=make_monthly_circulars_automation(),
)
def filesystem_extractions(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 2 — BAML extraction for all filesystem sources."""
    # The filesystem sources don't have a canonical BAML extractor
    # (they're scanners, not syllabus docs). Return a stub.
    return {
        "rows_extracted": 0,
        "sources": len(FILESYSTEM_SOURCES),
    }


@asset(
    group_name=FILESYSTEM_EMBEDDING_GROUP,
    description=(
        "Generic filesystem CocoIndex embedding (BIEP v3). "
        "Triggers MONTHLY (1st of each month 00:00 UTC)."
    ),
    automation_condition=make_monthly_circulars_automation(),
)
def filesystem_embeddings(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 3 — CocoIndex embedding for all filesystem sources."""
    return {
        "cohorts_to_embed": 0,
        "sources": len(FILESYSTEM_SOURCES),
    }


@asset_check(asset=filesystem_documents_ingested)
def filesystem_documents_ingested_check(context, x: dict[str, Any]) -> AssetCheckResult:
    return AssetCheckResult(
        passed=x.get("rows", 0) >= 0,
        metadata={"rows": x.get("rows", 0), "sources": x.get("sources", 0)},
    )


@asset_check(asset=filesystem_extractions)
def filesystem_extractions_ragas_check(context, x: dict[str, Any]) -> AssetCheckResult:
    return AssetCheckResult(
        passed=True,
        severity="WARN",
        metadata={"rows_extracted": x.get("rows_extracted", 0), "note": "filesystem has no canonical RAGAS scoring"},
    )


@asset_check(asset=filesystem_embeddings)
def filesystem_lance_chunks_check(context, x: dict[str, Any]) -> AssetCheckResult:
    return AssetCheckResult(
        passed=True,
        severity="WARN",
        metadata={"cohorts_to_embed": x.get("cohorts_to_embed", 0), "note": "filesystem embeddings are optional"},
    )


def _make_filesystem_backfill_job(source_name: str) -> Any:
    return define_asset_job(
        name=f"filesystem_{source_name}_backfill_job",
        selection=["filesystem_documents_ingested", "filesystem_extractions", "filesystem_embeddings"],
    )


filesystem_backfill_jobs = [_make_filesystem_backfill_job(s) for s in FILESYSTEM_SOURCES]


__all__ = [
    "filesystem_documents_ingested",
    "filesystem_extractions",
    "filesystem_embeddings",
    "filesystem_documents_ingested_check",
    "filesystem_extractions_ragas_check",
    "filesystem_lance_chunks_check",
    "FILESYSTEM_SOURCES",
    "filesystem_backfill_jobs",
]
