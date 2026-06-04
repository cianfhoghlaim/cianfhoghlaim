# Oideachais — The Celtic Education Lakehouse Engine

The `oideachais` workspace is the **offline-first ELT engine and lakehouse** at the
heart of the `cianfhoghlaim` stack. It extracts, loads, transforms, and serves
Irish, UK, and pan-Celtic education data — syllabi, exam papers, marking schemes,
Chief Examiner reports, and statistical publications — through a unified
DuckDB/DuckLake core that can deploy identically to local Garage S3 or to
Cloudflare R2 + PlanetScale + MotherDuck.

This README documents the engine itself: data contracts, asset topology, DLT
patterns, environment variables, and the conventions agents must follow when
extending it. For the consumer-facing web app see `oideachais/web/`; for the
operations notebooks see `oideachais/notebooks/`; for the storage stack
implementation see `infrastructure/stacks/storage/lakehouse/`.

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
cd infrastructure/stacks/storage/lakehouse
docker compose up -d

# Start Dagster
cd /Users/cianmacandeisigh/dev/kings_college_galway/oideachais
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
`infrastructure/stacks/storage/lakehouse/`:

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
gateway: the **LiteLLM proxy** at `infrastructure/stacks/engineering/litellm`.

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

The LiteLLM proxy (`infrastructure/stacks/engineering/litellm/`) provides:

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
cd infrastructure/stacks/storage/lakehouse
docker compose up -d

# 2. Start the LLM gateway + backends
cd infrastructure/stacks/engineering/litellm
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

See `infrastructure/stacks/engineering/litellm/config/config.yaml` for the
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
- `infrastructure/stacks/storage/lakehouse/` — Lakehouse source of truth
- `infrastructure/browser/` — Stagehand + Playwright + Browserbase
- `oideachais/notebooks/mission_control.py` — Operational dashboard
- `oideachais/web/` — TanStack Start + CopilotKit consumer app
- `.agents/skills/` — Skill library (dlt, dagster, marimo, motherduck, etc.)

---

## 11. Change Log (Cumulative Pipeline Improvements)

This section tracks the material changes that landed in the engine. Each
entry references the file that owns the change so the next agent can
navigate to the source of truth.

### 11.1 SEC Examinations.ie Scraper — ASP.NET Cascade + `?fp=` URL Discovery

The largest cumulative fix: the `exam_materials` DLT source and the
Playwright-native browser scraper in `infrastructure/browser/sruth_browser/tools/examinations_scraper.py`.

**Before** (broken):
- Assumed dropdown cascade was `Type → Level → Subject → Year` (wrong).
- Only extracted `<a href>` links ending in `.pdf` (missed all SEC PDFs).
- Checkbox used `cb.check()` (caused ASP.NET postback DOM detachment).
- Postback waits were a fixed `asyncio.sleep(3)` (unreliable).
- "Leaving Certificate" matched "Leaving Certificate Applied" first.

**After** (working — 4 PDF links verified for Mathematics LC 2024):
- Cascade is now `Checkbox → ViewType → YearSelect → ExaminationSelect → SubjectSelect`.
- Extracts obfuscated `?fp=` URLs (e.g. `examinations.ie?fp=92.109.94.99.100.113...`)
  via `page.evaluate()` JavaScript snippet that walks all `<a href>` links.
- Checkbox uses `cb.click()` to trigger the ASP.NET postback while preserving
  the DOM.
- Each postback waits on `page.wait_for_selector(state="visible", timeout=10s)`
  with a 5s `asyncio.sleep` fallback.
- Level match uses exact `text == "Leaving Certificate"` first, with
  `"leaving certificate applied"` excluded from the partial-match fallback.

The Playwright-native scraper (`scrape_materials_playwright`) runs first as the
default — zero LLM cost, deterministic. Stagehand (`scrape_materials_batch`) is
the LLM-driven fallback when Playwright returns no real materials.

### 11.2 DLT Source → Dagster Asset Wiring

The exam-materials DLT source was re-shaped to surface cleanly through
Dagster's `MultiPartitionsDefinition`:

- `ireland/exam_materials/leaving_certificate` — subject × material_type
- `ireland/exam_materials/junior_cycle` — subject × material_type
- `ireland/exam_materials/leaving_certificate_applied` — subject × material_type

Years are deliberately **not** a partition dimension; they are an
`ExamMaterialsConfig.years` run-config parameter (avoids ~1664+ sparsely
populated partition keys). See
`dagster_defs/assets/ireland/exam_materials_assets.py:101`.

### 11.3 Destination Factory Consolidation

