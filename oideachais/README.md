# Oideachais — The Celtic Education Lakehouse Engine

> The offline-first ELT engine and lakehouse that powers the entire
> `cianfhoghlaim` stack. Irish, UK, and pan-Celtic education data — syllabi,
> exam papers, marking schemes, Chief Examiner reports, statistical
> publications — through a unified DuckDB/DuckLake core that deploys
> identically to local Garage S3 or to Cloudflare R2 + PlanetScale +
> MotherDuck.

> See also: [`oideachais/AGENTS.md`](AGENTS.md) — the developer-quick-reference
> for the oideachais quadrant. The openspec specs that govern oideachais are
> at:
> - [`openspec/specs/oideachais-pipeline/spec.md`](../openspec/specs/oideachais-pipeline/spec.md)
> - [`openspec/specs/oideachais-leabharlann/spec.md`](../openspec/specs/oideachais-leabharlann/spec.md)
> - [`openspec/specs/oideachais-baml-schemas/spec.md`](../openspec/specs/oideachais-baml-schemas/spec.md)
> - [`openspec/specs/oideachais-cognify-knowledge-graph/spec.md`](../openspec/specs/oideachais-cognify-knowledge-graph/spec.md)
> - [`openspec/specs/oideachais-semantic-search/spec.md`](../openspec/specs/oideachais-semantic-search/spec.md)
> - [`openspec/specs/oideachais-marimo-dashboards/spec.md`](../openspec/specs/oideachais-marimo-dashboards/spec.md)
> - [`openspec/specs/ireland-primary-jc-dlt-baml/spec.md`](../openspec/specs/ireland-primary-jc-dlt-baml/spec.md)

## Status (2026-06-15)

| Metric | Value |
|:--|:--|
| Dagster assets wired | **228 / 228** (211 from `lateralise-british-isles-domains` Phase 0.1 + 7 IE medicine/law Phase 3.1-3.2 + 10 UK medicine/law Phase 3.3) |
| Test pass rate | **81 / 81** non-network tests pass in 3.10s (`oideachais/tests/`) |
| Container status | `cianfhoghlaim-oideachais-{frontend,api,dagster}` healthy on `bunchloch` (47h uptime, per `infrastructure/stacks/HEALTH_REPORT.md` Session 1) |
| DuckLake layout | `s3://ducklake/oideachais/{domain}.{nation}.{entity}/{table}/*.parquet` (per `api/ducklake_reader.py:260-300`) |
| Dagster code-location | `dagster_defs.definitions` (sole entry-point) loads 228 assets from the post-cleanup flat layout |

Full audit artifacts:

- `infrastructure/audit/scripts/inventory-bunchloch.sh` (deferred, will produce `bunchloch-<UTC>.json`)
- `infrastructure/deploy-runbooks/oideachais.md` (deferred content; not yet run)

## Known issues (2026-06-15)

| # | Issue | Tracked in | Severity |
|--:|:--|:--|:--|
| 1 | `pyproject.toml` line 47 comments out `sruth-shared[storage,graph,embeddings,observability]>=0.1.0` (the cross-quadrant `sruth/` workspace member is disabled). Any import of `from sruth.shared.http import ...` raises `ModuleNotFoundError`. | `oideachais/pyproject.toml` line 47; observed breaking `tuatha/dlt_sources/geospatial/gaeltacht_boundaries.py:21` | high — affects 1 known cross-quadrant import chain |
| 2 | The legacy `data_platform.*` namespace is gone (post-cleanup commit `8484a6353`) but a `dagster_assets_model_conversion_skipped` warning is still emitted at module-load. Cosmetic; the test `tests/test_cross_namespace.py` asserts no real import of the banned namespace. | `oideachais/dagster_defs/definitions.py:118-122` (guarded try/except) | low — warning only, no functional impact |
| 3 | SourceFactory's runtime constructors (`source`, `dlt_asset`, `dagster_asset`) raise `NotImplementedError` (Phase 5 wiring deferred). The 23 manual asset wrappers in `oideachais/dagster_defs/assets/{medicine,law}/{ie,en,ni,sct,wls}/*` bypass the SourceFactory and call the DLT sources directly. | GitHub issue #20 | medium — clean abstraction pending |
| 4 | Frontend Vite dev overlay has a workaround `stripTsrIgnoredRouteExports` plugin to strip the upstream TanStack Start plugin's duplicate `import.meta.hot` injection. Remove once `@tanstack/start-plugin-core` ships a fix. | `oideachais/web/apps/web/vite.config.ts` (per `HEALTH_REPORT.md` Session 2) | low — dev-only, prod unaffected |
| 5 | 3 frontend routes return 404 (`/exams`, `/lakehouse`, `/runs`) and 1 returns 500 (`/en/matriculation-auditor`, missing `../utils/orpc` import). Pre-existing dead links. | per `HEALTH_REPORT.md` Session 2 route audit | medium — should be fixed or sidebar links removed |
| 6 | Crown-dependency medicine + law DLT sources (IOM / JEY / GGY) are not yet implemented. The lateralise change wired the 4 IE medicine + 3 IE law + 6 UK medicine + 4 UK law sources, but left crown-deps as stubs. | GitHub issue #19 | medium — follow-up change |

