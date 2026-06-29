# Stub Filler — Phase 1A/1B/2/3 Decision Specs (Agent 129-132 consolidated)

**Date:** 2026-06-29
**Agent:** 129-132 (consolidated)
**Constraint:** ~15 min wall clock · webfetch + ccc + bash only (NO browserbase, NO firecrawl)
**Goal:** Add 5-7 ADDED Requirements to each of the 4 stub change spec files
based on the Wave 1 (25 agents) + Wave 2 (live-docs verifiers) research
under `openspec/research/2026-06-28-browserbase-program-2/`.

## Files updated (4)

| # | File | Original reqs | New reqs | Total reqs | Scenarios | Lines |
|:--|:--|--:|--:|--:|--:|--:|
| 1 | `openspec/changes/2026-06-28-browserbase-phase-1a-decisions/specs/oideachais-pipeline/spec.md` | 6 | 5 | 11 | 11 | 193 |
| 2 | `openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md` | 6 | 5 | 11 | 11 | 190 |
| 3 | `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md` | 8 | 4 | 12 | 16 | 231 |
| 4 | `openspec/changes/2026-06-28-browserbase-phase-3-decisions/specs/oideachais-pipeline/spec.md` | 7 | 4 | 11 | 12 | 203 |
| | **Total** | **27** | **18** | **45** | **50** | **817** |

## Validation results (all pass)

```
$ openspec validate 2026-06-28-browserbase-phase-1a-decisions --strict
Change '2026-06-28-browserbase-phase-1a-decisions' is valid

$ openspec validate 2026-06-28-browserbase-phase-1b-decisions --strict
Change '2026-06-28-browserbase-phase-1b-decisions' is valid

$ openspec validate 2026-06-28-browserbase-phase-2-decisions --strict
Change '2026-06-28-browserbase-phase-2-decisions' is valid

$ openspec validate 2026-06-28-browserbase-phase-3-decisions --strict
Change '2026-06-28-browserbase-phase-3-decisions' is valid
```

## New Requirements added per file

### Phase 1A (oideachais-pipeline) — 5 new

1. **dlt 1.28.1 with `[hub]` extra is the canonical install (Wave 2 drift fix)** — pins `dlt[hub]>=1.27.0,<2.0.0` to recover `dlt dashboard` / `dlt pipeline show` (split out in 1.27.0 on 2026-05-19); upgrades lock to 1.28.1 (2026-06-19); requires native Polars `LazyFrame` in `@dlt.resource` for column-projection + filter pushdown.
2. **Dagster `@dlt_assets` + `asset_check` is the canonical ingestion wrapper (Wave 2)** — wraps every dlt source in `build_dlt_asset_specs` + `DagsterDltTranslator`; emits 6 asset keys per source; attaches row-count `asset_check` + schema-drift `asset_observation`.
3. **LanceDB `IVF_HNSW_SQ` is the canonical vector index (Wave 2 drift fix)** — supersedes the P1B-06 standalone HNSW config (HNSW is a sub-index inside IVF partitions in v0.33+, not a top-level type); uses `IVF_PQ` for >1 M rows.
4. **Lakekeeper v0.12.4 is the canonical Iceberg REST catalog (Wave 2 verified)** — pin to v0.12.4 (2026-06-17) for the v0.12.0 Idempotency Keys + V3 Variant + OPA batch features; canonical org is `lakekeeper/lakekeeper` (the old `treeverse/lakekeeper` URL 404s).
5. **MotherDuck `mcp-server-motherduck` is the canonical agent-side SQL surface** — registers `uvx mcp-server-motherduck --db-path :memory: --read-write --allow-switch-databases` in `opencode.json` so OpenCode / Claude Code / Cursor / Copilot Studio agents can query the lakehouse via the MCP.

### Phase 1B (oideachais-storage) — 5 new

1. **LanceDB `IVF_HNSW_SQ` is the canonical vector index (Wave 2 drift fix)** — same rationale as 1A #3; recall@10 ≥ 0.95 at p50 ≤ 200 ms.
2. **LanceDB Blob v2 is the canonical large-object store for PDFs + images** — uses `pa.large_binary()` + Arrow field metadata `{"lance-encoding:blob": "true"}` for >1 MB PDFs and high-res images; 3 modes (`lazy`, `bytes`, `descriptions`).
3. **Graphiti bi-temporal tracking with FalkorDB + Dragonfly is canonical (Wave 2 verified)** — pins `graphiti-core >= 0.29.2` with FalkorDB 1.1.2 + `vector.so` loadable + Dragonfly episode cache; benchmarks 94.7% LoCoMo @ 155 ms, 90.2% LongMemEval @ 162 ms; auto fact invalidation on `add_episode` updates.
4. **LanceDB embedding registry with 15+ providers is canonical (Wave 2)** — uses the registry's 15+ providers (OpenAI, HF, Sentence Transformers, Cohere, Jina, VoyageAI, OpenCLIP, ImageBind, Bedrock, Gemini, Ollama, IBM watsonx, ColPali, Instructor, Superlinked) for every table that embeds at ingest time.
5. **Cognee 7-cluster knowledge graph with Postgres unified provider (Wave 2 confirmed)** — adds the 7th cluster (`leabharlann`) to the ontology; uses Cognee 0.1.22+ with the Postgres unified provider (Neo4j fallback for prod scale).

