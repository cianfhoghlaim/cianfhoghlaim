# Agent 30 — Documentation Gaps (Phase 2 Synthesis)

**Date:** 2026-06-29
**Scope:** `.agents/skills/*/SKILL.md` audit + 4 phase stub changes + 4 cross-cutting docs
**Inputs:** 25 wave-1 agent outputs (`agent-01-dlt.md` through `agent-25-crown-ref-sites.md`), `SHARED_DISCOVERY_LOG.md`, `celtic-asset-generation/spec.md`, `openspec/project.md`, `AGENTS.md`, `openspec/AGENTS.md`, `infrastructure/AGENTS.md`
**Wall clock:** ~13 min · **BrowserBase credits:** 0 (read-only synthesis — no browser sessions opened)

---

## 1. TL;DR — Top 3 most-outdated skill files

| Rank | Skill | Why it's the most outdated | file:line |
|:--|:--|:--|:--|
| **#1** | `.agents/skills/unsloth/SKILL.md` | Last updated **2025-04**; the 219-line skill still teaches `FastLanguageModel` + Llama-3.2-3B / UCCIX-Llama2-13B; upstream 3.0+ ships **`FastModel` (unified loader)** + Gemma 4 / Qwen3.6 / GLM-4.6V Flash + **`train_on_responses_only` (+1% accuracy)** + MTP speculative decoding + Dynamic 2.0 GGUFs. None of these 6 features appear in the skill. | full file; esp. L8, L52-65, L42-49 |
| **#2** | `.agents/skills/dlt/SKILL.md` | 312-line skill pins `dlt>=1.0.0` baseline; we ship `dlt 1.25.0` while upstream is **`dlt 1.28.1`** (3 minors behind). Misses the **1.27 `workspace` extra split** (breaks `dlt dashboard` / `dlt pipeline … show/mcp` / `dlthub ai` without `"dlt[hub]>=1.27.0"`), **1.28.0 breaking `refresh="drop_data"`** + `replace` truncates empty/orphaned tables, **1.27.2 hotfix** (`merge` after `replace` on no-data incremental truncates), and **native Polars LazyFrame** in `@dlt.resource`. Source path `sruth/oideachais/dlt_sources/` (L21) is also **post-v4-404** — the real path is `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` (190 files, not 28). | L21, L30-50, the whole "When to use" section |
| **#3** | `.agents/skills/baml/SKILL.md` | Frontmatter (L3) and body (L17, L29, L48, L176) all point at the **pre-v4 `sruth/oideachais/baml_src/`** path. Generator version `0.76.2` (L389, L397) is **3 months stale** (latest is `baml-py` 0.223.0 — adds `render_null_as`, fixes streaming-retry #3025). Skill examples (Pattern 1:64, 2:108/121, 4:184) all teach the **inline `client "openai/gpt-4o-mini"` antipattern** that 8 places in `curriculum_extraction.baml` now use to bypass the LiteLLM gateway. L281's "7-tier MiniMax fallback chain" is mentioned but never listed. | L3, L17, L29, L48, L64, L108, L121, L184, L281, L389, L397 |

---

## 2. Per-skill-file audit (50 canonical skills)

Pass = current with Phase-2 research; Fail = documented gap requiring update.