## Quick navigation — "I want to do X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new DLT source (e.g. a new curriculum PDF site) | `data_platform/dlt_sources/ireland/` + the matching `dagster_defs/assets/ireland/` |
| Add a new Dagster asset | `data_platform/dagster_defs/assets/` (per domain: `ireland/`, `uk/`, `celtic/`, `geospatial/`) |
| Run a single asset / pipeline | `mission_control.py` notebook, or `dagster job execute -m data_platform.dagster_defs.definitions -j daily_ingestion_job` |
| Browse exam papers, marking schemes, examiner reports | `notebooks/exam_papers_explorer.py` |
| Inspect the lakehouse (schemas, tables, counts) | `notebooks/ducklake_explorer.py` or `notebooks/lakehouse_inspector.py` |
| End-to-end pipeline smoke test | `notebooks/pipeline_e2e_test.py` |
| Work with raw curriculum PDFs | `data_platform/dlt_sources/ireland/pdf_downloader.py` |
| Add an MCP server | `mcp/` (filesystem, context7, mcpo) |
| Inspect the consumer-facing web app | `oideachais/web/` |
| Operate the operational dashboard | `dashboard/` (separate Vite app) |
| Deploy a new stack | `infrastructure/stacks/` (lakehouse, dagster, liteLLM, etc.) |
| Run LLM calls (BAML extraction) | `oideachais/data_platform/baml_src/` + `baml_client/` |
| Understand the data contracts | Section 2 below |
| Add an agent or evaluate RAG quality | `meaisínfhoghlaim/` (sister subproject) |
| Configure secrets | `.infisical.env` + `bun run secrets:init` |

---

This README documents the engine itself: data contracts, asset topology, DLT
patterns, environment variables, and the conventions agents must follow when
extending it. For the consumer-facing web app see `oideachais/web/`; for the
operations notebooks see `oideachais/notebooks/`; for the storage stack
implementation see `infrastructure/stacks/lakehouse/`.

---

## 1. Architecture Layers

| Layer | Technology | Local Dev | Production |
|-------|-----------|-----------|------------|
| **Orchestration** | Dagster + `dg` | `dagster dev` | Dagster Cloud / Komodo-scheduled |
| **Ingestion (ELT)** | DLT + Firecrawl + Stagehand + Playwright | DuckDB fallback | DuckLake (S3 + PostgreSQL) |
| **SQL Catalog** | Lakekeeper (Iceberg REST) | `localhost:8181` (PostgreSQL 5433) | PlanetScale |
| **Object Storage** | Garage S3 (CRDT) | `localhost:3900-3904` | Cloudflare R2 |
| **Vector Index** | LanceDB + Lance Namespace sidecar | `s3://lance/oideachais/` (Garage) | R2 + Lance Cloud |
| **Query Engine** | DuckDB | local `.duckdb` | MotherDuck (zero-egress) |
| **Browser Automation** | Stagehand (LLM) + Playwright (native) | `localhost:9222-9223` | Browserbase |
| **LLM Gateway** | LiteLLM | `localhost:4000` | OpenCode Go proxy |
| **Frontend** | TanStack Start + CopilotKit | Vite dev | Cloudflare Pages |
| **Auth/SSO** | Pocket ID (OIDC) | Pangolin ingress | Pocket ID |

The data flow is: **DLT sources** (dlt) → **DuckLake destination** (Parquet in
Garage S3, catalog in PostgreSQL) → **Dagster assets** (multi-partition) →
**Marimo notebooks** (operational) → **TanStack web** (consumer) →
**MotherDuck Dives** (embedded dashboards).

---

## 2. Data Contracts

All data lands in the `oideachais` DuckLake database. Tables are written by DLT
pipelines (`dlt_sources/ireland/*`, `dlt_sources/uk/*`, `dlt_sources/celtic/*`)
and consumed by Dagster assets, marimo notebooks, and the web app.

### 2.1 Curriculum Datasets (`curriculum` schema)

