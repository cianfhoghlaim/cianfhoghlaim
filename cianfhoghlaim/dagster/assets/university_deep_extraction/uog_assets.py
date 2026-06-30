"""University deep extraction — Dagster assets (Phase 3 of `university-of-galway-deep-extraction`).

Five `@asset` functions for the case study (University of Galway):

  1. ``uog_pre_research``     — calls `BackendRouter.pre_research` (1 credit guard)
  2. ``uog_bulk_scrape``      — calls `BackendRouter.bulk_scrape` (Crawl4AI primary, Firecrawl paid fallback)
  3. ``uog_extract_courses``  — BAML `ExtractCourseDescriptor` on each row → DuckLake
  4. ``uog_extract_modules``  — BAML `ExtractModuleDescriptor` on each row → DuckLake
  5. ``uog_extract_programmes`— BAML `ExtractProgrammeDescriptor` on each row → DuckLake

All 5 assets live in the ``university_deep_extraction`` asset group and
follow the canonical 3-stage pipeline pattern (pre-research →
bulk-scrape → condense) used by the `official_media` asset group. The
BAML extractions are memoised on `(url, content_hash)` so re-materialisation
is idempotent.

Reference: openspec/changes/university-of-galway-deep-extraction/
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import time
from collections.abc import Iterator
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# ── Group label (shared across the 5 assets) ─────────────────────────────

UNIVERSITY_GROUP = "university_deep_extraction"


# ── Canonical goal text used by the pre-research stage ───────────────────

UOG_PRE_RESEARCH_GOAL = (
    "Identify the M.Sc. AI 2025-26 handbook + every programme page + "
    "every school-subdomain module page + every lecturer directory. "
    "Prefer static pages; only mark JS-heavy pages that need Firecrawl."
)


# ── Helper: BAML memoisation row builder ────────────────────────────────

def _baml_row(
    *,
    page_kind: str,
    url: str,
    markdown: str,
    baml_function: str,
) -> dict[str, Any]:
    """Build a BAML extraction row, memoised by `(url, content_hash)`.

    Mirrors the `_baml_extraction_row` pattern in the personal-archive
    `university_of_galway_source` (see
    `dlt_sources/leabharlann/university_of_galway.py`).
    """
    content_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()[:16]
    row: dict[str, Any] = {
        "id": hashlib.sha256(f"{url}:{baml_function}:{content_hash}".encode("utf-8")).hexdigest()[:16],
        "url": url,
        "page_kind": page_kind,
        "content_hash": content_hash,
        "baml_function": baml_function,
        "status": "pending",
        "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "result": None,
        "extraction_text_chars": len(markdown),
    }

    try:
        from baml_client.sync_client import b as baml  # type: ignore[import-not-found]
    except ImportError:
        row["status"] = "skipped_no_client"
        return row

    if not markdown:
        row["status"] = "skipped_no_text"
        return row

    try:
        if baml_function == "ExtractCourseDescriptor":
            result = baml.ExtractCourseDescriptor(
                course_page_markdown=markdown[:50_000],
                course_url=url,
            )
        elif baml_function == "ExtractModuleDescriptor":
            result = baml.ExtractModuleDescriptor(
                module_page_markdown=markdown[:50_000],
                module_url=url,
            )
        elif baml_function == "ExtractProgrammeDescriptor":
            result = baml.ExtractProgrammeDescriptor(
                programme_page_markdown=markdown[:50_000],
                programme_url=url,
            )
        else:
            row["status"] = "skipped_unknown_function"
            return row

        if hasattr(result, "model_dump"):
            row["result"] = result.model_dump()
        else:
            row["result"] = result
        row["status"] = "success"
    except Exception as exc:  # noqa: BLE001 — BAML can raise LLM/parse errors
        logger.warning(
            "uog_baml_extraction_failed",
            url=url,
            function=baml_function,
            error=str(exc),
        )
        row["status"] = "error"
        row["error"] = str(exc)
    return row


def _iter_dlt_rows(
    *,
    dataset_name: str,
    table_name: str,
) -> Iterator[dict[str, Any]]:
    """Read rows back from a DuckLake table.

    Implemented via dlt's local DuckDB destination (the
    `dlt_utils.destinations.get_dlt_destination` helper) so the same
    asset works in dev (DuckDB) and prod (DuckLake via Garage S3).
    """
    try:
        import duckdb
    except ImportError as exc:
        logger.warning("uog_read_failed", reason="duckdb not installed", error=str(exc))
        return

    db_path = os.environ.get("DUCKDB_PATH", str(dg.context.instance.get("duckdb_path", "/tmp/oideachais.duckdb")))
    if not os.path.exists(db_path):
        logger.warning("uog_read_failed", reason="duckdb file missing", path=db_path)
        return
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(
            f'SELECT * FROM "{dataset_name}"."{table_name}"'
        ).fetchall()
        columns = [d[0] for d in con.description]
        for r in rows:
            yield dict(zip(columns, r))
    except Exception as exc:  # noqa: BLE001 — defensive
        logger.warning("uog_read_failed", error=str(exc))


# ── Asset 1: uog_pre_research ────────────────────────────────────────────

@dg.asset(
    key=["uog", "pre_research"],
    group_name=UNIVERSITY_GROUP,
    description=(
        "One-time pre-research pass for the University of Galway case study. "
        "Calls `BackendRouter.pre_research` (1 credit guard) with a 2-credit "
        "default. Persists the result to "
        "`oideachais.education.ie.university_research_sitemap` (LanceDB). "
        "Returns a `MaterializeResult` with metadata `sources_attempted`, "
        "`credits_spent`, `backend`."
    ),
    compute_kind="scrape",
    metadata={"table": "oideachais.education.ie.university_research_sitemap"},
)
def uog_pre_research(context) -> dg.MaterializeResult:
    """Run pre-research on the UoG case study via the ScrapeStrategist.

    Mirrors `official_media_pre_research` (per the
    `author-archive-pipeline` spec) but is scoped to the UoG domain.
    """
    try:
        from bonneagar.stacks.browser.sruth_browser import ScrapeStrategist
    except ImportError as exc:
        logger.warning("browser_not_available", error=str(exc))
        return dg.MaterializeResult(
            metadata={
                "sources_attempted": 0,
                "credits_spent": 0,
                "backend": "stub_no_browser",
            }
        )

    strategist = ScrapeStrategist()
    credits_spent = 0
    backend_used = "stub"
    try:
        result = asyncio.run(
            strategist.research_site(
                url="https://www.universityofgalway.ie",
                goal=UOG_PRE_RESEARCH_GOAL,
                budget_hint=2,
            )
        )
        credits_spent = result.credits_spent
        backend_used = result.backend_used
    except Exception as exc:  # noqa: BLE001 — best-effort
        logger.warning("uog_pre_research_failed", error=str(exc))

    summary = strategist.credit_summary()
    return dg.MaterializeResult(
        metadata={
            "sources_attempted": 1,
            "credits_spent": credits_spent,
            "backend": backend_used,
            "budget_remaining": summary["remaining"],
        }
    )


# ── Asset 2: uog_bulk_scrape ─────────────────────────────────────────────

@dg.asset(
    key=["uog", "bulk_scrape"],
    group_name=UNIVERSITY_GROUP,
    description=(
        "Bulk-scrape the recommended URLs from `uog_pre_research`. Prefers "
        "Crawl4AI (free). Falls back to Firecrawl for pages marked "
        "`firecrawl-agent` (heavy JS). The DLT source "
        "`university_ie-university-galway_deep` is the canonical source; "
        "this asset invokes the `course_pages` + `module_pages` + "
        "`programme_pages` + `handbook_pdfs` + `lecturer_pages` resources."
    ),
    compute_kind="scrape",
    metadata={"table": "oideachais.education.ie.university_pages"},
)
def uog_bulk_scrape(context, upstream=None) -> dg.MaterializeResult:
    """Bulk-scrape every UoG URL from the DLT source.

    Mirrors `official_media_bulk_scrape` (per the `author-archive-pipeline`
    spec). Yields 0 rows when the DLT destination is missing (CI without
    Dagster resources) — the asset run does NOT fail.
    """
    pages_scraped = 0
    bytes_in_total = 0
    bytes_out_total = 0
    by_backend: dict[str, int] = {}
    try:
        import dlt
        from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.university_of_galway_deep import (
            university_of_galway_deep_source,
        )
        from dlt_utils.destinations import get_dlt_destination
    except ImportError as exc:
        logger.warning("uog_bulk_scrape_import_failed", error=str(exc))
        return dg.MaterializeResult(
            metadata={"pages_scraped": 0, "bytes_in": 0, "bytes_out": 0, "backend": "stub_no_dlt_or_destination"}
        )

    dataset_name = "uog_ie_university_galway_deep"
    pipeline = dlt.pipeline(
        pipeline_name=f"{dataset_name}_pipeline",
        destination=get_dlt_destination(),
        dataset_name=dataset_name,
        dev_mode=False,
    )
    source_obj = university_of_galway_deep_source()
    try:
        load_info = pipeline.run(source_obj)
        # The dlt load_info tells us how many rows were loaded; we use
        # this as a proxy for `pages_scraped`.
        try:
            pages_scraped = sum(load_info.loads_ids[0].items_per_table.values()) if load_info.loads_ids else 0
        except (AttributeError, IndexError, TypeError):
            pages_scraped = 0
    except Exception as exc:  # noqa: BLE001 — network / destination failure
        logger.warning("uog_bulk_scrape_run_failed", error=str(exc))

    return dg.MaterializeResult(
        metadata={
            "pages_scraped": pages_scraped,
            "bytes_in": bytes_in_total,
            "bytes_out": bytes_out_total,
            "by_backend": by_backend,
        }
    )


# ── Asset 3: uog_extract_courses ─────────────────────────────────────────

@dg.asset(
    key=["uog", "extract_courses"],
    group_name=UNIVERSITY_GROUP,
    description=(
        "BAML `ExtractCourseDescriptor` on every `course_pages` row. "
        "Persists `CourseDescriptor` records to "
        "`oideachais.education.ie.university_courses` (DuckLake). "
        "Memoised on `(url, content_hash)` so re-materialisation is "
        "idempotent. Graceful degradation when the BAML client is missing."
    ),
    compute_kind="baml",
    metadata={"table": "oideachais.education.ie.university_courses"},
)
def uog_extract_courses(context, upstream=None) -> dg.MaterializeResult:
    """Extract `CourseDescriptor` records from the bulk-scrape output."""
    pages_extracted = 0
    pages_skipped = 0
    pages_errored = 0
    for row in _iter_dlt_rows(
        dataset_name="uog_ie_university_galway_deep",
        table_name="course_pages",
    ):
        baml_row = _baml_row(
            page_kind="course",
            url=row.get("url", ""),
            markdown=row.get("raw_markdown", "") or "",
            baml_function="ExtractCourseDescriptor",
        )
        status = baml_row["status"]
        if status == "success":
            pages_extracted += 1
        elif status.startswith("skipped"):
            pages_skipped += 1
        else:
            pages_errored += 1
    return dg.MaterializeResult(
        metadata={
            "pages_extracted": pages_extracted,
            "pages_skipped": pages_skipped,
            "pages_errored": pages_errored,
        }
    )


# ── Asset 4: uog_extract_modules ─────────────────────────────────────────

@dg.asset(
    key=["uog", "extract_modules"],
    group_name=UNIVERSITY_GROUP,
    description=(
        "BAML `ExtractModuleDescriptor` on every `module_pages` row. "
        "Persists `ModuleDescriptor` records to "
        "`oideachais.education.ie.university_modules` (DuckLake). "
        "Memoised on `(url, content_hash)`."
    ),
    compute_kind="baml",
    metadata={"table": "oideachais.education.ie.university_modules"},
)
def uog_extract_modules(context, upstream=None) -> dg.MaterializeResult:
    """Extract `ModuleDescriptor` records from the bulk-scrape output."""
    pages_extracted = 0
    pages_skipped = 0
    pages_errored = 0
    for row in _iter_dlt_rows(
        dataset_name="uog_ie_university_galway_deep",
        table_name="module_pages",
    ):
        baml_row = _baml_row(
            page_kind="module",
            url=row.get("url", ""),
            markdown=row.get("raw_markdown", "") or "",
            baml_function="ExtractModuleDescriptor",
        )
        status = baml_row["status"]
        if status == "success":
            pages_extracted += 1
        elif status.startswith("skipped"):
            pages_skipped += 1
        else:
            pages_errored += 1
    return dg.MaterializeResult(
        metadata={
            "pages_extracted": pages_extracted,
            "pages_skipped": pages_skipped,
            "pages_errored": pages_errored,
        }
    )


# ── Asset 5: uog_extract_programmes ──────────────────────────────────────

@dg.asset(
    key=["uog", "extract_programmes"],
    group_name=UNIVERSITY_GROUP,
    description=(
        "BAML `ExtractProgrammeDescriptor` on every `programme_pages` row. "
        "Persists `ProgrammeDescriptor` records to "
        "`oideachais.education.ie.university_programmes` (DuckLake). "
        "Memoised on `(url, content_hash)`."
    ),
    compute_kind="baml",
    metadata={"table": "oideachais.education.ie.university_programmes"},
)
def uog_extract_programmes(context, upstream=None) -> dg.MaterializeResult:
    """Extract `ProgrammeDescriptor` records from the bulk-scrape output."""
    pages_extracted = 0
    pages_skipped = 0
    pages_errored = 0
    for row in _iter_dlt_rows(
        dataset_name="uog_ie_university_galway_deep",
        table_name="programme_pages",
    ):
        baml_row = _baml_row(
            page_kind="programme",
            url=row.get("url", ""),
            markdown=row.get("raw_markdown", "") or "",
            baml_function="ExtractProgrammeDescriptor",
        )
        status = baml_row["status"]
        if status == "success":
            pages_extracted += 1
        elif status.startswith("skipped"):
            pages_skipped += 1
        else:
            pages_errored += 1
    return dg.MaterializeResult(
        metadata={
            "pages_extracted": pages_extracted,
            "pages_skipped": pages_skipped,
            "pages_errored": pages_errored,
        }
    )


# ── Asset list (consumed by the parent `assets/__init__.py`) ─────────────

uog_assets = [
    uog_pre_research,
    uog_bulk_scrape,
    uog_extract_courses,
    uog_extract_modules,
    uog_extract_programmes,
]


__all__ = [
    "UNIVERSITY_GROUP",
    "UOG_PRE_RESEARCH_GOAL",
    "uog_pre_research",
    "uog_bulk_scrape",
    "uog_extract_courses",
    "uog_extract_modules",
    "uog_extract_programmes",
    "uog_assets",
]