`dlt_utils/destinations.py` is the single entry point for switching between
local DuckLake (Garage S3 + PostgreSQL), production DuckLake (Cloudflare R2 +
PlanetScale), and the plain DuckDB fallback. It uses **path-style S3 URLs**
(`config_kwargs={"s3": {"addressing_style": "path"}}`) because Garage and
MinIO do not honour virtual-host DNS for bucket subdomains.

All Dagster assets wrap `pipeline.run()` in `safe_dlt_run()` (from
`dlt_utils/safety.py`) so writes go through `SerialDatabaseExecutor` — this
prevents the well-known concurrent-access segfault in DuckDB.

### 11.4 Concurrency Limits

`definitions.py:208` declares Dagster concurrency keys:

```python
CONCURRENCY_LIMITS = {
    "duckdb": 1,      # DuckDB is single-threaded only
    "firecrawl": 3,   # API rate limit
    "lancedb": 2,     # MVCC-safe but limit for performance
}
```

Op tags set per asset (`op_tags={"dagster/concurrency_key": ...}`) route
materializations through the right executor.

### 11.5 Offline Fallback (`USE_LOCAL_SCRAPES`)

To avoid burning Firecrawl / Stagehand credits during development, the DLT
sources honour `USE_LOCAL_SCRAPES=true`. When set, network calls are
intercepted and replaced with data from `stedding/ingest_queue/` (7000+
cached structural documents with base64 PDFs and Markdown).

### 11.6 PDF Downloader Status Taxonomy

`dlt_sources/ireland/pdf_downloader.py` populates `curriculum.pdf_downloads`
with a stable status enum:

| Status | Meaning |
|--------|---------|
| `downloaded` | 200 OK, content hash computed, file on disk |
| `skipped_too_large` | HEAD reports > 50 MB |
| `skipped_not_pdf` | Content-type not `application/pdf` and URL does not end in `.pdf` |
| `error_timeout` | 30s request timeout |
| `error_http_XXX` | non-2xx response |
| `error_unknown` | unexpected exception |

`pdf_download_dashboard.py` (notebook) breaks these down per minute for
throughput visualisation.

### 11.7 Lakehouse Stack — `infrastructure/stacks/storage/lakehouse/`

The four-service stack is up and running (verified via `docker ps`):

| Service | Container | Port(s) | Purpose |
|---------|-----------|---------|---------|
| **Garage S3** | `lakehouse-garage` | 3900-3904 | S3-compatible CRDT object storage |
| **PostgreSQL** | `lakehouse-postgres` | 5433 | Lakekeeper metadata |
| **Lakekeeper** | `lakehouse-lakekeeper` | 8181, 9100 | Iceberg REST catalog |
| **Lance NS** | `lakehouse-lance-namespace` | 8182 | Iceberg adapter for Lance tables |

The Lakekeeper sidecar (FastAPI, 567 lines) at
`lance-sidecar/main.py` registers Lance tables as Iceberg tables with
`table_type=lance` property — the "trojan horse" pattern that lets a
single Lakekeeper instance catalogue both Iceberg Parquet and Lance
columnar data.

The `cross_flow_client.py` (545 lines) provides unified search across the
three cianfhoghlaim flows (códeolas / oideachas / crypteolas) using
BAAI/bge-m3 1024-dim embeddings.

### 11.8 Notebooks — Operational Suite

The `oideachais/notebooks/` directory is the operator console. After the
recent expansion:

| Notebook | Tabs | Role |
|----------|------|------|
| `mission_control.py` | 7 | Health, Orchestrator, DLT Runner, Curriculum, Exams, Destinations, Search |
| `curriculum_educator.py` | — | Curriculum exploration |
| `ducklake_explorer.py` | — | DuckLake queries |
| `pipeline_e2e_test.py` | — | Pipeline smoke test |
| `exam_papers_explorer.py` | 8 | SEC ?fp= URL health, coverage heatmap, Lance search, raw SQL |
| `marking_scheme_analyzer.py` | 6 | PCLM / SRPs / equation rubric per subject, mark distribution, LLM keyword extraction |
| `syllabus_visualizer.py` | 7 | Concept graph, cross-cycle / cross-nation compare, Celtic-language coverage matrix, MotherDuck Dive export |
| `pdf_download_dashboard.py` | 5 | Live DLT status, throughput, retry queue, Garage bucket inspector |
| `lakehouse_inspector.py` | 6 | Service health, bucket inventory, Iceberg namespaces, Lance tables, DuckLake console, cross-flow search |

All five new notebooks honour the `MOTHERDUCK_ENABLED` env var to toggle
between a shared MotherDuck database and the local DuckDB / DuckLake
fallback. They all pass `marimo check` cleanly.

### 11.9 Asset Topology Summary

