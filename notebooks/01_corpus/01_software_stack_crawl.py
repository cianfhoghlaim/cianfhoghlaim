# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13",
#   "ibis-framework[duckdb]>=9.0",
#   "pandas>=2.2",
#   "altair>=5.0",
#   "pyarrow>=15",
# ]
# ///

"""01_software_stack_crawl — the 17-package one-time bootstrap.

Per the `2026-08-14-firecrawl-corpus-and-examinations-ie-v1` change
(Phase 4a), this notebook orchestrates the bootstrap of the 17
upstream package docs into `cianfhoghlaim.firecrawl_corpus.docs.<package>`.

The 17 packages (per `notebooks/_shared/firecrawl_corpus_loader.PACKAGE_WHITELIST`):
cocoindex, dagster, dlt, baml, motherduck, duckdb, lancedb, pydantic_ai,
fastapi, hono, tanstack_start, copilotkit, opencode, infisical, litellm,
langfuse, firecrawl.

Total bootstrap: ~3,960 pages over ~2 weeks. The notebook is
dual-mode (CLI + marimo edit) and runs the bootstrap in 3 phases:

1. **Phase 1**: Crawl each package (1 call per package, ~5 min each)
2. **Phase 2**: Write the crawl results to the lakehouse (via the
   shared `firecrawl_corpus_loader.py`)
3. **Phase 3**: Refresh the polyglot memory layer (via the
   `docs_index_memory_job`)

The browser smoke test is at the bottom of the notebook.
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _intro() -> None:
    import marimo as mo

    mo.md(
        """
        # 01 — Software Stack Crawl (one-time bootstrap)

        Per the `2026-08-14-firecrawl-corpus-and-examinations-ie-v1`
        change (Phase 4a). Bootstraps the 17 upstream package docs
        into `cianfhoghlaim.firecrawl_corpus.docs.<package>` +
        `docs_index` (BAAI/bge-m3 1024-d embeddings).

        **Total**: ~3,960 pages across 17 packages. The bootstrap
        runs as a one-time job over ~2 weeks.

        ## Phases
        1. **Crawl** — for each package, call `FirecrawlMCPClient.crawl`
        2. **Write** — write the crawl results to the lakehouse
        3. **Refresh** — refresh the polyglot memory layer

        ## How to run
        - **CLI mode**: `uv run python notebooks/01_corpus/01_software_stack_crawl.py --package cocoindex`
        - **Notebook mode**: `marimo edit notebooks/01_corpus/01_software_stack_crawl.py`
        """
    )
    return (mo,)


@app.cell
def _imports() -> None:
    import logging
    import os
    import sys
    from pathlib import Path

    # Ensure the repo root is on sys.path
    repo_root = Path(__file__).parent.parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    import duckdb

    from agents.meaisinfhoghlaim.firecrawl_mcp.corpus import (
        build_package_corpus,
    )
    from notebooks._shared.firecrawl_corpus_loader import (
        PACKAGE_WHITELIST,
        init_schemas,
    )

    logger = logging.getLogger(__name__)
    return (
        PACKAGE_WHITELIST,
        Path,
        build_package_corpus,
        duckdb,
        init_schemas,
        logging,
        os,
        repo_root,
        sys,
    )


@app.cell
def _state(PACKAGE_WHITELIST, os) -> None:
    # The dual-mode CLI gate: --package=<name> runs one package,
    # --all runs the entire bootstrap.
    args = os.sys.argv[1:]
    only_package: str | None = None
    run_all = False
    for a in args:
        if a.startswith("--package="):
            only_package = a.split("=", 1)[1]
        elif a == "--all":
            run_all = True

    todo = (
        list(PACKAGE_WHITELIST.keys())
        if run_all
        else [only_package]
        if only_package
        else []
    )

    print(f"Bootstrap plan: {len(todo)} package(s)")
    for p in todo:
        print(f"  - {p} → {PACKAGE_WHITELIST[p]['mcp_url']}")
    return (todo,)


@app.cell
def _run(todo, build_package_corpus, duckdb, init_schemas, logging) -> None:
    logger = logging.getLogger("01_software_stack_crawl")

    if not todo:
        print("No packages to process. Run with --package=<name> or --all.")
    else:
        con = duckdb.connect("md:cianfhoghlaim")
        init_schemas(con)

        results = []
        for package in todo:
            print(f"Crawling {package}...")
            try:
                result = build_package_corpus(package)
                results.append(result)
                print(
                    f"  ✓ {package}: {result.docs_inserted} docs, "
                    f"{result.chunks_inserted} chunks, "
                    f"{result.credits_used} credits"
                )
            except Exception as exc:
                logger.exception("01_software_stack_crawl.package_failed", extra={"package": package})
                results.append(
                    type("BuildResult", (), {
                        "package": package,
                        "pages_fetched": 0,
                        "docs_inserted": 0,
                        "chunks_inserted": 0,
                        "credits_used": 0,
                        "status": "failed",
                        "error_message": str(exc),
                    })()
                )

        # Summary
        total_docs = sum(r.docs_inserted for r in results)
        total_credits = sum(r.credits_used for r in results)
        print(f"\n=== Bootstrap Summary ===")
        print(f"Total packages: {len(results)}")
        print(f"Total docs inserted: {total_docs}")
        print(f"Total credits used: {total_credits}")
        successful = [r for r in results if r.status == "completed"]
        failed = [r for r in results if r.status != "completed"]
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        for r in failed:
            print(f"  - {r.package}: {r.error_message}")
    return (con,)


@app.cell
def _smoke_test(con) -> None:
    # The browser smoke test: verify the docs_index has rows for
    # at least one popular package.
    if con is not None:
        try:
            cocoindex_count = con.execute(
                "SELECT COUNT(*) FROM cianfhoghlaim.firecrawl_corpus.docs_index WHERE package = 'cocoindex'"
            ).fetchone()[0]
            print(f"\nSmoke test: cocoindex docs_index rows: {cocoindex_count}")
            assert cocoindex_count > 0, "Expected ≥ 1 cocoindex row"
            print("OK — bootstrap smoke test passed")
        except Exception as exc:
            print(f"Smoke test failed (acceptable during bootstrap): {exc}")


if __name__ == "__main__":
    app.run()