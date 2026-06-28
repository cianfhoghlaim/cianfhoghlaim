# Agent 28 — Misunderstandings-Corrector (BrowserBase Program 2)

**Date:** 2026-06-29
**Inputs:** 25 wave-1 agent outputs (`agent-01..25.md` + `SHARED_DISCOVERY_LOG.md`), 4 phase stub changes, 3 celtic-asset-generation spec versions, 33 P-spec + 12 S-spec first-pass files, `openspec/project.md`, `openspec/AGENTS.md`.
**Credit spend:** 0 (read-only synthesis from local files).

---

## 1. TL;DR — Top 3 corrections

1. **P1A-04 doc references a non-existent file.** `openspec/research/.../phase-1a/P1A-04-duckdb-ducklake.md:43` cites `cianfhoghlaim/core/ducklake/client.py` — the only thing in `core/ducklake/` is a 20-line re-export shim. The canonical 882-line `DuckLakeClient` is at `stedding/stedding/flows/education/storage/ducklake_client.py:225-258`. Open as a refactor (move + delete legacy `DuckLakeCatalog` 352-line dead code at `stedding/.../storage/ducklake.py`). **High runtime impact** — most P1A-04 code snippets don't match disk.
2. **P2-20 (OpenChamber) is a fictional stack.** The first-pass file claims `image: openchamber/openchamber:latest`, `ports: ["3030:8080"]`, an `openchamber-postgres` service, `LITELLM_BASE_URL=http://litellm:4000/v1`, a TanStack Start embed at `oideachais-web/src/routes/agents.tsx`, and a Langfuse env — **none exist** in `infrastructure/stacks/openchamber/compose.yaml`. Real stack: `ghcr.io/openchamber/openchamber:1.0.0@sha256:0…0` on `127.0.0.1:3000:3000`, no Postgres, no LiteLLM, bundled-mode + direct provider keys. **High runtime impact** — first-pass doc would mislead the build agent.
3. **P1B-06 LanceDB HNSW index call sites will fail at runtime.** First-pass files repeatedly use `index: { type: hnsw, m: 16, ef_construction: 200 }` (standalone) — but per Agent 04 (LanceDB OSS 0.33.0), valid HNSW names are `IVF_HNSW_FLAT`, `IVF_HNSW_SQ`, `IVF_HNSW_PQ` only. CocoIndex 1.0.7 `declare_vector_index` accepts `index_type="hnsw_pq"`. KCG 5 infra Apps don't declare `index_type` at all → they get `ivf_pq` (different index family). **High runtime impact** — `stacks/lakehouse/lance-namespace/config.yaml` and `core/cocoindex/mount_lance.py` will need a `IVF_HNSW_*` migration.

---

## 2. By-stub-change (corrections to the 4 phase stubs)

### 2.1 `2026-06-28-browserbase-phase-1a-decisions/specs/oideachais-pipeline/spec.md`

- **C-1.1** "Dagster `MultiPartitionsDefinition(subject, material_type)` for examinations asset (96 partitions = 24 subjects × 4 material types)" — **Wrong on count.** Per Agent 02 (`agent-02-dagster.md:32-33`), the canonical implementation at `partitions.py:218-228` is **26 subjects × 10 years × 3 levels = 780 partitions** for SEC; the 96 figure is the *simplified* post-`partitions_v2.py` cycle count. The spec delta hard-codes 24 subjects × 4 types = 96 which only matches the legacy `partitions.py` cycle view. **Severity: med** — runtime partition cardinality differs.
- **C-1.2** "All lakehouse tabular data as Iceberg tables on Garage S3" — **Drift per Agent 05 + Agent 08.** DuckLake (`motherduck_options.py:41-149`, `dlt_utils/destinations.py`) is the canonical catalog; Iceberg is a *table format* on Garage. The first-pass spec talks about "Iceberg catalog" but live code ATTACHes via `ducklake:postgres://...` and writes to `s3://lakehouse-bucket/ducklake/`, not `s3://lakehouse-bucket/iceberg/`. **Severity: med** — affects which S3 subdir `dlt destinations factory` resolves to.
- **C-1.3** "Polars DataFrame via `pl.from_arrow(...)`" — **Drift per Agent 02.** KCG codebase still uses `pandas`; `dlt 1.27+` added native Polars support but `pyproject.toml:39` is plain `dlt>=1.0.0` (locks to 1.25.0), so Polars native codepath is dormant. **Severity: low** — aspirational claim.

### 2.2 `2026-06-28-browserbase-phase-1a-decisions/specs/celtic-asset-generation/spec.md`

- **C-1.4** The delta says "5-stage PDF flow (secret injection → DLT SHA-256 scan → BAML extraction → CocoIndex v1 embedding → Cognee cognify)" — **The 5-stage flow in the live celtic-asset-generation spec is different.** It lists (1) BAML extraction, (2) CocoIndex v1 embedding with `BGE-large-en-v1.5` in 100+ batches, (3) Cognee cognify with 8 canonical relationship types, (4) Graphiti temporal memory, (5) LanceDB IVF_HNSW + FTS. The stub phase-1a delta compresses this to a different 5-stage sequence and changes the embed model. Per Agent 03 (`agent-03-cocoindex.md:296`), the live code uses **mixed models** (`BGE-large-en-v1.5` default + `BGE-m3` override), so neither number is right. **Severity: high** — these two specs now contradict each other in the same `changes/` tree.
- **C-1.5** "CocoIndex v1 App" — should also note that **5 of 14 v1 Apps don't declare `declare_vector_index`** (per Agent 03). The stub doesn't reference the v1 conformance contract. **Severity: med.**

### 2.3 `2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md`

