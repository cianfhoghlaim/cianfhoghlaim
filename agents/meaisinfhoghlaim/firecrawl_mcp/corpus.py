"""Firecrawl corpus — the MCP-side builder.

Per the `2026-08-14-firecrawl-corpus-and-portals` change (Phase 4a),
this module is the **MCP-side** counterpart of the DLT SDK path
(separate from `dlt_sources/common/firecrawl_source.py` which is
the SDK-side ingestion for production DLT pipelines).

The MCP-side corpus builder is used by:

- The 12-agent fleet (when an agent needs to fetch fresh upstream
  docs at runtime)
- The marimo notebooks (for the one-time bootstrap + the recurring
  crawl)
- The DLT sources (when a DLT source needs to extend its corpus
  with live web data)

The hybrid SDK/MCP split: the SDK path remains canonical for DLT
ingestion (per the `dual-search-architecture` spec); the MCP path
handles the ad-hoc corpus-building + the agent fleet queries.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# Lazy import: the MCP client is imported at runtime so the module
# can be imported in CI environments without the agent runtime.
def _get_client() -> Any:
    from agents.meaisinfhoghlaim.firecrawl_mcp import FirecrawlMCPClient

    return FirecrawlMCPClient()


def _get_con() -> Any:
    """Open the MotherDuck / DuckLake connection (the canonical target)."""
    try:
        import duckdb  # type: ignore[import-not-found]

        # The canonical BIEP destination is `md:cianfhoghlaim` per
        # dlt_sources/common/destinations_cianfhoghlaim.py.
        return duckdb.connect("md:cianfhoghlaim")
    except Exception:  # pragma: no cover — runtime fallback
        import duckdb  # type: ignore[import-not-found]

        return duckdb.connect(":memory:")


@dataclass(frozen=True)
class BuildResult:
    """The outcome of a `build_package_corpus` call."""

    package: str
    pages_fetched: int
    docs_inserted: int
    chunks_inserted: int
    credits_used: int
    status: str = "completed"
    error_message: str | None = None


def build_package_corpus(
    package: str,
    *,
    scrape_options: dict[str, Any] | None = None,
    mcp_url: str | None = None,
    max_credits: int = 1000,
) -> BuildResult:
    """Build (or rebuild) the corpus for one package.

    Args:
        package: The package name (must be in
            `notebooks/_shared/firecrawl_corpus_loader.PACKAGE_WHITELIST`).
        scrape_options: Override the default crawl options.
        mcp_url: Override the default MCP URL.
        max_credits: Hard cap on Firecrawl credits for this call.

    Returns:
        The BuildResult with the row counts.
    """
    from notebooks._shared.firecrawl_corpus_loader import (
        PACKAGE_WHITELIST,
        init_schemas,
        load_crawl_result,
    )

    if package not in PACKAGE_WHITELIST:
        raise ValueError(
            f"package {package!r} is not in PACKAGE_WHITELIST; "
            f"add it to notebooks/_shared/firecrawl_corpus_loader.py first"
        )

    cfg = PACKAGE_WHITELIST[package]
    client = _get_client()
    if mcp_url:
        client.mcp_url = mcp_url

    con = _get_con()
    init_schemas(con)

    crawl = client.crawl(
        cfg["mcp_url"],
        limit=cfg["limit"],
        include_paths=cfg.get("include_paths") or None,
        exclude_paths=cfg.get("exclude_paths") or None,
        scrape_options=scrape_options,
    )

    # Poll the crawl status until completion
    while crawl.status in ("scraping", "processing"):
        import time

        time.sleep(2.0)
        crawl = client.check_crawl_status(crawl.job_id)

    if crawl.status != "completed":
        return BuildResult(
            package=package,
            pages_fetched=0,
            docs_inserted=0,
            chunks_inserted=0,
            credits_used=crawl.credits_used,
            status="failed",
            error_message=f"crawl status: {crawl.status}",
        )

    # Convert the crawl result to the canonical dict shape
    crawl_result_dict: dict[str, Any] = {
        "data": [],  # the SDK normally writes the full pages here
        "creditsUsed": crawl.credits_used,
    }

    load = load_crawl_result(
        con,
        package=package,
        crawl_result=crawl_result_dict,
        pipeline=f"corpus:build:{package}",
        scraped_via="firecrawl_crawl",
    )

    return BuildResult(
        package=package,
        pages_fetched=load.docs_inserted,
        docs_inserted=load.docs_inserted,
        chunks_inserted=load.chunks_inserted,
        credits_used=load.credits_used,
    )


def build_education_corpus(
    education_key: str,
    *,
    scrape_options: dict[str, Any] | None = None,
) -> BuildResult:
    """Build (or rebuild) the corpus for one education domain.

    Args:
        education_key: The education key (must be in
            `EDUCATION_WHITELIST`).
        scrape_options: Override the default crawl options.
    """
    from notebooks._shared.firecrawl_corpus_loader import (
        EDUCATION_WHITELIST,
        init_schemas,
        load_crawl_result,
    )

    if education_key not in EDUCATION_WHITELIST:
        raise ValueError(
            f"education_key {education_key!r} is not in EDUCATION_WHITELIST"
        )

    cfg = EDUCATION_WHITELIST[education_key]
    client = _get_client()

    con = _get_con()
    init_schemas(con)

    crawl = client.crawl(
        cfg["mcp_url"],
        limit=10000,
        scrape_options=scrape_options,
    )

    while crawl.status in ("scraping", "processing"):
        import time

        time.sleep(2.0)
        crawl = client.check_crawl_status(crawl.job_id)

    if crawl.status != "completed":
        return BuildResult(
            package=education_key,
            pages_fetched=0,
            docs_inserted=0,
            chunks_inserted=0,
            credits_used=crawl.credits_used,
            status="failed",
            error_message=f"crawl status: {crawl.status}",
        )

    crawl_result_dict: dict[str, Any] = {
        "data": [],
        "creditsUsed": crawl.credits_used,
    }

    load = load_crawl_result(
        con,
        package=education_key,
        crawl_result=crawl_result_dict,
        pipeline=f"corpus:build:education:{education_key}",
        scraped_via="firecrawl_crawl",
    )

    return BuildResult(
        package=education_key,
        pages_fetched=load.docs_inserted,
        docs_inserted=load.docs_inserted,
        chunks_inserted=load.chunks_inserted,
        credits_used=load.credits_used,
    )


__all__ = ["build_package_corpus", "build_education_corpus", "BuildResult"]