| Table | Source | Columns (key) | Rows (target) |
|-------|--------|---------------|---------------|
| `curriculum_pages` | NCCA, curriculumonline.ie, CCEA, SQA, CfW | `cycle, subject, language, source, url, content, scraped_at` | ~5000 |
| `curriculum_pdfs` | same | `cycle, subject, language, pdf_url, content_hash, pdf_type` | ~500 |
| `pdf_downloads` | pdf_downloader | `url, status, size_bytes, content_hash, downloaded_at` | ~500 |
| `pdf_extracted_text` | pdf_processing (ColPali/OCR) | `pdf_url, page_num, text, ocr_engine` | ~50,000 |

### 2.2 Exam Materials Datasets (`examinations` schema)

| Table | Source | Columns (key) | Rows (target) |
|-------|--------|---------------|---------------|
| `exam_papers` | SEC scraper | `level, subject, year, material_type, pdf_url, scraper, status` | ~6000 |
| `marking_schemes` | SEC scraper | same | ~6000 |
| `all_exam_materials` | union | same | ~12,000 |
| `examinations_pages` | SEC crawler (Firecrawl) | `url, content_type, subject, year` | ~200 |
| `examiner_report_pdfs` | SEC mapper | `url, subject, year` | ~500 |

### 2.3 Vector Tables (LanceDB → registered in Lakekeeper)

| Table | Embedding | Purpose |
|-------|-----------|---------|
| `celtic_curriculum_embeddings` | BAAI/bge-m3 (1024-dim) | Cross-cycle curriculum search |
| `codeolas_code_chunks` | BAAI/bge-m3 | Code search (códeolas flow) |
| `unified_embeddings` | BAAI/bge-m3 | Protocol search (crypteolas flow) |
| `pdf_page_embeddings` | ColPali (multi-vector) | Visual PDF retrieval (math formulas, biology diagrams) |

---

## 3. Dagster Asset Topology

Dagster assets live in `oideachais/data_platform/dagster_defs/assets/`. The
combined `defs` is constructed in `definitions.py` and exposed via
`DAGSTER_HOME=. dagster dev -m dagster.definitions`.

### Curriculum (4 cycle assets, MultiPartition: subject × language)

| Asset Key | Cycle | Subjects | Languages | Source |
|-----------|-------|----------|-----------|--------|
| `ireland/curriculum/early_childhood` | Aistear, Síolta | 2 | en, ga | curriculumonline.ie |
| `ireland/curriculum/primary` | Primary | 8 | en, ga | NCCA + curriculumonline.ie |
| `ireland/curriculum/junior_cycle` | Junior Cycle | 18 | en, ga | NCCA |
| `ireland/curriculum/senior_cycle` | Senior Cycle | 33 | en, ga | NCCA |
| `ireland/curriculum/short_courses` | JC Short Courses | 8 | en, ga | curriculumonline.ie |

### Exam Materials (3 cycle assets, MultiPartition: subject × material_type)

| Asset Key | Cycle | Subjects | Material Types |
|-----------|-------|----------|----------------|
| `ireland/exam_materials/leaving_certificate` | LC | 33 | exam_papers, marking_schemes |
| `ireland/exam_materials/junior_cycle` | JC | 17 | exam_papers, marking_schemes |
| `ireland/exam_materials/leaving_certificate_applied` | LCA | 3 | exam_papers, marking_schemes |

**Critical pattern**: years are a `dg.Config` parameter, **NOT** a partition
dimension. This avoids ~1664+ sparsely populated partition keys. See
`dagster_defs/assets/ireland/exam_materials_assets.py:107`.

### PDF & Sylphabus Assets

- `ireland/curriculum/pdf_downloads` — pdf_downloader DLT
- `ireland/curriculum/pdf_extracted_text` — pdf_processing (OCR/ColPali)
- `enriched/*` — cross-domain enrichment
- `search/*` — unified search indexes

---

## 4. DLT Pipeline Patterns

### 4.1 Destination Factory (`dlt_utils/destinations.py`)

```python
from oideachais.data_platform.dlt_utils import (
    get_dlt_destination, get_duckdb_fallback_destination, create_pipeline,
)

# Switches on USE_DUCKLAKE + DLT_ENVIRONMENT env vars
destination = get_dlt_destination()  # DuckLake (Garage S3 + PostgreSQL)
pipeline = create_pipeline("exam_materials", "examinations")
```

`USE_DUCKLAKE=true` + `DLT_ENVIRONMENT=local` → Garage S3 + local PostgreSQL.
`USE_DUCKLAKE=true` + `DLT_ENVIRONMENT=production` → Cloudflare R2 + PlanetScale.
`USE_DUCKLAKE=false` → plain `.dlt/{pipeline}/{dataset}.duckdb` (single-threaded
fallback for quick testing).

### 4.2 Safety Layer (`dlt_utils/safety.py`)