- **C-1B.1** "Garage S3 (S3-compatible, 3-node cluster)" — **Wrong on version.** Per Agent 12 (`agent-12-garage.md:469`), Cianfhoghlaim is pinned at `dxflrs/garage:v1.0.1` (Dec 2024) but upstream latest is `v2.3.0` (Apr 2026). v2.0.0 (Jun 2025) **removed** `replication_mode` (we still use `replication_mode = "1"` in `garage.toml:5,18` — will fail to start) and reworked admin API `/v1/*` → `/v2/*` (our 90-line `garage-init` in `lakehouse/compose.yaml:71-160` hard-codes `/v1/` endpoints). The spec says "3-node HA" but does not say "currently broken in 2 ways." **Severity: high** — runtime deploy will fail.
- **C-1B.2** "FalkorDB driver connected at `falkordb:6379` with `vector.so` loadable loaded" — **Wrong on the loadable.** Per Agent 10 (`agent-10-falkordb.md:385`), `infrastructure/stacks/falkordb/compose.yaml:18-37` has **no `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]`** — the spec mandates the loadable but it's not in the deployed stack. **Severity: high** — every `db.idx.vector.queryNodes` call silently breaks.
- **C-1B.3** "Cognee … 6 typed datasets (aistear, primary, junior_cycle, senior_cycle, tertiary, cross_stage) with Postgres unified provider (Neo4j fallback for prod)" — **3 separate drifts per Agent 09:**
  - Default graph backend in Cognee v1.2+ is **Kuzu**, not Postgres-unified. Our `compose.yaml:42-59` uses `USE_UNIFIED_PROVIDER=pghybrid` which is an experimental flag not in current docs.
  - **Dataset naming drift (silent failure):** compose.yaml uses dot notation (`oideachais.aistear,oideachais.primary,...`) but `cross_stage_cognify.py:131` uses underscore (`oideachais_cross_stage`). The cross-stage asset will silently miss its dataset on first cognify run.
  - **`SearchType.INSIGHTS` doesn't exist** (referenced at `cognee_service.py:376`) — will throw `AttributeError` at runtime.
  - **Severity: high** — multiple runtime breakers.
- **C-1B.4** "LanceDB v2 (.lance format) with Lance Namespace REST Catalog (port 8182) bridging LanceDB to the lakehouse (Iceberg + Garage S3)" — **Drift on the REST namespace form.** Per Agent 04, the v0.33-canonical client is `connect_namespace("rest", {...})`, not `lancedb.connect("http://lakehouse-lance:8182")`. The P1B-06 sample uses the directory-namespace URI form which doesn't speak the REST API. **Severity: med.**

### 2.4 `2026-06-28-browserbase-phase-1b-decisions/specs/meaisinfhoghlaim-platform/spec.md`

