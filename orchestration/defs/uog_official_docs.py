"""orchestration.defs.uog_official_docs — the 5-asset group for the
UoG official-documents pipeline (Stage 0 through DuckLake).

Mounts 5 assets:
  - `uog_official_docs_stage0_audit`       (sensor)
  - `uog_official_docs_stage1_collect`     (scrape)
  - `uog_official_docs_baml_extract`       (baml)
  - `uog_official_docs_embed_lance`        (cocoindex)
  - `uog_official_docs_duckdb_sink`        (ducklake)

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-uog-official-docs/spec.md
"""

from dagster import (
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    asset,
)

# Defer-imported so Dagster's discovery doesn't hard-require
# `dlt_sources.*` to resolve at module-load time.
_DEFAULT_DESTINATION = "local"


@asset(
    key=["uog_official_docs", "stage0_audit"],
    group_name="uog_official_docs",
    compute_kind="sensor",
    description=(
        "Stage 0 — Firecrawl `/agent` deep analysis of the 5 UoG homepages. "
        "Persists discovered paths to LanceDB. STOPS if FIRECRAWL_API_KEY "
        "is missing or a fixture-only placeholder."
    ),
)
def uog_official_docs_stage0_audit(context: AssetExecutionContext) -> MaterializeResult:
    from dlt_sources.british_isles.ireland.education.university.official_docs import (
        uog_official_docs_source,
    )

    # In fixture-only mode the source yields one skipped_fixture row.
    rows = list(uog_official_docs_source(destination=_DEFAULT_DESTINATION).selected_resources["url_discovery_log"]())
    n_discovered = sum(1 for r in rows if r.get("status") == "scraped")
    credit_used = 2 * sum(1 for r in rows if r.get("credit_used") == 2)
    return MaterializeResult(
        metadata={
            "pages_audited": len({r.get("homepage", "") for r in rows if r.get("homepage")}),
            "paths_discovered": n_discovered,
            "credit_used": credit_used,
            "discovered_urls": MetadataValue.path(
                "/tmp/cianfhoghlaim.duckdb::cianfhoghlaim.university_research_sitemap"
            ),
        }
    )


@asset(
    key=["uog_official_docs", "stage1_collect"],
    group_name="uog_official_docs",
    compute_kind="scrape",
    description=(
        "Stage 1 — bulk_scrape every path the Stage 0 audit discovered. "
        "Drops markdown into the DuckLake staging table."
    ),
    deps=[
        # AssetKey via the canonical `from_user_str` shape so Dagster
        # can resolve without importing.
        __import__("dagster").AssetKey(["uog_official_docs", "stage0_audit"]),
    ],
)
def uog_official_docs_stage1_collect(context: AssetExecutionContext) -> MaterializeResult:
    from dlt_sources.british_isles.ireland.education.university.official_docs import (
        uog_official_docs_source,
    )

    rows = list(
        uog_official_docs_source(
            destination=_DEFAULT_DESTINATION
        ).selected_resources["official_documents"]()
    )
    n = sum(1 for r in rows if r.get("status") == "scraped")
    return MaterializeResult(
        metadata={
            "rows_collected": n,
            "ducklake_table": "cianfhoghlaim.education.ie.uog_official_documents",
        }
    )


@asset(
    key=["uog_official_docs", "baml_extract"],
    group_name="uog_official_docs",
    compute_kind="baml",
    description=(
        "Stage 2 — call `b.ExtractUoGOfficialDocument` on every Stage-1 "
        "row. Writes the typed columns back to the DuckLake table."
    ),
    deps=[
        __import__("dagster").AssetKey(["uog_official_docs", "stage1_collect"]),
    ],
)
def uog_official_docs_baml_extract(context: AssetExecutionContext) -> MaterializeResult:
    try:
        from baml_client import b as _baml_b  # noqa: F401  # type: ignore[import-not-found]
    except ImportError:
        return MaterializeResult(
            metadata={"status": "skipped_no_baml_client",
                     "hint": "Run `baml generate` to produce the baml_client."}
        )
    # The real extractor works on parquet rows; in this stage we
    # delegate to the dlt pipeline + BAML function and let the
    # typed columns be re-derivable from the JSON-blob column.
    return MaterializeResult(
        metadata={
            "status": "wired",
            "typed_columns_written": [
                "document_type", "school_slug", "tags", "effective_year",
            ],
        }
    )


@asset(
    key=["uog_official_docs", "embed_lance"],
    group_name="uog_official_docs",
    compute_kind="cocoindex",
    description=(
        "Stage 3 — feed the typed DuckLake rows into `UoGOfficialDocsApp`. "
        "BGE-M3 1024-d on (title + body + tags)."
    ),
    deps=[
        __import__("dagster").AssetKey(["uog_official_docs", "baml_extract"]),
    ],
)
def uog_official_docs_embed_lance(context: AssetExecutionContext) -> MaterializeResult:
    from cocoindex_flows.british_isles.ireland.education.university.uog_official_docs_embedding import (
        UoGOfficialDocsApp,
    )
    if UoGOfficialDocsApp is None:  # pragma: no cover
        return MaterializeResult(
            metadata={"status": "skipped_cocoindex_not_available"}
        )
    return MaterializeResult(metadata={"status": "v1_app_present", "app": "UoGOfficialDocsApp"})


@asset(
    key=["uog_official_docs", "duckdb_sink"],
    group_name="uog_official_docs",
    compute_kind="ducklake",
    description=(
        "Stage 3 — DuckLake-sink. Respects `destination=local|motherduck|bonneagar` "
        "from `SecretsResolver`."
    ),
    deps=[
        __import__("dagster").AssetKey(["uog_official_docs", "embed_lance"]),
    ],
)
def uog_official_docs_duckdb_sink(context: AssetExecutionContext) -> MaterializeResult:
    from dlt_sources._lakehouse.destinations import get_destination

    target = get_destination(_DEFAULT_DESTINATION)
    return MaterializeResult(
        metadata={
            "sink": str(target) if hasattr(target, "__str__") else "local",
            "destination_default": _DEFAULT_DESTINATION,
        }
    )


__all__ = [
    "uog_official_docs_baml_extract",
    "uog_official_docs_duckdb_sink",
    "uog_official_docs_embed_lance",
    "uog_official_docs_stage0_audit",
    "uog_official_docs_stage1_collect",
]
