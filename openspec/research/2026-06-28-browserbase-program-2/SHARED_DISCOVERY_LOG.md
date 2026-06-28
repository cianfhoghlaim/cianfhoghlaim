# Shared Discovery Log — BrowserBase Program 2

**Started:** 2026-06-28 23:03
**Wave 1:** 25 parallel research agents
**Credit budget:** 6,000 (5,000 Wave 1 + 250 Wave 2 + 50 Wave 3 + 700 reserve)
**Time budget:** 60 min wall clock

This log is the append-only cross-agent coordination file. All 25 wave-1 agents should read this file FIRST and append their discoveries here. Final wave-3 synthesis reads the full log.

## Agent 06 — LiteLLM (2026-06-28 23:25 UTC)

**Package:** `litellm` (LLM gateway) · **Wave:** 1 · **Credits:** ~12

### Findings

1. **`main-stable` Docker tag DEPRECATED — cutover 2026-06-30 (2 days)** — our pin `ghcr.io/berriai/litellm:main-stable` in `infrastructure/stacks/litellm/compose.yaml` must migrate to `:latest` or `:1.84.0+`. Source: `https://docs.litellm.ai/blog/cleaner-release-versions`.

2. **LiteLLM now ships a NATIVE `minimax` provider** (third-party Chinese AI MiniMax Inc., models `MiniMax-M2`/`M2.1`/`M2.1-lightning` at `api.minimax.io`) — our bare `minimax` alias does NOT collide today, but `minimax/MiniMax-M2.1` will route to MiniMax Inc. Add a doc note in `stacks/litellm/README.md`. Source: `https://docs.litellm.ai/docs/providers/minimax`.

3. **March 2026 supply-chain incident — v1.83.0 is the clean baseline.** Source: `https://docs.litellm.ai/blog/security-update-march-2026`. Confirm our deployed image ≥ v1.83.0.

4. **Langfuse v3 OTEL is now the recommended integration path** — we still use the v2 callback at `infrastructure/stacks/litellm/config/config.yaml:760-765`. Migration change needed: `openspec/changes/litellm-langfuse-otel/`. Source: `https://docs.litellm.ai/docs/observability/langfuse_integration`.

5. **DRIFT: Our fallback uses custom `model_info.fallback_chain`** (config.yaml:723-730) instead of canonical `litellm_settings.fallbacks`. Spec enforces order but if LiteLLM doesn't recognize the custom field, fallback may not fire. Write a Dagster asset check to verify.

6. **NEW docs pattern: `credential_list` + `litellm_credential_name`** — could centralize our 3 `OPENCODE_GO_API_KEY_0/1/2` slots. Verify slot rotation semantics preserved.

7. **Provider count updated: 100+ (was 70+)** per docs.litellm.ai header. New docs include native MiniMax, Manus, Pydantic AI Agents, ChatGPT Subscription (OAuth device flow), CometAPI, Xiaomi MiMo, OVHCloud AI — none currently used in our `config.yaml` but available as drop-in targets for chain expansion.

## Conventions
- Each entry: `## Agent {N} — {package} ({timestamp})`
- List 3-7 most surprising findings, each with `file:line` reference
- Cross-agent dependencies: `## Agent {X} relies on: {finding}`
- Conflicts: `## Conflict with Agent {X}: {description}`

## Agent 17 — Komodo (2026-06-28 22:14 UTC)

1. **The P2-12 spec is factually wrong on 4 counts.** `infrastructure/komodo/` has 5 sub-dirs (`servers/`, `stacks/`, `procedures/`, `resource-syncs/`, `sites/`), NOT 4 — there's no `builder/` dir, no `variables.toml`, only 2 servers (`arm1-oci` + `bunchloch`) not 3 (no `cax41-hetzner` in `servers.toml:14-43`), and `docs.komo.do/*` URLs serve a generic Rust sample. Real docs are at `https://komo.do/docs/{intro,setup,resources,deploy/compose,automate/procedures,automate/sync-resources,configuration/variables,automate/schedules,automate/webhooks,releases/v2.0.0}` (Docusaurus site, MDX-rendered).

2. **Stack TOML `server_id` vs upstream `server`.** Cianfhoghlaim uses `server_id = "bunchloch"` everywhere (e.g. `infrastructure/komodo/stacks/storage-lakehouse.toml:23,52`) but upstream Komodo v2 docs use `server = "..."` (`https://komo.do/docs/deploy/compose` example). Core accepts both silently — silent-drift risk if anyone copy-pastes from upstream docs.

3. **`procedures/storage-lakehouse.toml` is actually a `[[stack]]` definition, not a `[[procedure]]`.** Lines 26-47 declare `[[stack]]` not `[[procedure]]`, with `[[stack.depends_on]]` + `[[stack.procedures]]` (shell health-check snippets embedded inline). File location + filename are misleading.

4. **TWO competing `[[resource_sync]]` definitions for "storage-infrastructure".** One in `infrastructure/komodo/resource-syncs/storage-infrastructure.toml:8-29` (uses globs in `resource_path`) and a second inside `infrastructure/komodo/procedures/auto-deploy-stacks.toml:1538-1574` (uses explicit per-file paths in `resource_path`). Both target repo `cliste/bonneagar`. Core probably warns but doesn't fail.

