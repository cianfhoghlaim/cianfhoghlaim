# Feature Backlog — Cianfhoghlaim

**Agent 27 of 27 — feature-backlog-builder** · 2026-06-28 · Wave 2 synthesis
**Inputs:** 25 wave-1 agent outputs + `SHARED_DISCOVERY_LOG.md` (503 lines) + 34 capability specs
**Output budget:** 20+ NEW features (no refactors) · ≤ 400 lines

---

## 1. TL;DR — Top 3 features to ship next quarter

1. **Realtime CDC pipeline (RisingWave v3 + olake + Iceberg v3 exactly-once)** — the single biggest *unblocker* in the program. Every agent (RisingWave, olake, Iceberg, Dagster, dlt, CocoIndex) is already on the bus; the only missing piece is end-to-end glue. Once this lands, *every* dlt batch source becomes a streaming source for free, and Cognee/Graphiti/RAGAS all gain real-time triggers.
2. **Multilingual embeddings unification (bge-m3 everywhere)** — the Agent 03 finding (`bge-m3` vs `bge-large-en-v1.5` coexistence makes cross-App semantic search silently broken) is a quiet correctness bug that will compound as we add 6 more language corpora. One-week fix, ~10× improvement in Irish+English+Scottish+ Welsh+Manx retrieval.
3. **Edge BAML extraction (Cloudflare Workers + baml-edge)** — moves the 8 BAML inline `anthropic/claude-sonnet-4-20250514` calls (Agent 15 finding #1) off the LiteLLM hot path. Sub-100ms P50 for short extractions (curriculum area classification, fediverse actor resolution) = unlocks a new "click-and-extract" UX in TanStack Start.

---

## 2. Methodology

Backlog derived from three independent lenses, cross-checked against the 34 capability specs in `openspec/specs/`:

1. **Cross-package integration gaps** — agent outputs that name 2+ packages and surface a missing glue layer (e.g. Agent 01 ↔ 02 on dlt-dagster partitions, Agent 09 ↔ 04 on dead `LANCEDB_URI` config). Each gap is a *feature opportunity* (e.g. "unified observability", "unified embedding space").
2. **User pain points surfaced by agents** — Agent 23 (TCA-gated curriculumonline), Agent 24 (gov.wales WAF CAPTCHA), Agent 25 (Jersey CKAN zero-ingest). These are the *content* features that turn a 4-quadrant curiosity into a real public platform.
3. **Tech-debt → features** — items agents flag as drift, but framed as a *new capability* (e.g. Garage v1→v2 isn't a refactor, it's "Multi-region S3 with v2 admin API" — a feature for Tuatha's MMO and Croilar's portfolio).

Excluded by design: pure refactors (dagster-dlt pin bumps, dataset naming, Cognee v1 API migration). Those are *program-2 phase-3* work, not features.

Prioritisation rubric: **value = (new capability unlocked × external user impact) / (effort × cross-team coordination cost)**. S = < 1 wk solo, M = 1-3 wk squad, L = 1 quarter cross-team.

---

## 3. P0 — Next quarter (unlock new capabilities)

### F-01 · Realtime CDC pipeline (RisingWave v3 + olake → Iceberg v3)
- **Description:** End-to-end change-data-capture fabric. olake does batch snapshot CDC from PG/Mongo/MySQL; RisingWave v3 does streaming CDC + materialized views; both write to the existing Iceberg/Lakekeeper catalog with v3's new exactly-once commit (Agent 14 finding #3). Replaces the polling patterns in agent stacks with `CREATE SUBSCRIPTION` push (Agent 14 finding #6).
- **Value:** Every dlt batch source becomes a streaming source. Cognee `remember()` fires on upstream change instead of nightly cron. RAGAS asset checks run on every change.
- **Effort:** L (cross-team: RisingWave + olake + Dagster + Iceberg)
- **Dependencies:** Agent 14 (RisingWave v3 4-node split), Agent 01 (dlt 1.28.0 `refresh="drop_data"` behaviour), Iceberg REST catalog on Lakekeeper, `stacks/risingwave` + `stacks/olake` already exist.
- **MVP:** Wire `litellm_db_cdc` (already templated at `init.d/01_init.sql:124-138`) through RisingWave → Iceberg → LanceDB. One source end-to-end before generalising.

### F-02 · Multilingual embeddings unified (bge-m3 across all CocoIndex Apps)
- **Description:** Fix Agent 03 finding #2 — kill the silent bge-m3 + bge-large-en-v1.5 coexistence. Standardise on `BAAI/bge-m3` (multilingual, 1024-d) for *all* 14 v1 CocoIndex Apps (`codebase_indexing`, `api_indexing`, `filesystem_indexing`, `leabharlann_embedding`, etc.) and add `declare_vector_index(column="embedding", index_type="IVF_HNSW_SQ")` (Agent 03 finding #1 + Agent 04 vocabulary fix).
- **Value:** Cross-App semantic search actually works (cross-corpus queries on Irish + English + Scottish Gaelic + Welsh + Manx). CCC + Cognee + RAGAS queries can chain across App boundaries.
- **Effort:** M (single squad)
- **Dependencies:** Agent 04 LanceDB v0.33 vocabulary, Agent 03 `_lifespan.py` default, `oideachais-semantic-search` spec, 1× GPU warm pool for re-embedding 5 corpora (~12 M chunks).
- **MVP:** Re-embed `codebase_indexing` + `leabharlann_embedding` first, validate cross-corpus recall, then sweep the remaining 12 Apps.

### F-03 · Agent observability dashboard (Langfuse v3 OTEL)
- **Description:** Replace the v2 LiteLLM callback (Agent 06 finding #4) with native OTEL → Langfuse v3. Adds 3 panels: per-agent cost/latency, BAML `Collector(name)` token metrics (Agent 15 finding #5), RAGAS eval scores as a per-trace heatmap. Wires 12 specialised agents (`meaisinfhoghlaim-agent-frameworks`) + 13 model-layer agents (`indexing-and-cognition`) into one trace tree.
- **Value:** First time we can answer "which agent costs the most per curriculum task?" and "where does the Irish translation fallback chain fire?". Required for the budget-and-ROI conversation with MotherDuck business-tier spend.
- **Effort:** M
- **Dependencies:** Agent 06 LiteLLM→Langfuse OTEL migration (`openspec/changes/litellm-langfuse-otel/`), Agent 15 BAML `Collector` adoption, `agent-observability` spec.
- **MVP:** Langfuse v3 OTEL collector + one dashboard (per-agent cost). Defer RAGAS heatmap to P1.

### F-04 · Serverless GPU burst (Modal A100/H100)
- **Description:** Burstable GPU for Unsloth fine-tunes (Agent 19), Gemma 4 patches, MTP speculative-decoding evals, FIBO image gen. Modal's per-second billing + the M4 Mac's 36 GB cap (Agent 20) makes this the only sane path for >13B parameter work.
- **Value:** Unblocks Unsloth Gemma 4 31B training + any cross-encoder reranker fine-tune. Modal's `modal_unsloth.py` reference pattern + HF Jobs as fallback.
- **Effort:** M
- **Dependencies:** Agent 19 Unsloth FastModel migration (finding #1), HF `hf` CLI (Agent 21), `meaisinfhoghlaim-ocr-htr` spec, `unsloth_trainer.py:339` already wires `report_to=["mlflow"]`.
- **MVP:** Wrap Unsloth 11-model train loop with `modal.Image.from_registry(...)`; one Gemma 3 4B LoRA on A100 as the pilot.

### F-05 · Edge BAML extraction (Cloudflare Workers)
- **Description:** Move the 8 inline `anthropic/claude-sonnet-4-20250514` BAML calls (Agent 15 finding #1, `_oideachais_src/curriculum_extraction.baml:164-1086`) and the 6 `clients_0.baml` legacy Gemini clients to a Cloudflare Workers edge runtime. Use `baml-edge` (WASM-compiled BAML runtime) for type-safe structured extraction at <100 ms P50.
- **Value:** TanStack Start gets a "click-and-extract" UX (extract from any visible web text client-side). Removes 8 calls from the LiteLLM hot path → 30% gateway load reduction.
- **Effort:** L (new runtime, new infra stack)
- **Dependencies:** Agent 15 BAML `generators.baml` bump to 0.223.0, `infrastructure-stacks` (new `stacks/baml-edge/`), Locket secret injection at the edge.
- **MVP:** One Worker running `PreResearchSite.recommended_schema` extraction on `celtic-data-engineering-patterns` URL lists.

### F-06 · Cognee v1.0 remember/recall/forget migration
- **Description:** Migrate the 6 legacy `add/cognify/search` callers (Agent 09 finding #1) to the new `remember/recall/forget/improve/serve/push` v1.0 API. Unlocks 4 features: session-aware recall, `improve()` feedback weights, `serve()` HTTP exposure, and `push` to remote Cognee instances.
- **Value:** Agents gain persistent + session-aware memory; RAGAS eval can use the same memory; multi-tenant memory partitioning becomes trivial.
- **Effort:** M
- **Dependencies:** Agent 09 R1 (v1 API migration) + R2 (dataset naming) + R5 (config reconciliation).
- **MVP:** Migrate `cross_stage_cognify.py` + `leabharlann_cognify.py` only. Keep Memgraph path working via ABC.

### F-07 · Cognee + Graphiti dual-memory agent runtime
- **Description:** Single `agent_memory_client` ABC that lets the 12 specialised agents choose per-call: Cognee for document cognition (chunked semantics, summaries), Graphiti for temporal + episodic (Agent 11's 5 edge types, bi-temporal). Today the two are independent (Agent 09 conflict note).
- **Value:** Curriculum agents can reason over *what changed* (Graphiti) AND *what's documented* (Cognee) in one query. Required for any "explain why the new spec differs from the old one" tutor UX.
- **Effort:** L
- **Dependencies:** Agent 09 (Cognee v1), Agent 11 (Graphiti 16-param `add_episode`), `agent-memory-systems` spec.
- **MVP:** Dual-memory wrapper in `core/memory/memory/dual_memory_client.py`, used only by `Curriculum` agent.

---

## 4. P1 — Next 2 quarters (medium value)

### F-08 · Browserbase research codegen workflow
- **Description:** Programmatic version of the 43-prompt BrowserBase research flow that just produced this report. Reads `openspec/specs/*/spec.md`, asks the 7 standard code-pattern questions, emits one Markdown per package under `openspec/research/<date>/`, cognifies into `research_findings` Cognee dataset, runs RAGAS on every 5th output.
- **Value:** Every new package we adopt (CocoIndex, BAML, olake, etc.) gets a 7-section template document for free. Replaces ad-hoc docs hunts with a versioned research corpus.
- **Effort:** M
- **Dependencies:** This very synthesis + the SHARED_DISCOVERY_LOG pattern + `agent-experience` skill, Cognee `research_findings` dataset, RAGAS trace-based metric.
- **MVP:** Wrap Agent 27's own prompt as a template; re-run on `celtic-asset-generation` and `oideachais-baml-schemas`.

### F-09 · 3D asset generation (Tuatha MMO)
- **Description:** Babylon.js procedural Celtic asset pipeline (Celtic knots, ogham stones, round tower variants, illuminated-mana capital letters) using FIBO image gen (already wired at `litellm/config.yaml:654`) + a new TripoSR / InstantMesh mesh-from-image microservice. Output → `tuatha/game/assets/` in glTF 2.0.
- **Value:** Tuatha MMO gets 100+ free Celtic-themed 3D props/month without a 3D artist.
- **Effort:** L (cross-domain: gen + 3D pipeline + game client)
- **Dependencies:** `celtic-asset-generation` spec, mlx-omni `image-fibo` alias, Tuatha Babylon.js client.
- **MVP:** Round-tower generator (image → mesh → glTF → Babylon.js scene).

### F-10 · Multimodal search (text + image)
- **Description:** Extend `oideachais-semantic-search` to search over BAML-extracted `image_caption` + `image_embedding` columns. Use ColPali / ImageBind from LanceDB's embedding registry (Agent 04 finding #6). 3-stage: image embed → caption BAML extract → text search hybrid.
- **Value:** Duchas image archive (Agent 01 finding #2: `duchas_images.py` lazy-load) becomes queryable. "Find me all images showing round towers in fog" works.
- **Effort:** M
- **Dependencies:** Agent 01 (Polars fast path for image metadata), Agent 04 ColPali provider, `oideachais-semantic-search` spec.
- **MVP:** Text-only search over `image_caption` first; add image embed in the next iteration.

### F-11 · Audio transcription improvements
- **Description:** Wire `mlx-whisper` (Agent 20 finding #5 dep) + `mlx-audio[tts]` for Irish-language ASR/TTS. Add `whisper-large-v3-turbo` as the new default. 11 OCR models already have the compute path.
- **Value:** Tuatha in-game voice + Croilar podcast transcription + the `leabharlann` audio corpus (Mártainn Ó Cadhain recordings) all become searchable.
- **Effort:** M
- **Dependencies:** Agent 20 mlx-omni, `meaisinfhoghlaim-ocr-htr` spec (extend to audio), `local/irish` BAML client.
- **MVP:** Whisper large-v3-turbo on 50 hours of `leabharlann` audio; measure WER.

### F-12 · MotherDuck Dives customer-facing analytics
- **Description:** Dives (Agent 05 finding #3) replace marimo for the 4 customer-facing dashboards. Live React + SQL, version-controlled, shareable, stateful via URL. `REQUIRED_DATABASES` auto-attaches share-backed MotherDuck DBs.
- **Value:** Dives embed into TanStack Start with a single `<DiveEmbed src="..."/>`; first true "Cianfhoghlaim as a product" surface.
- **Effort:** M
- **Dependencies:** Agent 05 (BYOB bucket, MotherDuck auth, region pinning), `motherduck-analytics` skill.
- **MVP:** One Dive on the `oideachais_primary_curriculum` share → embed in `oideachais-web`.

### F-13 · IoM + Jersey + Guernsey legal corpus (crown dependency ingest)
- **Description:** Agent 25 R1 (IoM PDF harvester at `legislation.gov.im/cms/images/LEGISLATION/...`) + R6 (Jersey CKAN 110+ OGL-J-1.0 datasets) + R11/R12 (Guernsey `CHttpHandler.ashx` PDFs + session-cookie warmer). Cross-crown dependency legal corpus with deterministic URL patterns.
- **Value:** First time we have a structured Channel Islands + Isle of Man legal corpus. ~3,500 PDFs total, fully bilingual where applicable.
- **Effort:** M
- **Dependencies:** Agent 25 R1/R6/R11/R12, dlt `@dlt.incremental` (Agent 01), Infisical vault entries for any gated cookies.
- **MVP:** Jersey CKAN `education` package + IoM legislation PDFs (deterministic URL → no cookies).

### F-14 · Celtic Teacher Corpus (TCA-gated curriculumonline)
- **Description:** Agent 23 finding #3 — TCA-gated content is silent data loss. Add a teacher service-account flow: `oideachais/sources/curriculumonline_teacher/{email,password}` in Infisical, signed-in dlt source, automated reCAPTCHA handoff to a human queue when score crosses threshold.
- **Value:** Unlocks the 30% of curriculumonline content that is teacher-only. Required for any "Celtic teacher training" feature downstream.
- **Effort:** S (with a teacher; L without one)
- **Dependencies:** Agent 23 R3, Locket secret injection, `ireland-primary-jc-dlt-baml` spec.
- **MVP:** Stagehand `act("fill", email=...)` + `act("fill", password=...)` + manual reCAPTCHA fallback queue.

### F-15 · HuggingFace Webhooks + OAuth CIMD
- **Description:** Adopt Agent 21 finding #3 — (a) `webhooks` OAuth scope for real-time repo-change push into a CocoIndex v1 `upstream_hf_monitor` App; (b) Public OAuth apps + CIMD at `/.well-known/oauth-cimd` for native CLI auth (replaces `huggingface-cli` warning behaviour); (c) 5-min `RateLimit` HTTP header auto-parsing.
- **Value:** `upstream-package-monitoring` spec goes from 30-min polling to real-time. CLI auth stops prompting for tokens on every machine.
- **Effort:** S
- **Dependencies:** Agent 21, `upstream-package-monitoring` spec, Infisical `hf_oauth_client_id` + `hf_oauth_client_secret`.
- **MVP:** Webhook for 5 watched models (Unsloth Gemma 3 / Qwen 3) → CocoIndex App → RAGAS eval trigger.

---

## 5. P2 — 6 months (nice-to-have)

### F-16 · Garage v2.3 multi-region S3 (with v2 admin API)
- **Description:** Agent 12 — migrate `dxflrs/garage:v1.0.1` → v2.3.0. New `--single-node --default-access-key --default-bucket` env-var flags kill the 90-line `garage-init` bash sidecar. Hardcoded `rpc_secret` / `admin_token` move to envsubst.
- **Value:** Multi-region Garage for Tuatha (EU) + Croilar (US-east) + Oideachais (UK-west) → geofenced compliance.
- **Effort:** M (single infra change, 2-week validation)
- **Dependencies:** Agent 12, 2× `arm1-oci` peers, `infrastructure-stacks` spec.

### F-17 · Pangolin EE public-policies block (70+ stack blueprints)
- **Description:** Agent 16 R3 — extract the 70+ copies of `roles[0]: tinyauth@file` into one `public-policies` block, plus the new `public-resources.maintenance` block for graceful 502s on 5 public Traefik routes. EE features we currently leave on the table.
- **Value:** Single-point policy edits, zero-downtime maintenance, sub-domain wildcard routing.
- **Effort:** M
- **Dependencies:** Agent 16, `infrastructure-stacks` spec, Pangolin EE license activation.

### F-18 · FalkorDB recommendation engine (in-graph vector + Cypher)
- **Description:** Agent 10 — fix the missing `vector.so` loadable, expose `db.idx.vector.queryNodes` for the Cognee adapter. Build a recommendation engine over the 3 cross-archive edges (cites / builds-on / contradicts) using FalkorDB's 11 built-in algorithms (PageRank + Betweenness for "most influential paper in the leabharlann").
- **Value:** "Papers every Leaving Cert Irish teacher should read" becomes a graph query, not a SQL one.
- **Effort:** M
- **Dependencies:** Agent 10 R1 + R4 (Cypher-injection fix), `oideachais-cognify-knowledge-graph` spec.

### F-19 · Irish-language ASR leaderboard (RAGAS-driven)
- **Description:** Eval suite for the 11 OCR + new ASR models on the 6 Celtic languages. Each model gets a per-language WER/CER, served as a public Marimo notebook + a MotherDuck Dive (F-12).
- **Value:** First open Irish ASR leaderboard. Useful for academic cred + external adoption.
- **Effort:** S (uses existing RAGAS + Marimo + MotherDuck)
- **Dependencies:** F-11, `meaisinfhoghlaim-ocr-htr` spec, `oideachais-marimo-dashboards` spec.

### F-20 · MTP speculative decoding (1.4-2.2× inference speedup)
- **Description:** Agent 19 finding #4 — enable MTP on Qwen3 27B/35B-A3B. Upstream llama.cpp PR #22673 (2026-06-21). One line in `llama-swap-config.yaml:120`.
- **Value:** Free 1.4-2.2× inference for any Qwen3 model with zero accuracy loss.
- **Effort:** S
- **Dependencies:** Agent 19, llama-swap stack.

---

## 6. P3 — Backlog (speculative)

### F-21 · Zotero-API-fed leabharlann ingestion
- **Description:** Agent 25 R15/R19 — replace filesystem-derives-arxiv_id hack with `pyzotero` + `Last-Modified-Version` incremental cursor. 4-concurrent limit + Backoff/Retry-After/429 semantics baked in.
- **Value:** Real citation graph instead of filename guesses. Cross-link to arXiv OAI-PMH (Agent 25 R20/R21).
- **Effort:** M

### F-22 · gov.wales WAF CAPTCHA solver (or Welsh via `llyw.cymru`)
- **Description:** Agent 24 finding #7 — gov.wales now has CloudFront + AWS WAF CAPTCHA. Either Browserbase persistent context with residential proxy + a CAPTCHA-solving service, OR pivot to `llyw.cymru` (Welsh mirror) + `hwb.gov.wales` (Thinqi LMS).
- **Value:** Wales curriculum corpus; AoLEs 1-6 cross-linked.
- **Effort:** L (CAPTCHA) or S (`llyw.cymru` mirror)
- **Dependencies:** Browserbase credits (Phase 0.8 calibration), `ireland-primary-jc-dlt-baml` spec.

### F-23 · arXiv OAI-PMH bulk sync (200K+ papers)
- **Description:** Agent 25 R20/R21 — use `https://oaipmh.arxiv.org/oai?verb=ListRecords&from=<last>` with `cs:cs:AI` set. The mandatory "Thank you to arXiv" acknowledgement in F-23.
- **Value:** Per-author + per-paper enrichment for the leabharlann cognition graph.
- **Effort:** S
- **Dependencies:** dlt `@dlt.incremental`, Cognee consumer.

### F-24 · MLA citation auto-generator (BAML `CiteMLA`)
- **Description:** New BAML function: input = leabharlann ZoteroItem, output = MLA 9 + APA 7 + Chicago + Harvard citations. Replaces the 4 hand-maintained citation styles in `celtic-data-engineering-pipeline`.
- **Value:** One citation generator across all 4 styles, language-aware (Irish: `agus` → `and` for English MLA).
- **Effort:** S
- **Dependencies:** `oideachais-baml-schemas` spec, F-21.

### F-25 · Self-improving BAML loop (RAGAS → re-train few-shot examples)
- **Description:** RAGAS eval failures on BAML extraction → store as `ex_few_shot` in the `.baml` file's `default_role` → re-run extraction → loop. BAML `Collector(name)` + Langfuse v3 (F-03) make this a 200-line script.
- **Value:** BAML accuracy improves *automatically* on every eval cycle. Compounds with F-03.
- **Effort:** M
- **Dependencies:** F-03, F-15 webhooks, `oideachais-baml-schemas` spec.

### F-26 · MLX-omni Anthropic `/v1/messages` surface
- **Description:** Agent 20 finding #3 — Anthropic surface is uncommitted. Wire it via LiteLLM `anthropic/` route. Replaces the `clients_0.baml` legacy Gemini clients entirely.
- **Value:** Unified Anthropic API across local (MLX) and cloud (Anthropic SDK).
- **Effort:** S
- **Dependencies:** Agent 20, Agent 15 (delete `clients_0.baml`).

---

## 7. Cross-cutting dependencies

Most features depend on the **same 5 platform primitives** (Dagster 1.13.x, BAML 0.223+, Cognee v1, Langfuse v3 OTEL, LiteLLM gateway with verified minimax routing). Blocking on these:

1. **LiteLLM v1.83.0+ clean baseline** (Agent 06 finding #3) — gates F-03, F-05, F-26.
2. **Cognee v1.0 remember/recall migration** (F-06) — gates F-07, F-25.
3. **Langfuse v3 OTEL path** (F-03) — gates F-15, F-25.
4. **bge-m3 standardisation** (F-02) — gates F-10.
5. **Garage v2.3 migration** (F-16) — gates multi-region F-04 (Modal artifacts in regional S3) and F-12 (MotherDuck BYOB).

**Feature clusters (recommended batch delivery):**
- **Cluster A (Realtime + Memory):** F-01 + F-06 + F-07 — single "real-time + persistent agents" theme.
- **Cluster B (Multilingual + Multimodal):** F-02 + F-10 + F-11 + F-19 — "Celtic language platform" theme.
- **Cluster C (Observability + Auto-improve):** F-03 + F-15 + F-25 — "agent that improves itself" theme.
- **Cluster D (Edge + GPU):** F-04 + F-05 + F-26 — "inference substrate" theme.
- **Cluster E (Content + Sites):** F-13 + F-14 + F-21 + F-22 + F-23 + F-24 — "Celtic + Crown Dependencies corpus" theme.

**Total: 26 features** (F-01 → F-26). P0 = 7, P1 = 8, P2 = 5, P3 = 6.

---

## 1-paragraph summary

The Cianfhoghlaim feature backlog comprises **26 NEW features** across 4 priority tiers, derived from cross-package integration gaps (RisingWave↔olake↔Iceberg CDC; Cognee↔Graphiti dual-memory; CocoIndex↔LanceDB vector index gap), user pain points surfaced by the site research (TCA-gated curriculumonline teacher corpus, IoM/Jersey/Guernsey crown dependency legal ingest, gov.wales WAF CAPTCHA, Jersey CKAN zero-ingest), and tech-debt reframed as features (Garage v2.3 multi-region S3, Pangolin EE public-policies, FalkorDB vector.so recommendation engine). The 7 P0 features unblock the next quarter's strategic themes (realtime + memory, multilingual + multimodal, observability + auto-improve, edge + GPU) and share 5 common platform primitives (LiteLLM v1.83+, Cognee v1, Langfuse v3 OTEL, bge-m3, Garage v2.3) that should be sequenced as a single coordinated foundation. P1 (8 features) extends the corpus, observability, and crown-dependency themes; P2 (5 features) and P3 (6 features) cover the long tail. Recommended delivery: ship Cluster A (F-01/F-06/F-07) + Cluster B (F-02) first, then fan out to Clusters C-E in parallel.