- **C-1B.5** Stub (18 lines) cross-references "Cognee + Letta patterns" but the actual first-pass P1B-09 + Agent 09 + Agent 11 findings surface 8 separate Cognee/Graphiti drifts. The stub is too thin to capture any of them. **Severity: low** (it's a stub), but the gap is the real problem.

### 2.5 `2026-06-28-browserbase-phase-2-decisions/specs/infrastructure-stacks/spec.md`

- **C-2.1** Stub claims "6-file GOLD_STANDARD alignment" but Agent 16 + Agent 22 surface that the R3 (`public-policies`) refactor would cut 70+ files simultaneously (R1+R2+R3 cluster). The stub doesn't enumerate the EE-vs-OSS gap (we use EE for PostgreSQL catalog but not yet for `public-resources.maintenance`, `public-policies` reusable blocks, `wildcard-resources`, wildcard TLS, or `sites:` for multi-site failover). **Severity: low** (stub).

### 2.6 `2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md`

- **C-2.2** "Unsloth (local M4 Max, MLX + GGUF, QLoRA 4-bit) as the primary fine-tuning framework" — **Drift per Agent 19** — the canonical upstream 3.0+ loader is `FastModel` (not `FastVisionModel`), and `FastModel.get_peft_model` auto-dispatches text/vision/audio. KCG `unsloth_trainer.py:108` still uses the old API. Also the Gemma 4 + Qwen3.6 model IDs the spec inherits from `meaisinfhoghlaim-ocr-htr` are **aspirational** — per Agent 21 (`agent-21-huggingface.md:502`), **8 of P2-23's 11 vision models don't exist on HF Hub today**. **Severity: high** — `hf_hub_download()` will fail at first training.
- **C-2.3** "LiteLLM … `minimax` alias as the default model (7-tier fallback chain)" — **Drift per Agent 06** — (a) `main-stable` Docker tag is deprecated (cutover 2026-06-30, 2 days from research date); (b) LiteLLM v1.83.0+ is the clean baseline post-March 2026 supply-chain incident; (c) LiteLLM now ships a native `minimax` provider (third-party Chinese AI MiniMax Inc., not the same name as the KCG `minimax` alias) — collision risk for `minimax/MiniMax-M2.1` routes. **Severity: med.**
- **C-2.4** "PlanetScale Postgres is the canonical managed DB" — **Wrong per Agent 08 + Agent 17.** PlanetScale is referenced in legacy `ducklake_client.py:160-165` as Postgres creds (the `PLANETSCALE_*` env vars are stale aliases). The canonical managed DB is **`lakehouse-postgres`** Compose stack (per `crypteolas/.../ducklake_resource.py:28-46`). Agent 08 calls for renaming to `DUCKLAKE_PG_*` for consistency. **Severity: med.**
- **C-2.5** "OpenChamber is the canonical agent IDE … embedded in TanStack Start at `oideachais-web/agents`" — **Completely fictional per Agent 22.** Real stack uses no TanStack Start embed, no LiteLLM, no Postgres, no Langfuse env. **Severity: high** — see C-3.2 below.

### 2.7 `2026-06-28-browserbase-phase-3-decisions/specs/oideachais-pipeline/spec.md`

- **C-3.1** "gov.uk standard rate limiting ~10 req/sec per IP" — **Wrong per Agent 24** — gov.uk robots.txt has no `Crawl-delay:` for default UA. Recommended `User-Agent: Googlebot/2.1` to skip LUX speedcurve. Also: **`/sitemap.xml` is 1-day-old, lastmod `2026-06-28 02:56:49 GMT`** — sitemap.xml-seeded `dlt.sources.sitemap(...)` is correct but the spec should add `If-Modified-Since` revalidation. **Severity: med.**
- **C-3.2** "BAML ExtractEn + ExtractEnStrong is the canonical extraction stack" — **Drift per Agent 15:** `_oideachais_src/curriculum_extraction.baml:164-1086` has **8 inline `client "anthropic/claude-sonnet-4-20250514"` calls that bypass the LiteLLM gateway** — no fallback chain, no Langfuse trace. Defeats the Phase 0.4 vendor-de-risking goal. **Severity: high** — runtime bypass.
- **C-3.3** "Zotero Web API v3 (OAuth 1.0a) … with rate limiting at 10 req/sec (free tier)" — **Wrong per Agent 25:** Zotero enforces **4-concurrent-requests max** + `Backoff` / `429 + Retry-After` headers + `Last-Modified-Version` for conditional GETs. `leabharlann/zotero.py:94-124` reads **filesystem PDFs only** — zero Zotero API calls. **Severity: high** — the canonical Zotero source is not actually wired.
- **C-3.4** "arXiv API + OAI-PMH … with rate limiting at 1 req/sec (per arxiv TOS)" — **Wrong per Agent 25:** arXiv requires **3-second polite delay**, max 30,000 results in 2,000-result slices. OAI-PMH at `https://oaipmh.arxiv.org/oai` supports bulk sync via `ListRecords&from=<last>`. The codebase never enriches GeminiReport→ZoteroPaper with arxiv abstracts/DOIs. **Severity: med.**
- **C-3.5** "Bilingual processing for Irish + Welsh sites … `/en/` and `/ga/`" — **Wrong per Agent 23:** curriculumonline.ie's `/en/` returns 404; live pattern is `/primary/curriculum-areas/{subject}/` (no `/en/`). Bilingual is **`/ga-ie/` PATH PREFIX**, not subdir. **`/sitemap.xml` does NOT exist** — must use Firecrawl `map` seeded by stage+subject index. **Severity: high** — dlt sources would 404 on first run.

---

## 3. By-spec (corrections to celtic-asset-generation, 3 archive versions)

The 3 versions are: live (`openspec/specs/celtic-asset-generation/spec.md`, 122 lines) · round-8 archive (`changes/archive/2026-06-23-sync-skills-from-docs-round-8/specs/celtic-asset-generation/spec.md`, 96 lines) · consolidate-v4 archive (`changes/archive/2026-06-28-2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/specs/celtic-asset-generation/spec.md`, 31 lines).

- **C-SP.1 (live, R-1)** "BGE-large-en-v1.5 in 100+ batches" — Per Agent 03, the canonical embed model in v4 is **mixed**: `bge-large-en-v1.5` is `_lifespan.py:92` default, `bge-m3` is `codebase_indexing.py:93` override. Two embedding spaces coexist; cosine between them is meaningless. Spec hard-codes `bge-large-en-v1.5` only. **Severity: high** — affects which embed model to fine-tune against.
- **C-SP.2 (live, R-1)** "Cognee cognify with 8 canonical relationship types" — **Number is unverified.** No code file lists exactly 8 relationship types; Agent 11 found 5 edge types in `EntityEdge` (MENTIONS, community, HasEpisodeEdge, NextEpisodeEdge) but those are Graphiti-internal, not Cognee. The celtic-asset-generation "8 canonical relationship types" appears to be aspirational; no Cognee-side enum exists. **Severity: med.**
- **C-SP.3 (live, R-1)** "LanceDB IVF_HNSW + FTS" — **Wrong per Agent 04:** IVF_HNSW is not a standalone valid name; the only valid HNSW sub-indexes in LanceDB 0.33.0 are `IVF_HNSW_FLAT`, `IVF_HNSW_SQ`, `IVF_HNSW_PQ`. Plus 5 of 14 CocoIndex v1 Apps never call `declare_vector_index` (per Agent 03) — they're brute-force today. **Severity: high.**
- **C-SP.4 (live, R-1)** "`BilingualText` class … dialect handling: Connacht / Munster / Ulster" — **Class is not in the BAML source tree.** Per Agent 15, `_oideachais_src/curriculum_extraction.baml:164-1086` has 8 inline `client "anthropic/claude-sonnet-4-20250514"` calls and 264-line `clients.baml`; no `BilingualText` class found. **Severity: med.**
- **C-SP.5 (live, R-1 + v4 R-3)** "Pipeline runs in `sruth/oideachais/dagster_defs/assets/celtic_assets.py`" — **Pre-v4 path.** Per Agent 02, the v4 entry point is `cianfhoghlaim/assets/definitions.py` (root) + `cianfhoghlaim/assets/_oideachais_dagster_defs/definitions.py:496` (sub-tree). The v4 archive spec already moved the path to `cianfhoghlaim/assets/asset_generation/...` for the 4 INDEPENDENT pipelines (R-3) — the live spec still has the v3 path. **Severity: high** — files don't exist.
- **C-SP.6 (live, R-2)** "VLM backbone (Bolmo / Molmo2 / Qwen3-VL)" — **Qwen3-VL is not in the registry.** Per `meaisinfhoghlaim-ocr-htr` spec in `openspec/project.md:58`, the 11 OCR vision models are Gemma 4 + Qwen3.6 + GLM-4.6V. Agent 21 confirms 8 of these are aspirational HF IDs that don't exist today. **Severity: med.**
- **C-SP.7 (round-8 archive, R-1)** Same path drift as C-SP.5. **Severity: high.**
- **C-SP.8 (consolidate-v4 archive, R-3)** "4 successive INDEPENDENT pipelines at `cianfhoghlaim/assets/asset_generation/`" — **Path is correct for v4 but the 4 sub-pipelines (`official_documents/`, `subject_assets/`, `language_assets/`, `exporters/`) are not yet implemented.** Per Agent 03 + the Asset Generation Source Schema Provisional requirement, the layout is provisional. No code lives there yet (no `official_documents/syllabus.py` etc.). **Severity: low** (intentional provisional).

---

## 4. By-P-spec (corrections to first-pass research files)

Grouped by phase. Each row: P-spec ID · claim · correction · source · severity.

### Phase 1A (P1A-01..05)

- **P1A-01** "dlt sources live at `cianfhoghlaim/dlt_sources/` (28 sources)" — Actually `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` (190 `.py` files, 12 subdirs). [Agent 01, finding #1] **High.**
- **P1A-01** "`dlt>=1.7.0,<2.0.0`" — Actual pin is `dlt>=1.0.0` (lock resolves to 1.25.0). Should be `"dlt[hub]>=1.27.0,<2.0.0"` after 1.27 `workspace` split. [Agent 01, finding #2] **High.**
- **P1A-01** "DLT destination `dlt.destinations.postgres` + `dlt.destinations.filesystem`" — Actually `dlt.destinations.ducklake(credentials=...)` (per `dlt_utils/destinations.py`). [Agent 01] **Med.**
- **P1A-02** "Single code-location at `oideachais/dagster_defs/definitions.py`" — v4 moved to `cianfhoghlaim/assets/definitions.py` (root) + `cianfhoghlaim/assets/_oideachais_dagster_defs/definitions.py:496` (sub-tree). [Agent 02, finding #5] **High.**
- **P1A-02** "`MultiPartitionsDefinition` (subject × material_type) — 24 subjects × 4 types = 96 partitions" — Actual: 26 subjects × 10 years × 3 levels = **780** for SEC; 96 is simplified `partitions_v2.py` figure. [Agent 02, finding #7] **Med.**
- **P1A-02** "6 `@asset_check` decorators in `checks/cognee_models.py`" — Those checks were **deleted** during v4 cleanup. Current: 9 + 12 (`WIRE_UNWIRED_DLT_CHECKS`) + 1 (LLM gateway) = 22 checks. [Agent 02, finding #5 conflict note] **Med.**
- **P1A-02** "`dagster-dlt>=0.25.0,<1.0.0`" — Latest is 0.29.11 (4 minor behind). Should be `>=0.29.11,<1.0.0`. [Agent 02, finding #1] **High.**
- **P1A-03** "`EMBEDDING_MODEL=BAAI/bge-m3` (1024-dim)" — Actual: mixed — `_lifespan.py:92` defaults `bge-large-en-v1.5`, `codebase_indexing.py:93` overrides with `bge-m3`. Cross-App semantic search is silently broken. [Agent 03, finding #2; Agent 04 cross-conflict] **High.**
- **P1A-03** "`EMBEDDING_PROVIDER=litellm`" — Actual: `SentenceTransformerEmbedder` (local, not LiteLLM). [Agent 03 conflict note] **Med.**
- **P1A-03** "`LANCEDB_URI=lance://lakehouse-lance:8182/codebase`" — Actual: `rest://lance-api.cianfhoghlaim.ie`. [Agent 03 conflict note] **Med.**
- **P1A-03** "CocoIndex version pin `>=1.0.0,<2.0.0`" — **v1.0.8 was YANKED** (2026-06-11). Should be `>=1.0,<2.0,!=1.0.8`. [Agent 03, finding #3] **Med.**
- **P1A-03** "14 v1 Apps" — Actually 14, but **5 of them missing `declare_vector_index`** (codebase_indexing, api_indexing, filesystem_indexing, storage_indexing, config_indexing). [Agent 03, finding #1] **High.**
- **P1A-04** "DuckLake client at `cianfhoghlaim/core/ducklake/client.py`" — **Non-existent.** Canonical 882-line `DuckLakeClient` at `stedding/stedding/flows/education/storage/ducklake_client.py`. `core/ducklake/` only has a 20-line re-export shim. [Agent 08, finding #1] **High.**
- **P1A-04** "`ducklake>=0.3,<1.0`" — Should be `>=1.0,<2.0` (DuckLake 1.0 `v1.5-variegata`, April 2026). [Agent 08, finding #3] **High.**
- **P1A-04** "`ATTACH 'ducklake:postgres://lakehouse-postgres:5432/lakehouse_catalog'`" — **URI form is one of two.** Production-safe is `CREATE SECRET` + `ATTACH 'ducklake:secret_xxx'`. Plus SQL-injection risk via f-string `ducklake_client.py:454`. [Agent 08, findings #2 + #5] **High.**
- **P1A-05** "MotherDuck 0.5" — Wrong; current docs require DuckDB **1.5.4** (1.4.0+ in us-east-1). [Agent 05, finding #2] **High.**
- **P1A-05** "`MCP_MOTHERDUCK_COMMAND=uvx mcp-server-motherduck --db-path :memory: --read-write --allow-switch-databases`" — `--read-write --allow-switch-databases` is **explicitly anti-pattern #2** in current audit. Production should be `--read-only --saas-mode`. [Agent 05, finding #2 + finding #7] **High.**
- **P1A-05** "MotherDuck token `infisical://dev-baile/motherduck/token`" — Per Agent 05, the Business-tier token lives at this URI but **`USE_LOCAL_SCRAPES` defaults make the live MotherDuck path dormant in dev/CI.** [Agent 09, finding #7] **Low.**

### Phase 1B (P1B-06..10)

- **P1B-06** "LanceDB 0.10+ with v2 `.lance` format" — Current stable is **0.33.0** (May 2026); pre-release **0.34.0-beta.3** ships breaking change. Pin should be `lancedb>=0.33,<0.34`. [Agent 04, finding #2] **High.**
- **P1B-06** "LanceDB index `type: hnsw, m: 16, ef_construction: 200`" — **Invalid.** Only `IVF_HNSW_FLAT`, `IVF_HNSW_SQ`, `IVF_HNSW_PQ` are valid. [Agent 04, finding #1] **High.**
- **P1B-06** "`db = lancedb.connect('http://lakehouse-lance:8182')`" — Should be `connect_namespace("rest", {...})` with `headers.x-api-key` (Locket-resolved). [Agent 04, finding #4] **High.**
- **P1B-06** "Lance Blob — large object support" — The schema marker is `pa.large_binary()` + `metadata={"lance-encoding:blob": "true"}`, not just "Lance Blob." [Agent 04, finding #5] **Med.**
- **P1B-07** "FalkorDB `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]`" — **Missing in the deployed compose.** [Agent 10, finding #3] **High.**
- **P1B-07** "Graphiti `FalkorDriver(host="falkordb", port=6379)` import" — **Stale.** graphiti-core 0.5+ uses `Graphiti(uri="falkordb://...")` with auto-fallback to `falkordb_lite`. [Agent 10, finding #4] **High.**
- **P1B-07** "`await graphiti.add_episode(name, episode_body, source_description, reference_time, source)`" — **`add_episode` is 16 params, not 5.** KCG legacy shim at `crypteolas/.../knowledge_graph_service.py:53-80` silently fails on every call. [Agent 11, finding #1 + #3] **High.**
- **P1B-07** "3 cross-archive edge types (cites, builds-on, contradicts)" — **Wrong on shape.** These map onto `EntityEdge` labels; there are 5 edge types total in Graphiti (`EntityEdge`, `EpisodicEdge`, `CommunityEdge`, `HasEpisodeEdge`, `NextEpisodeEdge`). [Agent 11, finding #4] **Med.**
- **P1B-07** "RisingWave v3 (4-node production pattern)" — KCG runs **all-in-one**, not the documented 4-node pattern. Per `compose.yaml:17`. [Agent 14, finding #1] **Med.**
- **P1B-08** "Garage `replication_mode = "1"` + `/v1/*` admin endpoints" — Both **invalid in v2.0+** (Jun 2025 breaking change). 90-line `garage-init` bash sidecar will 404. [Agent 12, finding #2] **High.**
- **P1B-08** "Lakekeeper `LAKEKEEPER__AUTH_DISABLE=true`" — Per Agent 07, dev-only override; production must use Pangolin SSO via `pangolin.yaml`. Spec doesn't say. [Agent 07] **Med.**
- **P1B-09** "Cognee client at `oideachais/agents/meaisinfhoghlaim/memory/cognee_client.py`" — Wrong post-v4 path. Actual: `cianfhoghlaim/core/memory/memory/cognee_service.py`. [Agent 09, finding #6] **High.**
- **P1B-09** "Postgres unified provider (Neo4j fallback for prod)" — Cognee v1.2+ default is **Kuzu**, not Postgres-unified. `USE_UNIFIED_PROVIDER=pghybrid` is experimental. [Agent 09, finding #2] **High.**
- **P1B-09** "6 datasets (aistear, primary, junior_cycle, senior_cycle, tertiary, cross_stage)" — **Dataset naming drift:** compose uses dots, code uses underscores → silent miss on cross-stage cognify. [Agent 09, finding #3] **High.**
- **P1B-09** "`SearchType.GRAPH_COMPLETION` canonical" — **`SearchType.INSIGHTS` is referenced but doesn't exist** (will AttributeError). [Agent 09, finding #4] **High.**
- **P1B-09** "Letta is planned Tier 2" — Not present in any compose or first-pass; aspirational. **Low.**
- **P1B-10** "Cloudflare R2 + Workers + D1" — R2 path is correct; `wrangler.toml` `database_id = "infisical://dev-baile/cloudflare/d1_database_id"` is **wrong type** — D1 IDs are 32-char hex strings, not URIs. [Agent 22 cross-dep] **Med.**
- **P1B-10** "BetterAuth (with D1 session table)" — Per AGENTS.md, the auth layer is **BetterAuth (customer-facing) → Pocket ID (admin) → TinyAuth (proxy) → Infisical (secrets)** — BetterAuth is not directly on D1. [AGENTS.md] **Med.**

### Phase 2 (P2-11..33 — only the most egregious)

- **P2-11** "Pangolin `protocol: http` in 9 v4 stacks" — Upstream prefers `mode:` over `protocol:` (both accepted, back-compat). [Agent 16, finding #1] **Low.**
- **P2-11** "Pangolin catalog DB: PlanetScale Postgres" — KCG `infrastructure/stacks/pangolin/compose.yaml:17-33` uses `postgres:17` container, not PlanetScale. [Agent 16, finding #3] **Med.**
- **P2-11** "Image `fosrl/pangolin:ee-postgresql-1.19.4`" — Per Agent 16, no specific version was verified; `pangolin` repo is `fosrl/pangolin` on GitHub. **Low.**
- **P2-12** "Komodo: 3 hosts (arm1-oci + bunchloch + cax41-hetzner)" — **Only 2 hosts exist**: `arm1-oci` + `bunchloch`. No `cax41-hetzner` in `servers.toml:14-43`. [Agent 17, finding #1] **High.**
- **P2-12** "4 sub-dirs (servers, stacks, builder, procedures)" — Actually **5 sub-dirs** (servers, stacks, procedures, resource-syncs, sites). No `builder/`, no `variables.toml`. [Agent 17, finding #1] **High.**
- **P2-12** "KCG uses `server_id = "bunchloch"`" — Per Agent 17, KCG TOML uses `server_id = "..."` but upstream v2 docs use `server = "..."`; both work silently. [Agent 17, finding #2] **Low.**
- **P2-12** "`procedures/storage-lakehouse.toml` is a `[[procedure]]`" — Actually a `[[stack]]` definition (lines 26-47). [Agent 17, finding #3] **Med.**
- **P2-13** "Infisical self-hosted on arm1-oci" — Correct, but `INFISICAL_TOKEN` should be Universal Auth, not scoped tokens. [Agent 18] **Low.**
- **P2-14** "`ghcr.io/berriai/litellm:main-stable`" — **DEPRECATED 2026-06-30 (2 days from research date).** Use `:latest` or `:1.84.0+`. [Agent 06, finding #1] **High.**
- **P2-14** "minimax alias 7-tier: opencode-go/minimax-m3-slot{0,1,2} → qwen3.7-max → kimi-k2.6 → glm-4.6 → local/math/qwen25-math" — **Drift per Agent 06** — LiteLLM now ships a native `minimax` provider (third-party Chinese AI MiniMax Inc.) — collision risk for `minimax/MiniMax-M2.1` routes. Also, the fallback uses custom `model_info.fallback_chain` instead of canonical `litellm_settings.fallbacks`. [Agent 06, findings #2 + #5] **Med.**
- **P2-14** "Langfuse v2 callback" — **Langfuse v3 OTEL is the recommended integration path.** [Agent 06, finding #4] **Med.**
- **P2-15** "PlanetScale" — Per Agent 08, PlanetScale was **replaced by `lakehouse-postgres`** Compose stack. Spec is stale. **High.**
- **P2-16** "PostgreSQL" — `PLANETSCALE_*` env vars in `ducklake_client.py:160-165` are stale aliases. Rename to `DUCKLAKE_PG_*`. [Agent 08, finding #7] **Med.**
- **P2-17** "OLake" — General claim, no concrete drift; OK. **None.**
- **P2-18** "MLflow artifact `s3://mlflow-artifacts/`" — Per Agent 18, MLflow artifacts are tracked in `mlflow-artifacts` Garage bucket, OK. **Low.**
- **P2-19** "Langfuse v2 callback" — Same as P2-14: v3 OTEL preferred. **Med.**
- **P2-20 (OpenChamber)** — **Entirely fictional.** See C-3.2 + Agent 22 finding #1. **High.**
- **P2-23 (HuggingFace)** "uses `huggingface-cli download`" — **`hf` CLI is the canonical entry point** since `huggingface_hub` ≥1.20.1; `huggingface-cli` is a deprecated shim. 9 refs across `spaces/build-small-2026-runbook.md:26,92,98,304,315-316` and P2-23:74 still use the old CLI. `[cli]` extra renamed to `[hf]` in v1.0+. [Agent 21, finding #1] **High.**
- **P2-23 (HuggingFace)** "`unsloth/gemma-4-{31B,26B-A4B,E4B,E2B}-it-GGUF`" — **8 of P2-23's 11 vision model IDs don't exist on HF Hub.** Google Gemma 4 not released; Alibaba Qwen 3.6 not released. [Agent 21, finding #2] **High.**
- **P2-24 (MLX-omni)** "package `mlx-omni`, CLI `mlx-omni serve`" — Actually `mlx-omni-server` package, `mlx-omni-server` CLI (no `serve` subcommand; auto-discovers from HF cache; only `--port` accepted). Dockerfile:39 has the **broken invocation** `mlx-omni serve --host 0.0.0.0 --port 10240`. [Agent 20, finding #2] **High.**
- **P2-24** "Repo `qifengle/marketplace-mlx-omni-server`" — Actually `madroidmaq/mlx-omni-server` (730★, 296 commits, v0.5.3). [Agent 20, finding #1] **High.**
- **P2-24** "OpenAI-compatible only" — v0.5.3 added **dual API**: OpenAI + Anthropic (`/anthropic/v1/messages`). KCG wires only OpenAI. [Agent 20, finding #3] **Med.**
- **P2-24** "11 vision + 4 text models" — Aspirational. Currently 3 models wired (`granite-docling`, `olmocr-mlx`, `image-fibo`). [Agent 20, finding #6] **Med.**
- **P2-25 (InvokeAI)** — Per Agent 18, InvokeAI is correctly referenced via `invokeai:9090/api/v1`. **None.**
- **P2-26 (Marimo)** — No major drift; marimo is consumed by 11 notebooks per project.md. **None.**
- **P2-27 (Nimtable)** — Nimtable Iceberg UI on port 8183 is correctly referenced. **Low.**
- **P2-32 (Unsloth)** "`FastVisionModel` loader" — **Superseded by `FastModel` in 3.0+** (auto-dispatches text/vision/audio). [Agent 19, finding #1] **High.**
- **P2-32 (Unsloth)** "`random_state=42`" — Unsloth convention is **`random_state=3407`**. [Agent 19, finding #6] **Med.**
- **P2-32 (Unsloth)** "`save_merged()` defaults to `q4_k_m`" — **`ud-q4_k_xl` (Dynamic 2.0 GGUFs) is SOTA Pareto on KLD**. Free win. [Agent 19, finding #5] **Med.**
- **P2-32 (Unsloth)** "`--spec-type draft-mtp --spec-draft-n-max 2` MTP speculative decoding" — Not enabled in `cianfhoghlaim/core/llama-swap-config.yaml:120`. 1.4-2.2x inference speedup for Qwen3.6 27B/35B-A3B. [Agent 19, finding #4] **Med.**
- **P2-33 (Modal)** — Per Agent 19, `modal_unsloth.py` is the canonical burst pattern. **Low.**

### Phase 3 (S01..S12)

- **S01 (curriculumonline.ie)** "`/en/Primary/{subject}/{strand}/{unit}`" — **404.** Live pattern is `/primary/curriculum-areas/{subject}/` (no `/en/`). PDF pattern is `/getmedia/{guid}/{slug}.{ext}?ext=.png&width=...`, NOT `/getfile/{id}`. [Agent 23, finding #1] **High.**
- **S01** "5 broad areas" — Actually **5 broad areas** (Language, STEM, Wellbeing, Arts Education, Social & Environmental Education), confirmed. Spec drift on count is correct. **OK.**
- **S01** "TCA teacher-only gate" — Stagehand can't solve reCAPTCHA. Need Infisical service-account at `oideachais/sources/curriculumonline_teacher/{email,password}`. [Agent 23, finding #3] **High.**
- **S02 (examinations.ie)** "`/en/educational-resources/`, `/en/exam-archive/leaving-certificate/`" — **All hallucinated, all 404.** Real landing is `/exammaterialarchive/` with T&Cs gate. [Agent 23, finding #4] **High.**
- **S02** "T&Cs click is missing in `examinations.py:306-399`" — `sec_examinations_browser_source` opens archive but does NOT click T&Cs checkbox; subject/year dropdown never renders. [Agent 23, finding #5] **High.**
- **S02** "Subdomain `fees.examinations.ie` must be excluded" — Confirmed anti-scraping posture is weak except for this fees subdomain. [Agent 23, finding #6] **Med.**
- **S03 (ncca.ie)** "`source_adapters.py:262-263` returns `'ncca.ie'` (no scheme)" — Should be `'https://ncca.ie'`. [Agent 23, finding #7] **Low.**
- **S03** "Dublin Core metadata is unused" — `<meta name="DC.Title|Identifier|Date.Created|Rights|Format|Language">` present in every page head but `ncca.py:149-308` dlt sources discard it. Should populate `NormalizedPage.metadata.dublin_core`. [Agent 23, finding #8] **Med.**
- **S04 (gov.uk)** "10 req/sec rate limit" — No `Crawl-delay:` for default UA. [Agent 24, finding #2] **Med.**
- **S05 (education.gov.scot)** "site is up" — **ACTIVE OUTAGE:** `/`, `/sitemap.xml`, `/robots.txt` all return **HTTP 500** via Azure Application Gateway. [Agent 24, finding #4] **High.**
- **S06 (gov.wales)** "Cloudflare" — **Now CloudFront + AWS WAF with CAPTCHA** (`x-amzn-waf-action: captcha`, HTTP 405). [Agent 24, finding #7] **High.**
- **S07 (education-ni.gov.uk)** "sitemap single page" — **3-page paginated** sitemap (`?page=1,2,3`). [Agent 24, finding #9] **Med.**
- **S07** "robots.txt `*.pdf` blocks direct access" — True; AI crawlers must use 5s delay. [Agent 24, finding #9] **Med.**
- **S08 (gov.im)** "use the live HTML portal" — **Robots blocks GPTBot**; PDFs at `https://legislation.gov.im/cms/images/LEGISLATION/{...}.pdf` never fetched. [Agent 25, finding #2] **High.**
- **S09 (gov.je)** "110+ CKAN datasets — we ingest ZERO" — **Highest-ROI refactor (R6).** [Agent 25, finding #1] **High.**
- **S10 (gov.gg)** "session-cookie persistence" — Mandatory session cookies + `CHttpHandler.ashx?id=…` PDF pattern not implemented in `ggy/education/channel_islands.py:23-44`. [Agent 25, finding #3] **High.**
- **S11 (zotero.org)** "filesystem PDFs only" — Should use Zotero API v3 with `@dlt.incremental` on `Last-Modified-Version`. 5 best libs incl. `urschrei/pyzotero`. [Agent 25, finding #4] **High.**
- **S12 (arxiv.org)** "2,000-result slice max, no auth" — Real: 30,000 results in 2,000 slices, 3s polite delay, OAI-PMH at `oaipmh.arxiv.org/oai` for bulk sync. [Agent 25, finding #5] **Med.**

---

## 5. By-cross-cutting (corrections to `openspec/project.md`, `openspec/AGENTS.md`, root `AGENTS.md`)

- **C-CC.1** `project.md:12` says "33 user-pre-selected selfhosted Docker Compose stacks" — Per Agent 17 + Agent 18, the actual fleet is **90 stacks** in `infrastructure/komodo/stacks/*.toml`. **High.**
- **C-CC.2** `project.md:40` claims "33 user-pre-selected" + "57 staying at `infrastructure/stacks/`" — Same number, same direction. **High.**
- **C-CC.3** `project.md:11` mentions "33 user-pre-selected" — this includes the Agent 16 finding that **Pangolin R3 refactor (`public-policies`) would cut 70+ files simultaneously**. Not accounted for in `project.md` counts. **Med.**
- **C-CC.4** `AGENTS.md` (root) Section "Critical Agent Protocols" item 2 — "respect the ingestion cache" via `USE_LOCAL_SCRAPES=true` — Per Agent 09 (Cognee), this default in `cognify/cognee_integration/{cross,leabharlann,official_media}_cognify.py` **disables production cognify runs in CI/local dev**. Easy to miss. **Med.**
- **C-CC.5** `AGENTS.md` "Dagster 1.13+ with `dg` CLI" — Per Agent 02, the v4 layout has BOTH `assets/definitions.py` AND `assets/_oideachais_dagster_defs/definitions.py`; `dg.toml` `module_name = "oideachais.dagster_defs.definitions"` is misleading. **Med.**
- **C-CC.6** `AGENTS.md` "MLE Star Leabharlann 2,395 PDFs" — Per Agent 25, the leabharlann zotero.py reads **filesystem PDFs only** (filename-derives arxiv_id). Zotero API not called. The 2,395 figure is filesystem-derivable but Zotero corpus size is unknown. **Med.**
- **C-CC.7** Root `AGENTS.md` "5 priority skills" include `ccc` and `cognee` — Per Agent 09, the Cognee skill has 7+ clusters but the CLI form `cognee.cognify()` is legacy; canonical is `cognee.remember/recall/improve`. **Low.**

---

## 6. By-component (corrections to docker compose, k8s manifests, etc.)

- **C-CO.1** `infrastructure/stacks/falkordb/compose.yaml:18-37` — **Missing** `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]`. [Agent 10] **High runtime impact.**
- **C-CO.2** `infrastructure/stacks/garage/...` + `infrastructure/stacks/lakehouse/garage.toml:5,18` — `replication_mode = "1"` is removed in v2.0+. [Agent 12] **High.**
- **C-CO.3** `infrastructure/stacks/lakehouse/compose.yaml:71-160` — 90-line `garage-init` hard-codes `/v1/` admin endpoints; should be `/v2/`. [Agent 12] **High.**
- **C-CO.4** `infrastructure/stacks/lakehouse/garage.toml:31,68` — Hardcoded `rpc_secret` and `admin_token` (standalone stack uses envsubst correctly). [Agent 12] **High security.**
- **C-CO.5** `infrastructure/stacks/litellm/compose.yaml` — Image `ghcr.io/berriai/litellm:main-stable` deprecated 2026-06-30. [Agent 06] **High (2 days from research).**
- **C-CO.6** `infrastructure/stacks/cognee/compose.yaml:42-59` — `USE_UNIFIED_PROVIDER=pghybrid` is experimental; Cognee v1.2+ default is Kuzu. [Agent 09] **High.**
- **C-CO.7** `infrastructure/stacks/cognee/compose.yaml:42` — Dot-notation dataset names; `cognify/cognee_integration/cross_stage_cognify.py:131` uses underscores → silent miss. [Agent 09] **High.**
- **C-CO.8** `infrastructure/stacks/cognee/compose.yaml:60` — `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` is dead config; `VECTOR_DB_PROVIDER=pgvector` overrides. [Agent 09, finding #8] **Med.**
- **C-CO.9** `infrastructure/stacks/risingwave/compose.yaml:17` — All-in-one, not 4-node production pattern. [Agent 14] **Med.**
- **C-CO.10** `infrastructure/stacks/pangolin/compose.yaml:17-33` — `postgres:17` container, not PlanetScale. [Agent 16] **Med.**
- **C-CO.11** `infrastructure/komodo/stacks/pangolin-core-arm1.toml` and `pangolin-tunnels.toml` — Could be replaced by `pangolin apply blueprint` CLI call. [Agent 16, finding #7] **Med.**
- **C-CO.12** `infrastructure/stacks/openchamber/compose.yaml` — Real config: `ghcr.io/openchamber/openchamber:1.0.0@sha256:0…0` on `127.0.0.1:3000:3000`, no Postgres, no LiteLLM, no Langfuse. The P2-20 compose in first-pass is fictional. [Agent 22] **High.**
- **C-CO.13** `infrastructure/stacks/mlx-omni/Dockerfile:39` — Broken invocation `mlx-omni serve --host 0.0.0.0 --port 10240`; actual is `mlx-omni-server --port 10240`. [Agent 20] **High.**
- **C-CO.14** `infrastructure/ci/spaces-sync.yml:64` — `[cli]` extra deprecated; should be `[hf]`. [Agent 21] **Med.**
- **C-CO.15** `infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml:30` — `/changelog` is Next.js 404; needs goal-text patch. [Agent 05, finding #4] **Med.**

---

## 7. Critical misunderstandings (those that affect runtime, not just docs)

The following 12 are **runtime-breaking** (would prevent successful deploy or cause silent data loss), ranked by severity:

1. **C-3.5 (P3 / bilingual processing)** curriculumonline.ie `/en/` 404s. First dlt run returns 0 docs. [Agent 23, finding #1] **Critical.**
2. **C-1B.1 (Garage v2 breaking changes)** `replication_mode = "1"` and `/v1/` admin endpoints will fail to start in v2.0+. [Agent 12, finding #2] **Critical.**
3. **C-3.2 (BAML inline `client "anthropic/claude-sonnet-4-20250514"`)** 8 calls in `curriculum_extraction.baml:164-1086` bypass LiteLLM → no fallback chain, no Langfuse trace. [Agent 15, finding #1] **Critical.**
4. **C-1B.2 (FalkorDB vector.so missing)** Every `db.idx.vector.queryNodes` silently breaks. [Agent 10, finding #3] **Critical.**
5. **C-1B.3 (Cognee dataset naming)** Dot-vs-underscore mismatch → cross-stage cognify silently misses its dataset. [Agent 09, finding #3] **Critical.**
6. **C-2.2 (HF aspirational model IDs)** `hf_hub_download()` fails for Gemma 4 + Qwen3.6 + GLM-4.6V. [Agent 21, finding #2] **Critical.**
7. **C-3.3 (Zotero API not wired)** `leabharlann/zotero.py:94-124` reads filesystem PDFs only; Zotero API is the spec. [Agent 25, finding #4] **Critical.**
8. **C-P2.20 (OpenChamber fictional stack)** Real `compose.yaml` diverges from P2-20 in 6 lines; first-pass spec is misleading. [Agent 22, finding #1] **Critical.**
9. **C-1A-1B (Dagster code-location path drift)** v4 moved to `cianfhoghlaim/assets/definitions.py`; first-pass still cites `cianfhoghlaim/dagster_defs/definitions.py`. [Agent 02, finding #5] **High.**
10. **C-P1A-04 (DuckLake client path)** `cianfhoghlaim/core/ducklake/client.py` doesn't exist. [Agent 08, finding #1] **High.**
11. **C-P1B-06 (LanceDB HNSW index invalid name)** Will fail in `table.create_index(...)`. [Agent 04, finding #1] **High.**
12. **C-1A-4 (CocoIndex `bge-m3` vs `bge-large-en-v1.5` drift)** Two embedding spaces coexist; cross-App search is silently broken. [Agent 03, finding #2] **High.**

**Summary:** 6 critical (1-6), 4 high (7-10), 2 high (11-12). The minimum set of changes to make the next 4 phase stub changes deployable is: (a) re-pin LiteLLM to `:1.84.0+`; (b) migrate Garage to v2.x; (c) add `vector.so` to FalkorDB compose; (d) reconcile Cognee dataset naming; (e) replace P2-20 OpenChamber stack; (f) fix the BAML inline client calls; (g) fix the dlt source path; (h) fix the Dagster code-location path; (i) drop aspirational HF model IDs; (j) wire Zotero API v3; (k) fix curriculumonline.ie URL pattern; (l) declare `IVF_HNSW_*` index types.

---

## 8. Return summary (1 paragraph)

The 25 wave-1 agents and the SHARED_DISCOVERY_LOG surfaced **at least 30+ specific misunderstandings** in the first-pass research files, phase stub changes, and 3 celtic-asset-generation spec versions, of which **12 are runtime-breaking** (curriculumonline.ie URL drift, Garage v2 breaking changes, BAML inline `anthropic/claude-sonnet-4-20250514` calls bypassing LiteLLM, FalkorDB `vector.so` loadable missing, Cognee dot-vs-underscore dataset naming, aspirational HuggingFace model IDs, Zotero API not wired, OpenChamber fictional compose, Dagster + dlt + DuckLake v4 path drift, LanceDB `hnsw` invalid index name, CocoIndex embedding-model drift, and LanceDB 0.33 namespace form). The most-cited cross-cutting misalignments are: (a) `project.md` "33 stacks" should be "90 stacks"; (b) `AGENTS.md` V4 path references (e.g., `oideachais/dagster_defs/` vs `cianfhoghlaim/assets/_oideachais_dagster_defs/`); (c) LiteLLM `main-stable` image tag deprecated 2026-06-30 (2 days from research date). The minimum set of changes to make the 4 phase stub changes deployable is enumerated in §7. Severity-tagged corrections are organised by-stub-change (§2, 16 items), by-spec (§3, 8 items), by-P-spec (§4, 30+ items), by-cross-cutting (§5, 7 items), by-component (§6, 15 items), and critical runtime (§7, 12 items).
