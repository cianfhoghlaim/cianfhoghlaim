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