5. **Komodo's GitOps primitive is a `[[resource_sync]]` with `resource_path = [...]`**. The `[[resource_sync]]` globs `*.toml` files from git (e.g. `bonneagar/komodo/stacks/*.toml`) and feeds them into Core's resource DB. `managed = true` makes Core write UI changes back to git; `delete = false` is the safe default (won't delete resources when TOML files are removed). See `https://komo.do/docs/automate/sync-resources` for the canonical pattern.

6. **Cianfhoghlaim's Komodo deployment is fully v2.** All three properties visible: PKI SPKI `public_key` fields in `servers.toml:24,43` (not legacy `passkey`), outbound Periphery (`address = ""` in `servers.toml:21,41`), and image tags pinned to Semver (the v2+ convention; Komodo no longer publishes `:latest`). v2.2.0 latest was May 7 2026.

7. **Komodo's webhook URL pattern is `https://<HOST>/listener/github/<RESOURCE_TYPE>/<ID_OR_NAME>/<EXECUTION>`.** Resource types: `build`, `repo`, `stack`, `sync`, `procedure`, `action`. Stack executions: `/deploy`, `/refresh`. Procedure/Action executions: branch name or `/__ANY__`. The `github` auth type covers Forgejo/Gitea too (X-Hub-Signature-256 HMAC).

## Agent 17 relies on: Agent 16 (Pangolin)
The 90-stack fleet is exposed publicly through Pangolin (`infrastructure/komodo/stacks/*.toml` references `pangolin.yaml` as a `file_paths` entry alongside `compose.yaml` and `sidecar.yaml`). The `private-resources.<name>.*` 6-label pattern that Pangolin exposes to authenticated clients is the inverse of the Komodo `[[stack]]` definition — they MUST stay in lock-step. See `stacks/storage-lakehouse.toml:25,54` for the canonical triplet.

## Conflict with Agent 16 (Pangolin): possible
Agent 16 documented Pangolin's TOML blueprint schema (`public-resources`, `private-resources`, `public-policies`, `sites`). Komodo's `sites/` subdir at `infrastructure/komodo/sites/` is empty — could collide with Pangolin's `sites:` blueprint key. If a future Cianfhoghlaim Komodo file uses `sites = "..."` (matches both Komodo swarm monitoring and Pangolin blueprint sites), disambiguation will be needed.


## Agent 19 — Unsloth (2026-06-28 22:10 UTC)

**Package:** Unsloth 3.0+ — fine-tuning library. **Codebase anchors:** `cianfhoghlaim/ocr/training/training/unsloth_config.py:166`, `unsloth_trainer.py:108,121`. **Output:** `openspec/research/2026-06-28-browserbase-program-2/agent-19-unsloth.md`.

Surprising findings (each with `file:line` reference):

1. **Upstream unified loader `FastModel` supersedes `FastVisionModel`** for Gemma 4 (`unsloth_trainer.py:108` still uses the old API). Upstream 3.0+ has `FastModel.from_pretrained` + `FastModel.get_peft_model` that auto-dispatch text/vision/audio without three separate classes. Migration would unify our 11 OCR models under one loader.

2. **`train_on_responses_only` is the documented accuracy booster (+1%)** per the QLoRA paper (`unsloth.ai/docs/.../lora-hyperparameters-guide#training-on-completions-only`). Our `UnslothTrainer.train()` at `unsloth_trainer.py:278` does NOT call this — easy +1% accuracy win for the 11 OCR models on multi-turn Irish conversational data.

3. **Gemma 4 has 3 critical upstream patches** (`unsloth.ai/docs/models/gemma-4/train`):
   - **E2B/E4B `use_cache=False` produces garbage logits** (KV-shared layers); Unsloth fix makes output bit-exact.
   - **31B/26B `num_kv_shared_layers=0` IndexError** (Python `-0 == 0` → `layer_types[:0] == []`).
   - **Audio fp16 overflow** with `attention_invalid_logits_value = -1e9`.
   None of these are referenced in our codebase. If we hit any, we'll be the first to encounter them.

4. **MTP speculative decoding gives 1.4-2.2x inference speedup with ZERO accuracy loss** for Qwen3.6 27B/35B-A3B (`unsloth.ai/docs/models/qwen3.6#mtp-guide`). Upstream llama.cpp merged MTP support PR #22673 (2026-06-21). Recommended flag: `--spec-type draft-mtp --spec-draft-n-max 2`. Our llama-swap config (`cianfhoghlaim/core/llama-swap-config.yaml:120`) does NOT yet enable MTP.

5. **Dynamic 2.0 GGUFs (`UD-Q4_K_XL`) are SOTA Pareto on KLD benchmarks** — top-performing in 21 of 22 model sizes vs other quant providers (`unsloth.ai/docs/basics/unsloth-dynamic-2.0-ggufs`). Our `UnslothTrainer.save_merged()` at `unsloth_trainer.py:409` defaults to `q4_k_m`; switching to `ud-q4_k_xl` is free win for accuracy.

6. **Unsloth convention is `random_state=3407`** (not `42`) — matches published Unsloth notebooks and Gemma 4 docs. Our `TrainingConfig` at `unsloth_config.py:103` hardcodes `seed=42`. Should align.

7. **LoRA target modules should be the full 7-layer set** (`q/k/v/o_proj` + `gate/up/down_proj`); `target_modules="all-linear"` is upstream's new shorthand. Our code already passes the explicit list at `unsloth_config.py:37-47` — correct.

8. **Docker image `unsloth/unsloth` is 13.1 GB**, Blackwell-compatible, non-root user, exposes ports 8888 (Jupyter), 8000 (Studio), 2222 (SSH). Updated 2026-05-31; pulls 4,667/week. We don't yet package this in our `mise run` tasks.

## Agent 19 relies on: Agent 33 (Modal — for `modal_unsloth.py` burst pattern); Agent 23 (HuggingFace — for `push_to_hub_gguf` HF auth); Agent 18 (MLflow — for `TrainingArguments.report_to=["mlflow"]` already wired in `unsloth_trainer.py:339`).
## Agent 19 conflicts with: none (all findings are additive improvements to the existing P2-32 spec).

## Agent 15 — BAML (2026-06-28 23:15)

**Package:** BAML (Basically a Made-up Language) — schema-validated LLM extraction. 73 `.baml` files across `cianfhoghlaim/core/baml/_*_src/`. Upstream: `github.com/BoundaryML/baml` (Apache-2.0, 8.4k★, Rust 66.4% / TS 12.2% / BAML 8.2% / Python 4.0%).

1. **`_oideachais_src/curriculum_extraction.baml:164-1086` has 8 inline `client "anthropic/claude-sonnet-4-20250514"` calls that bypass the LiteLLM gateway.** No fallback chain, no Langfuse trace, no `MiniMax` vendor-de-risking — defeats Phase 0.4's stated goal. 1-line sed to fix.

2. **`generators.baml:7` pins version `"0.74.0"` but `baml-py` is at `0.223.0` (2026-06-23) and `baml-language` is at `0.13.0` (2026-06-28, today).** Missed the streaming-retry bugfix in 0.221 (#3025) and the `render_null_as` output format option in 0.223. `default_client_mode sync` should be `async` per skill recommendation.

3. **9 named clients all gateway-routed: `LiteLLM`, `MiniMax`, `ExtractEn`, `ExtractEnStrong`, `LocalVision`, `LocalOCR`, `LocalIrish`, `LocalMath`, `ImageGen`.** They alias to `model "extract"`, `"minimax"`, `"extract-en"`, `"extract-en-strong"`, `"vision"`, `"ocr"`, `"irish"`, `"math"`, `"image-fibo"` respectively — the actual provider chain lives in `infrastructure/stacks/litellm/config/config.yaml`. BAML is downstream of the gateway.

4. **Client definitions are spread across 5 files:** `_oideachais_src/clients.baml` (264 lines, 9 canonical) + `clients_0.baml` (39 lines, obsolete Gemini — should be deleted) + `generators.baml` (54 lines, 5 legacy) + `_tuatha_src/tuatha_clients.baml` + `_croilar_baml/clients.baml` (3 `fallback` strategy chains). Consolidate to 1 per sub-package.

5. **BAML `template_string`, `@@assert`/`@check`, `b.stream.<F>`, `@@dynamic`+`TypeBuilder`, `Collector(name)` + `@trace` are ALL unused.** The codebase uses only 20% of BAML's feature surface — most relevant gaps: `@@dynamic` for `PreResearchSite.recommended_schema` (currently stringly-typed), `Collector(name)` in Dagster asset wrappers (no per-call token metrics), `b.stream.<F>` for `LazyExtractExamPaper` (200-500s long extraction without progress).

6. **`_oideachais_src/author_archive.baml:810` is the gold-standard reference file.** 12 classes, 4 enums, 4 extraction functions using `ExtractEn`/`ExtractEnStrong`, 4 `test` blocks with realistic fixtures (CPS UK, gaHealth paper). Use as the template for new BAML functions.

7. **BAML upstream breaking change in 0.218 (2026-01-22):** Added `BamlError` base class + improved error hierarchy across TS/Python/Go. Migrate to `BamlError` / `BamlValidationError` / `BamlClientFinishReasonError` / `BamlAbortError` instead of generic `Exception` catches.

**Agent 15 relies on:**
- Agent 14 (LiteLLM): for the 9 gateway model aliases — if P2-14 retires `extract-en-strong`, the `ExtractEnStrong` BAML client silently breaks.
- Agent 19 (Langfuse): for the observability path — `Collector(name)` → Langfuse span correlation needs P2-19's tracing decisions.

**Conflict with Agent 19 (Langfuse):** Both Boundary Studio v2 (`BOUNDARY_API_KEY`) AND Langfuse auto-instrumentation via LiteLLM can trace BAML calls. Only one is needed — pick one, not both, to avoid double-counting in cost dashboards. Recommend LiteLLM→Langfuse (it's already wired into `cognify/rules/llm_gateway_health.py`).

## Agent 04 — LanceDB (2026-06-28 23:08)

**Package:** LanceDB OSS Python 0.33.0 stable / 0.34.0-beta.3 preview — [docs.lancedb.com](https://docs.lancedb.com/llms.txt), [PyPI](https://pypi.org/project/lancedb/), [GitHub releases](https://github.com/lancedb/lancedb/releases), [lance.org/format/namespace](https://lance.org/format/namespace)

### Key findings (7)

1. **CRITICAL DRIFT FROM P1B-06**: HNSW is **NOT** a standalone top-level vector index in LanceDB v0.33. It's a sub-index inside IVF partitions — only valid names are `IVF_HNSW_FLAT`, `IVF_HNSW_SQ`, `IVF_HNSW_PQ`. The P1B-06 YAML's `index: { type: hnsw, m: 16, ef_construction: 200 }` will **fail** in `table.create_index(...)`. `stacks/lakehouse/lance-namespace/config.yaml` needs an `index_type` migration. (Source: `docs.lancedb.com/indexing/vector-index`)

2. **LanceDB moved past "0.10+" baseline** — current stable is **0.33.0 (May 28 2026)**, pre-release **0.34.0-beta.3 (Jun 25 2026)** ships a breaking change: `IndexStatistics.loss` field removed (PR #3496). Pin `lancedb>=0.33,<0.34` to hold this out. (Source: PyPI release history)

3. **Lance Namespace** is now production-grade with a standardised client spec — 6 implementations: Directory, REST, Hive Metastore, Unity Catalog, Apache Polaris, Apache Iceberg REST Catalog. SDKs: Java (`org.lance:lance-namespace-core`), Python (`lance_namespace`), Rust (`lance-namespace`). Cianfhoghlaim uses **REST** via the `lance-namespace` Compose stack on :8182. (Source: `lance.org/format/namespace`)

4. **`connect_namespace("rest", {...})` is the v0.33-canonical client**. The P1B-06 code sample uses `lancedb.connect("http://lakehouse-lance:8182")` which is the directory-namespace URI form. REST namespace requires `headers.x-api-key` (Locket-resolved) or `headers.Authorization`. **DRIFT-FIX REQUIRED** in `cianfhoghlaim/core/cocoindex/mount_lance.py`.

5. **Lance Blob v2** is the new lazy-loading path for large objects (PDFs/audio/video). Schema marker: `pa.large_binary()` + `metadata={"lance-encoding:blob": "true"}`. `to_pandas(blob_mode=...)` accepts `lazy` (default), `bytes` (eager), `descriptions` (offsets only). Added in v0.31.0-beta.2 (Jun 23 2026, PR #3528). Recommended for `leabharlann_books.pdf_bytes` etc.

6. **Embedding registry ships 15+ providers** (OpenAI, HuggingFace, Sentence Transformers, Cohere, Jina, VoyageAI, AWS Bedrock, Gemini, Ollama, IBM watsonx, ColPali, Instructor, OpenCLIP, ImageBind, Superlinked) + custom registration via `@register("my-embedder")`. Provider secrets injected via `registry.set_var("api_key", ...)` + `$var:api_key` placeholders — **Locket-friendly** out of the box.

7. **v0.31.0-beta.0 (Jun 18 2026) added table branches** (`feat: add table branch support`, PR #3490+3504), `Expr.isin` (PR #3523), `IndexConfig` rich per-index metadata (PR #3497), and **`approx` mode for vector queries** (PR #3549). Async Python is first-class (`await lancedb.connect_async(...)`) with query embeddings on a dedicated executor.

### Cross-agent deps

- **Agent 04 relies on:** Agent 03 (MotherDuck/DuckLake) for the Lakekeeper integration with the REST Catalog; Agent 09 (Cognee) for the `research_findings` dataset that the Cognee cognify below writes to.
- **Conflict with Agent 04's prior self (P1B-06):** the index-vocabulary + connect-URI form are stale. Build agent should treat P1B-06 as **read-only historical context** and use `agent-04-lancedb.md` as the v0.33 source of truth.
- **Hands off to:** anyone wiring `IVF_HNSW_SQ` defaults in Dagster sensors; anyone updating the embedding registry in `core/cocoindex/_lifespan.py`.`

## Agent 05 — MotherDuck (2026-06-28 23:10 UTC)

Findings (file:line refs in `agent-05-motherduck.md` §8 + decision matrix):

1. **`md:` prefix split between two MCP servers** — `https://motherduck.com/docs/sql-reference/mcp/` confirms the canonical split is **Remote** (`api.motherduck.com/mcp`, OAuth, 25 tools, fully managed) vs **Local** (`mcp-server-motherduck` from `motherduckdb/mcp-server-motherduck`, stdio, customisable). KCG uses Local in `opencode.json` per `.agents/skills/agent-observability/references/mcp/MCP_SERVERS.md:106-108`. The Phase 0.3 runbook calls Local canonical.

2. **Pricing drift** — P1A-05 said "MotherDuck 0.5" but the Python install page (`motherduck.com/docs/getting-started/interfaces/client-apis/python/installation-authentication`) requires **DuckDB 1.5.4** (accepts 1.4.0+ in us-east-1, 1.4.1+ elsewhere). P1A's `--read-write --allow-switch-databases` MCP flags are explicitly anti-pattern #2 in the new audit (P1A's own anti-pattern #3 actually flagged it).

3. **Dives is a workspace-native React framework, not raw SQL** — `https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/` documents `REQUIRED_DATABASES` exports from JSX components that auto-attach share-backed DBs before queries fire. 4 AWS regions, no Ireland-region pinning in KCG docs yet. **Dives are versioned + shareable + stateful-via-URL** (much more than marimo).

4. **`/docs` restructure** — `motherduck.com/docs/dives`, `/docs/connect/python`, `/docs/key-concepts/sharing`, `/docs/sql-reference/motherduck-sql-commands` all **404** as of 2026-06-28. New canonical paths: `/docs/key-tasks/ai-and-motherduck/dives/`, `/docs/getting-started/interfaces/client-apis/python/installation-authentication/`, `/docs/key-tasks/sharing-data/sharing-overview`, `/docs/sql-reference/motherduck-sql-reference/{create-share,attach}`. **`/changelog` is also Next.js 404** — affects upstream monitor at `infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml:30` (needs goal-text patch).

5. **CREATE SHARE has 3 axes** — `ACCESS (ORGANIZATION|UNRESTRICTED|RESTRICTED)`, `VISIBILITY (DISCOVERABLE|HIDDEN)`, `UPDATE (MANUAL|AUTOMATIC)`. OR REPLACE rotates the URL (clients must re-attach). Default = ORGANIZATION+DISCOVERABLE+MANUAL. All shares region-scoped (MotherDuck org is single-region). `ATTACH 'md:_share/<db>/<token>' AS <alias>` — alias must match source DB name if shared DB has views with fully-qualified refs.

6. **3 hosting options for DuckLake on MotherDuck** — `managed` / `byob` / `byoc`. KCG default = `byob` (catalog + compute on MotherDuck, storage in our Garage S3). Defined at `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/motherduck_options.py:41-149`. MotherDuck docs note BYOB is the "sweet spot".

7. **`opencode.json` MCP entry ships with `--allow-switch-databases`** — dangerous in prod (lets agent switch DBs, leak data across customers). `.agents/skills/agent-observability/references/mcp/MCP_SERVERS.md:108` and the real `opencode.json` (per Agent 5 audit) both use this for dev convenience. Production should be `--read-only --saas-mode` with a read-scaling token.

## Agent 05 relies on:

- **Agent 02 (LanceDB)**: cross-verify Dive manifest components export `REQUIRED_DATABASES` for share-backed DBs.
- **Agent 04 (Garage S3)**: confirm `MOTHERDUCK_S3_ENDPOINT` resolves to Garage in prod (not `http://localhost:3900`).
- **Agent 06 (Infisical)**: confirm `dev-baile/motherduck/token` vault entry exists with Business-tier token.
- **Agent 09 (Dagster)**: add upstream sensor to `motherduck_sync_asset` (no drift detection today).
- **Agent 17 (DuckLake)**: confirm `motherduck_options.py` passes DuckLake 1.0 features (GEOMETRY, VARIANT, SORTED BY) through `DuckLakeCredentials`.

## Conflict with Agent {X}:

- Conflict with **P1A-05 (Phase 1A)**: P1A pricing "MotherDuck 0.5" — current docs mandate DuckDB 1.5.4. Update the P2-29 recheck to reflect this.

## Agent 11 — Graphiti (2026-06-28 23:14)

1. **`add_episode` is 16 params (not 5).** The 0.29 API is `add_episode(name, episode_body, source_description, reference_time, source, group_id, uuid, update_communities, entity_types, excluded_entity_types, previous_episode_uuids, edge_types, edge_type_map, custom_extraction_instructions, saga, saga_previous_episode_uuid)` — 5× the surface most KCG code assumes. `getzep/graphiti/graphiti_core/graphiti.py:596`.
2. **`SagaNode` watermarks are bi-temporal by design.** `last_summarized_at` = wall-clock (filter for next run); `last_summarized_episode_valid_at` = event-time (public watermark for "how recent is the summary"). `getzep/graphiti/graphiti_core/graphiti.py:357-432`.
3. **KCG has a *legacy* `add_episode(content, source, source_type, metadata)` shim that silently fails on every call.** `cianfhoghlaim/docs/legacy/crypteolas/api/services/knowledge_graph_service.py:53-80` predates the 0.17 `graph_driver` API. Drift, not a bug in `graphiti_core`.
4. **Five edge types, not just "facts".** `EntityEdge` + `EpisodicEdge` (MENTIONS) + `CommunityEdge` + `HasEpisodeEdge` (saga→episode) + `NextEpisodeEdge` (saga→next episode). The 3 KCG cross-archive edges (`cites`, `builds-on`, `contradicts`) map onto `EntityEdge` labels.
5. **15 search recipes, three rerankers.** `search_config_recipes.py` ships `RRF` / `MMR` / `NODE_DISTANCE` / `EPISODE_MENTIONS` / `CROSS_ENCODER` for `COMBINED` / `EDGE` / `NODE` / `COMMUNITY` — 15 total. Rerankers: `OpenAIRerankerClient` (default), `GeminiRerankerClient` (gemini-2.5-flash-lite), `BGERerankerClient` (bge-reranker-v2-m3).
6. **Telemetry is ON by default.** `GRAPHITI_TELEMETRY_ENABLED=false` is required in compose; PostHog-cdn is reachable from the control plane. KCG `secrets.env` for `stacks/graphiti/` does NOT yet set it (drift).
7. **`build_indices_and_constraints` is load-bearing.** Without it, bi-temporal range queries degrade from O(log N) to O(N²) on `EntityEdge.valid_at + invalid_at`. The KCG canonical init calls it (`graphiti_client.py:100`) but the legacy shim at `crypteolas/.../knowledge_graph/graphiti_client.py` does NOT — another drift surface.

## Agent 11 relies on: Agent 9 (FalkorDB) for the `vector.so` loadable + port 6379 contract. Agent 11 relies on: Agent 7 (Dragonfly) for the episode-cache Redis-protocol contract.

## Agent 14 — RisingWave (2026-06-28 22:14 UTC)

**Package:** `risingwave` (Streaming SQL database) · **Wave:** 1 · **Credits:** ~6 (Firecrawl fallbacks; 1 BrowserBase session opened/closed)

### Findings

1. **Current KCG stack runs all-in-one, NOT the documented 4-node pattern** — `infrastructure/stacks/risingwave/compose.yaml:17` uses a single `risingwave` container. Upstream `deploy/risingwave-docker-compose:5` explicitly states all-in-one "is not recommended for production." Refactor target: split into 4 services (compute-node / meta-node / compactor-node / frontend-node).

2. **RisingWave v3.0.0 released 3 weeks ago (2026-06-11)** — we pin `:latest` so already on v3; 121 total upstream releases. Should pin to `v3.0.0` deliberately.

3. **Iceberg v3 exactly-once commit shipped 4 days ago** (PR #25708, 2026-06-24) — brand-new premium-tier feature; would change the Iceberg sink config in our `init.d/01_init.sql:145-155`.

4. **Premium features block our planned auto-schema-change** — `auto.schema.change = 'true'` on Iceberg sinks AND on `postgres-cdc` sources is tagged "PREMIUM FEATURE" in upstream docs; requires Enterprise/Cloud license. Open question for KCG.

5. **Native `postgres-cdc` doesn't need Debezium** — supports PG 10-17 + RDS/Aurora/Neon/Supabase via logical replication (`ingestion/sources/postgresql/pg-cdc`). Our `init.d/01_init.sql:124-138` has 2 commented templates ready to enable.

6. **`CREATE SUBSCRIPTION` is a Postgres-protocol push primitive** — `get-started/recipes/subscription-push` shows agents can `DECLARE cur SUBSCRIPTION CURSOR` + `FETCH NEXT FROM cur WITH (timeout = '5s')` for pushed events without polling or message broker. Replaces polling patterns in the agent stack.

7. **`auto.schema.change = 'true'` requires exactly-once + sink_decouple** (per `iceberg/deliver-to-iceberg`) — important caveat; without sink_decouple, schema changes silently don't propagate.

## Agent 14 relies on: Agent 12 (olake) — sibling batch CDC, writes to same Iceberg catalog (per `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:57-74`). Agent 4 may share Iceberg sink target. Agent 14 provides the push primitive for Agent 1 (Agno) / Agent 8 (CopilotKit) agents via `CREATE SUBSCRIPTION`.

## Conflict with Agent 6 (LiteLLM): none on package surface, but Agent 14's `init.d/01_init.sql:124-138` references `litellm_db_cdc` as a planned CDC source — if Agent 6 migrates `litellm-postgres` (e.g., new auth schema), the CDC schema mapping breaks.
## Agent 01 — dlt (2026-06-28 23:09 UTC)

**Package:** `dlt` (Data Load Tool) · **Wave:** 1 · **Credits:** ~110 BrowserBase + 1 GitHub API · **Time:** ~8 min

Authoritative upstream: latest is **dlt 1.28.1** (2026-06-19); we pin **`dlt>=1.0.0`** (`cianfhoghlaim/pyproject.toml:39`) and the lock resolves to **v1.25.0** (`uv tree`) — **3 minor versions behind**.

1. **First-pass file P1A-01 points to a 404 path.** It claims dlt sources live at `cianfhoghlaim/dlt_sources/` but post-v4 the real location is **`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/`** (190 `.py` files across 12 subdirs). Update P1A-01 path anchors; cc Agent 02 / 04 if they cite the old path.

2. **`@dlt.hub.transformation` / dashboard / `dlthub ai` require `dlt[hub]` extra after dlt 1.27.0** (2026-05-19). Our `pyproject.toml:39` is plain `dlt>=1.0.0`; an unannotated bump to 1.27+ will break dashboard commands silently. Fix: `"dlt[hub]>=1.27.0,<1.29.0"`.

3. **Three lazy-load TODOs predict a dlt 1.27+ break**: `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/culture/duchas_images.py:20-23`, `_duchas_images_helpers.py:14-17`, `hidden_heritages.py:18-21` — each has a `try/except` with the comment `# dlt.sources.incremental moved; use dlt.sources.incremental.IncrementalCursorProvider instead`. The `try/except` masks the import on 1.25; will throw on 1.27+.

4. **Test uses dlt private API.** `cianfhoghlaim/tests/_oideachais/dlt_sources/domains/uk/test_crown_deps.py:138` reads `res._hints.get("primary_key")` (private `_hints` dict). Will break on any dlt internal rename.

5. **dlt 1.28.0 (2026-06-15) has TWO breaking changes for our stack**: (a) `refresh="drop_data"` no longer frees Delta/Iceberg storage — must add explicit `vacuum`; (b) `replace` now fully truncates empty/orphaned tables. Plus the **1.27.2 hotfix** that truncates a `merge` table after a no-data run — highest-risk code path is `ie/law/irish_statute_book.py:87`.

6. **dlt 1.27+ native Polars DataFrame/LazyFrame support** — none of our `@dlt.resource` functions yield Polars. Strongest candidate: `leabharlann/zotero.py` (2,395 PDFs). 1.27 release notes promise ~2× row→arrow conversion via the pure-Arrow fast path.

7. **dlt destinations factory still in `docs/legacy/crypteolas/`** but migration target `cianfhoghlaim/pipelines/ingest/dlt_utils/destinations.py` is already documented in `web/apps/_oideachais_apps/CHANGELOG.md:177`. 50+ source files hard-code `destination="duckdb"` and bypass the factory's `local | production | duckdb-fallback` switch.

### Agent 01 → Agent 02 (Dagster) dependency
The 1.27 `workspace` split means **`dagster-dlt`'s `dlt_assets` decorator still works** (it's in the base dlt wheel) but **dashboard loaders / MCP servers shipped with `dagster-dlt>=0.25`** may now require `dlt[hub]`. Verify `infrastructure/dagger/.../dagster_assets.py` and any `from dlt._workspace import …` lines.

### Agent 01 → Agent 04 (DuckLake) coordination
dlt 1.28.0 bumped `ducklake` to 1.0 and `duckdb` to 1.5.3. If `stacks/lakehouse/pyproject.toml` pins older versions, the resolver will conflict on the dlt bump. **Coordinated bump required.**

## Agent 09 — Cognee (2026-06-28 23:14 UTC)

**Package:** `cognee` (knowledge-graph memory) · **Wave:** 1 · **Credits:** ~12 (Firecrawl markdown; one BrowserBase session kept open, fell back to Firecrawl for reliability) · **Time:** ~8 min

1. **Major v1.0 API redesign shipped** — `docs.cognee.ai/python-api` documents new `remember/recall/forget/improve/serve/push` as recommended entry points, replacing legacy `add/cognify/search/memify`. The legacy API still works but is being deprecated. **All 6 cognify helpers in `cianfhoghlaim/cognify/cognee_integration/*.py` and `core/memory/memory/cognee_service.py:210-216,266-267,313-314,345-346` are on the legacy path** — refactor R1.

2. **Default graph backend drifted Neo4j → Kuzu** — `docs.cognee.ai/setup-configuration/overview` documents Kuzu (file-based) as the new default for v1.2+. Our `infrastructure/stacks/cognee/compose.yaml:42-59` uses `USE_UNIFIED_PROVIDER=pghybrid` which is an **experimental flag not mentioned in current docs**. Recommended stable path: `GRAPH_DATABASE_PROVIDER=postgres` + Apache AGE (refactor R3).

3. **Dataset naming drift — silent failure risk** — `compose.yaml:42` uses dot notation (`oideachais.aistear,oideachais.primary,...`) but `cognify/cognee_integration/cross_stage_cognify.py:131` uses underscore (`oideachais_cross_stage`). Cross-stage asset will silently miss its dataset on first cognify run because Cognee dataset names are case-sensitive strings (refactor R2).

4. **`SearchType.INSIGHTS` is referenced but doesn't exist** — `core/memory/memory/cognee_service.py:376` maps `"insights"` → `SearchType.INSIGHTS` which is **not in the v1.2.2 SearchType enum** (current: SUMMARIES, CHUNKS, RAG_COMPLETION, GRAPH_COMPLETION, etc.). Will throw `AttributeError` at runtime (refactor R7).

5. **Config drift between two paths** — `infrastructure/stacks/cognee/compose.yaml` uses Postgres unified (modern lakehouse); `cianfhoghlaim/core/memory/memory/cognee_config.py:66-94` uses **Memgraph + LanceDB** (legacy crypteolas path). Two configs for one package — needs reconciliation (refactor R5).

6. **Spec path drift after v4 consolidation** — `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/P1B-09-cognee-letta.md` references paths like `oideachais/agents/meaisinfhoghlaim/memory/cognee_client.py` and `cognify/cognee_integration/graph_models/oideachais_primary.py` — these **don't exist** post-consolidation. Actual paths: `cianfhoghlaim/core/memory/memory/cognee_service.py` and `cianfhoghlaim/cognify/cognee_integration/{cross,leabharlann,official_media,...}_cognify.py`. P1B-09 spec needs updating.

7. **All cognify helpers are stub-mode by default** — `USE_LOCAL_SCRAPES=true` is the default in `cognify/cognee_integration/{cross_stage,leabharlann,official_media}_cognify.py` — production cognify runs are **disabled in CI/local dev** and only run in real production. Easy to miss during testing; check `os.environ['USE_LOCAL_SCRAPES']` before assuming a helper ran.

### Agent 09 → Wave 3 synthesis
Decide on (a) v1.0 API migration timeline + (b) Postgres-unified vs Kuzu default backend before agents touching MCP tools or compose.yaml ship conflicting changes.

### Agent 09 → Agent 06 (LiteLLM)
LiteLLM proxy is the LLM gateway for Cognee (`LLM_BASE_URL=http://litellm:4000/v1`). Agent 06's `minimax` vendor note matters here — our `LLM_MODEL=${COGNEE_LLM_MODEL:-minimax}` will route through litellm, so when Agent 06 finalizes minimax derisking, check the Cognee → litellm → minimax path actually works end-to-end (current `compose.yaml:30-41` uses DeepSeek as the *actual* default).

### Agent 09 → Agent 04 (DuckLake)
Cognee compose.yaml references `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` (line 60) but `VECTOR_DB_PROVIDER=pgvector` overrides the vector store. The LanceDB URI is dead config (refactor R8). If Agent 04 confirms Garage S3 + Lakekeeper namespace is the canonical vector target, we may want to actually wire that up instead of pgvector.

### Conflict with Agent {X}
- None at the package level. Agent 11 (Graphiti) and Agent 09 (Cognee) both interface with FalkorDB/Memgraph/Neo4j as agent memory backends — keep them distinct (Cognee = doc cognition, Graphiti = temporal agent memory).
- If another agent claims "Postgres unified is the only graph backend in KCG", note that `core/memory/memory/cognee_config.py` ALSO configures Memgraph (legacy Celtic linguistics path). Two configs, one package — may be intentionally split but the spec needs to make this explicit.

## Agent 16 — Pangolin EE (2026-06-28 22:10 UTC)

**Package:** `pangolin` (Pangolin EE + Gerbil + Newt + Pocket ID + TinyAuth) · **Wave:** 1 · **BrowserBase credits:** ~6 (1 nav + 4 Firecrawl + 1 end) · **Time:** ~7 min · **Output:** `agent-16-pangolin.md` (8 sections, 10 refactor opportunities)

1. **`mode:` is preferred over `protocol:` upstream** but **all 9 v4 `cianfhoghlaim/stacks/*/pangolin.yaml` files still use `protocol: http`** (e.g. `cianfhoghlaim/stacks/lakehouse/pangolin.yaml:11`). Upstream accepts both for back-compat; refactor R1 in `agent-16-pangolin.md` normalizes.

2. **Hyphenation rule is enforced by `stack-doctor`** — `destination_port` (underscore) fails exit 8 per `openspec/specs/infrastructure-stacks/spec.md:644-651`. All 17 stacks we ship today use `destination-port` correctly, but this is a foot-gun for new stacks. CCC already enforces the shape via the `GOLD_STANDARD.md:136-153` template.

3. **EE-vs-OSS delta for what we actually use vs. ignore**: we use EE for **(a) PostgreSQL catalog** (`postgres:17` container in `infrastructure/stacks/pangolin/compose.yaml:17-33`). We DON'T yet use **(b) `public-resources.maintenance: { enabled, type: forced|automatic, ... }`** for graceful 502s on the 5 public Traefik routes (oideachais-web/api/dagster/agent-os/adk-agents), **(c) `public-policies` reusable blocks** (we repeat `roles[0]: tinyauth@file` 9× instead of one policy), **(d) `wildcard-resources`** for sub-domain routing, **(e) wildcard TLS**. All EE; we're leaving them on the table.

4. **Newt blueprint modes are subtly different**: `--blueprint-file` (declarative, **continuous apply**, dashboard edits get overwritten) vs `--provisioning-blueprint-file` (one-shot bootstrap during `spk_...` site-provisioning-key exchange). Our `infrastructure/stacks/pangolin/newt.yaml` does neither — relies on per-stack container labels + `DOCKER_SOCKET=/var/run/docker.sock`, the **third supported mode** (works only when `sites.<key>.docker-socket-enabled: true` is set on the site).

5. **Multi-site failover is invisible without `sites:` in the blueprint** — omitting `sites:` defaults to "the Newt that applied this". Fine for 1 site; broken for HA. Our v4 `pangolin.yaml` files all omit it; `pangolin-tunnels.toml:18-29` already has the `newt-oci` skeleton ready for a `newt-bunchloch` peer. Refactor R2 in `agent-16-pangolin.md`.

6. **License posture: free EE for < $100K USD gross annual revenue** (we qualify); Starter/Scale paid tiers exist. License activated at `/admin/license` on the EE image. Same DB schema as OSS — container swap = upgrade/downgrade. (No drift today; documented in P2-11.)

7. **`pangolin apply blueprint --api-key <id.secret> --endpoint ... --org <org_id> --file /path/to/blueprint.yaml`** is the GitOps path: `PUT /org/{orgId}/blueprint` with base64-encoded JSON body. Our `infrastructure/komodo/stacks/pangolin-core-arm1.toml` and `pangolin-tunnels.toml` could be replaced by one CLI call — single source of truth, no Compose indirection. Refactor R7.

### Agent 16 — Cross-agent dependencies

- **Agent 11 (Graphiti) relies on:** the `roles[0]: tinyauth@file` pattern that all 9 v4 stacks share — refactor R3 (`public-policies`) cuts all of them simultaneously, including `graphiti.cianfhoghlaim.ie`.
- **Agent 12 (Cognee) relies on:** same — `cognee.cianfhoghlaim.ie` blueprint.
- **Agent 7 (FalkorDB) relies on:** same — `falkordb.cianfhoghlaim.ie` blueprint.
- **Agent 4 (langfuse) + Agent 5 (mlflow) rely on:** same — the 9-stack R1+R2+R3 refactor cluster under one change proposal: `openspec/changes/2026-06-28-pangolin-blueprint-v4-cleanup/`.
- **Agent 17 (openclaw), Agent 18 (forgejo), Agent 19 (frontend), Agent 20 (croilar-convex / croilar-hono-api), Agent 21 (dozzle), Agent 22 (tuatha)** all share the same `roles[0]: tinyauth@file` shape — R1+R3 normalizes them.
- **Agent 25 (Windmill), Agent 26 (Stirling-PDF), Agent 27 (SearXNG), Agent 28 (Headplane), Agent 29 (Olake)** (Phase 1B lineage) emit the SAME blueprint form in `infrastructure/stacks/<name>/blueprint.yaml` — confirmed via CCC `private-resources` search returning 70+ hits. R3 (`public-policies`) cuts 70+ files.
- **OpenSpec anchor:** `openspec/specs/infrastructure-stacks/spec.md:644-651` already has a `Scenario: A pangolin.yaml is malformed` requirement (hyphen rule). R3 (policy block) and R4 (maintenance block) should be added as new Requirements under `infrastructure-stacks`.

## Agent 03 — CocoIndex v1 (2026-06-28 23:30 UTC)

**Package:** `cocoindex` (incremental indexing engine) · **Wave:** 1 · **Credits:** ~8 (mostly webfetch; 1 BrowserBase session opened/closed, fell back to webfetch after CDP session returned only internal state)

### Findings

1. **Vector-index gap (5 Apps missing `declare_vector_index`).** `codebase_indexing.py:600-605`, `api_indexing.py:421-443`, `filesystem_indexing.py:271-281`, `storage_indexing.py:449-455`, `config_indexing.py:485-491` all call `lancedb.mount_table_target(...)` but **never** `target_table.declare_vector_index(column="embedding")`. Every `search_codebase()` query is currently brute-force over 1024-d bge-m3 vectors on a `rest://lance-api.cianfhoghlaim.ie` URI. Only `codebase_graph_app` and `docs_skills_consolidation.py` declare vector indexes. Single biggest perf regression in the codebase.

2. **Embedding-model identity drift across Apps.** `_lifespan.py:92` defaults `OIDEACHAIS_EMBED_MODEL="BAAI/bge-large-en-v1.5"` (English-only, 1024-d) but `codebase_indexing.py:93` overrides with `CODEBASE_EMBED_MODEL="BAAI/bge-m3"` (multilingual, 1024-d). Other Apps (`leabharlann_embedding.py`, `docs_skills_consolidation.py`) use the lifespan default. Both 1024-d so schema stable, but **two embedding spaces coexist** — cosine similarity between bge-m3 and bge-large-en-v1.5 vectors is meaningless. Cross-App semantic search is silently broken.

3. **Version pin is `cocoindex>=0.2.0` at `cianfhoghlaim/pyproject.toml:46`** — dangerous; would resolve to v0.3.39 if the lockfile is regenerated. The 1.0.8 release was YANKED (2026-06-11). Pin should be `>=1.0,<2.0,!=1.0.8`. Current latest is **1.0.14** (2026-06-25).

4. **14 v1 Apps in `embeddings/_oideachais_src/`** (not 12 or 13 as v4 spec claims). The conformance linter (`cocoindex_v1_conformance.py:243-258`) auto-discovers them via `repo_root.glob("*.py")`, so the inventory is dynamic — not declared in a manifest.

5. **KCG has not adopted ANY of the 1.0.1–1.0.7 engine features** — no `memo_key={...}`, no `deps=`, no `version=`, no `logic_tracking=`, no `coco.auto_refresh`, no `coco.stats_group(...)`. All `@coco.fn(memo=True)` decorators use default behavior with all args in the cache key.

6. **LanceDB vector index default is `ivf_pq` (NOT `hnsw_pq`)** per v1.0.7 connector docs. KCG infra Apps don't declare `index_type=...`, so they get `ivf_pq` (faster build, slower query) instead of HNSW-PQ.

7. **`COCOINDEX_DB` env var is not set anywhere in code** — `_lifespan.py` doesn't call `builder.settings.db_path = ...`, so LMDB state file location is implicit. Multi-process orchestration (Dagster + CLI) may produce fragmented state.

### Cross-agent deps

- **Agent 03 relies on:** Agent 04 (LanceDB) for the `rest://lance-api.cianfhoghlaim.ie` URI contract + `LanceAsyncConnection` connection lifecycle. Agent 03's `lancedb.mount_table_target(LANCE_DB, ...)` calls go through the same async connection that Agent 04 documents.
- **Agent 03 → Agent 04**: confirm whether KCG should be using `connect_namespace("rest", {...})` (per Agent 04's finding #4) or the direct `connect_async(rest://...)` form. The 14 v1 Apps currently use the latter.

### Conflict with Agent {X}

- **Conflict with P1A-03 (Phase 1A spec)**: spec claims `EMBEDDING_MODEL=BAAI/bge-m3` and `EMBEDDING_PROVIDER=litellm`. Actual code uses mixed models (`bge-large-en-v1.5` default in `_lifespan.py:92`, `bge-m3` override in `codebase_indexing.py:93`) and `SentenceTransformerEmbedder` (local, not LiteLLM). Spec also claims `LANCEDB_URI=lance://lakehouse-lance:8182/codebase` but actual default is `rest://lance-api.cianfhoghlaim.ie`. Update P1A-03 to reflect.
- **Conflict with Agent 04 (LanceDB)**: Agent 04 documented `IVF_HNSW_FLAT` / `IVF_HNSW_SQ` / `IVF_HNSW_PQ` as the only valid HNSW sub-index names in v0.33.0. CocoIndex 1.0.7 `declare_vector_index()` accepts `index_type="hnsw_pq"` (matches Agent 04's `IVF_HNSW_PQ`) but the KCG infra Apps don't declare `index_type` at all, so they get `ivf_pq` (a different index family entirely). Verify with Agent 04 whether the KCG `rest://` URI vs Agent 04's `lance-namespace:8182` stack are the same backend or two distinct LanceDB deployments.

## Agent 02 — Dagster (2026-06-28 23:10 UTC)

**Package:** `dagster` + `dagster-dlt` (orchestration) · **Wave:** 1 · **Credits:** ~70 BrowserBase · **Time:** ~8 min · **Latest:** dagster 1.13.11 / dagster-dlt 0.29.11 (2026-06-25)

### Findings (7)

1. **DRIFT — `dagster-dlt` pin is stale.** `cianfhoghlaim/pyproject.toml` (per P1A-02) pins `dagster-dlt>=0.25.0,<1.0.0`. Current latest is **0.29.11** (2026-06-25) — **4 minor versions behind, missing 6 bugfixes + 4 features**. Most important new feature: **`DltLoadCollectionComponent.partitions_def` + `backfill_policy`** support (added in 0.29.9 = Dagster 1.13.9). Bump to `>=0.29.11,<1.0.0`. → Agent 01 (dlt) coordination needed: confirm `dagster-dlt>=0.29.11` is compatible with our `dlt>=1.0.0` pin.

2. **Re-implementing upstream: `CelticDltSourceComponent` duplicates `DltLoadCollectionComponent`.** `cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_dlt_source.py:29-97` (100 lines) is a hand-rolled `dg.Component` that wraps a single DLT source. The upstream `DltLoadCollectionComponent` (shipped with `dagster-dlt>=0.29.9`) does the same thing + has native `partitions_def` support. **Delete the KCG component** and migrate 28+ DLT sources to `dg scaffold defs dagster_dlt.DltLoadCollectionComponent <name> --source X --destination Y`.

3. **NEW 1.13.x asset_check API we should adopt.** Dagster 1.13.x added 3 things we're not using: (a) **`@multi_asset_check(specs=[AssetCheckSpec(...)])`** — replaces our 12-hand-written-check loop in `assets/wire_unwired_dlt_sources.py`; (b) **`@asset_check(asset=orders, blocking=True)`** — gate downstream materialization on check failure (we have no blocking checks; the `minimax_alias_health` check at `asset_checks.py:227` is the prime candidate); (c) **`@asset_check(partitions_def=...)`** — PREVIEW feature, per-partition DQ badges in the UI.

4. **Hierarchical asset groups (1.13.9).** `group_name` now supports `/` separators (e.g. `"celtic/duchas"`) for nested UI rendering + `group:"celtic/*"` wildcard selection. Our flat names (`"celtic_language"`, `"uk_education"`, `"curriculum"`, `"pdf_processing"`, `"gguf_"`, `"leabharlann"`) need migration. One-time scripted change across ~50 `@dg.asset` decorators.

5. **v4-consolidation entry point lives at `cianfhoghlaim/assets/definitions.py` (root)**, NOT at `oideachais/dagster_defs/definitions.py` (P1A-02 path). The v4 layout has BOTH: `assets/definitions.py` (top-level 6 KB) AND `assets/_oideachais_dagster_defs/definitions.py` (587-line sub-tree). `dg.toml` modules: `oideachais.dagster_defs.definitions`. Code-locations: `oideachais` (3080), `_croilar`, `_meaisinfhoghlaim`, `_tuatha`.

6. **`@dlt_assets` decorator lives in `dagster-dlt` (not in `dlt` core).** The 7 Leaving Cert `@dlt_assets` in `assets/leaving_cert/dlt_assets.py:50` use `from dagster_dlt import dlt_assets, DagsterDltResource`. The `dlt_assets` API is unchanged in 0.29.x — our 7 sources don't need rewriting. But the hand-written `@dg.asset(compute_kind="dlt", ...)` pattern in `assets/celtic_language_assets.py:391`, `assets/uk_education_assets.py:261,351` (curriculum + 2 UK sources) is the legacy path — replace with `@dlt_assets` + `DagsterDltResource` for native asset graph integration.

7. **PARTITION CAVEAT — only 2D MultiPartitionsDefinition supported.** `partitions.py:178-179` docstring + Dagster docs both confirm Dagster only supports 2 dimensions. Our work-around: `cycle__subject` separator (line 182-193) and `subject__year` (line 218-228). Parsing via `cycle_subject.split("__")` (line 494). No 3D partitions ever. Total partition count capped at 100,000 per asset (Dagster UI warning).

### Agent 02 relies on:
- **Agent 01 (dlt)**: confirm `dagster-dlt>=0.29.11` pin is compatible with `dlt>=1.0.0` (Agent 01 noted 1.27+ has `dlt[hub]` extras requirement + 1.28.0 breaking changes).
- **Agent 03 (CocoIndex)**: the KCG Component `CelticCocoindexV1Component` (`components/celtic_cocoindex_v1.py:28-129`) wraps CocoIndex Apps — needs to align with Agent 03's findings on bge-m3 vs bge-large-en-v1.5 embedding model drift.
- **Agent 04 (LanceDB)**: the KCG Component `CelticLancedbHnswComponent` (`components/celtic_lancedb_hnsw.py:24-87`) builds HNSW indexes — Agent 04 flagged that "HNSW" alone is invalid in LanceDB 0.33 (must be `IVF_HNSW_*`). Verify what `oideachais.lancedb.indexing.build_hnsw_index` actually does.
- **Agent 05 (MotherDuck)**: Agent 05 noted "Agent 09 (Dagster) should add upstream sensor to `motherduck_sync_asset`" — actually Agent 02 territory (the breaking-change sensor at `_oideachais_dagster_defs/sensors/`).
- **Agent 06 (LiteLLM)**: Agent 06 found a potential issue with the `minimax` alias routing — the Dagster `@asset_check(asset=AssetKey(["llm_gateway"])) minimax_alias_health` is the right place to verify routing.

### Conflict with Agent {X}:
- **Conflict with P1A-02 (Phase 1A spec)**: P1A-02 says "single code-location at `oideachais/dagster_defs/definitions.py`" but v4 consolidation moved it to `cianfhoghlaim/assets/_oideachais_dagster_defs/definitions.py:496` (plus a v4 root at `cianfhoghlaim/assets/definitions.py`). P1A-02 also says "6 `@asset_check` decorators in `checks/cognee_models.py`" but those got deleted during v4 cleanup (see `asset_checks.py:35-37` comment: "Legacy checks removed - assets were in deleted ie_education_assets.py"). Current count: 9 + 12 (from `WIRE_UNWIRED_DLT_CHECKS`) + 1 (LLM gateway) = 22 `@asset_check` decorators across `asset_checks.py`.
- **Conflict with P1A-02 partition claim**: P1A-02 says "24 subjects × 4 types = 96 partitions" for `examinations`, but actual implementation in `partitions.py:218-228` is 26 subjects × 10 years × 3 levels = **780 partitions** for SEC. The 96 is the simplified figure post-`partitions_v2.py` (4 cycles vs 208).

## Agent 08 — DuckLake (2026-06-28 22:11 UTC)

**Package:** DuckLake (DuckDB + Postgres + Iceberg) · **Wave:** 1 · **Credits:** ~120 BrowserBase · **Time:** ~6 min

1. **Phase 1A-04 doc points to a non-existent file** — `phase-1a/P1A-04-duckdb-ducklake.md:43` references `cianfhoghlaim/core/ducklake/client.py` but `ls cianfhoghlaim/core/ducklake/` shows **only** `_tuatha_storage/__init__.py` (a 20-line re-export shim, unrelated). The actual canonical 882-line `DuckLakeClient` lives at `stedding/stedding/flows/education/storage/ducklake_client.py` (refactor R1).

2. **Two distinct ATTACH patterns in the codebase** — URI form (`ducklake_client.py:225-258`): `ATTACH 'ducklake:postgres:dbname=... host=... port=...'`; Secret form (`crypteolas/.../ducklake_resource.py:119-159`): `CREATE SECRET ... TYPE DUCKLAKE, METADATA_PARAMETERS MAP {'TYPE': 'postgres', 'SECRET': 'catalog_secret'}, DATA_PATH 's3://...'` then `ATTACH 'ducklake:secret_xxx'`. Both work; Secret form is prod-safer (no creds in SQL string) (refactor R6).

3. **DuckLake 1.0 (`v1.5-variegata`, April 2026) is out but version pin blocks it** — Phase 1A-04 pins `ducklake>=0.3,<1.0` (`phase-1a/P1A-04-duckdb-ducklake.md:144`) but `ducklake_options.py` already uses 1.0 features (`ALTER TABLE ... SET SORTED BY (id)`, `SET PARTITIONED BY (bucket(1000, id))`, `data_inlining_row_limit=100`). Bump pin to `>=1.0,<2.0` (refactor R2).

4. **`ducklake_time_travel` table-function may be 0.x API** — `ducklake_client.py:454` uses `ducklake_time_travel('{catalog}', {snap_id}, $${query}$$)` but the canonical GitHub README shows the SQL form `FROM lake.tbl AT (VERSION => n)`. Verify the table-function form actually exists in 1.0+ (the README for 1.5-variegata doesn't mention it).

5. **`time travel` helper has SQL-injection risk** — `ducklake_client.py:454` uses f-string interpolation for `snapshot_id` and `query` inside `ducklake_time_travel(...)`. Use bound params via `conn.execute(query, [snapshot_id])` (refactor R9).

6. **Dead code in the repo** — `stedding/stedding/flows/education/storage/ducklake.py` (352-line `DuckLakeCatalog` class) is **dead code**, pre-DuckLake-canonical (per the `2026-06-27-croilar-audit-phase-2-delete-pipelines-shared-drift` change). Only referenced by `tests/test_smoke.py` (import assertion) and `pipelines/shared/destinations.py` (which itself has no production callers). Safe to delete (refactor R4).

7. **PlanetScale env-var aliases are legacy** — `ducklake_client.py:160-165` reads `PLANETSCALE_HOST`, `PLANETSCALE_PORT`, `PLANETSCALE_DATABASE`, etc. as Postgres creds. PlanetScale was replaced by `lakehouse-postgres` (compose stack) — rename to `DUCKLAKE_PG_*` for consistency with the new `crypteolas/.../ducklake_resource.py:28-46` (refactor R3).

### Agent 08 → Agent 04 (MotherDuck)
The `infrastructure/stacks/lakehouse/examples/DuckLake to MotherDuck_ Validate locally, deploy to cloud in minutes.md` flow is the canonical Phase 4 deployment path: same DuckLake catalog, MotherDuck provides the runtime for cross-host shared data. MotherDuck **does not** replace the DuckLake catalog — they're complementary (catalog stays in `lakehouse-postgres`, compute moves to MotherDuck). Agent 04 should verify the `minimax` model doesn't break this path (Cognee → litellm → minimax, per Agent 09's note).

### Agent 08 → Agent 11 (LanceDB / vector)
DuckLake and LanceDB are **sibling storage layers**, not alternatives — same lakehouse stack, same Garage S3 bucket, different subdirs (`ducklake/` vs `lance/`). LanceDB goes through Lakekeeper/Iceberg namespace (per Agent 04); DuckLake goes through its own Postgres catalog. Agent 11's `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` dead-config issue (per Agent 09) does NOT affect DuckLake.

### Conflict with Agent 04 (MotherDuck): none on package surface, but if Agent 04 decides MotherDuck should be the only catalog (replacing the Postgres catalog), DuckLake's `ducklake_client.py` `ATTACH 'ducklake:postgres:...'` pattern would need to change to `ATTACH 'md:...'` (MotherDuck attach). Currently DuckLake is on Postgres catalog only; MotherDuck is purely runtime.

### Conflict with Phase 1A-04 (P1A-04): the doc references a file path that doesn't exist (`cianfhoghlaim/core/ducklake/client.py`). P1A-04 should either (a) update to `stedding/stedding/flows/education/storage/ducklake_client.py` as the canonical, or (b) drive a refactor to move the canonical client into `cianfhoghlaim/core/ducklake/client.py` as part of the v4 consolidation (R1).

## Agent 10 — FalkorDB (2026-06-28 23:14 UTC)

**Package:** `falkordb` (vector + graph hybrid, Redis-module built on GraphBLAS). **Wave:** 1 · **Credits:** ~9 (Firecrawl; 1 BrowserBase session opened and closed when CDP fell back to internal-state errors). **Output:** `agent-10-falkordb.md` (~300 lines, 10 refactor opportunities).

1. **Vector index uses HNSW only — NO FLAT option exists.** `docs.falkordb.com/cypher/indexing/vector-index.html` — dimension range 1–4096, similarity functions limited to `euclidean` or `cosine`. Three HNSW params: `M` (default 16), `efConstruction` (default 200), `efRuntime` (default 10). Vector data type `vecf32([...])`. Query form `CALL db.idx.vector.queryNodes(label, attr, k, vec) YIELD node, score`.

2. **Dual wire protocol: RESP (Redis) + Bolt (Neo4j-style).** `docs.falkordb.com` confirms FalkorDB speaks Redis protocol on port 6379 AND Bolt — same instance. This is why `falkordb-py` (RESP) and `neo4j-driver` (Bolt) both work; KCG uses RESP via `falkordb://` URI scheme.

3. **DRIFT: `vector.so` is NOT loaded in the production compose stack.** `infrastructure/stacks/falkordb/compose.yaml:18-37` — no `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]`. Phase-1B P1B-07 spec mandates this; the stack silently breaks every `db.idx.vector.queryNodes` call. **HIGH priority refactor** (R1 in `agent-10-falkordb.md`).

4. **graphiti-core 0.5+ introduced FalkorDB Lite (SQLite-backed embedded mode).** `cianfhoghlaim/core/cognee/_graph/graphiti_client.py:111-131` — `GraphitiClient.connect()` auto-falls-back from production `falkordb://falkordb:6379` to `falkordb_lite` at `/tmp/falkordb_lite` if unreachable. The Phase-1B P1B-07 snippet still shows the OLD `FalkorDriver(host="falkordb", port=6379)` import path — **stale**.

5. **License is SSPLv1 (Server Side Public License v1), not Apache 2.0.** `hub.docker.com/r/falkordb/falkordb` and `FalkorDB/FalkorDB/LICENSE.txt` — MongoDB-style copyleft. Blocking for any future "FalkorDB-as-a-Service" play on `arm1-oci`; fine for self-hosted use. 500K+ Docker pulls.

6. **11 built-in algorithms in 4 categories.** `docs.falkordb.com/algorithms/` — BFS, SPpath (single-source → single-target), SSpath (single-source → all), MSF (pathfinding); PageRank, Betweenness, Harmonic (centrality); WCC, CDLP (community); MaxFlow (network flow). All invoked as `CALL algo.<name>() YIELD ...`, all matrix-based on GraphBLAS.

7. **Required Redis is 8.0.0+ — 7.x and earlier NOT supported.** `docs.falkordb.com/getting-started/` — "Minimum Redis version: FalkorDB requires Redis 8.0.0 or later. Earlier versions (including the Redis 7.x series) are not supported." Docker image bundles Redis 8 internally; self-hosting requires explicit Redis 8 upgrade.

8. **Memory cost: 1M × 768-dim float32 = ~3 GB + 20% HNSW overhead.** `docs.falkordb.com/cypher/indexing/vector-index.html` — formula `vectors × dimensions × 4 bytes + ~20%`. Compose stack has `memory: 2G` limit (`compose.yaml:42`) → caps at ~660k × 768-dim vectors before OOM.

9. **`FalkorDBClient._build_property_string` (Cognee adapter) has Cypher injection.** `cianfhoghlaim/core/cognee/_graph/_shared/falkordb.py:170-177` interpolates user-controlled values into Cypher via f-strings. Refactor R4 — use `params=` binding.

### Agent 10 → Agent 11 (Graphiti)
Agent 10 found that the KCG Graphiti client (`cianfhoghlaim/core/cognee/_graph/graphiti_client.py:111-131`) uses graphiti-core 0.5's new `Graphiti(uri=...)` constructor with FalkorDB Lite fallback — not the legacy `FalkorDriver` import. Agent 11's finding #1 about the 16-param `add_episode` API applies here too (the KCG client at `graphiti_client.py:158-164` only forwards 5 of those 16 — missing `group_id`, `entity_types`, `edge_types`, `edge_type_map`).

### Agent 10 → Agent 09 (Cognee)
Both interface with FalkorDB. KCG has TWO separate FalkorDB clients: the Graphiti one (modern, with Lite fallback) and the Cognee one (`_graph/_shared/falkordb.py`, no vector method, Cypher-injection bug). Agent 09 should NOT replace the Cognee FalkorDB adapter with the Graphiti one — they serve different purposes. But the vector-query capability gap should be filled in the Cognee ABC (refactor R5).

### Agent 10 → Agent 16 (Pangolin)
`pangolin/private-resources.blueprint.yaml:62-97` exposes falkordb Browser UI at `falkordb.cianfhoghlaim.ie` (port 3000) but NOT the RESP port 6379. If we ever run the Graphiti server on a different stack host (e.g. dedicated agent VM on `arm1-oci`), we'll need to add a Pangolin route for `falkordb.cianfhoghlaim.ie:6379`. (Agent 10 refactor R7.)

### Conflict with Agent {X}:
- **Conflict with P1B-07 (Phase 1B spec)**: P1B-07 mandates `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]` (`phase-1b/P1B-07-falkordb-graphiti-dragonfly-risingwave.md:34-38`) but `infrastructure/stacks/falkordb/compose.yaml` does NOT have this `command:` field. P1B-07 snippet also shows the stale `FalkorDriver` import path. Open a `openspec/changes/falkordb-vector-so-loadable/` change to fix.

## Agent 20 — MLX-omni (2026-06-28 22:10 UTC)

1. **CRITICAL: P2-24 spec drift on upstream repo** — P2-24:1 declares `qifengle/marketplace-mlx-omni-server`, but `infrastructure/stacks/mlx-omni/Dockerfile:19` and `README.md:55` actually use `madroidmaq/mlx-omni-server` (730★, 296 commits, v0.5.3 May 2026). The `qifengle/marketplace-mlx-omni-server` repo appears not to exist or be a fork.

2. **CRITICAL: P2-24 spec drift on package name + CLI** — P2-24:26 declares `pip install mlx-omni` + `mlx-omni serve --model …`. Upstream `pyproject.toml:2,38` shows actual package name is `mlx-omni-server`, CLI is `mlx-omni-server` (no `serve` subcommand, auto-discovers from HF cache, only accepts `--port`). `infrastructure/stacks/mlx-omni/Dockerfile:39` has the **broken invocation** `mlx-omni serve --host 0.0.0.0 --port 10240` — needs fix.

3. **CRITICAL: P2-24 spec drift on API surface** — P2-24:10 says "OpenAI-compatible server". Upstream v0.5.3 added **dual API**: OpenAI `/v1/*` AND Anthropic `/anthropic/v1/*` (`/v1/messages` with tools, streaming, thinking mode). Cianfhoghlaim only wires OpenAI surface via LiteLLM (`config.yaml:34-65`) — Anthropic surface is uncommitted.

4. **MLX quantization spectrum confirmed** — mlx-community registry (`huggingface.co/mlx-community`, 5,184 models as of 2026-06-28) hosts MLX weights at **3-bit, 4-bit, 5-bit, 6-bit, 8-bit, bf16, fp16**. Naming convention: `{model_name}-{quant}` (e.g. `Qwen3-4B-Instruct-2507-4bit` = 0.6B params, 2.26 GB on disk). The 4-bit suffix is the dominant pattern.

5. **7-package MLX dependency tree** — upstream `pyproject.toml:20-39` depends on `mlx>=0.31.2,<0.32` (darwin-only via `sys_platform == 'darwin'`), `mlx-lm`, `mlx-vlm`, `mlx-audio[tts]`, `mlx-whisper`, `mlx-embeddings`, `mflux>=0.17.5`, `f5-tts-mlx`. **Pinned** `outlines==1.0.4` for structured output. `transformers>=5.5.0,<5.9` (transformers v5).

6. **3 actual MLX models wired into LiteLLM** — `config.yaml:34-65` wires `local/document/granite-docling` (258M), `local/ocr/olmocr-mlx` (2-7B 4-bit), `local/image/fibo` (Bria FIBO JSON-driven). 4 alias routes (`ocr:565`, `document:591`, `image-fibo:654`) prefer MLX with GGUF fallback. P2-24:90 claim of "11 vision + 4 text" is **aspirational, not currently wired**.

7. **Memory + hosting constraint** — `compose.yaml:46` caps at 36 GB (M-series unified memory); P2-24:80 anti-pattern says "Don't exceed 48 GB". MLX darwin-only dep confirmed via `pyproject.toml:21` `sys_platform == 'darwin'` and Dockerfile:26-29 explicit warning. P2-24:79 anti-pattern holds.

### Agent 20 → Agent 14 (litellm)
Confirmed `http://mlx-omni:10240/v1` is canonical URL in `infrastructure/stacks/litellm/config/config.yaml:34,37,48,59`. The 3 model_list entries + 4 alias routes (`ocr`, `document`, `image-fibo`, `document/granite-docling`) ALL prefer mlx-omni over GGUF/cloud. Agent 14's litellm work should preserve this priority order.

### Agent 20 → Agent 22 (llama-swap)
MLX (mlx-omni :10240) vs GGUF (llama-swap :8080) is a **hosting-axis split**: MLX is darwin-only (M-series), GGUF is cross-arch (CPU/any). The `ocr` alias `fallback_chain` (`config.yaml:575`) is `["local/ocr/olmocr-mlx", "local/ocr/deepseek-ocr", "gemini/gemini-2.5-flash"]` — first MLX attempt, then GGUF, then cloud. This is the canonical 3-tier local→cloud fallback.

### Conflict with P2-24
- **Spec drift (5 separate conflicts)** — see findings #1, #2, #3, #6 above. All 5 are easy fixes to `P2-24-mlx-omni.md` once Agent 20's output is reviewed.

## Agent 22 — OpenChamber — top 3 findings

1. **CRITICAL: P2-20 research file is drifted from the deployed reality** — `phase-2/P2-20-openchamber.md` claims `image: openchamber/openchamber:latest`, `ports: ["3030:8080"]`, an `openchamber-postgres` service, `LITELLM_BASE_URL=http://litellm:4000/v1`, and an embed in `oideachais-web/src/routes/agents.tsx` — **none of which exist in `infrastructure/stacks/openchamber/compose.yaml`**. The actual stack uses `ghcr.io/openchamber/openchamber:1.0.0@sha256:0…0` on `127.0.0.1:3000:3000`, named-volume state only, and direct provider keys. P2-20 is the document that ships a fictional Postgres+LiteLLM stack; the real stack is bundled-mode + Pangolin + direct keys. (R1 — rewrite P2-20.)

2. **Upstream is REAL and well-architected (5.9k★, 620 forks, MIT, v1.11.7)** — `openchamber/openchamber` is a Bun + React + Electron 41 + VS Code extension monorepo (`packages/{ui, web, electron, vscode}`). Server is Express (`packages/web/server/index.js`); Electron **boots the web server in-process** via `startWebUiServer({...})` — no sidecar subprocess. OpenCode wire is `import @opencode-ai/sdk/v2` + Express-side `createOpencodeServer`; state is Zustand + SSE event pipeline. Our `compose.yaml` follows the upstream bundled-mode contract (no `OPENCODE_HOST`, no `OPENCHAMBER_TUNNEL_TOKEN`).

3. **Komodo glue from proposal.md is not on disk yet** — `openspec/changes/add-openchamber-stack-and-opencode-ui/proposal.md:82-87` references `infrastructure/komodo/stacks/openchamber-arm1-oci.toml` and `infrastructure/komodo/procedures/deploy-openchamber-arm1-oci.toml`, **but these files do not exist**. The 6-file GOLD_STANDARD compose set is in place; the Komodo deploy automation is the missing piece. (R4 cross-link with Agent 17 — komodo.) Also `compose.yaml:29` still has the zero-digest placeholder `sha256:0000…0000` — R2 says resolve the real digest before first deploy.

### Agent 22 → Agent 06 (litellm)
**No LiteLLM integration in openchamber stack.** The 3 LLM provider keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MINIMAX_API_KEY`) are direct Infisical refs injected by Locket — the upstream `provider picker` UX bypasses LiteLLM. Agent 06's work is not affected; do **not** add `LITELLM_BASE_URL` to `secrets.env` (would break upstream provider picker).

### Agent 22 → Agent 17 (komodo)
The `deploy-openchamber-arm1-oci` procedure and `openchamber-arm1-oci.toml` stack file referenced in the proposal do not exist on disk. The change is partially-merged: compose set in place, Komodo glue missing. R4 in agent-22 output is for the openchamber README; the Komodo-side follow-up belongs to Agent 17.

### Agent 22 → Agent 21 (openclaw)
**Two complementary agent-UI surfaces, no consolidation needed.** `openclaw` is the chat-assistant UI; `openchamber` is the coding-agent IDE (OpenCode-specific). Both share the same `arm1-oci / 1 CPU / 1 GB / bundled + no-tunnel` budget pattern. R4 recommends a cross-link in both READMEs so operators see them side-by-side.

### Conflict with P2-20
- **6-line spec drift** — see finding #1 above. All 6 lines in `phase-2/P2-20-openchamber.md` (image, port, Postgres, LiteLLM, Langfuse, TanStack Start embed) need to be deleted/replaced with the actual deployed reality.

## Agent test-rerun — verified at 2026-06-28 22:43 UTC — status: working

## Agent 25 — Crown+Reference — top 3 findings per site (15 lines total)

1. **Jersey opendata.gov.je is a full CKAN 2.8.12 with 110+ OGL-J-1.0 datasets and a JSON API at `/api/3/action/{package_list,package_show,datastore_search}` — and we ingest ZERO of them.** `sources.yaml:278-284` declares jey.education.govje as `kind: firecrawl_pages`; the `education` CKAN package alone has a structured `total-students-by-school-type.csv` (Statistics Jersey, 618 bytes, modified 2024-11-28). **CRITICAL DRIFT — single highest-ROI refactor in this report (R6).**
2. **IoM uses F5 Volterra ADC + iLAWSSYNC legislation CMS, robots.txt explicitly blocks GPTBot, and `legislation.gov.im` exposes 750+ Acts / 2,500+ versions as deterministic PDFs at `https://legislation.gov.im/cms/images/LEGISLATION/{PRINCIPAL|SUBORDINATE|BILLS|GAZETTES}/{year}/{id}/{id}_{version}.pdf`.** `iom/law/legislation.py:24-29` crawls the HTML portal at `max_pages=50` but never fetches the actual PDFs. The "Advanced Search" link in the live site now points to a 3rd-party VPS at `888295.vps-10.com` — a security/audit smell. Add a PDF harvester (R1).
3. **Guernsey uses GOSS iCM CMS with no robots.txt, no sitemap.xml, mandatory session cookies ("Your session has expired" on every page), and PDFs served via `CHttpHandler.ashx?id=…`.** `ggy/education/channel_islands.py:23-44` crawls only `/education*` + `/schools*` paths with no PDF harvest and no session-cookie persistence. Add a `gs_*` cookie warmer + a `CHttpHandler.ashx` PDF harvester (R11/R12).
4. **Zotero API v3 at `https://api.zotero.org` returns JSON/Atom/bib/CSL-JSON, no auth for public libs, but enforces 4-concurrent-requests max + `Backoff` / `429 + Retry-After` headers + `Last-Modified-Version` for conditional GETs.** `leabharlann/zotero.py:94-124` reads **filesystem PDFs only** (filename-derives arxiv_id) — zero Zotero API calls. The 5 best client libs (per docs): `urschrei/pyzotero` is the Python choice. Add a `@dlt.incremental` on `Last-Modified-Version` (R15/R19).
5. **arXiv REST at `http://export.arxiv.org/api/query` requires a 3-second polite delay between calls, max 30,000 results in 2,000-result slices, returns Atom 1.0 with `arxiv:doi` / `arxiv:journal_ref` / `arxiv:primary_category` extensions.** OAI-PMH at `https://oaipmh.arxiv.org/oai` (since March 2025) supports bulk sync via `ListRecords&from=<last>` with sets like `cs:cs:AI`. `cognify/rules/leabharlann_cross_archive.py` matches GeminiReport→ZoteroPaper by arxiv_id but **never enriches** with abstract/authors/DOI from arXiv. Add `arxiv_api_source` + bulk `arxiv_oai_pmh_source` (R20/R21) + the mandatory "Thank you to arXiv" acknowledgement (R23).

**Output:** `openspec/research/2026-06-28-browserbase-program-2/agent-25-crown-ref-sites.md` (247 lines, 23 refactor items R1–R23). **Agent 25 relies on:** Agent 09 (Cognee) for the leabharlann cognify consumer of the enriched metadata; Agent 01 (dlt) for the `@dlt.incremental` cursor pattern; Agent 18 (Infisical) for the new `LEABHARLANN_ZOTERO_API_KEY` vault entry.

## Agent 12 — Garage — top 3 findings (3 lines)
1. **SEVERE VERSION DRIFT**: Cianfhoghlaim pinned at `dxflrs/garage:v1.0.1` (Dec 2024) but upstream latest is **v2.3.0** (Apr 2026, 8 releases behind, 18 months stale); present in BOTH `infrastructure/stacks/garage/compose.yaml:21` AND `infrastructure/stacks/lakehouse/compose.yaml:30`.
2. **v1→v2 BREAKING CHANGES BLOCK UPGRADE**: v2.0.0 (Jun 2025) removed `replication_mode` (we still use `replication_mode = "1"` in `garage.toml:5,18` — will fail to start) and reworked admin API `/v1/*` → `/v2/*` (our 90-line `garage-init` in `lakehouse/compose.yaml:71-160` hard-codes `/v1/` endpoints — will 404).
3. **v2.3.0 OBSOLETES OUR INIT CONTAINER**: New `garage server --single-node --default-access-key --default-bucket` env-var flags auto-create layout, access key, and bucket — enables deleting the entire 90-line `garage-init` bash sidecar; PLUS security: `lakehouse/garage.toml:31,68` has hardcoded `rpc_secret` and `admin_token` (standalone stack does this right with envsubst). Repo is on `git.deuxfleurs.fr` (Forgejo) — GitHub URLs `txpipe/garage` and `Deuxfleurs/garage` both 404.

## Agent 23 — Ireland sites — top 3 findings per site (9 lines total)

1. **curriculumonline.ie (NCCA primary+JC+SC portal)**: The `phase-3/S01` URL pattern `/en/Primary/{subject}/{strand}/{unit}` is DEAD — `/en/` returns 404. Live pattern is `/primary/curriculum-areas/{subject}/` (no `/en/`). New `/2026-primary/...` route redirects to `/User/Signin` (reCAPTCHA + TCA teacher-only gate). PDF pattern is `/getmedia/{guid}/{slug}.{ext}?ext=.png&width=...` NOT `/getfile/{id}`. `source_adapters.py:230-238` hardcodes the broken legacy URL.
2. **curriculumonline.ie — spec drift on curriculum areas**: Phase 3 S01 claims "12 curriculum areas × ~3 docs"; live site confirms **5 broad areas** (Language, STEM, Wellbeing, Arts Education, Social & Environmental Education). Bilingual is `/ga-ie/` PATH PREFIX (not subdir), only on the legacy `/en/...` paths. `/sitemap.xml` does NOT exist — must use Firecrawl `map` seeded by stage+subject index.
3. **curriculumonline.ie — TCA-gated content is silent data loss**: `[TCA]` marker means teacher-only. `agentic_discovery.py:273-302` falls back to Stagehand but Stagehand can't solve reCAPTCHA. Need a teacher service-account stored in Infisical at `oideachais/sources/curriculumonline_teacher/{email,password}`.
4. **examinations.ie (State Examinations Commission)**: Phase 3 S02 URL pattern `/en/educational-resources/`, `/en/exam-archive/leaving-certificate/`, `/en/exams/-archive-leaving-cert/...` ALL HALLUCINATED — they 404. Real landing is **`/exammaterialarchive/`** with a T&Cs checkbox gate. Real PDF pattern is **`/tmp/{unix_ts}_{id}.pdf`** or `/misc-doc/EN-{cat}-{id}.pdf`. Bilingual via `?l=ir&mc=...&sc=...` query params (NOT `/ga/`).
5. **examinations.ie — T&Cs click is the critical missing step in `examinations.py:306-399`**: `sec_examinations_browser_source` opens the archive but does NOT click the T&Cs checkbox — the subject/year dropdown never renders. Add `stagehand_act("click", selector="input[type='checkbox'][name='accept-terms']")` BEFORE any subject interaction. Bypass via ~40 direct-PDF links from SEC home + `/about-us` (no Stagehand needed for those).
6. **examinations.ie — anti-scraping posture is WEAK**: `robots: index, follow`, no Cloudflare challenge, no rate limit, server-side HTML, no JS. Only blocker is the T&Cs checkbox + the per-page `?l=en&mc=...&sc=...` nav (3 query params, 6 levels, 5 components = 90 permutations per subject — fully enumeratable). Subdomain `fees.examinations.ie` MUST be excluded.
7. **ncca.ie (NCCA main portal — policy/research)**: Sister site to curriculumonline (this one hosts **frameworks, background papers, consultations, research reports**; curriculumonline hosts the **specs**). Bilingual via clean `/en/` + `/ga/` SUBDIRS. Real PDF pattern is **`/media/{id}/{slug}.pdf`** with TWO ID formats coexisting (5-char alnum like `5gfbsf4c` + numeric like `1085`, `1504` — legacy migration). `source_adapters.py:262-263` returns `"ncca.ie"` (no scheme) — should be `"https://ncca.ie"`.
8. **ncca.ie — Dublin Core metadata is unused**: `<meta name="DC.Title|Identifier|Date.Created|Rights|Format|Language">` tags present in every page head but `ncca.py:149-308` dlt sources only scrape body, discarding the free metadata. Should be `NormalizedPage.metadata.dublin_core` block. **`googlebot: noindex,indexifembedded`** = site explicitly blocks Google index (but allows embed) — use Firecrawl not Google. Image cache-bust `?v={hash}` (e.g. `v=1db62a9b183edd0`) breaks content-dedup.
9. **Cross-site synthesis**: 3 sites = 3 URL conventions, 3 PDF patterns, 2 bilingual mechanisms. ~3,000 PDFs total. Cross-site dedup documented in `content_deduplication.py:87-88` but not implemented (Mathematics spec appears on both curriculumonline + ncca). Best first ingest = **ncca.ie** (open, smallest, DC metadata); best parallel-corpus demo = **curriculumonline.ie** (cleanest `/ga-ie/` mirror); most expensive = **examinations.ie** (T&Cs + Stagehand + 3,600 PDFs). Wayback fallback viable for all 3.
