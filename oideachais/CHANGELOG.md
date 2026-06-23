# Oideachais — Cumulative Pipeline Change Log

> This file tracks material changes to the `oideachais/` engine over time.
> Each entry references the file that owns the change so the next agent
> can navigate to the source of truth. Newest entries at the top.

## Recent Changes

### 11.12 Frontend Stack — `oideachais/web/`

| Tech | Role |
|------|---------|
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

### 11.8 Notebooks — Operational Suite

The `oideachais/notebooks/` directory is the operator console:

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

All new notebooks honour the `MOTHERDUCK_ENABLED` env var to toggle
between a shared MotherDuck database and the local DuckDB / DuckLake
fallback. They all pass `marimo check` cleanly.

### 11.7 Lakehouse Stack — `infrastructure/stacks/lakehouse/`

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

### 11.5 Offline Fallback (`USE_LOCAL_SCRAPES`)

To avoid burning Firecrawl / Stagehand credits during development, the DLT
sources honour `USE_LOCAL_SCRAPES=true`. When set, network calls are
intercepted and replaced with data from `stedding/ingest_queue/` (7000+
cached structural documents with base64 PDFs and Markdown).

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

### 11.3 Destination Factory Consolidation

`dlt_utils/destinations.py` is the single entry point for switching between
local DuckLake (Garage S3 + PostgreSQL), production DuckLake (Cloudflare R2 +
PlanetScale), and the plain DuckDB fallback. It uses **path-style S3 URLs**
(`config_kwargs={"s3": {"addressing_style": "path"}}`) because Garage and
MinIO do not honour virtual-host DNS for bucket subdomains.

All Dagster assets wrap `pipeline.run()` in `safe_dlt_run()` (from
`dlt_utils/safety.py`) so writes go through `SerialDatabaseExecutor` — this
prevents the well-known concurrent-access segfault in DuckDB.

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

---

## Older Changes

Earlier entries (pre-11.1) are archived in git history:
`git log --oneline -- oideachais/`