**Always** wrap `pipeline.run()` in `safe_dlt_run()` — it serialises all DuckDB
writes through `SerialDatabaseExecutor` to prevent concurrent-access segfaults:

```python
from oideachais.data_platform.dlt_utils import safe_dlt_run
load_info = safe_dlt_run(pipeline, source)
```

### 4.3 SEC Scraper Cascade (Critical)

The examinations.ie site uses ASP.NET progressive disclosure with this cascade:

1. **Checkbox** (`#MaterialArchive__noTable__cbv__AgreeCheck`) → reveals ViewType
2. **ViewType** (`#MaterialArchive__noTable__sbv__ViewType`) → reveals YearSelect
3. **YearSelect** (`#MaterialArchive__noTable__sbv__YearSelect`) → reveals ExaminationSelect
4. **ExaminationSelect** (`#MaterialArchive__noTable__sbv__ExaminationSelect`) → reveals SubjectSelect
5. **SubjectSelect** (`#MaterialArchive__noTable__sbv__SubjectSelect`) → results after View button

**PDF download links are obfuscated `?fp=` URLs** (e.g.
`examinations.ie?fp=92.109.94.99.100.113...`) — not direct `.pdf` hrefs. The
Playwright-native scraper uses `page.evaluate()` to extract these. See
`infrastructure/browser/sruth_browser/tools/examinations_scraper.py`.

### 4.4 Concurrency Limits (`definitions.py:208`)

```python
CONCURRENCY_LIMITS = {
    "duckdb": 1,      # DuckDB is single-threaded only
    "firecrawl": 3,   # API rate limit
    "lancedb": 2,     # MVCC-safe but limit for performance
}
```

### 4.5 Offline Fallback (`USE_LOCAL_SCRAPES`)

To avoid burning Firecrawl/Stagehand API credits during development, set
`USE_LOCAL_SCRAPES=true`. DLT sources automatically intercept network calls and
load from `stedding/ingest_queue/` (7000+ cached structural documents).

---

## 5. Environment Variables

| Var | Default | Purpose |
|-----|---------|---------|
| `USE_DUCKLAKE` | `true` | Toggle DuckLake vs plain DuckDB |
| `DLT_ENVIRONMENT` | `local` | `local` (Garage) or `production` (R2) |
| `USE_LOCAL_SCRAPES` | `false` | Skip browser, use cached data |
| `DUCKLAKE_POSTGRES_HOST` | `localhost` | Lakekeeper PostgreSQL host |
| `DUCKLAKE_POSTGRES_PORT` | `5433` | Lakekeeper PostgreSQL port |
| `DUCKLAKE_POSTGRES_DB` | `ducklake_oideachais` | Lakekeeper database |
| `AWS_ENDPOINT_URL` | `http://localhost:3900` | Garage S3 endpoint |
| `AWS_REGION` | `garage` | S3 region (path-style URLs) |
| `MOTHERDUCK_TOKEN` | — | MotherDuck cloud token |
| `MOTHERDUCK_ENABLED` | `false` | Toggle MotherDuck query engine |
| `LITELLM_ENDPOINT` | `http://localhost:4000/v1` | LiteLLM proxy |
| `BROWSER_CDP_URL` | `http://127.0.0.1:9223` | Playwright browser grid |

Secrets are managed by Infisical (`dev-baile` vault) and hydrated by `mise`
directory hooks or Locket sidecars. **Never** hand-edit `.env` files.

---

## 6. Skill & Notebook Inventory

### Notebooks (`oideachais/notebooks/`)

| Notebook | Purpose | Tabs |
|----------|---------|------|
| `mission_control.py` | Operational dashboard | 7 |
| `curriculum_educator.py` | Curriculum exploration | — |
| `ducklake_explorer.py` | DuckLake queries | — |
| `pipeline_e2e_test.py` | Pipeline smoke test | — |
| `exam_papers_explorer.py` | SEC exam paper browser + ?fp= health | 8 |
| `marking_scheme_analyzer.py` | PCLM/SRPs rubric patterns | 6 |
| `syllabus_visualizer.py` | NCCA concept graph + cross-nation compare | 7 |
| `pdf_download_dashboard.py` | Live download status + Garage inspector | 5 |
| `lakehouse_inspector.py` | Iceberg/Lance/DuckLake cross-flow console | 6 |

### Skills (`.agents/skills/`)

- `dlt` — DLT pipeline construction
- `dagster` — Dagster asset design + partitions
- `marimo` — Reactive notebook patterns
- `motherduck` — Dives + dual-execution
- `copilotkit` — AGUI generative UI
- `tanstack-start` — SSR + server functions
- `dignified-python` — Python quality standards
- `oideachas-pipeline` — Domain knowledge

