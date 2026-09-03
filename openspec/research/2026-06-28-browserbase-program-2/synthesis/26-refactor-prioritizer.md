# Agent 26 — Refactor Prioritizer (Wave 2 synthesis)

**Date:** 2026-06-28 · **Budget:** 0 BrowserBase credits (read-only synthesis) · **Sources:** 25 wave-1 agent outputs + SHARED_DISCOVERY_LOG.md + P1A/P1B/P2/P3 first-pass research

---

## 1. TL;DR

Three takeaways:

1. **P0 has 11 BLOCKING items, two of them already silently broken in production.** FalkorDB is missing `vector.so` (every vector query 404s), Garage is pinned to v1.0.1 with `replication_mode` (will not start on v2.x), dlt's plain pin `dlt>=1.0.0` will break `dlt dashboard` the day we bump past 1.27, Cognee references the non-existent `SearchType.INSIGHTS` (AttributeError on import), and LiteLLM's `main-stable` Docker tag is deprecated on **2026-06-30 — 2 days from today**. P0 must be triaged this week.
2. **Cross-cutting dependency: BAML, dlt, dagster-dlt, cocoindex, lancedb, falkordb all share a single "engine v1.x + langfuse v3 + storage v2.x" cutover.** Doing P0 fixes in isolation will cause 3× the work — bundle the LiteLLM→Langfuse-OTEL + dlt-[hub] + dagster-dlt-0.29.11 + cocoindex-1.0.14 + LanceDB-0.33 + FalkorDB-vector.so changes into one coordinated release train.
3. **~150 refactor items consolidate to ~30 P0/P1 + ~40 P2 + ~80 P3.** 80% of value is in 20% of items — the 11 P0s and 13 P1s below.

---

## 2. Methodology

Prioritization axes (in order of weight):

| Axis | Weight | Why |
|:--|:-:|:--|
| **Silent breakage** (works today, fails tomorrow) | 5× | E.g. FalkorDB vector.so — every vector call 404s in production today |
| **Hard date / upstream deadline** | 4× | LiteLLM main-stable cutover 2026-06-30, Infisical CLI repo 2026-09-16 |
| **Cross-stack blast radius** | 3× | E.g. BAML inline clients affect all 5 BAML sub-packages; Komodo `server_id` rename affects 30+ stacks |
| **Removes maintenance burden** | 2× | Dead code (Dragonfly duplicate stack), obsolete specs (P1A-04, P2-20, P2-23) |
| **UX/feature gain** | 1× | CocoIndex HNSW (100× search speedup), BAML Collector (cost tracking) |

Effort: **S** = ≤1 day, **M** = 2-5 days, **L** = 1-2 weeks. Risk: low/med/high.

Cross-referenced against the 34 openspec capability specs in `openspec/specs/` (priority: `oideachais-pipeline`, `infrastructure-stacks`, `agent-memory-systems`, `indexing-and-cognition`, `dagger-pipelines`).

---

## 3. P0 — Critical, 1-2 weeks (BLOCKING or silently broken)