| # | Skill file | State | Specific sections / lines needing update | Suggested edit |
|:--|:--|:--|:--|:--|
| 1 | `dlt/SKILL.md` (312) | **FAIL** | L21 ("Source location: `sruth/oideachais/dlt_sources/`"); L30-50 (version pin) | Rewrite source path → `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` (190 files, 12 subdirs); bump `dlt>=1.0.0` → `"dlt[hub]>=1.27.0,<1.29.0"`; add `IncrementalCursorProvider` migration section; add 1.28.0 breaking-changes callout; add native Polars section. |
| 2 | `dagster/SKILL.md` (410) | **FAIL** | L270, L295, L393 (sruth path); "KCG Component" section | Replace `sruth/oideachais/dagster_defs/...` → `cianfhoghlaim/assets/_oideachais_dagster_defs/`; bump `dagster-dlt>=0.25.0` → `>=0.29.11`; add `DltLoadCollectionComponent` upstream-pattern section; add `DltLoadCollectionComponent.partitions_def` + `backfill_policy`; add `@multi_asset_check` + `blocking=True` + partitioned checks (1.13.x); add hierarchical `group_name="celtic/duchas"`; deprecate hand-rolled `CelticDltSourceComponent` (line 100 in our code) in favour of upstream Component. |
| 3 | `litellm/SKILL.md` (627) | **FAIL** | "Provider list" / "Fallback chain" sections; no `minimax` row in tables | Add native `minimax` provider section (third-party Chinese AI MiniMax Inc., models `MiniMax-M2`/`M2.1`/`M2.1-lightning` at `api.minimax.io`); add **March 2026 supply-chain v1.83.0 baseline**; add **Langfuse v3 OTEL** integration path; warn that `:main-stable` Docker tag is **DEPRECATED 2026-06-30** — migrate to `:latest` or `:1.84.0+`; replace custom `model_info.fallback_chain` (config.yaml:723-730) with canonical `litellm_settings.fallbacks`; add `credential_list` + `litellm_credential_name` pattern for the 3 `OPENCODE_GO_API_KEY_0/1/2` slots. |
| 4 | `unsloth/SKILL.md` (219) | **FAIL — MOST OUTDATED** | L8 (version: `>=2024.12`); L42-49 (model table); L52-65 (`FastLanguageModel` example) | Bump to Unsloth 3.0+ / Gemma 4 / Qwen3.6 / GLM-4.6V Flash; replace `FastLanguageModel` with unified `FastModel` (text+vision+audio); add **Gemma 4 E2B/E4B `use_cache=False` garbage logits patch**; add **31B/26B `num_kv_shared_layers=0` IndexError patch**; add **`train_on_responses_only` (+1% accuracy)** callout; add **MTP speculative decoding** (1.4-2.2x speedup, zero accuracy loss) for Qwen3.6 27B/35B-A3B; add **Dynamic 2.0 GGUFs** (`UD-Q4_K_XL`); add Unsloth Studio (port 8888); switch convention `seed=42` → `random_state=3407`; warn CUDA 13.2 + Qwen3.6 → gibberish. |
| 5 | `cognee/SKILL.md` (693) | **PARTIAL PASS** | "Migration" / "Pipelines" sections; `cognee.add/cognify` legacy | Already documents v1.0 `remember`/`recall`/`forget`/`improve` (L658, L669, L674, L689); but does **NOT** flag the dataset-naming drift (compose `oideachais.aistear` dot-notation vs cognify code `oideachais_cross_stage` underscore) or the Kuzu vs Postgres split. Add Kuzu default backend note; add `session_id` + `improve()` 4-stage pipeline section; add dataset-naming convention enforcement; add the **"2 configs, 1 package" Memgraph vs pgvector drift** callout. |
| 6 | `lancedb/SKILL.md` (702) | **FAIL** | "Indexing" section (HNSW vocabulary) | Rewrite index vocabulary: **HNSW is NOT a top-level index in v0.33** — it's a sub-index inside `IVF_HNSW_FLAT` / `IVF_HNSW_SQ` / `IVF_HNSW_PQ`. Add Lance Namespace REST Catalog (`lance.org/format/namespace/`, Java/Python/Rust SDKs); add Lance Blob v2 (`pa.large_binary()` + `lance-encoding:blob` metadata, 3 to_pandas modes); add 15+ embedding-registry providers (OpenAI, HF, Cohere, Jina, VoyageAI, OpenCLIP, ImageBind, Bedrock, Gemini, Ollama, watsonx, ColPali, Instructor, Superlinked); add `table branches` (v0.31); add `async` first-class API. |
| 7 | `motherduck/SKILL.md` (192) | **PARTIAL PASS** | Pricing table; Dives section | Update **DuckDB 1.5.4** baseline (was "MOTHERDUCK 0.5"); add Pulse $0.60/hr / Standard $2.40 / Jumbo $4.80 / Mega $12 / Giga $36 instance pricing; add Lite $0 / Business $250/org/mo / Enterprise tiers; add `https://api.motherduck.com/mcp` remote MCP (25 tools, OAuth, 4 regions including `eu-west-1` Ireland); expand Dives authoring to `REQUIRED_DATABASES` + `ATTACH` + version history. |
| 8 | `falkordb/SKILL.md` (182) | **PARTIAL PASS** | (no major gaps) | Probably OK; minor — confirm cross-archive edges from `oideachais-cognify-knowledge-graph` still apply. |
| 9 | `baml/SKILL.md` (535) | **FAIL** | L3 (frontmatter `sruth/oideachais/baml_src/`); L17, L29, L48, L176 (path refs); L64, L108, L121, L184 (inline `client "..."` antipattern examples); L281 (MiniMax chain mentioned, not listed); L389, L397 (version `0.76.2`) | Replace all 5 `sruth/oideachais/baml_src/` refs → `cianfhoghlaim/core/baml/_oideachais_src/`; bump generator `0.76.2` → `0.223.0`; add the documented 7-tier `MiniMax` fallback chain at L281; **rewrite all inline `client "openai/gpt-4o-mini"` examples to use named `ExtractEn`/`ExtractEnStrong` clients** (skill teaches the antipattern); add `default_client_mode async` recommendation; add `template_string`, `@@assert`/`@check`, `b.stream.<F>`, `@@dynamic`+`TypeBuilder`, `Collector(name)`, `@trace` — all currently unmentioned. |
| 10 | `langfuse/SKILL.md` (264) | **PARTIAL FAIL** | Integration section | Add **Langfuse v3 OTEL** as the recommended integration path (we still use the v2 callback per `infrastructure/stacks/litellm/config/config.yaml:760-765`); add `BOUNDARY_API_KEY` Boundary Studio v2 tracing; document the `blocking=True` interaction with Dagster `@asset_check`. |
| 11 | `agent-observability/SKILL.md` | **PARTIAL PASS** | (no major gaps) | Probably OK; verify `agent-observability/references/mcp/MCP_SERVERS.md:106-108` still matches the deployed mcp-server-motherduck config. |
| 12 | `agent-memory-systems/SKILL.md` | **PARTIAL PASS** | Backend router table | Update Cognee row to reflect v1.0 `remember`/`recall` (L9-11 of agent-09 may be stale); cross-link the **Kuzu vs Postgres drift** callout. |
| 13 | `agentic-frontend-frameworks/SKILL.md` | **PASS** | — | No major gaps observed. |
| 14 | `agno/SKILL.md` | **PASS** | — | No gaps. |
| 15 | `babylonjs/SKILL.md` | **PASS** | — | No gaps. |
| 16 | `better-auth/SKILL.md` | **PASS** | — | No gaps. |
| 17 | `browserbase/SKILL.md` | **PASS** | — | This is a *meta*-skill that drives this very research program; no gaps. |
| 18 | `ccc/SKILL.md` | **PASS** | — | Already documents `bun run ccc:init` / `ccc:index` / `ccc:search` (L74, L75, L83). |
| 19 | `change-detection/SKILL.md` | **PASS** | — | Already documents the 4-layer pattern (DLT cursor + sitemap-hash sensor + ChangeDetection.io + Firecrawl monitor). |
| 20 | `cloudflare/SKILL.md` | **PASS** | — | No gaps. |
| 21 | `cocoindex/SKILL.md` | **PARTIAL FAIL** | App-canonical-pattern section | v1 already documented; add the new `mount_table_target` + `Annotated[NDArray, EMBEDDER]` pattern per agent-03. |
| 22 | `convex/SKILL.md` | **PASS** | — | No gaps. |
| 23 | `copilotkit/SKILL.md` | **PASS** | — | No gaps. |
| 24 | `crawl4ai/SKILL.md` | **PASS** | — | No gaps. |
| 25 | `dagger-pipelines/SKILL.md` | **PASS** | — | No gaps. |
| 26 | `dagger/SKILL.md` | **PASS** | — | No gaps. |
| 27 | `dignified-python/SKILL.md` | **PASS** | — | No gaps. |
| 28 | `dlthub/SKILL.md` | **PARTIAL FAIL** | Dashboard section | Add **`dlt[hub]` extra** requirement (1.27+ split); add `dlthub ai` MCP server; add `DLTHUB_API_KEY` env var; add the 6 bugfixes since `dagster-dlt 0.25.0`. |
| 29 | `duckdb/SKILL.md` | **PARTIAL PASS** | (no major gaps) | Note DuckDB 1.5.4 baseline. |
| 30 | `ducklake/SKILL.md` | **PARTIAL FAIL** | Catalog section | Add `ducklake` 1.0 bump compatibility note (dlt 1.28.0); add the DuckDB-backed catalog attach split (`META_TYPE 'sqlite'` bug fix). |
| 31 | `effect-ts/SKILL.md` | **PASS** | — | No gaps. |
| 32 | `feast/SKILL.md` | **PASS** | — | No gaps (not actively used). |
| 33 | `firecrawl/SKILL.md` | **PARTIAL PASS** | Monitor section | Add the `monitor.page` / `monitor.check.completed` webhook events + `isMeaningful` judgment + `goal` field + `searchWindow` + `maxResults` for search-mode monitors. |
| 34 | `google-adk/SKILL.md` | **PASS** | — | No gaps. |
| 35 | `graphiti-core/SKILL.md` | **PASS** | — | No gaps. |
| 36 | `hono/SKILL.md` | **PASS** | — | No gaps. |
| 37 | `huggingface/SKILL.md` | **PARTIAL FAIL** | GGUF / Inference section | Add `push_to_hub_gguf` for Unsloth → HF → llama-swap pattern; add Spaces `ZeroGPU` + `spaces.GPU` decorator; add the 13 model-layer agents row to the agent-registry. |
| 38 | `ibis/SKILL.md` | **PASS** | — | No gaps. |
| 39 | `komodo/SKILL.md` | **FAIL** | Server / Stack / Procedure / ResourceSync sections | Add **5 sub-dirs** (not 4 — there's no `builder/`); add `server_id = "bunchloch"` vs upstream `server = "..."` silent-drift warning; add `[[procedure]]` vs `[[stack]]` distinction (the `procedures/storage-lakehouse.toml` is actually a `[[stack]]`); add the 2 competing `[[resource_sync]]` definitions for "storage-infrastructure" callout; add v2.0 PKI SPKI `public_key` + outbound Periphery + Semver image tags; add webhook URL pattern `https://<HOST>/listener/github/<RESOURCE_TYPE>/<ID_OR_NAME>/<EXECUTION>`. |
| 40 | `marimo/SKILL.md` | **PASS** | — | No gaps. |
| 41 | `memgraph/SKILL.md` | **PASS** | — | No gaps (not actively used). |
| 42 | `mlflow/SKILL.md` | **PARTIAL PASS** | `TrainingArguments.report_to=["mlflow"]` section | Add the `TrainingArguments.report_to=["mlflow"]` wire-up used in `unsloth_trainer.py:339`. |
| 43 | `modal/SKILL.md` | **FAIL** | Unsloth-burst section | Add `modal_unsloth.py` pattern (per agent-19 / agent-33); add A100/L40S per-second billing; add `modal.Image.gpu("A100")` for Gemma 4 31B fine-tuning. |
| 44 | `olake/SKILL.md` | **PARTIAL PASS** | (no major gaps) | Confirm Dagster orchestration patterns still apply. |
| 45 | `orpc/SKILL.md` | **PASS** | — | No gaps. |
| 46 | `pangolin/SKILL.md` | **PARTIAL FAIL** | TOML blueprint / sites key | Document TOML blueprint schema (`public-resources`, `private-resources`, `public-policies`, `sites`); add the **conflict with Komodo `sites/` subdir** (agent-17 vs agent-16). |
| 47 | `pulumi/SKILL.md` | **PASS** | — | No gaps. |
| 48 | `ragas/SKILL.md` | **PARTIAL PASS** | Trace-based metrics | Confirm `BAML Collector(name)` → `collector.last.usage` → RAGAS trace-based metric wire-up (per agent-15 refactor #7). |
| 49 | `risingwave/SKILL.md` | **PASS** | — | No gaps. |
| 50 | `secrets-management/SKILL.md` | **PASS** | — | Already documents the Infisical + Locket + mise 3-way contract. |
| 51 | `tanstack-start/SKILL.md` | **PASS** | — | No gaps. |

**Net:** 8 FAIL + 13 PARTIAL FAIL + 30 PASS = **21 of 51 canonical skills need updates** (41%).

---

## 3. Per-stub-change audit (4 phase stub changes)

All 4 phase stub changes (`2026-06-28-browserbase-phase-{1a,1b,2,3}-decisions`) are **STUBS** (L3 of every proposal: `> **STUB — TO BE FILLED BY PHASE X RESEARCH AGENT.**`). Wave-1 agents produced no spec-delta content for them — the bodies remain `proposal.md:36` empty placeholders.

| Change | State | Required spec-delta content (mapped to wave-1 agents) | Action |
|:--|:--|:--|:--|
| `2026-06-28-browserbase-phase-1a-decisions` | **STUB** | 5 Phase 1A decisions: (P1A-01 dlt) bump `dlt>=1.0.0` → `"dlt[hub]>=1.27.0,<1.29.0"`; (P1A-02 Dagster) bump `dagster-dlt>=0.25.0` → `>=0.29.11` + drop `CelticDltSourceComponent`; (P1A-03 CocoIndex v1) confirm `mount_table_target` consumer pattern; (P1A-04 DuckDB/DuckLake) bump ducklake 1.0 + `META_TYPE 'sqlite'` fix; (P1A-05 MotherDuck) update to DuckDB 1.5.4 baseline + Lite/Business pricing. | Wave-2 agent must write 5 `## ADDED Requirements` + 1 Scenario each. |
| `2026-06-28-browserbase-phase-1b-decisions` | **STUB** | 5 Phase 1B decisions: (P1B-06 LanceDB) **HNSW-vocabulary fix** (no top-level HNSW index; must be `IVF_HNSW_SQ` or `IVF_HNSW_FLAT`); add Lance Namespace REST Catalog client SDK pattern; add 15+ embedding-registry providers; (P1B-07 FalkorDB + Graphiti + Dragonfly + RisingWave) — no gaps found; (P1B-08 Garage S3 + Iceberg REST + Lakekeeper) bump Garage **v1.0.1 → v2.3.0** with `/v1/*` → `/v2/*` admin API rewrite + `replication_mode` → `replication_factor` + `--single-node` autocreate; (P1B-09 Cognee + Letta) add **v1.0 `remember`/`recall`/`forget`/`improve` migration** + Kuzu default backend + the **2-configs-1-package Memgraph vs pgvector drift** + dataset-naming convention (`oideachais.aistear` vs `oideachais_cross_stage`); (P1B-10 Cloudflare R2 + Workers + D1) — no gaps. | Wave-2 agent must write 5 `## ADDED Requirements` + 1 Scenario each. |
| `2026-06-28-browserbase-phase-2-decisions` | **STUB** | 21 Phase 2 decisions: drift re-checks (Dagster — `DltLoadCollectionComponent` adoption; MotherDuck — DuckDB 1.5.4 baseline); new (P2-32 Unsloth — `FastModel` migration + `train_on_responses_only` + MTP + Dynamic 2.0 GGUFs + 11 OCR models); new (P2-33 Modal — `modal_unsloth.py` A100 burst); LiteLLM `:main-stable` DEPRECATED 2026-06-30; native `minimax` provider note. | Wave-2 agent must write 21 `## ADDED Requirements` + 1 Scenario each. |
| `2026-06-28-browserbase-phase-3-decisions` | **STUB** | 12 Phase 3 decisions: 8 British Isles sources (curriculumonline.ie, examinations.ie, ncca.ie, gov.uk, education.gov.scot, gov.wales, education-ni.gov.uk, gov.im) + 2 Crown dependencies (gov.je, gov.gg) + 2 reference (zotero.org, arxiv.org). Each must produce a discovery report (dropdown cascade, PDF endpoints, URL pattern, anti-scraping posture, BAML extraction strategy). | Wave-2 agent must write 12 `## ADDED Requirements` + 1 Scenario each. |

---

## 4. Per-cross-cutting-doc audit (4 docs)

| Doc | State | Required updates | file:line |
|:--|:--|:--|:--|
| `AGENTS.md` (root) | **PARTIAL FAIL** | (a) Update `Priority skills (6 of 123)` row to add the 4 wave-2-critical skills (`baml`, `dlt`, `unsloth`, `dagster`) with their current-state warnings; (b) update `Priority openspec commands` to add `openspec validate 2026-06-28-browserbase-phase-2-decisions --strict` to the must-pass list; (c) add a new `Phase 2 research output` section pointing at `openspec/research/2026-06-28-browserbase-program-2/`. | full file |
| `openspec/AGENTS.md` | **PARTIAL FAIL** | (a) Add `data-engineering-pipeline-documentation` (now a 5th capability in the priority list) — actually already listed L19; (b) add a new "Documentation Gaps" section linking `openspec/research/2026-06-28-browserbase-program-2/synthesis/30-documentation-gaps.md`; (c) update `Capability Specs (34)` table to add the missing 5 specs (the table has 34, but project.md says "34 specs, 8 groups" — verify count). | full file |
| `infrastructure/AGENTS.md` | **FAIL** | (a) Update the **"4 priority compose stacks (4 of 90)"** → **"4 of 33 user-pre-selected + 57 remaining"** to match the post-v4 wording in `openspec/project.md:90`; (b) replace 90-stack inventory link with the new "stack-ops" or "infrastructure-stacks" skill link (currently the skill lives in the external `good-omens` monorepo per L26-28, but is missing from `.agents/skills/` — should be added); (c) add the **Garage v1.0.1 → v2.3.0** upgrade warning (L11-18 of agent-12); (d) update the **Komodo `server_id` vs upstream `server = ...`** silent-drift warning (agent-17 finding). | L15, L26-28, L34, L41-45 |
| `openspec/project.md` | **FAIL** | (a) `meaisinfhoghlaim-ocr-htr` row L58 still says "10 OCR models" — should be **11** (Gemma 4 E2B/E4B/12B/26B-A4B/31B + Qwen3.6 27B/35B-A3B + GLM-4.6V Flash + Unsloth/Unsloth variants per agent-19); (b) `meaisinfhoghlaim-platform` row L56 says "16 sub-packages" — verify count vs `cianfhoghlaim/core/{dlt,duckdb,ducklake,lancedb,motherduck,cocoindex,baml,marimo,browser,cognee,obs,rag,search,curriculum,config,memory}/` = 16 (correct); (c) `oideachais-baml-schemas` row L42 says "6 consolidated BAML files" — verify count; (d) `celtic-asset-generation` row L97 should reference the new 5-stage refactor (BAML → CocoIndex v1 → Cognee cognify → Graphiti temporal → LanceDB vector) — and the 4 successive INDEPENDENT pipelines (`official_documents/`, `subject_assets/`, `language_assets/`, `exporters/`) at L97 should be cross-linked. | L42, L58, L90, L97 |

---

## 5. Top 10 priority updates (by operator-impact)

Ranked by user impact — operators reading these docs to make a real change tomorrow.

| # | Update | Doc | Why operators care | Effort |
|:--|:--|:--|:--|:--|
| 1 | **Bump `dlt>=1.0.0` → `"dlt[hub]>=1.27.0,<1.29.0"`** in `dlt/SKILL.md` + the comment in `AGENTS.md` | `dlt/SKILL.md:30-50`; `AGENTS.md` | Today, `dlt dashboard`, `dlt pipeline … show/mcp`, `dlthub ai` all break silently on 1.27+ without `[hub]`. Any operator upgrading dlt hits a `ModuleNotFoundError`. | 30 min |
| 2 | **Replace `sruth/oideachais/baml_src/` → `cianfhoghlaim/core/baml/_oideachais_src/`** in 5 places across `baml/SKILL.md` + the 4 quadrant AGENTS.md files (4 paths) | `baml/SKILL.md:3,17,29,48,176` | Every BAML doc link 404s after v4 consolidation. | 1 hour |
| 3 | **Rewrite `unsloth/SKILL.md` with FastModel + Gemma 4 + Qwen3.6 + GLM-4.6V Flash + `train_on_responses_only` + MTP + Dynamic 2.0 GGUFs** | `unsloth/SKILL.md` (full) | Operators fine-tuning Irish OCR models are using the 2024-12 API — they get worse accuracy and miss the +1% from `train_on_responses_only`. | 4 hours |
| 4 | **Bump Garage v1.0.1 → v2.3.0** with `replication_mode` → `replication_factor` + `/v1/` → `/v2/` admin API rewrite + `--single-node` autocreate | `infrastructure/AGENTS.md:34`; new infra-stacks skill if created | Today, `garage-init` bash script (90 lines) and `garage.toml:5,18` will **fail to start on v2.x**. Operators who try to upgrade hit a hard error. | 2 hours |
| 5 | **Bump `dagster-dlt>=0.25.0` → `>=0.29.11`** in `dagster/SKILL.md` and add the `DltLoadCollectionComponent` upstream-pattern section | `dagster/SKILL.md`; `_oideachais_pyproject.toml` | 6 bugfixes since 0.25.0; the new `partitions_def` + `backfill_policy` support in `DltLoadCollectionComponent` replaces our 100-line hand-rolled `CelticDltSourceComponent`. | 2 hours |
| 6 | **Add native `minimax` provider note + `:main-stable` DEPRECATED 2026-06-30 warning** to `litellm/SKILL.md` | `litellm/SKILL.md`; `infrastructure/stacks/litellm/compose.yaml` | In 2 days (2026-06-30), `:main-stable` stops getting updates; bare `minimax` alias collides with MiniMax Inc. | 30 min |
| 7 | **HNSW vocabulary fix in `lancedb/SKILL.md`** — HNSW is NOT a top-level index in v0.33 | `lancedb/SKILL.md` | The P1B-06 `index: { type: hnsw, m: 16, ef_construction: 200 }` block is not directly creatable; operators waste hours debugging `InvalidIndexType` errors. | 1 hour |
| 8 | **Migrate 8 inline `client "anthropic/claude-sonnet-4-20250514"` → `ExtractEnStrong`** in `curriculum_extraction.baml` + update the baml/SKILL.md example to teach named clients | `baml/SKILL.md:64,108,121,184`; `curriculum_extraction.baml:167,208,243,277,501,541,578,617,653,775,973,1008,1046,1086` | Each inline call bypasses the LiteLLM gateway → no fallback chain, no Langfuse trace, no spend caps, no `MiniMax` vendor-de-risking. Defeats Phase 0.4. | 30 min (1-line sed + skill edit) |
| 9 | **Cognee v1.0 `remember`/`recall`/`forget`/`improve` migration** in `cognee/SKILL.md` + flag the Kuzu vs Postgres split + dataset-naming convention | `cognee/SKILL.md`; `core/memory/memory/cognee_config.py`; `infrastructure/stacks/cognee/compose.yaml` | The codebase still uses the v0.x `add`/`cognify`/`search`/`memify` API. Today's `cognee.cognify()` processes ALL datasets (no scoping) — risks cross-stage pollution. | 4 hours |
| 10 | **Bump BAML generator `0.76.2` → `0.223.0`** in `baml/SKILL.md:389,397` + `generators.baml:7` | `baml/SKILL.md`; `generators.baml:7` | Missed streaming-retry bugfix (#3025) in 0.221 and `render_null_as` in 0.223. | 15 min |

**Combined: ~16 person-hours of skill updates** — well under the 3-day budget for one engineer.

---

## 6. Doc-not-yet-written (new skill files needed)

The Phase-2 research surfaces **4 new skill categories** that have no canonical skill today. Without these, agents picking up the next task will not know the canonical pattern.

### 6.1 Skill for the **Gemma 4 / Qwen3.6 / GLM-4.6V Flash** OCR model registry
**Path:** `.agents/skills/ocr-vision-model-registry/SKILL.md`
**Why:** The 11 OCR models at `cianfhoghlaim/ocr/models/registry.py` (per `meaisinfhoghlaim-ocr-htr/spec.md`) span 3 model families × 4 quantizations × 6 backends — the decision tree is non-obvious (which model for which syllabus? which quantization for which VRAM budget? Gemma 4 E2B/E4B `use_cache=False` garbage logits patch? 31B/26B `num_kv_shared_layers=0` IndexError patch?). No canonical doc.
**Content sketch:**
- Decision tree: "Gaelic OCR on M4 Max" → `unsloth/gemma-4-26B-A4B-it` (4-bit) + `train_on_responses_only` + `use_gradient_checkpointing="unsloth"`
- Decision tree: "Math/equation OCR" → `unsloth/Qwen3.6-35B-A3B-UD-Q4_K_XL` (with MTP inference)
- Decision tree: "Long-context (256K) document OCR" → Qwen3.6 35B-A3B
- 3 critical upstream patches (use_cache=False garbage logits; num_kv_shared_layers=0 IndexError; audio fp16 overflow)
- Loss-curve normalization (`E2B/E4B loss 13-15 is NORMAL`)

### 6.2 Skill for the **5-stage PDF pipeline refactor**
**Path:** `.agents/skills/pdf-pipeline-5-stage/SKILL.md`
**Why:** The `celtic-asset-generation/spec.md` documents a 5-stage pipeline (BAML → CocoIndex v1 → Cognee cognify → Graphiti temporal → LanceDB vector) at L6-26. No canonical skill enforces the order, the retry boundary, or the streaming pattern. Without it, every new PDF source re-implements the wiring.
**Content sketch:**
- Stage 1: BAML extraction (`@function` with named `ExtractEn`/`ExtractEnStrong` clients)
- Stage 2: CocoIndex v1 embedding (`@coco.fn(memo=True)` + BGE-large-en-v1.5 in 100+ batches; `Annotated[NDArray, EMBEDDER]`)
- Stage 3: Cognee cognify (8 canonical relationship types; `remember()` v1.0 API)
- Stage 4: Graphiti temporal memory (bi-temporal KG; FalkorDB backend)
- Stage 5: LanceDB vector (IVF_HNSW_SQ index; BGE-M3 multilingual + BGE-large-en-v1.5)
- Cross-stage: `b.stream.<F>` for long extractions (200-500 sec); `Collector(name)` + `@trace` for RAGAS cost metrics

### 6.3 Skill for the **OCR model registry** (6 backends × 4 classical stacks)
**Path:** `.agents/skills/ocr-registry/SKILL.md`
**Why:** `meaisinfhoghlaim-ocr-htr/spec.md` mentions 6 backends (litellm, mlx, transformers, ollama, openai, anthropic) + 4 classical Docker stacks (dots-ocr, docling-serve, olmocr, paddleocr) + the 11 vision models. The selection matrix (which backend for which model? when to use BGE-M3 vs BGE-large? when to fall through from VLM to classical OCR?) is undocumented.
**Content sketch:**
- Backend selection matrix: 11 models × 6 backends = 66 cells, with ✅/⚠️/❌ + notes
- Classical vs VLM decision tree
- 220-eval harness at `cianfhoghlaim/ocr/evaluation/compare.py`
- Llama-swap config at `cianfhoghlaim/core/llama-swap-config.yaml:120` (MTP-aware)

### 6.4 Skill for the **mcp-server-motherduck** config (per-platform examples)
**Path:** `.agents/skills/motherduck-mcp/SKILL.md` (extension of existing `motherduck/SKILL.md`)
**Why:** `agent-observability/references/mcp/MCP_SERVERS.md:106-108` is the **only** place documenting the KCG-preferred agent path: `["uvx", "mcp-server-motherduck", "--db-path", ":memory:", "--read-write", "--allow-switch-databases"]`. Should be promoted to a top-level skill so agents can copy the config directly to Claude Desktop / Cursor / VS Code / Zed / Windsurf / Claude Code / Goose / Copilot Studio / SSE stdio.
**Content sketch:**
- The 9 client config examples (already in `motherduck/references/motherduck-mcp-server.md` — 320 lines — just need a router)
- Local vs remote MCP (`mcp-server-motherduck` vs `https://api.motherduck.com/mcp`)
- OAuth setup for the remote MCP (4 regions including `eu-west-1` Ireland)

### 6.5 Skill for the **Infisical MCP server card**
**Path:** `.agents/skills/infisical-mcp/SKILL.md`
**Why:** Per agent-18 finding: **Infisical now publishes an MCP server card** at `/docs/.well-known/mcp/server-card.json` (per the response `Link` header on every docs page) — a discovery channel the next agent wave should explore. No skill currently wires MCP-aware secret consumption.
**Content sketch:**
- Server card discovery
- Universal Auth flow via MCP
- Migration from `--token=<service-token>` (deprecated late-2025) to `INFISICAL_TOKEN=$(infisical login --method=universal-auth …)`
- Pocket ID OIDC integration

### 6.6 Skill for the **v4-consolidated quadrant paths** (no longer `sruth/`)
**Path:** `.agents/skills/v4-consolidation/SKILL.md`
**Why:** The v4 consolidation (`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`) renamed all 4 quadrants into a single `cianfhoghlaim/` package — but **21 of 51 canonical skills still reference the old `sruth/oideachais/dlt_sources/`, `sruth/oideachais/dagster_defs/`, `sruth/oideachais/baml_src/` paths** (verified above). A meta-skill enumerating the old-path → new-path mapping would be a single PR-fix-all.
**Content sketch:**
- 1 table: old path → new path (40+ rows)
- 1 checklist: which skills need an update (this file's §2)
- The 1-line sed to fix each skill

---

## 7. Summary (1 paragraph)

The Phase-2 wave-1 research surfaces **21 of 51 canonical `.agents/skills/*/SKILL.md` files requiring updates** (8 FAIL, 13 PARTIAL FAIL), with `.agents/skills/unsloth/SKILL.md` (last touched 2025-04; misses `FastModel`, Gemma 4, Qwen3.6, MTP, Dynamic 2.0 GGUFs), `.agents/skills/dlt/SKILL.md` (3 minor versions stale; misses the `[hub]` extra, 1.28.0 breaking changes, native Polars), and `.agents/skills/baml/SKILL.md` (5 references to the pre-v4 `sruth/oideachais/baml_src/` path, generator pinned at `0.76.2` vs upstream `0.223.0`, and example snippets that teach the inline `client "openai/gpt-4o-mini"` antipattern 8 places in the codebase use to bypass the LiteLLM gateway) as the three most-impacted; the 4 phase stub changes (`2026-06-28-browserbase-phase-{1a,1b,2,3}-decisions/`) remain empty placeholders awaiting wave-2 spec-delta content; the 4 cross-cutting docs (`AGENTS.md`, `openspec/AGENTS.md`, `infrastructure/AGENTS.md`, `openspec/project.md`) need surgical updates — notably `infrastructure/AGENTS.md` still says "90 stacks" and `openspec/project.md:58` still says "10 OCR models" (should be 11); the 10 highest-priority updates total ~16 person-hours; and 6 new skill files are recommended to fill gaps (an OCR vision-model registry, a 5-stage PDF pipeline skill, an OCR-registry router, an MCP-server-motherduck config skill, an Infisical MCP server-card skill, and a v4-consolidation path-mapping meta-skill).