---

## 7. Quickstart

```bash
# From repo root
bun run setup                     # mise install + bun install + uv sync + secrets

# Hydrate environment (Infisical → .env)
bun run secrets:init              # or rely on `mise` directory hooks

# Start lakehouse stack
cd infrastructure/stacks/lakehouse
docker compose up -d

# Start Dagster (from the oideachais subdir, not absolute path)
cd oideachais
DAGSTER_HOME=. uv run dagster dev -m data_platform.dagster_defs.definitions

# Start marimo ops dashboard
cd oideachais
uv run marimo edit notebooks/mission_control.py

# Run a pipeline directly (DLT)
USE_DUCKLAKE=false uv run python -c "
from data_platform.dlt_sources.ireland.examinations import sec_examinations_browser_source
from data_platform.dlt_utils import create_pipeline, safe_dlt_run
pipeline = create_pipeline('exam_materials', 'examinations')
load = safe_dlt_run(pipeline, sec_examinations_browser_source(
    subjects=['mathematics'], years=[2024], level='leaving_certificate',
    material_types=['exam_papers'],
))
print(load)
"
```

---

## 8. Lakehouse Stack

The complete storage stack implementation lives in
`infrastructure/stacks/lakehouse/`:

- `compose.yaml` — Garage, PostgreSQL, Lakekeeper, Lance Namespace sidecar
- `blueprint.yaml` — Pangolin ingress (iceberg/lance/ducklake S3 endpoints, private
  Lakekeeper + Lance API)
- `secrets.env` — Locket/Infisical injection template
- `cross_flow_client.py` — Unified search across codeolas/oideachas/crypteolas
- `lance-sidecar/main.py` — FastAPI that registers Lance tables as Iceberg
  `table_type=lance` properties in Lakekeeper
- `notebooks/lakehouse_pipeline.py` — Marimo demo of the full stack

Service health check:

```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep lakehouse
# lakehouse-garage            Up 6 days (healthy)
# lakehouse-postgres          Up 7 days (healthy)
# lakehouse-lakekeeper        Up 6 days (healthy)
# lakehouse-lance-namespace   Up 6 days (healthy)
```

---

## 8.5 LLM Gateway — Why LiteLLM Matters for Oideachais

The Oideachais data platform has **zero direct calls** to any LLM provider. Every
text generation, embedding, OCR, and image generation call goes through a single
gateway: the **LiteLLM proxy** at `infrastructure/stacks/litellm`.

### 8.5.1 Why a gateway is non-negotiable here

The Oideachais pipeline has to mix:

| Need | Provider |
|:--|:--|
| **High-quality BAML extraction** of curriculum specs and exam papers | Gemini 2.5 Pro, Claude Sonnet 4 (cloud) |
| **High-volume OCR** of SEC PDFs | Gemini 2.5 Flash, plus local VLM fallback |
| **Multimodal vision** for handwritten SEC marking schemes | Qwen2.5-VL 7B (GGUF), Granite Docling (MLX) |
| **Math reasoning** for worked-example generation | Qwen2.5-Math 7B (GGUF) |
| **Irish text generation** for tutoring | UCCIX Llama2 13B (GGUF), Qwen2.5-Math English fallback |
| **Embeddings** (BGE-M3, GaBERT, ColPali) | transformers (local), not llama-swap |
| **Image generation** for study assets (FIBO JSON config → Bria FIBO) | Bria FIBO (MLX), Z-Image-Turbo (GGUF), FLUX.2 (GGUF), Qwen-Image (GGUF), SDXL (InvokeAI) |
| **Cheap generic** tasks (entity extraction, classification) | OpenCode Go subscription per `Go.md` |
| **Privacy-sensitive** on-device work | MLX on MacBook M4 Max, llama-swap with F16 mmproj |

Without a gateway, every Dagster asset, BAML function, marimo notebook, and
FastAPI endpoint would have to:

1. Hardcode which provider + which model to call
2. Implement its own retry / fallback / circuit-breaker logic
3. Set up its own Langfuse / MLflow / RAGAS integration
4. Track its own rate limits and spend caps
5. Re-validate the JSON schema on every provider's quirk

That's ~5–10× more code per call site, and the moment you add a new model
you have to touch every consumer.

### 8.5.2 What the gateway gives us

The LiteLLM proxy (`infrastructure/stacks/litellm/`) provides:

- **One OpenAI-compatible URL** for everything (`http://litellm:4000/v1`)
- **Alias routes** that abstract model choice:
  - `ocr` → `local/ocr/olmocr-mlx` → `local/ocr/deepseek-ocr` → `gemini-2.5-flash`
  - `vision` → `local/vision/qwen25-vl` → `local/vision/gemma3-vision` → `gemini-2.5-flash`
  - `document` → `local/document/granite-docling` → `local/vision/qwen25-vl`
  - `extract` → `gemini-2.5-pro` → `glm-4.6` → `gemini-2.5-flash`
  - `math` → `local/math/qwen25-math` → `glm-4.6`
  - `irish` → `local/irish/uccix` → `local/math/qwen25-math` → `gemini-2.5-flash`
  - `image` → `local/image/z-image-turbo` → `local/image/qwen-image` → `local/image/flux2` → `local/image/sdxl`
  - `image-fibo` → `local/image/fibo` → `local/image/z-image-turbo`
  - `embedding-curriculum` → `celtic/embedding/bge-m3`
  - `general` → `opencode-go/deepseek-v4-flash` → `glm-4.6` → `gpt-4o-mini`
- **Langfuse tracing** for every request (full lineage: which alias → which
  model → which asset)
- **Spend caps** in the gateway config (per-model rate limits, monthly budget)
- **BAML clients** (`baml_src/clients.baml`) that point all functions to
  `client LiteLLM` — no more `client Claude`, no direct Anthropic SDK
- **Resource**: `oideachais/data_platform/dagster_defs/resources.py`
  defines `LiteLLMResource` so any Dagster asset can call the gateway
  uniformly

### 8.5.3 Bringing up the full stack

```bash
# 1. Start the lakehouse (Garage, PostgreSQL, Lakekeeper)
cd infrastructure/stacks/lakehouse
docker compose up -d

# 2. Start the LLM gateway + backends
cd infrastructure/stacks/litellm
docker compose -f compose.yaml -f sidecar.yaml up -d   # gateway + Locket
cd ../../engineering/mlx-omni
docker compose -f compose.yaml -f sidecar.yaml up -d   # Apple Silicon MLX
cd ../meaisínfhoghlaim
docker compose -f compose.yaml -f sidecar.yaml up -d   # llama-swap GGUF
cd ../../engineering/invokeai
docker compose -f compose.yaml -f sidecar.yaml up -d   # SDXL

# 3. Verify all routes
curl -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
     http://localhost:4000/v1/models | jq '.data[].id' | head -20

# 4. From Dagster, materialise the model_conversion job
#    (downloads HF models, converts to GGUF, copies to /stedding/huggingface/gguf)
uv run dagster dev -m data_platform.dagster_defs.definitions
# → Open http://localhost:3000 → Jobs → model_conversion → Materialize
```

### 8.5.4 The BAML bridge

Every BAML function in `baml_src/*.baml` now declares `client LiteLLM`
(see the swap in `curriculum_extraction.baml` — 10 `client Claude`
references replaced with `client LiteLLM`). The BAML client points to
`LITELLM_BASE_URL` and the gateway in turn:

- Tries `extract` (Gemini Pro) first for BAML extraction (strongest JSON
  schema adherence, best Irish support)
- Falls back to `glm-4.6` if Gemini quota exceeded
- Falls back to `gemini-2.5-flash` for cost
- Falls back to `local-vision` (Qwen2.5-VL on llama-swap) if all cloud routes
  are down

BAML tests in `baml_src/curriculum_extraction.baml` still pass — the schema
is identical, only the routing changed.

### 8.5.5 Why not just call providers directly?

Three reasons specific to this project:

1. **Irish + Bilingual Reliability** — Gemini Flash occasionally returns
   English even when prompted in Irish. The gateway's `extract` alias falls
   through to UCCIX 13B (which is Irish-trained) before returning. Calling
   Gemini directly would miss this.
2. **Local-First by Default** — The oideachais monorepo is run on a
   **MacBook M4 Max with no always-on cloud**. The gateway's `ocr` and
   `vision` aliases start on local MLX/GGUF, so an offline oideachais
   session still works (the only things that break are cloud fallbacks).
3. **BAML Just Works** — The BAML compiler validates schema adherence on
   every response, but it doesn't care which LLM answered. Pointing it at
   the gateway means we can swap entire model families in `config.yaml`
   without regenerating BAML.

See `infrastructure/stacks/litellm/config/config.yaml` for the
full route table, and `docs/meaisínfhoghlaim/Setting Up Local LLM Services on Mac.md`
for the architectural rationale.

---

## 9. Agent Guidelines

If you are extending these pipelines, **assume the `data-engineer` persona**.

- **NEVER** use absolute imports originating from the root (e.g.
  `from oideachais.data_platform...`) inside `data_platform/`. Use relative
  imports (`from .dagster_defs...`) to prevent Dagster module-resolution
  crashes.
