# Design note — Firecrawl `/agent` Stage 0 audit pattern

## What Stage 0 is

The Oideachas / Cianfhoghlaim data orchestration has 4 canonical
stages for any new website surface:

| Stage | Stage name | Outcome | Tool |
|---|---|---|---|
| **0** | Audit | Discover the URL sitemap + dropdown structure | `BackendRouter.pre_research(base_url, goal, budget_hint=2)` (calls `Firecrawl /agent`) |
| **1** | Collect | Scrape the discovered pages into markdown | `BackendRouter.bulk_scrape(url, hint)` |
| **2** | Condense | Extract typed BAML rows per page | `b.ExtractUoGOfficialDocument(...)` |
| **3** | Embed | Write to LanceDB + DuckLake + Cognee | `@coco.fn`, `dlt` runner, cognify pass |

**Stage 0 is the only stage the user has explicitly called out.**
Without it, the deep-extraction factory relies on a
hand-curated `school_subdomain_paths` whiltelist (which can be
out-of-date the day UoG redesigns their pages).

## Why Firecrawl `/agent` specifically

The existing `BackendRouter.pre_research` method (added by the
prior `_university_deep_factory.py` change) calls
`FirecrawlApp.async_crawl_url` + `/agent` to:

1. Get the full rendered DOM of the homepages
2. Inspect dropdowns, sidebars, breadcrumbs
3. Walk `/sitemap.xml` if present
4. Cross-reference the URL patterns that the deep-extraction
   factory already knows about
5. Return a `ResearchSiteMap` with a `discovered_paths: list[URL]`
   plus a `recommended_strategy` ("crawl4ai-static" vs
   "firecrawl-agent")

This is the right tool for the user's call-out:
> "scrapes of key pages and associated pages like
> https://www.universityofgalway.ie/course-information/module/
> and https://www.universityofgalway.ie/colleges-and-schools/
> which the features of firecrawl (not just simple search they
> have such website analysis tools via mcp or sdk) should help
> in a stage 0 audit of each university get appropriate url
> paths"

## The flow

```
+--------------------+   1. pre_research   +---------------------+
|  pre_research_dag  | ────────────────▶  |  firecrawl /agent   |
|     asset          | ◀──── ResearchSiteMap ───────┘            |
+--------------------+                     +---------------------+
            |
            | 2. persist discovered paths to LanceDB
            v
+--------------------+   3. bulk_scrape    +---------------------+
|  bulk_scrape_dag   | ────────────────▶  |  firecrawl /scrape   |
|     asset          | ◀──── markdown    ───────┘ (credits)      |
+--------------------+                     +---------------------+
            |
            | 4. extract rows
            v
+--------------------+                     +---------------------+
|  baml_extract_dag  | ────────────────▶  |  BAML ExtractEn     |
|     asset          | ◀──── UoGCanonicalRow  ──────┘           |
+--------------------+                     +---------------------+
            |
            | 5. sink to DuckLake + Lance + Cognee
            v
+--------------------+   6. write to      +---------------------+
|  duckdb_sink_dag   | ────────────────▶  |  cianfhoghlaim.      |
|     asset          |                    |  education.ie.       |
+--------------------+                    |  uog_official_documents
                                          +---------------------+
```

## How Stage 0 is wired in this change

`uog_official_docs_stage0_audit` is the Stage 0 asset. It:

1. Iterates over the canonical UoG homepages
   `["https://www.universityofgalway.ie/",
     "https://www.universityofgalway.ie/course-information/module/",
     "https://www.universityofgalway.ie/colleges-and-schools/",
     "https://www.universityofgalway.ie/about-us/",
     "https://www.universityofgalway.ie/student-life/students-union/"]`
2. Calls `BackendRouter.pre_research(base_url, goal, budget_hint=2)`
3. Persists every discovered path to the
   `university_research_sitemap` LanceDB table
4. Emits a `MaterializeResult` with metadata
   `{"pages_audited": N, "paths_discovered": M, "credit_used": 2*N}`

The downstream `uog_official_docs_stage1_collect` reads those
paths and calls `BackendRouter.bulk_scrape` for each.

## Cache + idempotency

The Stage 0 audit is deterministic for a given `(base_url, goal,
academic_year)` tuple. Each result is persisted with
`content_hash = sha256(base_url + goal)[:16]` so re-runs skip the
Firecrawl credit.

## Safety rails

- `budget_hint=2` per page = 2 Firecrawl credits per homepage.
  We hard-cap at `STAGE_0_MAX_CREDITS=20` so a misconfigured
  run doesn't burn the whole monthly budget.
- The audit runs in fixture-only mode (returns `skipped_fixture`)
  when `SecretsResolver.has_real_credentials() == False` or
  `FIRECRAWL_API_KEY` is not configured.

## Open question for the thesis reviewer

If the Firecrawl MCP / SDK proves unstable in the project
environment, the Stage 0 audit can fall back to a
`crawl4ai-static` strategy that uses only the local browser.
The factory already handles this fallback path via the existing
`prefer_free_browser=True` config flag.
