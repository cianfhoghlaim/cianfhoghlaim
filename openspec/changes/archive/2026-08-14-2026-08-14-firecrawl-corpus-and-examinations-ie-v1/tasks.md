# Tasks: Firecrawl Corpus + Examinations.ie Interact (Phase 4a)

## Phase A — Lakehouse schema + corpus loader (4 tasks, ~2 hours)

- [ ] A1 Create `notebooks/_shared/firecrawl_meta_schema.sql` with
  the 3 new schemas (`firecrawl_corpus`, `firecrawl_meta`) + the
  3 tables (`docs.<package>`, `docs_index`, `scrapes`, `budget`)
  + indexes. ~80 LOC.
- [ ] A2 Create `notebooks/_shared/firecrawl_corpus_loader.py` — the
  Python helper that:
  - takes a `firecrawl_crawl` result dict
  - writes one row per page to `firecrawl_corpus.docs.<package>`
  - computes BGE-M3 1024-d embeddings via the shared `_lifespan.py`
  - writes one row per chunk to `firecrawl_corpus.docs_index`
  - logs the scrape to `firecrawl_meta.scrapes`
  - flushes the LanceDB companion table
  - ~200 LOC.
- [ ] A3 Update the firecrawl-corpus CCC guide in
  `.cocoindex_code/guides.yml` with the new `files:` list (now that
  the files exist).
- [ ] A4 `mise run lint:guides-yml` exits 0.

## Phase B — marimo notebooks + corpus MCP module (3 tasks, ~3 hours)

- [ ] B1 Create `notebooks/01_corpus/01_software_stack_crawl.py` — the
  17-package orchestrator (CocoIndex, Dagster, DLT, BAML,
  MotherDuck, DuckDB, LanceDB, Pydantic AI, FastAPI, Hono,
  TanStack Start, CopilotKit, OpenCode, Infisical, LiteLLM,
  Langfuse, Firecrawl). Iterates a per-package config dict
  (`mcp_url`, `include_paths`, `exclude_paths`, `limit`,
  `sitemap`); calls `FirecrawlMCPClient.crawl` + `firecrawl_mcp_corpus`
  + writes to DuckLake. ~300 LOC.
- [ ] B2 Create `notebooks/01_corpus/02_education_corpus_crawl.py` — the
  17-domain recurring orchestrator (NCCA, examinations.ie, SQA,
  Pearson, etc.). Similar pattern, scopes per-domain. ~300 LOC.
- [ ] B3 Create `agents/meaisinfhoghlaim/firecrawl_mcp/corpus.py` — the
  MCP-side builder (a thin wrapper around `FirecrawlMCPClient` +
  the loader). ~200 LOC.

## Phase C — PII flags on site_crawler + 3 sources (2 tasks, ~1 hour)

- [ ] C1 Update `dlt_sources/common/site_crawler.py` to honor
  `redact_pii` + `zero_data_retention` + `sensitivity` flags
  (per-source dict at the top of each source file).
- [ ] C2 Set `sensitivity: "pii"` on the 3 PII sources:
  - `dlt_sources/british_isles/ireland/medicine/hse.py`
  - `dlt_sources/british_isles/scotland/statistics/gov_scot_statistics.py`
  - `dlt_sources/british_isles/wales/education/welsh_medium.py`

## Phase D — examinations.ie DLT sources (2 tasks, ~2 hours)

- [ ] D1 Create `dlt_sources/british_isles/ireland/education/examinations_papers.py`
  — the DLT source for exam papers via Interact + Parse. Uses the
  `state-exams-ie` persistent profile (read-only mode); opens an
  Interact session, searches for the paper, downloads the PDF,
  parses it, writes to `cianfhoghlaim.lc_exam_papers.<subject>.<year>`.
  ~300 LOC.
- [ ] D2 Create `dlt_sources/british_isles/ireland/education/examinations_marking_schemes.py`
  — the DLT source for marking schemes. Same pattern but for the
  `marking-scheme` URL. ~250 LOC.

## Phase E — state-exams-ie stack + Infisical secrets (3 tasks, ~1 hour)

- [ ] E1 Create `bonneagar/stacks/state-exams-ie/` with the 6
  GOLD_STANDARD files (`compose.yaml`, `sidecar.yaml`,
  `secrets.env`, `pangolin.yaml`, `blueprint.yaml`, `.env.example`).
  The services are: the persistent profile vault + the Locket
  sidecar (no real workload — the profile state is stored on
  the bunchloch filesystem + served via Locket). ~250 LOC.
- [ ] E2 Update `bonneagar/dagger/cianfhoghlaim_dagger/__init__.py`
  with 2 new `InfisicalSecret` entries: `examinations-ie/username`
  + `examinations-ie/password`.
- [ ] E3 Update the root `.infisical.env` with 2 new entries:
  `infisical://dev-baile/cianfhoghlaim/examinations-ie/username` +
  `/password`.

## Phase F — Budget asset + sensor + lint task (3 tasks, ~2 hours)

- [ ] F1 Create `orchestration/defs/4_budget/firecrawl_budget_asset.py`
  — the nightly budget tracker that reads `firecrawl_meta.scrapes`
  + writes `firecrawl_meta.budget` + flags any pipeline > 150% of
  allocation. ~200 LOC.
- [ ] F2 Create `orchestration/defs/4_sensors/examinations_paper_sensor.py`
  — the daily poll-on-demand sensor that polls
  `examinations.ie/?lang=en&search=` once per day + compares
  against the manifest + triggers a re-materialization.
  ~150 LOC.
- [ ] F3 Create `scripts/lint_firecrawl_budget.py` — the developer
  terminal wrapper that runs the budget asset in dry-run mode
  + exits 1 if any pipeline > 150% of allocation. ~100 LOC. Wired
  via `[tasks."lint:firecrawl-budget"]` in `mise.toml` (already
  added by Phase 1).

## Phase G — Polyglot memory modules + docs_index memory job (3 tasks, ~2 hours)

- [ ] G1 Create `agents/meaisinfhoghlaim/firecrawl_mcp/memory/__init__.py`
  + `graphiti_store.py` + `lancedb_store.py` + `cognee_store.py` +
  `router.py` — the polyglot memory layer over `docs_index`. The
  router takes an intent string + routes to the right backend:
  - "What was X in version Y?" → Graphiti (temporal)
  - "What's the relevant chunk for this query?" → LanceDB (vector)
  - "How does X relate to Y?" → Cognee (cross-doc graph)
  - ~600 LOC total.
- [ ] G2 Create `orchestration/defs/4_memory/docs_index_memory_job.py`
  — the nightly job that re-syncs all 3 stores from `docs_index`.
  ~100 LOC.
- [ ] G3 Wire `model_for(family="text_llm", role="docs_summariser")`
  for any LLM-touching summarisers in the polyglot memory layer
  (per the centralized-registry contract).

## Phase H — Validation + archive (6 tasks, ~1 hour)

- [ ] H1 `openspec validate
  2026-08-14-firecrawl-corpus-and-examinations-ie-v1 --strict`
  returns 0 errors.
- [ ] H2 `mise run lint:guides-yml` exits 0 (the 31st guide's
  `files:` list validates).
- [ ] H3 `mise run lint:skills && mise run lint:drift-docs` exit 0.
- [ ] H4 `bun run scripts/validate-ccc-freshness.ts` exits 0 (the
  CCC index is < 7 days old on `main`).
- [ ] H5 `mise run sync:all` passes (the 7-layer sync loop).
- [ ] H6 `openspec archive 2026-08-14-firecrawl-corpus-and-examinations-ie-v1
  --yes` succeeds.