### Phase 2 (meaisinfhoghlaim-platform) — 4 new

1. **Unsloth 3.0 `FastModel` + `train_on_responses_only` is the canonical fine-tuning loader (Wave 2)** — supersedes `FastVisionModel` for Gemma 4; adopts 4 Wave-2 patch categories (`use_cache=False` for E2B/E4B, `num_kv_shared_layers=0` for 31B/26B, `train_on_responses_only` for the +1% accuracy booster, Dynamic 2.0 GGUFs for export).
2. **Google ADK agents SHALL route through LiteLLM via `LiteLlm` 1-line swap (bypass fix)** — replaces every `LlmAgent(model="gemini-2.0-flash")` hardcode (32 sites across 7 agents) with `LlmAgent(model=LiteLlm(model="minimax", api_base="http://litellm:4000"))`; gated on `minimax_alias_health` Dagster asset check.
3. **Pydantic Logfire is the canonical Python tracing layer (Wave 2 confirmed)** — Logfire for FastAPI/Celery/BAML span trees; Langfuse reserved for LLM-call-side telemetry; cross-linked via `trace_id`.
4. **BAML 0.13+ is the canonical LLM-structured-output layer** — defines schemas in `.baml` files under `cianfhoghlaim/core/baml/_oideachais_src/`; uses `ExtractEn` + `ExtractEnStrong` clients routed through LiteLLM `minimax`.

### Phase 3 (oideachais-pipeline) — 4 new

1. **per-site BAML extraction schema with T&Cs gate (Wave 2)** — one BAML schema per source site under `cianfhoghlaim/core/baml/_oideachais_src/site_schemas/`; every site-specific BAML call gated on the `site_posture` Iceberg table (T&Cs, robots.txt, rate limit).
2. **Wave 3 marimo dashboard is the canonical ingestion-health surface** — `oideachais_ingestion_health.py` marimo notebook with a 12-row health grid, a "last 7 days incidents" stacked bar chart, and a "TCA-only" filter.
3. **examinations.ie PHP-form dropdown cascade + arxiv OAI-PMH are the canonical exam + research sources** — Playwright/Stagehand for the `exammaterialarchive.php` form; OAI-PMH for arxiv with `[cs.LG, cs.CL, cs.AI, cs.CV]` filter + 1 req/3 sec rate limit (Wave 2 update to the v2 etiquette).
4. **gov.scot / gov.wales / education-ni rate-limited ingestion** — Scotland ≤5 req/sec, Wales ≤10 req/sec + bilingual split, NI ≤2 req/sec with Friday-afternoon 503 exponential-backoff retry (1s/2s/4s/8s/30s cap).

## Cross-references

- Wave 1 source files read: `agent-{01-dlt,02-dagster,03-cocoindex,04-lancedb,05-motherduck,06-litellm,11-graphiti,19-unsloth,23-ireland-sites,24-uk-sites,25-crown-ref-sites}.md` and `adk-logfire/{63-google-adk-usage-audit,64-pydantic-logfire-usage-audit}.md`
- Wave 2 source files read: `live-docs/{71-live-dlt-128,72-live-dagster-113,74-live-lancedb-033,75-live-motherduck-current,76-live-litellm-184,86-live-iceberg-current,87-live-ducklake-current,88-live-risingwave-current,89-live-mlflow-current,90-live-langfuse-v3}.md` and `live-sites/{96-live-unsloth-docs,98-live-motherduck-dives,99-live-motherduck-flights,100-live-ducklake-deep,106-live-gov-uk,108-live-gov-im,109-live-gov-je}.md`
- Specs touched (canonical): `oideachais-pipeline`, `oideachais-storage`, `meaisinfhoghlaim-platform` (per `openspec/AGENTS.md` capability spec list)

## Notes / drift observed

- Existing stubs already had 6-8 requirements filled (prior Phase 1A/1B/2/3 work); this pass is purely additive
- `dlt 1.27.0` `[hub]` extra split is the highest-priority drift item (any `dlt pipeline show` invocation fails today)
- P1B-06 standalone HNSW index config is a 3-minor-version-stale assumption; needs the IVF_HNSW_SQ drift fix in the next `oideachais-cocoindex-v1` skill update
- Google ADK → LiteLLM bypass is the 1-line fix that unblocks 32 `LlmAgent` sites across 7 agents; should be the next PR
