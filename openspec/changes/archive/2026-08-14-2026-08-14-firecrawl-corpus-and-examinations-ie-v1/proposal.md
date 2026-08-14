# Change: Firecrawl Corpus + Examinations.ie Interact (Phase 4a — Focused Data Acquisition)

## Why

The 2026-08-14-firecrawl-mcp-ccc-dual-search-v1 change established the
dual-search architecture (ccc + Cognee + Firecrawl MCP) but **did not
yet ingest any content** — the agents need a populated reference
corpus to query. There are also 2 specific gaps:

1. **No corpus for the 12-agent fleet** — the agents have a
   centralized model registry (`meaisinfhoghlaim/models/model_registry.py`)
   but no equivalent upstream-documentation corpus. When an agent is
   asked "how does Dagster 1.13.x handle asset partitions", the
   answer must come from either Cognee (if a doc was cognified) or
   a fresh `firecrawl_scrape` call. There is no cached, embedded
   index.

2. **Examinations.ie exam papers + marking schemes are not
   ingestible via plain scrape** — the State Examinations Commission
   login-gates the PDFs. The agent stack needs
   `firecrawl_interact` + persistent profiles to authenticate
   and download the exam papers.

This change:

- Ingests ~3,960 pages of upstream package docs (17 packages) + 17
  education domains into `cianfhoghlaim.firecrawl_corpus.docs.<package>`
  + `docs_index` (BAAI/bge-m3 1024-d embeddings).
- Adds 2 DLT sources for examinations.ie exam papers + marking
  schemes via the `state-exams-ie` persistent profile.
- Adds the `firecrawl_budget_asset` (nightly cost tracker) +
  `examinations_paper_sensor` (daily poll-on-demand change
  detection — replaces the recursive Firecrawl Monitor pattern).
- Adds 3 PII flags (`redact_pii`, `zero_data_retention`) on the
  existing `dlt_sources/common/site_crawler.py` for the 3 PII
  sources (HSE + Scottish NHS + Welsh health).
- Stand up the polyglot memory layer (Graphiti + LanceDB + Cognee)
  over `docs_index` so the 12-agent fleet can query via the
  right surface per intent.

## What Changes

- **Lakehouse schema**: `notebooks/_shared/firecrawl_meta_schema.sql`
  creates 3 new schemas (`firecrawl_corpus.docs.<package>`,
  `firecrawl_corpus.docs_index`, `firecrawl_meta.scrapes`,
  `firecrawl_meta.budget`) in `md:cianfhoghlaim`.
- **Corpus loader**: `notebooks/_shared/firecrawl_corpus_loader.py`
  writes a `firecrawl_crawl` result to DuckLake + computes BGE-M3
  embeddings via the shared `_lifespan.py` embedder.
- **2 marimo notebooks**:
  - `notebooks/01_corpus/01_software_stack_crawl.py` — the 17-package
    one-time bootstrap
  - `notebooks/01_corpus/02_education_corpus_crawl.py` — the 17-domain
    recurring crawl
- **Corpus module**: `agents/meaisinfhoghlaim/firecrawl_mcp/corpus.py`
  — the MCP-side corpus builder (different from the DLT SDK path).
- **2 DLT sources** at `dlt_sources/british_isles/ireland/education/`:
  - `examinations_papers.py` — uses the `state-exams-ie` persistent
    profile + `firecrawl_interact` to log in + `firecrawl_parse`
    to extract text
  - `examinations_marking_schemes.py` — same pattern, marking
    schemes
- **`bonneagar/stacks/state-exams-ie/`**: the persistent profile
  vault + Locket sidecar (the 6-file GOLD_STANDARD pattern).
- **2 new Infisical secrets**: `examinations-ie/username` +
  `examinations-ie/password` (under `dev-baile/cianfhoghlaim/`).
- **PII flags on `site_crawler.py`**: `redact_pii` + `zero_data_retention`
  + `sensitivity: "pii"` propagation.
- **2 Dagster assets**: `firecrawl_budget_asset` (nightly budget
  tracker) + `examinations_paper_sensor` (daily poll-on-demand).
- **Polyglot memory**: `agents/meaisinfhoghlaim/firecrawl_mcp/memory/`
  with Graphiti + LanceDB + Cognee stores + a router.
- **`mise run lint:firecrawl-budget`**: the budget linter.
- **Specs**: `firecrawl-corpus-and-portals` (new capability spec).

## Why now (post-Phase 1)

Phase 1 stood up the dual-search architecture but no agent has
called `firecrawl_search` yet. We need a populated corpus before the
agents can use the corpus_query pattern. The 17-package software
stack crawl (~3,960 pages over ~2 weeks) is a one-time bootstrap that
unlocks every subsequent agent query.

## Dependencies

`Blocked by: 2026-08-14-firecrawl-mcp-ccc-dual-search-v1` (the
dual-search architecture Phase 1 change). `Blocked by (soft):
none`. `Affected repos: cianfhoghlaim (single repo) + 1
Komodo-managed stack (state-exams-ie persistent profile vault) +
1 platform-level Infisical environment (the 2 new SEC secrets)`.

## Impact

- **Capabilities**: NEW `firecrawl-corpus-and-portals` (1 spec,
  5 Requirements, 7 Scenarios).
- **Code**: ~16 new files (3 schema + 5 notebooks + 2 DLT sources +
  6-file stack + 2 secrets + 1 lint script + 1 budget asset + 1
  sensor + 1 memory module + 1 spec) + ~7 modified files.
- **Risk**: medium — the 3,960-page bootstrap is a 1-2 week
  scrape-and-embed job (the limiting factor is the Firecrawl
  embedding quota at 1 credit/page); the examinations.ie Interact
  flow requires a real-world login (the persistent profile is
  created in a manual session 1, then reused by the sensor).
- **Credit cost**: ~$19.80 one-time bootstrap + ~$9/mo run-rate
  (per the detailed breakdown in the plan).

## Success criteria

1. `mise run lint:guides-yml` passes after the
   `firecrawl_corpus_loader.py` + `corpus.py` + 2 notebooks + 2
   DLT sources + 1 budget asset + 1 sensor + 5 memory modules
   reference the new `firecrawl-corpus` CCC guide's `files:` list.
2. `notebooks/01_corpus/01_software_stack_crawl.py` runs end-to-end
   and ingests ≥3,000 of the 3,960 pages into
   `cianfhoghlaim.firecrawl_corpus.docs.<package>`.
3. `agents/meaisinfhoghlaim/firecrawl_mcp/memory/router.py` query
   "how does Dagster 1.13.x handle asset partitions" returns ≥3
   relevant chunks via at least 1 of the 3 backends.
4. `examinations_paper_sensor` triggers on a synthetic test
   paper release + the `state-exams-ie` Interact session opens +
   downloads the PDF + `firecrawl_parse` extracts the text + the
   row lands in `cianfhoghlaim.lc_exam_papers.<subject>.<year>`.
5. `mise run lint:firecrawl-budget` exits 0 after the bootstrap
   completes.
6. `openspec validate 2026-08-14-firecrawl-corpus-and-examinations-ie-v1
   --strict` exits 0.
7. `mise run lint:skills && mise run lint:drift-docs` exit 0.