| # | Item | File:line | Current → Target | Effort | Risk | PR title |
|:-:|:--|:--|:--|:-:|:-:|:--|
| **P0-1** | **FalkorDB `vector.so` loadable missing** — every `db.idx.vector.queryNodes` 404s | `infrastructure/stacks/falkordb/compose.yaml:18-37` | no `command:` → add `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]` | S | high (silent prod failure today) | `fix(falkordb): load vector.so for HNSW vector queries` |
| **P0-2** | **Garage v1→v2 breaking-change drift** — `replication_mode` removed + admin API `/v1→/v2` | `infrastructure/stacks/garage/compose.yaml:21`, `garage.toml:5`; `infrastructure/stacks/lakehouse/compose.yaml:30,71-160`, `garage.toml:18,31,68` | v1.0.1 + `replication_mode="1"` + `/v1/*` API → v2.3.0 + `replication_factor=1` + `/v2/*` API | M | med (read path unchanged; admin/init rewrite) | `fix(garage): upgrade v1.0.1→v2.3.0 + migrate config syntax` |
| **P0-3** | **dlt pin missing `[hub]` extra** — bump to 1.27+ breaks dashboard/MCP/AI silently | `cianfhoghlaim/pyproject.toml:39` | `dlt>=1.0.0` → `"dlt[hub]>=1.27.0,<1.29.0"` | S | med (silent in CI, breaks in prod) | `fix(dlt): add [hub] extra for 1.27+ workspace split` |
| **P0-4** | **LiteLLM `main-stable` Docker tag deprecation** — 2 days until cutover | `infrastructure/stacks/litellm/compose.yaml` | `ghcr.io/berriai/litellm:main-stable` → `:1.84.0` (pin) or `:latest` (roll) | S | high (2026-06-30 deadline) | `fix(litellm): migrate main-stable→1.84.0 pin before 2026-06-30 cutover` |
| **P0-5** | **Cognee `SearchType.INSIGHTS` doesn't exist** — `AttributeError` at import | `cianfhoghlaim/core/memory/memory/cognee_service.py:376` | `SearchType.INSIGHTS` → `SearchType.SUMMARIES` (v1.2.2 compatible) | S | high (runtime crash) | `fix(cognee): replace SearchType.INSIGHTS with SUMMARIES` |
| **P0-6** | **dlt source path drift** — P1A-01 spec points to `cianfhoghlaim/dlt_sources/` (404) | `openspec/research/2026-06-28-browserbase-credit-program/phase-1a/P1A-01-dlt-dlthub-pro.md:1-50` | path → `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` (190 files) | S | med (misleading spec) | `docs(dlt): fix P1A-01 source path post-v4 consolidation` |
| **P0-7** | **DuckLake path drift + version pin** — P1A-04 ref non-existent file + `ducklake<1.0` blocks 1.0 features | `openspec/research/.../phase-1a/P1A-04-duckdb-ducklake.md:43,142-146` | path → `stedding/.../ducklake_client.py`; pin `ducklake>=1.0,<2.0` | S | med (already using 1.0 features) | `docs(ducklake): fix P1A-04 path + unblock 1.0 pin` |
| **P0-8** | **FalkorDB Cypher injection** — user values f-stringed into query | `cianfhoghlaim/core/cognee/_graph/_shared/falkordb.py:170-177,204-212` | f-string → `graph.query(cypher, params=...)` bound params | S | high (security) | `fix(falkordb): bind user values via params (Cypher injection)` |
| **P0-9** | **MLX-omni broken Docker invocation** — wrong package + non-existent `serve` subcommand | `infrastructure/stacks/mlx-omni/Dockerfile:39` | `mlx-omni serve …` → `mlx-omni-server --port 10240` (real package: `mlx-omni-server` 0.5.3) | S | high (container won't start) | `fix(mlx-omni): correct package + CLI to mlx-omni-server@0.5.3` |
| **P0-10** | **OpenChamber P2-20 fictional spec** — 6 lines reference Postgres/LiteLLM/embed that don't exist | `openspec/research/.../phase-2/P2-20-openchamber.md:1-90` | rewrite to match deployed bundled-mode (named volume + direct keys + no DB) | S | med (misleading spec) | `docs(openchamber): rewrite P2-20 to match deployed reality` |
| **P0-11** | **P2-23 aspirational HF model IDs** — 8 model IDs that don't exist on HF Hub | `openspec/research/.../phase-2/P2-23-huggingface.md:25-47` | `unsloth/gemma-4-*`, `unsloth/Qwen3.6-*` → real `unsloth/gemma-3-*`, `unsloth/Qwen3-*` | S | high (broken `hf_hub_download`) | `docs(hf): replace 8 aspirational P2-23 model IDs with real ones` |

**P0 total: 11 items, ~6-8 days, must land in 1 coordinated release (LiteLLM-OTEL + dlt-[hub] + dagster-dlt-0.29.11 + cocoindex-1.0.14 + LanceDB-0.33 + FalkorDB-vector.so + Garage-v2.3.0 cutover train).**

---

## 4. P1 — High impact, 2-4 weeks

| # | Item | File:line | Current → Target | Effort | Risk | PR title |
|:-:|:--|:--|:--|:-:|:-:|:--|
| **P1-1** | **BAML inline `client "anthropic/..."` bypasses LiteLLM** — 8 calls in curriculum_extraction.baml | `cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml:164-1086` | inline → named `ExtractEn` (gateway-routed, fallback-chain enabled) | M | med (BAML recompile) | `refactor(baml): migrate 8 inline clients to gateway aliases` |
| **P1-2** | **CocoIndex HNSW indexes missing on 5 Apps** — brute-force over 1024-d vectors | `codebase_indexing.py:600-605`, `api_indexing.py:421-443`, `filesystem_indexing.py:271-281`, `storage_indexing.py:449-455`, `config_indexing.py:485-491` | no `declare_vector_index` → `declare_vector_index(column="embedding", index_type="ivf_pq")` | S | low | `perf(cocoindex): add vector indexes to 5 Apps (100× search speedup)` |
| **P1-3** | **LanceDB HNSW index vocabulary drift** — `type: hnsw` invalid in 0.33 | `infrastructure/stacks/lakehouse/lance-namespace/config.yaml` | `type: hnsw` → `index_type: IVF_HNSW_SQ` (or `IVF_PQ`) | S | med (silently fails) | `fix(lancedb): migrate index type to IVF_HNSW_* per v0.33` |
| **P1-4** | **LanceDB `connect_namespace` rewrite** — wrong URI form for REST catalog | `cianfhoghlaim/core/cocoindex/mount_lance.py` | `lancedb.connect("http://...")` → `lancedb.connect_namespace("rest", {"uri":"...","headers.x-api-key":...})` | S | med | `fix(lancedb): adopt v0.33 connect_namespace("rest", ...) client` |
| **P1-5** | **Komodo `server_id` → `server` rename** — 30+ TOMLs use KCG-local key | `infrastructure/komodo/stacks/*.toml` (~30 files) | `server_id = "..."` → `server = "..."` (upstream canonical) | S | low (Core accepts both) | `refactor(komodo): rename server_id→server across 30 stack TOMLs` |
| **P1-6** | **Drop hand-rolled `CelticDltSourceComponent`** — upstream `DltLoadCollectionComponent` supersedes | `cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_dlt_source.py:29-97` | 100-line KCG Component → upstream `DltLoadCollectionComponent` (1.13.9+) | M | med (28+ sources to migrate) | `refactor(dagster): drop CelticDltSourceComponent, adopt DltLoadCollectionComponent` |
| **P1-7** | **Bump `dagster-dlt` 0.25→0.29.11** — 4 minor versions stale; missing `DltLoadCollectionComponent` | `cianfhoghlaim/pyproject.toml` | `dagster-dlt>=0.25,<1.0` → `>=0.29.11,<1.0` (6 bugfixes) | S | low | `fix(dagster-dlt): bump 0.25→0.29.11 (6 bugfixes + Component support)` |
| **P1-8** | **Garage hardcoded secrets** — `rpc_secret` + `admin_token` plaintext in git | `infrastructure/stacks/lakehouse/garage.toml:31,68` | hardcoded → `${GARAGE_RPC_SECRET}` / `${GARAGE_ADMIN_TOKEN}` (envsubst) | S | low | `fix(garage): externalize hardcoded rpc_secret + admin_token to Locket` |
| **P1-9** | **BAML generators version pin** — `0.74.0` (Sept 2024) vs `0.223.0` (Jun 2026) | `cianfhoghlaim/core/baml/_oideachais_src/generators.baml:7` | `version "0.74.0"` → `"0.223.0"` + `default_client_mode async` | S | low (re-gen client) | `fix(baml): bump generators 0.74.0→0.223.0 + switch to async` |
| **P1-10** | **Dragonfly `DRAGONFLY_URL` password mismatch** — 9 consumers omit password; compose has `--requirepass` | `infrastructure/stacks/tuatha/compose.yaml:20` + 8 more | `redis://dragonfly:6379` → drop `--requirepass` (internal-only) OR add `:${PASSWORD}@` to all 9 | S | med (auth) | `fix(dragonfly): align URL password with --requirepass` (or drop auth) |
| **P1-11** | **Cognee dataset naming drift** — dot vs underscore silently misses cross_stage | `infrastructure/stacks/cognee/compose.yaml:42` vs `cognify/cognee_integration/cross_stage_cognify.py:131` | `oideachais_aistear,...` (underscore) → `oideachais.aistear,...` (dot, canonical) | S | high (silent first-cognify miss) | `fix(cognee): align dataset names (dot vs underscore) — pick one` |
| **P1-12** | **CocoIndex embedding model split** — 2 embedding spaces coexist (bge-m3 vs bge-large-en-v1.5) | `_lifespan.py:92`, `codebase_indexing.py:93` | mixed → unified `BAAI/bge-m3` (multilingual, correct for Irish/Welsh) | S | med (one-time re-embed) | `refactor(cocoindex): unify embedding model on bge-m3` |
| **P1-13** | **OpenChamber zero-digest placeholder** — `sha256:0000…` will pass `docker compose config` but pull nothing | `infrastructure/stacks/openchamber/compose.yaml:29` | placeholder → real `@sha256:…` from `docker pull ghcr.io/openchamber/openchamber:1.0.0` | S | high (first-deploy blocker) | `fix(openchamber): resolve real SHA256 digest for v1.0.0 pin` |

**P1 total: 13 items, ~3-4 weeks. Most unlocks 5-10× performance or removes a category of bug.**

---

## 5. P2 — Medium, 1-2 months

| # | Item | File:line | Current → Target | Effort | Risk | PR title |
|:-:|:--|:--|:--|:-:|:-:|:--|
| P2-1 | **HuggingFace CLI migration** — `huggingface-cli` deprecated; use `hf` | `spaces/build-small-2026-runbook.md:26,92,98,304,315,316` + `P2-23-huggingface.md:74` | `huggingface-cli` → `hf` (9 refs) | S | low | `refactor(hf): migrate huggingface-cli→hf CLI` |
| P2-2 | **CocoIndex 1.0.7 engine features** — `memo_key`, `@coco.fn.as_async(batching=True)`, `coco.stats_group` | `codebase_indexing.py` + `leabharlann_embedding.py` | sync + uncached → async + batched + memo-keyed | M | low | `perf(cocoindex): adopt 1.0.7 batching + memo_key + stats_group` |
| P2-3 | **Unsloth `train_on_responses_only`** — QLoRA +1% accuracy win | `cianfhoghlaim/ocr/training/training/unsloth_trainer.py:278` | not called → `unsloth.chat_templates.train_on_responses_only(trainer, ...)` | S | low | `perf(unsloth): add train_on_responses_only (+1% accuracy)` |
| P2-4 | **Unsloth MTP speculative decoding** — 1.4-2.2× inference speedup for Qwen3.6 | `cianfhoghlaim/core/llama-swap-config.yaml:120` | no MTP → `--spec-type draft-mtp --spec-draft-n-max 2` | S | low | `perf(unsloth): enable MTP speculative decoding for Qwen3.6` |
| P2-5 | **Unsloth `random_state=3407`** — upstream convention; current `42` | `cianfhoghlaim/ocr/training/training/unsloth_config.py:103` | `seed=42` → `seed=3407` | S | zero | `refactor(unsloth): align random_state to upstream 3407` |
| P2-6 | **Unsloth `FastVisionModel` → `FastModel`** — unified text+vision+audio loader | `cianfhoghlaim/ocr/training/training/unsloth_trainer.py:108,121` | 3-class API → unified `FastModel.from_pretrained` (3.0+) | M | med | `refactor(unsloth): migrate to FastModel unified loader` |
| P2-7 | **BAML `Collector(name)` + `@trace` in Dagster asset wrapper** — unlocks token/cost tracking | `core/baml/.../extraction` (called from `_oideachais_dagster_defs/`) | no collector → `Collector(name=f"extract_en_{run_id}")` + log usage | M | low | `feat(baml): wire Collector(name) + @trace for RAGAS cost tracking` |
| P2-8 | **Garage `garage-init` 90-line bash → `--single-node` flag** — v2.3.0 obsoletes the sidecar | `infrastructure/stacks/lakehouse/compose.yaml:71-160` | bash init → `command: ["--single-node"]` + `--default-access-key` + `--default-bucket` env | M | low | `refactor(garage): replace garage-init bash with v2.3.0 --single-node flag` |
| P2-9 | **Cognee v1.0 `remember/recall/forget/improve` migration** — 6 files on legacy `add/cognify/search` | `cognify/cognee_integration/*.py` + `core/memory/memory/cognee_service.py:210-346` | legacy → v1.0 `remember/recall` | M | med | `refactor(cognee): migrate 6 files to v1.0 remember/recall API` |
| P2-10 | **Cognee `USE_UNIFIED_PROVIDER=pghybrid` is experimental** | `infrastructure/stacks/cognee/compose.yaml:42-59` | experimental → `GRAPH_DATABASE_PROVIDER=postgres` + Apache AGE | M | med | `refactor(cognee): replace pghybrid with explicit postgres+AGE` |
| P2-11 | **Cognee config drift** — compose uses Postgres-unified, code uses Memgraph+LanceDB | `compose.yaml` vs `core/memory/memory/cognee_config.py:66-94` | two configs → one canonical (or document split) | M | med | `refactor(cognee): reconcile compose vs code config (Postgres vs Memgraph)` |
| P2-12 | **LiteLLM Langfuse v3 OTEL migration** — current uses v2 callback | `infrastructure/stacks/litellm/config/config.yaml:760-765` | v2 callback → OTEL (litellm v3 recommended) | M | low | `refactor(litellm): migrate Langfuse v2 callback→v3 OTEL` |
| P2-13 | **LiteLLM `minimax` provider namespace collision** — our alias vs MiniMax Inc. | `infrastructure/stacks/litellm/config/config.yaml:714-730` + `stacks/litellm/README.md` | bare `minimax` → add disambiguation doc + `model_info.comment` | S | low | `docs(litellm): add minimax alias vs MiniMax Inc. disambiguation` |
| P2-14 | **Pangolin `public-policies` block** — 9 stacks repeat `roles[0]: tinyauth@file` 9× | `infrastructure/pangolin/private-resources.blueprint.yaml` (all 9 stacks) | 9 inline → 1 `public-policies` reusable block | M | med | `refactor(pangolin): consolidate 9 tinyauth@file into public-policies` |
| P2-15 | **Pangolin `sites:` multi-site failover** — Newt blueprint needs `newt-oci` + `newt-bunchloch` | `infrastructure/pangolin/private-resources.blueprint.yaml` | omit `sites:` → add 2-peer failover | M | med | `refactor(pangolin): add multi-site Newt failover (newt-oci + newt-bunchloch)` |
| P2-16 | **Komodo `procedures/storage-lakehouse.toml` is actually a stack** | `infrastructure/komodo/procedures/storage-lakehouse.toml:26-47` | mis-located stack → move to `stacks/storage-lakehouse.toml` | S | low | `refactor(komodo): relocate misnamed procedure→stacks/` |
| P2-17 | **Komodo `variables.toml` for shared image tags** | `infrastructure/komodo/` (new file) | inline vars → single `variables.toml` referenced by resource_sync | S | low | `refactor(komodo): add variables.toml for shared image tags` |
| P2-18 | **Komodo `server_id` → `server` rename (all 30+ stacks)** | `infrastructure/komodo/**/*.toml` | `server_id` → `server` | S | low | `refactor(komodo): rename server_id→server (30+ TOMLs)` |
| P2-19 | **Infisical CLI Linux repo migration** — Cloudsmith→artifacts-cli.infisical.com 2026-09-16 | `infrastructure/ansible/roles/infisical-cli/tasks/main.yml` | `apt.cloudsmith.io/infisical/...` → `artifacts-cli.infisical.com` (pin `infisical@0.41.x`) | S | high (2026-09-16 deadline) | `fix(infisical): migrate CLI repo to artifacts-cli.infisical.com` |
| P2-20 | **Infisical MCP server adoption** — first-party `/.well-known/mcp/server-card.json` | `.agents/skills/secrets-management/SKILL.md` + `oideachais-mcp-filesystem` | Bun init-vault.ts → MCP tools `infisical_secret_get/set` | M | low | `feat(infisical): adopt first-party MCP server` |
| P2-21 | **Lakekeeper OIDC prod wiring** — dev ships `AUTH_DISABLE=true` | `infrastructure/stacks/lakehouse/compose.yaml:228` | dev-only → prod overlay wires Pocket ID OIDC | M | med | `fix(lakekeeper): wire Pocket ID OIDC for prod (was AUTH_DISABLE=true)` |
| P2-22 | **Lakekeeper `lance-namespace` generic-tables registration** — 1 RBAC for Parquet+Lance+Delta | `infrastructure/stacks/lakehouse/` | separate catalogs → unified Lakekeeper generic-tables | M | med | `feat(lakekeeper): register lance-namespace as generic-tables` |
| P2-23 | **DuckLake `ATTACH` URI form (KMS) vs Secret form (prod)** | `stedding/.../ducklake_client.py:225-258` + `crypteolas/.../ducklake_resource.py:119-159` | 2 patterns → 1 canonical (Secret form) gated by `ADOPT_DUCKLAKE_SECRET_FORM=1` | S | low | `refactor(ducklake): pick Secret-form ATTACH for prod` |
| P2-24 | **DuckLake `time_travel` SQL injection risk** | `stedding/.../ducklake_client.py:454` | f-string → bound params via `conn.execute(query, [snapshot_id])` | S | med (security) | `fix(ducklake): bind time_travel params (SQL injection)` |
| P2-25 | **DuckLake dead code `DuckLakeCatalog` class (352 lines)** | `stedding/stedding/flows/education/storage/ducklake.py` | dead → delete (referenced only by `tests/test_smoke.py` import assertion) | S | low | `chore(ducklake): delete dead DuckLakeCatalog class` |
| P2-26 | **MLX-omni dual API surface (OpenAI + Anthropic)** — Anthropic `/anthropic/v1/messages` uncommitted | `infrastructure/stacks/litellm/config/config.yaml:34-65` | OpenAI only → wire Anthropic surface too | M | low | `feat(mlx-omni): wire Anthropic /anthropic/v1/messages surface` |
| P2-27 | **Dagster hierarchical `group_name` migration** — `celtic/duchas` style | 50+ `@dg.asset` decorators | flat → hierarchical (1.13.9+) | M | low | `refactor(dagster): migrate 50+ assets to hierarchical group_name` |
| P2-28 | **Dagster `@multi_asset_check` for 12 WIRE_UNWIRED_DLT_CHECKS** | `assets/wire_unwired_dlt_sources.py` | 12 funcs → 1 `@multi_asset_check` | S | low | `refactor(dagster): consolidate 12 checks into @multi_asset_check` |
| P2-29 | **Dagster `blocking=True` on LLM gateway health check** | `assets/llm_gateway_assets.py:227` | non-blocking → `blocking=True` (gates downstream) | S | low | `feat(dagster): block downstream on minimax_alias_health failure` |
| P2-30 | **Dagster `CelticCocoindexV1Component` alignment with bge-m3** | `components/celtic_cocoindex_v1.py:28-129` | bge-large-en-v1.5 default → bge-m3 (P1-12) | S | low | `refactor(cocoindex): align KCG component to unified bge-m3` |
| P2-31 | **dlt 1.27+ Polars LazyFrame adoption** — `leabharlann/zotero.py` 2,395 PDFs | `pipelines/ingest/_oideachais_dlt_sources/leabharlann/zotero.py` | dict rows → `pl.scan_parquet(...)` | M | low | `perf(dlt): adopt 1.27 native Polars in leabharlann/zotero.py` |
| P2-32 | **dlt 1.27.2 hotfix audit** — `merge` after `replace` on no-data truncates | `ie/law/irish_statute_book.py:87` + 49 more | pattern → wrap with no-data branch or migration to `IncrementalCursorProvider` | M | med (silent truncation) | `fix(dlt): audit replace+merge interaction per 1.27.2 hotfix` |
| P2-33 | **dlt 50+ `destination="duckdb"` calls bypass factory** | 50+ source files | hardcoded → `dlt_utils/destinations.py` factory (local|production|duckdb-fallback) | M | low | `refactor(dlt): route 50+ pipelines through destinations.py factory` |
| P2-34 | **dlt 11 `dlt.sources.incremental` → `IncrementalCursorProvider`** | 11 call sites | old API → new (1.27+) | M | low | `refactor(dlt): migrate 11 incremental callers to IncrementalCursorProvider` |
| P2-35 | **dlt test `res._hints.get("primary_key")` private API** | `tests/.../test_crown_deps.py:138` | private → `resource.apply_hints({"primary_key":...})` | S | low | `refactor(dlt): drop test on private _hints dict` |
| P2-36 | **BAML centralize 5 client files → 1 per sub-package** | `_oideachais_src/clients.baml` + 4 more | 5 files → 1 canonical (delete `clients_0.baml` + `_clients_legacy.baml`) | S | low | `refactor(baml): consolidate 5 client files into 1 per sub-package` |
| P2-37 | **BAML TS/React generator** — for TanStack Start front-end | `_oideachais_src/generators.baml` | python-only → python + typescript | M | low | `feat(baml): add typescript/react generator for oideachais-web` |
| P2-38 | **BAML `@@dynamic` + `TypeBuilder` for `PreResearchSite.recommended_schema`** | `_oideachais_src/...` | stringly-typed → `@@dynamic` | M | low | `refactor(baml): adopt @@dynamic for PreResearchSite.recommended_schema` |
| P2-39 | **BAML `@@assert` / `@check` runtime evals** — 6 standard eval categories | `cognee_integration/.../runtime_evals.baml` (new) | none → `@@assert sum == total` + Dagster asset_check | M | low | `feat(baml): add runtime evals (@@assert / @check) for 6 categories` |
| P2-40 | **Graphiti `add_episode` 5→16 param gap** | `cianfhoghlaim/core/cognee/_graph/graphiti_client.py:158-164` | 5 params → 16 (group_id, entity_types, edge_types, edge_type_map, etc.) | M | low | `refactor(graphiti): wire 11 missing add_episode params` |
| P2-41 | **Phase 3 site spec corrections** (curriculumonline, examinations.ie, gov.uk) | 3 Phase-3 spec files (S01, S02, S05) | URL/pattern drift → real patterns (T&Cs click, /ga-ie/ prefix, reCAPTCHA teacher account) | M | med (data loss) | `docs(phase-3): fix 3 site spec drift items` |
| P2-42 | **Crown dependency Jersey CKAN ingestion** — 110+ datasets, zero ingested | `pipelines/ingest/_oideachais_dlt_sources/jey/` | none → `kind: ckan_api` source for `education`, `gov`, etc. | M | med | `feat(dlt): add Jersey CKAN source (110+ OGL-J-1.0 datasets)` |
| P2-43 | **IoM legislation PDF harvester** — `legislation.gov.im` 750+ Acts | `iom/law/legislation.py:24-29` | HTML only → PDF harvester for `/cms/images/LEGISLATION/{...}.pdf` | M | med | `feat(dlt): add IoM legislation PDF harvester (750+ Acts)` |
| P2-44 | **Zotero API ingestion** — `pyzotero` + `Last-Modified-Version` cursor | `leabharlann/zotero.py:94-124` | filesystem only → API + conditional GETs | M | low | `feat(dlt): add Zotero API v3 source (2,592 episodes)` |
| P2-45 | **ArXiv OAI-PMH bulk sync** — `ListRecords&from=<last>` | `cognify/rules/leabharlann_cross_archive.py` | none → arxiv_api_source + arxiv_oai_pmh_source + ack string | M | low | `feat(dlt): add arXiv OAI-PMH bulk sync (30k results)` |

---

## 6. P3 — Backlog (nice-to-have)

| # | Item | File | PR title |
|:-:|:--|:--|:--|
| P3-1 | CocoIndex multimodal `leabharlann_flow.py` + `ocr_aware_flow.py` skeleton→live | `core/cocoindex/{leabharlann_flow,ocr_aware_flow}.py` | `feat(cocoindex): promote multimodal flows skeleton→live` |
| P3-2 | Lance Blob v2 schema docs in skill | `.agents/skills/lancedb/SKILL.md` | `docs(lancedb): document Blob v2 schema marker` |
| P3-3 | Add Lance IVF_RQ benchmark | `agent-observability` Langfuse dashboard | `bench(lancedb): IVF_PQ vs IVF_HNSW_SQ vs IVF_RQ` |
| P3-4 | Pinecone/HF webhooks to 4-layer change-detection (Agent 19) | `oideachais-pipeline` | `feat(change-detection): add HF webhooks as 5th layer` |
| P3-5 | BAML `@trace` decorator on Python wrappers (non-LLM helpers) | `core/baml/...` | `feat(baml): wire @trace on pre_process_text, full_analysis` |
| P3-6 | LiteLLM `credential_list` + `litellm_credential_name` (centralize 3 OPENCODE_GO keys) | `infrastructure/stacks/litellm/config/config.yaml` | `refactor(litellm): adopt credential_list for 3-key rotation` |
| P3-7 | LiteLLM 100+ providers (Manus, Pydantic AI, ChatGPT OAuth) for chain expansion | `infrastructure/stacks/litellm/config/config.yaml` | `feat(litellm): add 8 new providers (chain expansion targets)` |
| P3-8 | FalkorDB `falkordb-bulk-loader` (10-100× faster ingestion) | `oideachais-pipeline` | `perf(falkordb): adopt falkordb-bulk-loader for 2,592 episodes` |
| P3-9 | FalkorDB Graphiti `falkordb.backend=production|lite` Langfuse span tag | `graphiti_client.py` | `feat(graphiti): add falkordb.backend Langfuse span tag` |
| P3-10 | RisingWave 4-node split (compute/meta/compactor/frontend) — upstream anti-recommendation for all-in-one | `infrastructure/stacks/risingwave/compose.yaml:17` | `refactor(risingwave): split all-in-one → 4-node production` |
| P3-11 | Pangolin EE `public-resources.maintenance` (graceful 502) for 5 public routes | `infrastructure/pangolin/...` | `feat(pangolin): enable EE maintenance block on 5 routes` |
| P3-12 | Pangolin EE `wildcard-resources` + wildcard TLS for sub-domain routing | `infrastructure/pangolin/...` | `feat(pangolin): enable EE wildcard sub-domain routing` |
| P3-13 | Komodo hoisted `actions/<domain>.toml` (one file per domain) | `infrastructure/komodo/procedures/*.toml` (73 files) | `refactor(komodo): hoist 73 [[action]] blocks to actions/<domain>.toml` |
| P3-14 | Komodo empty `sites/` subdir (populate or `.gitkeep`) | `infrastructure/komodo/sites/` | `chore(komodo): populate or gitkeep empty sites/ subdir` |
| P3-15 | Komodo duplicate `[[resource_sync]]` dedup (storage-infrastructure + auto-deploy-stacks) | `resource-syncs/storage-infrastructure.toml` + `procedures/auto-deploy-stacks.toml:1538-1574` | `refactor(komodo): dedup dual resource_sync definitions` |
| P3-16 | Cognee compose `LANCEDB_URI` dead-config removal (pgvector overrides) | `infrastructure/stacks/cognee/compose.yaml:60` | `chore(cognee): remove dead LANCEDB_URI` |
| P3-17 | Cognee pin image `latest` → `1.2.2` | `infrastructure/stacks/cognee/compose.yaml` | `fix(cognee): pin image to 1.2.2` |
| P3-18 | Cognee v0.1.2+ `cognee[graphiti]` extra (temporal backend) | `cognify/cognee_integration/cross_stage_cognify.py` | `feat(cognee): adopt cognee[graphiti] for temporal features` |
| P3-19 | Infisical per-host machine identities + trusted-IP allowlists | `infrastructure/infisical/` (kill universal-auth-anywhere) | `refactor(infisical): provision per-host scoped machine identities` |
| P3-20 | BAML skill inline `client "openai/gpt-4o-mini"` → named `ExtractEn` | `.agents/skills/baml/SKILL.md` (Patterns 1,2,4) | `docs(baml): replace inline clients in skill examples` |
| P3-21 | FalkorDB `dragonfly_pangolin_route` for port 6379 (cross-host) | `infrastructure/pangolin/private-resources.blueprint.yaml:62-97` | `feat(pangolin): expose falkordb RESP 6379 for cross-host clients` |
| P3-22 | P2-12 Komodo spec factual error corrections (4 items) | `phase-2/P2-12-komodo.md` | `docs(komodo): correct 4 P2-12 factual errors` |
| P3-23 | P2-30 Dragonfly spec reconcile (4 errors) | `phase-2/P2-30-dragonfly.md` | `docs(dragonfly): reconcile 4 P2-30 errors` |
| P3-24 | FalkorDB `falkordb-abc-vector-method` — uniform vector query on `GraphClient` ABC | `cognee/_graph/_shared/interface.py` | `refactor(memory-abc): add vector_query method to GraphClient` |
| P3-25 | FalkorDB SSPLv1 license audit (SaaS future blocker) | `openspec/specs/agent-memory-systems/spec.md` | `docs(memory): document FalkorDB SSPLv1 license posture` |
| P3-26 | BAML TS-to-Zod pipeline (after TS generator) | `web/apps/oideachais-web/src/` | `feat(oideachais-web): wire BAML→Zod schema validation` |
| P3-27 | BAML `BOUNDARY_API_KEY` + Studio v2 auto-trace (avoid double-counting with Langfuse) | `core/baml/...` | `feat(baml): adopt BOUNDARY_API_KEY for Boundary Studio v2` |
| P3-28 | Unsloth `use_rslora` + `loftq_config` (LoRA enhancements) | `unsloth_config.py:30` | `feat(unsloth): expose use_rslora + loftq_config` |
| P3-29 | Unsloth Gemma-4 QAT (3× memory reduction) | `UnslothConfig.for_gaelic_ocr()` | `feat(unsloth): add Gemma-4 QAT model variants` |
| P3-30 | Unsloth `target_modules="all-linear"` shorthand | `unsloth_config.py:37-47` | `refactor(unsloth): use "all-linear" shorthand` |
| P3-31 | P2-24 MLX-omni spec 5 factual error corrections | `phase-2/P2-24-mlx-omni.md` | `docs(mlx-omni): correct 5 P2-24 spec errors` |
| P3-32 | MLX-omni spec 11 vision + 4 text wiring (currently 3 wired) | `infrastructure/stacks/litellm/config/config.yaml:34-65` | `feat(mlx-omni): wire remaining 8 vision + 4 text models` |
| P3-33 | HF `inference-api` OAuth scope tier (per-user rate limits) | `spaces/_common/baml_client.py:85-100` | `feat(hf): add inference-api OAuth scope tier` |
| P3-34 | HF KCG public OAuth app + CIMD at `oci.cianfhoghlaim.ie/.well-known/oauth-cimd` | new `infrastructure/oauth-cimd/cimd.json` | `feat(hf): register KCG public OAuth app with CIMD` |
| P3-35 | HF `[cli]` → `[hf]` extra rename in CI | `infrastructure/ci/spaces-sync.yml:64` | `chore(hf): rename [cli]→[hf] extra in CI` |
| P3-36 | OpenChamber Litestream-style backup hint for `openchamber-state` | `infrastructure/stacks/openchamber/README.md` | `docs(openchamber): add restic backup hint` |
| P3-37 | Unsloth `weight_decay 0.001→0.01` (upstream recommendation) | `unsloth_config.py` | `refactor(unsloth): bump weight_decay to upstream 0.01` |
| P3-38 | Unsloth `UnslothVisionDataCollator` for VLMs | `unsloth_trainer.py` | `feat(unsloth): adopt UnslothVisionDataCollator` |
| P3-39 | Unsloth `mise run unsloth:studio` task | `mise.toml` | `feat(mise): add unsloth:studio task` |
| P3-40 | Unsloth `mise run unsloth:pull` (pre-cache 13.1 GB image) | `mise.toml` | `feat(mise): add unsloth:pull pre-cache task` |

**P3 total: 40 items, low priority, do in batches during quieter sprints.**

---

## 7. Cross-cutting dependencies (Mermaid)

```mermaid
graph TD
    %% P0 cluster
    subgraph P0[Critical 1-2wk]
        P0_1[FalkorDB vector.so]
        P0_2[Garage v1→v2]
        P0_3[dlt [hub] extra]
        P0_4[LiteLLM main-stable]
        P0_5[Cognee SearchType]
        P0_9[MLX-omni CLI]
        P0_10[OpenChamber P2-20]
        P0_11[P2-23 model IDs]
    end

    %% P1 cluster
    subgraph P1[High 2-4wk]
        P1_1[BAML inline→gateway]
        P1_2[CocoIndex HNSW]
        P1_3[LanceDB IVF_HNSW_*]
        P1_4[LanceDB connect_namespace]
        P1_5[Komodo server_id]
        P1_6[CelticDltSourceComponent]
        P1_7[dagster-dlt bump]
        P1_8[Garage secrets]
        P1_9[BAML gen 0.223]
        P1_10[Dragonfly URLs]
        P1_11[Cognee dataset names]
        P1_12[CocoIndex embed model]
        P1_13[OpenChamber digest]
    end

    %% Cutover train
    subgraph CT[Coordinated release train]
        CT1[dlt 1.27+ hub]
        CT2[dagster-dlt 0.29.11]
        CT3[cocoindex 1.0.14]
        CT4[lancedb 0.33]
        CT5[Garage 2.3.0]
        CT6[LiteLLM 1.84+]
    end

    %% P2 high-leverage
    subgraph P2[Medium 1-2mo]
        P2_7[BAML Collector]
        P2_9[Cognee v1.0 API]
        P2_12[Langfuse v3 OTEL]
        P2_14[Pangolin public-policies]
        P2_19[Infisical CLI 2026-09-16]
        P2_28[Dagster @multi_asset_check]
        P2_31[dlt Polars]
        P2_32[dlt 1.27.2 hotfix]
        P2_41[Phase 3 spec fix]
    end

    %% Dependencies
    P0_3 --> CT1 --> P1_7
    CT1 --> P1_6
    P1_7 --> P2_28
    P1_3 --> P2_14
    P1_4 --> P2_14
    P1_12 --> P2_30
    P1_5 --> P2_17
    P0_2 --> P1_8
    P0_2 --> P2_8
    P1_2 --> P1_12
    P1_2 --> P2_2
    P1_1 --> P2_7
    P2_7 --> P2_39
    P1_9 --> P1_1
    P1_9 --> P2_37
    P0_5 --> P2_9
    P1_11 --> P2_9
    P2_9 --> P2_10
    P2_9 --> P2_11
    P0_1 --> P2_8
    P0_6 --> P0_3
    P0_7 --> P2_23
    P0_8 --> P1_5
    P2_41 -.uses.-> P0_11
    P2_19 -.harddate.-> P0_4

    style P0_3 fill:#ff6b6b
    style P0_4 fill:#ff6b6b
    style P0_5 fill:#ff6b6b
    style P0_1 fill:#ff6b6b
    style P0_2 fill:#ff6b6b
    style CT fill:#ffe66d
```

**Key dependency chains:**

1. **Release train** (CT cluster): P0-3 (dlt [hub]) → P1-6 (drop CelticDltSourceComponent) → P1-7 (dagster-dlt 0.29.11) → P2-28 (Dagster @multi_asset_check). All four land together; any one in isolation will fail.
2. **CocoIndex chain** (P1-2 → P1-12 → P2-2): declare HNSW indexes → unify embedding model on bge-m3 → adopt 1.0.7 engine features. Must be in this order (HNSW reuses same embedding space).
3. **Pangolin chain** (P1-3, P1-4 → P2-14, P2-15): LanceDB IVF_HNSW_* + connect_namespace → Pangolin public-policies block + multi-site failover.
4. **Cognee chain** (P0-5 → P1-11 → P2-9 → P2-10, P2-11): fix SearchType → align dataset names → v1.0 API → graph backend + config reconciliation.
5. **BAML chain** (P1-1 → P1-9 → P2-7 → P2-39): migrate inline clients → bump generators 0.223 → wire Collector → add runtime evals. BAML recompile gate.
6. **Hard-date external**: P0-4 (LiteLLM 2026-06-30) and P2-19 (Infisical CLI 2026-09-16) are externally-mandated.

---

## Summary

The 11 P0 items are not optional — FalkorDB vector.so, Garage v2, dlt [hub], LiteLLM main-stable, Cognee SearchType, the dlt path/version drifts, MLX-omni CLI, OpenChamber P2-20, and P2-23 model IDs are all either silently broken in production today (vector queries 404, dlt dashboard will fail on bump, MLX-omni container won't start, P2-23 hf_hub_download will fail) or have hard upstream deadlines (LiteLLM 2026-06-30, Infisical 2026-09-16). P0 must land in a single coordinated release train (LiteLLM→Langfuse-OTEL + dlt-[hub] + dagster-dlt-0.29.11 + cocoindex-1.0.14 + LanceDB-0.33 + FalkorDB-vector.so + Garage-v2.3.0) within 1-2 weeks. The 13 P1 items (BAML inline clients, CocoIndex HNSW, LanceDB IVF_HNSW_*, Komodo server_id, CelticDltSourceComponent, Garage secrets, BAML 0.223, Dragonfly URLs, Cognee dataset names, CocoIndex embed model, OpenChamber digest) add 3-4 weeks of high-impact work that should run in parallel to the P0 train. The 45 P2 items are 1-2 month backlog that should be batched (Phase 3 spec fixes, HuggingFace CLI migration, CocoIndex 1.0.7 features, Unsloth accuracy/inference wins, BAML Collector/TS/runtime-evals, Pangolin EE features, Komodo variable/action files, Infisical MCP, Lakekeeper OIDC, DuckLake ATTACH/secrets, Dagster hierarchical groups, dlt Polars/incremental, Crown Dep site harvests). P3 is the long-tail nice-to-haves (40 items) for quieter sprints. Total backlog: 109 items, ~80% of value in 11 P0 + 13 P1 = 24 items.