- **Always** wrap `pipeline.run()` in `safe_dlt_run()`.
- **Always** commit after pipeline changes:
  `./scripts/sync_agent_docs.sh` updates local telemetry blocks.
- **Always** respect the `USE_DUCKLAKE` and `USE_LOCAL_SCRAPES` toggles.
- **Always** test with `USE_DUCKLAKE=false` (DuckDB fallback) before production
  runs.
- **Never** commit secrets. Use `.infisical.env` template + Locket injection.
- **Prefer** `@dlt.resource(write_disposition="merge", primary_key=...)` for
  incremental dedup, especially for `pdf_url` and `url`.
- **Prefer** `MultiPartitionsDefinition` over many `StaticPartitionsDefinition`
  axes. Years are config, not partitions.
- **Verify** the lakehouse is up before running any pipeline
  (`docker ps | grep lakehouse`).

---

## 10. Related Documentation

- `AGENTS.md` (repo root) — Global agent orchestration rules
- `infrastructure/AGENTS.md` — Infrastructure stacks and Komodo/Pangolin
- `infrastructure/stacks/lakehouse/` — Lakehouse source of truth
- `infrastructure/browser/` — Stagehand + Playwright + Browserbase
- `oideachais/notebooks/mission_control.py` — Operational dashboard
- `oideachais/web/` — TanStack Start + CopilotKit consumer app
- `.agents/skills/` — Skill library (dlt, dagster, marimo, motherduck, etc.)

---

## 11. Change Log (Cumulative Pipeline Improvements)

The full cumulative change log has been extracted to
[`CHANGELOG.md`](CHANGELOG.md) to keep this README focused on the
engine itself. See CHANGELOG.md for entries 11.1 (SEC ?fp= URL
discovery), 11.2 (DLT → Dagster asset wiring), 11.3 (destination
factory), 11.4 (concurrency limits), 11.5 (`USE_LOCAL_SCRAPES`),
11.6 (PDF downloader status taxonomy), 11.7 (lakehouse stack),
11.8 (notebooks operational suite), 11.9 (asset topology),
11.10 (DLT source inventory), 11.11 (CocoIndex flows), and
11.12 (frontend stack).

---

## 12. Adding a New DLT Source (Agent Recipe)

1. **Pick a DLT file** in `dlt_sources/ireland/` (or `uk/`, `celtic/`).
2. **Define a `@dlt.resource(write_disposition="merge", primary_key=...)`**
   with the canonical columns (subject, year, level, pdf_url, content_hash).
3. **Wire to Dagster** by adding a new `dg.asset(...)` in the right
   `dagster_defs/assets/<domain>/` file with a `MultiPartitionsDefinition`
   over the new domain's partition axes.
4. **Add the job** to `definitions.py` (`define_asset_job(name=..., selection=...)`).
5. **Update the schedule** in `dagster_defs/schedules.py` if periodic.
6. **Document the data contract** in section 2 of this README.
7. **Add a notebook tab** in the relevant operational dashboard.
8. **Run `./scripts/sync_agent_docs.sh`** to refresh local telemetry blocks.
9. **Run `marimo check`** on all touched notebooks.
10. **Commit + push** per AGENTS.md landing-the-plane workflow.

## 13. Adding a New Marimo Notebook (Agent Recipe)

1. **Create** the file under `oideachais/notebooks/`.
2. **Use `@app.cell`** for every block; **never** use `return` (marimo
   cells are top-level).
3. **Prefix cell-private variables** with `_` (e.g. `_con`, `_df`, `_err`)
   to avoid the `multiple-definitions` marimo error.
4. **Use the runtime query-engine selector** for any notebook that
   hits the lakehouse:
   ```python
   if os.getenv("MOTHERDUCK_ENABLED", "false").lower() == "true":
       _con = duckdb.connect(f"md:?motherduck_token={os.environ['MOTHERDUCK_TOKEN']}")
   else:
       _con = duckdb.connect(DUCKDB_PATH, read_only=True)
   ```
5. **Validate** with `marimo check notebooks/<file>.py`.
6. **Add a section** to the notebook inventory in section 6 of this README.
7. **Commit + push**.

## 14. OpenSpec Workflow (For Behaviour-Changing Work)

For changes that affect data contracts, add new DLT sources, change the
catalog schema, or wire new AGUI capabilities, follow the OpenSpec workflow
at `openspec/AGENTS.md`:

```bash
bun run spec:list                       # see existing change-IDs
# Author proposal/tasks/spec deltas in openspec/changes/<id>/
bun run spec:validate <id> --strict     # schema + cross-refs pass
# Implement
bun run spec:archive <id>               # fold into the canonical specs
```

