"""
browser — DLT source factory for the per-domain browser asset group.

Wires the refactored bonneagar.stacks.browser.sruth_browser stack (formerly
`sruth_browser`) into a single DltLoadCollectionComponent. This is
the per-domain implementation of the browser-stack + Crawl4AI
refactor (see openspec/changes/2026-06-29-browser-stack-crawl4ai-refactor).

The browser defs are split into 4 sub-defs (per Phase A.1):
- defs.yaml            (this file's parent; the DltLoadCollectionComponent)
- crawl4ai_defs.yaml   (the new Crawl4AI App Component)
- firecrawl_defs.yaml  (the Firecrawl fallback Component)
- auth_defs.yaml       (the Skyvern+Stagehand opt-in Component; deferred to Phase D)

The 5 backends (Moderate choice, 5 = 3 default + 2 opt-in):
1. Crawl4AI              (self-hosted; default ON; port 11235)
2. Firecrawl             (paid fallback; default ON; MCP API)
3. 1 self-hosted Playwright (CDP; default ON; port 9222)
4. Skyvern               (opt-in via BROWSER_ENABLE_SKYVERN=1)
5. Stagehand             (opt-in via BROWSER_ENABLE_STAGEHAND=1)

The 3 DLT source factories:
- browser.search          (Crawl4AI + Firecrawl search)
- browser.bulk_crawl      (Crawl4AI deep crawl)
- browser.bulk_scrape     (Firecrawl + Crawl4AI batch scrape)
"""
from __future__ import annotations

from typing import Iterator

import dlt

from cianfhoghlaim.core.dlt._oideachais_dlt_utils.destinations import get_dlt_destination


# The 3 browser-stack backends that are default-ON.
# Skyvern + Stagehand are opt-in via BROWSER_ENABLE_SKYVERN=1 /
# BROWSER_ENABLE_STAGEHAND=1 env vars (per Phase D.2/D.3).
DEFAULT_BROWSER_BACKENDS: list[str] = [
    "crawl4ai",
    "firecrawl",
    "playwright_cdp",
]


@dlt.source(name="browser_search")
def browser_search_source() -> Iterator:
    """Yield one DLT resource per browser-search query.

    Uses Crawl4AI as the primary backend (free, self-hosted);
    Firecrawl as the paid fallback (anti-bot + structured
    extraction). The router picks the cheapest viable backend
    per call.
    """
    from bonneagar.stacks.browser.sruth_browser import BrowserClient

    client = BrowserClient()
    for backend in DEFAULT_BROWSER_BACKENDS:
        try:
            for result in client.search(
                backend=backend,
                limit_per_query=50,
            ):
                yield result
        except Exception as e:
            # Router should never raise BudgetExhausted to caller;
            # it falls back to a free backend. Log and continue.
            import structlog
            structlog.get_logger().warning(
                "browser_search_backend_failed",
                backend=backend,
                error=str(e),
            )


@dlt.source(name="browser_bulk_crawl")
def browser_bulk_crawl_source() -> Iterator:
    """Yield one DLT resource per bulk-crawl seed URL.

    Uses Crawl4AI's BFS/DFS deep-crawl strategy for full-site
    crawling of new curriculum sources. Returns 1 row per
    crawled page.
    """
    from bonneagar.stacks.browser.sruth_browser import BrowserClient

    client = BrowserClient()
    for result in client.bulk_crawl(
        strategy="BFS",
        max_depth=3,
        backend="crawl4ai",
    ):
        yield result


@dlt.source(name="browser_bulk_scrape")
def browser_bulk_scrape_source() -> Iterator:
    """Yield one DLT resource per bulk-scrape URL.

    Uses Firecrawl as the primary (fast, paid) and Crawl4AI
    as the free fallback. Best for known-structure pages
    (NCCA, SEC, DES, Apple Award CVs).
    """
    from bonneagar.stacks.browser.sruth_browser import BrowserClient

    client = BrowserClient()
    for result in client.bulk_scrape(
        backends=["firecrawl", "crawl4ai"],
    ):
        yield result


# Single shared DLT pipeline for the entire Component.
browser_pipeline = dlt.pipeline(
    pipeline_name="browser",
    destination=get_dlt_destination(),
    dataset_name="browser",
    dev_mode=False,
)


__all__ = [
    "DEFAULT_BROWSER_BACKENDS",
    "browser_search_source",
    "browser_bulk_crawl_source",
    "browser_bulk_scrape_source",
    "browser_pipeline",
]
