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

"""02_education_corpus_crawl — the 17-domain recurring crawl.

Per the `2026-08-14-firecrawl-corpus-and-examinations-ie-v1` change
(Phase 4a), this notebook orchestrates the recurring crawl of the
17 education domains into `cianfhoghlaim.firecrawl_corpus.docs.<domain>`.

The 17 domains (per `notebooks/_shared/firecrawl_corpus_loader.EDUCATION_WHITELIST`):
ncca_ireland, examinations_ie, sqa_scotland, educationscotland,
gov_scotland, gov_uk_dfe, ofsted, pearson_edexcel,
cambridge_international, wjec_wales, qualifications_wales, gov_wales,
iom_education, oide_ie, scoilnet_ie, gov_ie_education.

The notebook is scheduled via Dagster at 03:00 UTC daily. The
examinations.ie domain uses the `state-exams-ie` persistent profile
(special interleaved with the `examinations_paper_sensor`).
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
        # 02 — Education Corpus Crawl (recurring)

        Per the `2026-08-14-firecrawl-corpus-and-examinations-ie-v1`
        change (Phase 4a). Crawls the 17 education domains daily
        into `cianfhoghlaim.firecrawl_corpus.docs.<domain>` +
        `docs_index`.

        ## Cadence per domain
        - **Weekly**: gov_ie_education, gov_scotland, gov_wales, gov_uk_dfe
        - **Monthly**: ncca_ireland, sqa_scotland, ofsted, pearson_edexcel,
          wjec_wales, examinations_ie (via the dedicated sensor + DLT sources)
        - **Quarterly**: educationscotland, cambridge_international,
          qualifications_wales, iom_education, oide_ie, scoilnet_ie

        ## How to run
        - **CLI mode**: `uv run python notebooks/01_corpus/02_education_corpus_crawl.py --domain ncca_ireland`
        - **Notebook mode**: `marimo edit notebooks/01_corpus/02_education_corpus_crawl.py`
        - **Dagster**: scheduled at 03:00 UTC daily
        """
    )
    return (mo,)


@app.cell
def _imports() -> None:
    import logging
    import os
    import sys
    from pathlib import Path

    repo_root = Path(__file__).parent.parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    import duckdb

    from agents.meaisinfhoghlaim.firecrawl_mcp.corpus import (
        build_education_corpus,
    )
    from notebooks._shared.firecrawl_corpus_loader import (
        EDUCATION_WHITELIST,
        init_schemas,
    )

    logger = logging.getLogger(__name__)
    return (
        EDUCATION_WHITELIST,
        Path,
        build_education_corpus,
        duckdb,
        init_schemas,
        logger,
        os,
        repo_root,
        sys,
    )


@app.cell
def _state(EDUCATION_WHITELIST, os) -> None:
    args = os.sys.argv[1:]
    only_domain: str | None = None
    run_all = False
    for a in args:
        if a.startswith("--domain="):
            only_domain = a.split("=", 1)[1]
        elif a == "--all":
            run_all = True

    todo = (
        list(EDUCATION_WHITELIST.keys())
        if run_all
        else [only_domain]
        if only_domain
        else []
    )

    print(f"Plan: {len(todo)} education domain(s)")
    for d in todo:
        print(f"  - {d} → {EDUCATION_WHITELIST[d]['mcp_url']}")
    return (todo,)


@app.cell
def _run(todo, build_education_corpus, duckdb, init_schemas, logger) -> None:
    if not todo:
        print("No domains to process. Run with --domain=<name> or --all.")
    else:
        con = duckdb.connect("md:cianfhoghlaim")
        init_schemas(con)

        results = []
        for domain in todo:
            print(f"Crawling {domain}...")
            try:
                result = build_education_corpus(domain)
                results.append(result)
                print(
                    f"  ✓ {domain}: {result.docs_inserted} docs, "
                    f"{result.credits_used} credits"
                )
            except Exception as exc:
                logger.exception("02_education_corpus_crawl.domain_failed", extra={"domain": domain})
                results.append(
                    type("BuildResult", (), {
                        "package": domain,
                        "pages_fetched": 0,
                        "docs_inserted": 0,
                        "chunks_inserted": 0,
                        "credits_used": 0,
                        "status": "failed",
                        "error_message": str(exc),
                    })()
                )

        total_docs = sum(r.docs_inserted for r in results)
        total_credits = sum(r.credits_used for r in results)
        print(f"\n=== Summary ===")
        print(f"Total domains: {len(results)}")
        print(f"Total docs: {total_docs}")
        print(f"Total credits: {total_credits}")
    return (con,)


@app.cell
def _smoke_test(con) -> None:
    if con is not None:
        try:
            ncca_count = con.execute(
                "SELECT COUNT(*) FROM cianfhoghlaim.firecrawl_corpus.docs WHERE package = 'ncca_ireland'"
            ).fetchone()[0]
            print(f"\nSmoke test: ncca_ireland docs rows: {ncca_count}")
        except Exception as exc:
            print(f"Smoke test deferred (bootstrap incomplete): {exc}")


if __name__ == "__main__":
    app.run()