The first AGUI visualiser route (`/exams`) is the canonical Phase-B example
of an `openspec/changes/agui-exam-visualiser/` change bundle.

---

## 15. TanStack Start Frontend Migration (Phase B)

The `oideachais/web/` directory has been migrated from the previous
Vite-only setup to TanStack Start (Vinxi + TanStack Router + SSR + server
functions). The new layout follows the canonical TanStack Start template:

```
oideachais/web/
├── app.config.ts          # Vinxi + TanStack Start Vite plugin
├── app/
│   ├── app.css            # Tailwind 4 entry
│   ├── client.tsx         # CSR hydration root
│   ├── router.tsx         # getRouter() factory
│   ├── routeTree.tsx      # Composes all routes + root layout
│   ├── components/        # Header, Sidebar, AwenChat
│   ├── lib/
│   │   └── ai-tools.ts    # TanStack AI tool defs (queryDuckLake, etc.)
│   ├── routes/
│   │   ├── index.tsx       # /
│   │   ├── dives.tsx       # /dives (MotherDuck embed)
│   │   ├── exams.tsx       # /exams (full AGUI visualiser)
│   │   ├── marking-schemes.tsx # /marking-schemes
│   │   ├── syllabus.tsx    # /syllabus
│   │   ├── lakehouse.tsx    # /lakehouse
│   │   └── runs.tsx         # /runs (Dagster run history)
│   └── server/
│       ├── motherduck.ts   # getEmbedSession (REST API proxy)
│       └── lakehouse.ts    # queryLakehouse, listExamMaterials,
│                            # getMarkingSchemeSummary, listBuckets
├── package.json
└── tsconfig.json
```

### 15.1 Server Functions (TanStack Start `createServerFn`)

`createServerFn({ method: "POST" }).inputValidator(zod).handler(...)` is the
canonical pattern. Server functions are called from the client exactly like
RPCs — TanStack Start serialises the validated `data` over the wire.

| Function | Schema | Purpose |
|----------|--------|---------|
| `getEmbedSession` | `{ username, sessionHint? }` | Mint MotherDuck Dive session |
| `queryLakehouse` | `{ sql, limit }` | Run DuckDB SQL (local or MotherDuck) |
| `listExamMaterials` | `{ subject, year, level, materialType }` | Filter exam_materials |
| `getMarkingSchemeSummary` | `{ subject }` | Per-subject rubric + years |
| `listBuckets` | (none) | List Garage S3 buckets |

All lakehouse server functions route via the `MOTHERDUCK_ENABLED` env var
exactly like the marimo notebooks: when `true`, the call hits the
MotherDuck HTTP query API; otherwise, the local DuckDB-WASM path is used.

### 15.2 CopilotKit AGUI Exam Visualiser (`/exams`)

The `/exams` route is the canonical AGUI experience:

1. **Filter rail** (left) — TanStack Form with subject / year / level /
   material_type controls. State synced to URL search params via
   `validateSearch`.
2. **Exam cards** (centre) — Driven by `useQuery({ queryKey: ['exam-materials', search], queryFn: () => listExamMaterials(...) })`.
   Each card shows the obfuscated `?fp=` URL and a link to open the PDF.
3. **Awen chat** (right) — `useCopilotAction` wires the TanStack AI tools
   (`queryDuckLake`, `listExamMaterials`, `getMarkingSchemeSummary`) so the
   agent can render Generative UI cards in response to natural language.

### 15.3 Build Status (Phase B as of v1)

| Check | Status |
|-------|--------|
| `bun install` (deps install) | ✅ passing |
| `bun run typecheck` (`tsc --noEmit`) | ✅ passing (0 errors) |
| `bun run build` (`vinxi build`) | ⚠️ blocked on Vinxi 0.5.x API drift |

The Vinxi 0.5.x release changed the app construction model and breaks
TanStack Start 1.145's expected config layout (`defineConfig({ routers: [...] })`
vs the simpler plugin-only pattern). The current config in
`app.config.ts` uses Vite's `defineConfig` with the `tanstackStart()` plugin,
which is correct for newer versions of the toolchain. To build, pin
`vinxi@0.4.3` in `package.json` and use:

```ts
// vinxi.config.ts (sibling of app.config.ts)
import { defineConfig } from "@tanstack/react-start/config";
export default defineConfig({
  routers: [
    {
      name: "web",
      type: "spa",
      root: ".",
      handler: "app/client.tsx",
      target: "browser",
    },
  ],
});
```

The TypeScript-clean code in `app/` is the actual Phase B deliverable; the
Vinxi-config tweak is a 4-line patch that any follow-up session can apply
once the team decides which Vinxi version to standardise on.