| Group | Asset | Partition | DLT Pipeline | Cycle |
|-------|-------|-----------|--------------|-------|
| curriculum | `ireland/curriculum/early_childhood` | subject × language | `curriculum_source` | Aistear / Síolta |
| curriculum | `ireland/curriculum/primary` | subject × language | same | Primary |
| curriculum | `ireland/curriculum/junior_cycle` | subject × language | same | JC |
| curriculum | `ireland/curriculum/senior_cycle` | subject × language | same | SC |
| curriculum | `ireland/curriculum/short_courses` | course × language | same | JC Short |
| pdf | `ireland/curriculum/pdf_downloads` | none | `pdf_download_source` | — |
| pdf | `ireland/curriculum/pdf_extracted_text` | none | `pdf_processing` | — |
| exams | `ireland/exam_materials/leaving_certificate` | subject × material_type | `sec_examinations_browser_source` | LC |
| exams | `ireland/exam_materials/junior_cycle` | subject × material_type | same | JC |
| exams | `ireland/exam_materials/leaving_certificate_applied` | subject × material_type | same | LCA |
| enriched | `enriched/*` | none | cross-domain | — |
| search | `search/*` | none | unified index | — |

### 11.10 DLT Source Inventory

```
dlt_sources/
├── ireland/                # 20+ modules
│   ├── ncca.py             # NCCA curriculumonline.ie crawler
│   ├── curriculum_source.py # Multi-subject orchestrator (977 lines)
│   ├── curriculum_registry.py # Subject URL registry (494 lines)
│   ├── examinations.py     # SEC browser scraper (579 lines, ?fp= aware)
│   ├── pdf_downloader.py   # HEAD → GET → SHA-256 → filesystem (547 lines)
│   ├── sec_aural_transcripts.py
│   ├── edcolearning.py     # EdCo Learning audio source
│   ├── parallel_corpus.py  # Bilingual corpus builder
│   ├── subject_adapters.py # Per-subject specialised adapters
│   ├── content_deduplication.py
│   ├── local_documents.py  # Local PDF / JSON ingestion
│   ├── json_seed.py        # Initial seed data
│   ├── oide.py             # Oide (Teachers' Council) source
│   ├── agentic_discovery.py
│   └── subjects/           # senior_cycle / junior_cycle / base adapters
├── uk/                     # 4 nations × 4 sources
│   ├── england/{dfe,ofsted,national_curriculum,school_info}
│   ├── scotland/, wales/, northern_ireland/
├── celtic/                 # pan-Celtic language sources
│   ├── canuint.py          # Dialect/pronunciation
│   ├── duchas.py           # Duchas folkloric archive
│   ├── gaois.py            # National Terminology Database
│   └── universal_dependencies.py
├── crown_dependencies/     # Isle of Man, Channel Islands
├── geospatial/             # DuckDB Spatial + GeoHive
└── common/, constants/, http_client.py, pagination.py
```

### 11.11 CocoIndex Flows (Embedding + Indexing)

`data_platform/cocoindex_flows/` runs the embedding + indexing DAGs:

| Flow | Purpose |
|------|---------|
| `curriculum_embedding.py` | BAAI/bge-m3 embed of curriculum pages |
| `curriculum_specification_extraction.py` | LLM-extracted concept specs |
| `curriculum_translation.py` | en → 6 Celtic languages |
| `learning_outcome_graph.py` | Concept graph across cycles |
| `pdf_embedding.py` | ColPali multi-vector of PDF pages |
| `ocr_embedding.py` | OCR + embedding for HTR corpora |
| `geospatial_indexing.py` | DuckDB Spatial + Lance geo-tables |
| `research_embedding.py` | Research paper embeddings |
| `transforms/caighdean_standardize.py` | Irish orthographic standardisation |
| `transforms/terminology_linking.py` | TermLink cross-walk |

### 11.12 Frontend Stack — `oideachais/web/`

| Tech | Role |
|------|------|
| TanStack Router (file-based) | Routing |
| TanStack DB | Local differential sync |
| TanStack AI | Tool-calling for the AGUI visualiser |
| TanStack Query | Server-state cache |
| TanStack Form | Filter forms |
| CopilotKit | Agent-Generative UI (chat + tool rendering) |
| better-auth | Web3 / OIDC auth |
| recharts | In-app charts |
| Tailwind 4 | Styling |
| Vite | Dev server (pre-TanStack-Start) |
| Vinxi / TanStack Start | SSR + server functions (next stage) |

Routes shipped so far: `/` (Welcome), `/dives` (MotherDuck embed).
Routes queued for the next stage: `/exams`, `/marking-schemes`, `/syllabus`,
`/lakehouse`, `/runs` (all AGUI-powered, all backed by TanStack Start
server functions that proxy MotherDuck / DuckLake).

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
