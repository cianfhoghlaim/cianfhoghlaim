# Tasks: 2026-07-06-ireland-legal-pipeline

## Phase 1 — Five new DLT sources under `ireland/law/`

### Sub-batch 1.1 — injuries.ie (PIAB)

- [ ] 1.1.1 Create `cianfhoghlaim/dlt/british_isles/ireland/law/injuries_ie.py` — DLT source `piab` with `pages` resource (merge on url); routes: process, forms, news, about; honour `USE_LOCAL_SCRAPES=true` fallback to `stedding/ingest_queue/injuries.ie/`
- [ ] 1.1.2 Add entity types: `piab_pages` (crawled pages), `piab_forms` (PDF forms catalogue); the 2 resources share the same `_crawl_source` helper
- [ ] 1.1.3 Register in `cianfhoghlaim/dlt/british_isles/ireland/law/__init__.py`

### Sub-batch 1.2 — courts.ie (Courts Service)

- [ ] 1.2.1 Create `cianfhoghlaim/dlt/british_isles/ireland/law/courts_ie.py` — DLT source `courts_ie` with 4 resources:
  - `forms` (merge on url) — `/forms/` + `/forms/<court>/`
  - `judgements` (merge on url) — Judgements.ie (Courts Service)
  - `fees` (merge on url) — court fees schedules
  - `rules` (merge on pdf_path) — Rules of Court PDFs
- [ ] 1.2.2 Honour `USE_LOCAL_SCRAPES=true` → `stedding/ingest_queue/courts.ie/`
- [ ] 1.2.3 Register in `cianfhoghlaim/dlt/british_isles/ireland/law/__init__.py`

### Sub-batch 1.3 — workplacerelations.ie (WRC)

- [ ] 1.3.1 Create `cianfhoghlaim/dlt/british_isles/ireland/law/workplace_relations.py` — DLT source `wrc` with 2 resources:
  - `pages` (merge on url) — procedures, forms, news
  - `decisions` (merge on case_ref) — published adjudication decisions
- [ ] 1.3.2 Honour `USE_LOCAL_SCRAPES=true` → `stedding/ingest_queue/workplacerelations.ie/`
- [ ] 1.3.3 Register in `cianfhoghlaim/dlt/british_isles/ireland/law/__init__.py`

### Sub-batch 1.4 — citizensinformation.ie (CIB)

- [ ] 1.4.1 Create `cianfhoghlaim/dlt/british_isles/ireland/law/citizensinformation.py` — DLT source `citizensinfo` with `articles` resource (merge on url) — categories: justice, employment, social-welfare, housing, health, consumer, money-and-tax
- [ ] 1.4.2 Honour `USE_LOCAL_SCRAPES=true` → `stedding/ingest_queue/citizensinformation.ie/`
- [ ] 1.4.3 Register in `cianfhoghlaim/dlt/british_isles/ireland/law/__init__.py`

### Sub-batch 1.5 — gov.ie (all sub-departments)

- [ ] 1.5.1 Create `cianfhoghlaim/dlt/british_isles/ireland/law/gov_ie_law.py` — DLT source `gov_ie` with `pages` resource (merge on url) — routes: department, publication, news, organisation (covers DoJ, DoH, DES, DBEI, DECC, DAFM, DTCAGSM, DHLGH, DPER, DRCD, etc.)
- [ ] 1.5.2 Honour `USE_LOCAL_SCRAPES=true` → `stedding/ingest_queue/gov.ie/`
- [ ] 1.5.3 Register in `cianfhoghlaim/dlt/british_isles/ireland/law/__init__.py` (alongside the existing `doj` source which is kept for backwards compat)

## Phase 2 — BAML extraction schemas

### Sub-batch 2.1 — New BAML file

- [ ] 2.1.1 Create `cianfhoghlaim/baml_src/processing/ireland_legal_extraction.baml` with:
  - 1 enum: `CourtLevel` (DISTRICT | CIRCUIT | HIGH | SUPREME | COURT_OF_APPEAL | SPECIAL)
  - 1 enum: `WRCComplaintType` (UNFAIR_DISMISSAL | EMPLOYMENT_EQUALITY | PAYMENT_OF_WAGES | WORKING_TIME | REDUNDANCY | OTHER)
  - 1 enum: `GovIEDepartment` (DOJ | DOH | DES | DBEI | DECC | DAFM | DTCAGSM | DHLGH | DPER | DRCD | OTHER)
  - 9 classes: `PIABPage`, `CourtForm`, `Judgement`, `CourtFee`, `CourtRule`, `WRCDecision`, `WRCProcedure`, `CitizensInfoArticle`, `GovIEPressRelease`
  - 9 functions: the matching `Extract*` for each class (default client: `litellm/gemini-2.5-flash`)
- [ ] 2.1.2 Re-use the existing `CaseCategory`, `Jurisdiction`, `TimelineEvent`, `StatuteReference` from `legal_case_profile.baml` via `import` (BAML supports cross-file imports)
- [ ] 2.1.3 Register the new module in `cianfhoghlaim/baml_src/processing/__init__.py`
- [ ] 2.1.4 Run `mise run baml:generate` to refresh `baml_client/`

### Sub-batch 2.2 — BAML context + prompts

For each of the 9 functions, write a focused system prompt that:
- Names the source (PIAB / Courts Service / WRC / CIB / gov.ie)
- Names the expected extractable fields
- Handles EN-only in v1 (Irish GA deferred to v2)
- References the relevant statutes (e.g. Personal Injuries Assessment Board Act 2003, Courts Service Act 1998, Employment Equality Act 1998, etc.) as ground-truth anchors

## Phase 3 — CocoIndex v1 embedding flow

- [ ] 3.1 Create `cianfhoghlaim/cocoindex/ireland_legal_embedding.py`:
  - R1: `from ._lifespan import shared_lifespan`
  - R2: uses `ContextKeys` from `._lifespan`
  - R3: `IrelandLegalEmbedding = coco.App(name="IrelandLegalEmbedding")` at module scope
  - R4: ≥1 `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`
  - 1 `IrelandLegalChunk` dataclass (chunk_id, source, entity_type, url, title, text, extra, embedding)
  - Read from the 5 DuckLake tables via canonical `duckdb` query (matches `university_embedding.py:89-100` pattern)
  - 100-row upsert batches (HNSW-DROP-THRESHOLD rule)
- [ ] 3.2 Add to `cianfhoghlaim/cocoindex/_lifespan.py` if new tables needed (else reuse existing)
- [ ] 3.3 Run `mise run upstream:conformance` to verify R1–R4

## Phase 4 — Dagster orchestration (5-layer architecture)

### Sub-batch 4.1 — L1 Ingestion (5 new defs.yaml)

For each of `injuries_ie`, `courts_ie`, `workplace_relations`, `citizensinformation`, `gov_ie_law`:

- [ ] 4.1.1 Create `cianfhoghlaim/orchestration/defs/1_ingestion/law/ie_<slug>/defs.yaml`:
  ```yaml
  type: cianfhoghlaim.orchestration.components.CelticIngestionComponent
  attributes:
    source_id: ie.law.<slug>
    domain: law
    nation: ie
    automation: on_cron
    automation_cron: "0 5 * * *"
  ```

### Sub-batch 4.2 — L2 Materials

- [ ] 4.2.1 Create `cianfhoghlaim/orchestration/defs/2_materials/legal_research/ireland_legal_extraction/defs.yaml`:
  ```yaml
  type: cianfhoghlaim.orchestration.components.CelticMaterialsComponent
  attributes:
    baml_function: b.ExtractPIABPage
    source_asset: 1_ingestion/law/ie/injuries_board
    partition_strategy: by_nation
    asset_check_kind: row_count
    subject: ireland_legal
    language: en
    automation_cron: "0 6 * * *"
  ```
- [ ] 4.2.2 Create `cianfhoghlaim/orchestration/defs/2_materials/legal_research/ireland_legal_extraction/ireland_legal_assets.py` with 9 BAML extraction `@asset` functions (1 per BAML fn)
- [ ] 4.2.3 Wire the 8 remaining BAML fns as additional L2 assets

### Sub-batch 4.3 — L3 Model Lifecycle (CocoIndex v1)

- [ ] 4.3.1 Create `cianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/ireland_legal/defs.yaml`:
  ```yaml
  type: cianfhoghlaim.orchestration.components.CelticModelLifecycleComponent
  attributes:
    app_name: IrelandLegalEmbedding
    module: cianfhoghlaim.cocoindex.ireland_legal_embedding
    embedding_model: BAAI/bge-m3
    hnsw_index: true
    conformance_required: true
  ```

### Sub-batch 4.4 — L4 Asset Generation (5 marimo dashboards)

For each of the 5 per-source notebooks:

- [ ] 4.4.1 Create `cianfhoghlaim/orchestration/defs/4_asset_generation/marimo_dashboards/ireland_legal_<slug>/defs.yaml`:
  ```yaml
  type: cianfhoghlaim.orchestration.components.CelticAssetGenerationComponent
  attributes:
    dashboard_kind: marimo
    dashboard_path: cianfhoghlaim/notebooks/12_ireland_law/<NN>_<topic>.py
    upstream_assets:
      - 2_materials/legal_research/ireland_legal_extraction
      - 3_model_lifecycle/cocoindex_v1/ireland_legal
    refresh_on:
      - "0 6 * * *"
    slug: ireland_legal_<slug>
  ```

## Phase 5 — Marimo notebooks

For each of the 6 notebooks under `cianfhoghlaim/notebooks/12_ireland_law/`:

- [ ] 5.1 `01_personal_injury_journey.py` — 5 cells:
  1. PIAB process flowchart (PIABPage.process_steps)
  2. PIAB forms catalogue (PIABPage.forms_mentioned → download links)
  3. High Court personal injury forms index (CourtForm.kind="personal_injury")
  4. Personal injury time limits (PIABPage.statutory_deadlines)
  5. Cross-reference: citizensinformation personal injury article (semantic match)
- [ ] 5.2 `02_courts_index.py` — 5 cells:
  1. Court forms catalogue (CourtForm by court_level + category)
  2. Court fees (CourtFee by court_level + fee_code)
  3. Court rules (CourtRule by order + court)
  4. Recent Judgements.ie publications (Judgement by year)
  5. Cross-source: find the form for a given Judgement type
- [ ] 5.3 `03_wrc_decision_search.py` — 5 cells:
  1. WRC decision search box (semantic over WRC decisions + procedures)
  2. Decision outcome breakdown (donut: upheld / dismissed / settled / referred)
  3. Statutes cited in WRC decisions (top-N bar chart)
  4. Time-to-decision histogram (decision_date − referral_date)
  5. Cross-source: WRC decision → relevant citizensinfo article → relevant ISB section (unified query)
- [ ] 5.4 `04_citizensinfo_rights.py` — 5 cells:
  1. Article explorer (filter by category: justice / employment / social-welfare / housing / health / consumer / money-and-tax)
  2. Eligibility criteria + entitlements (article body → mo.ui.table)
  3. Appeals procedure index (articles mentioning "appeal")
  4. Statutory references (top-N statutes cited in CIB articles)
  5. Cross-source: rights article → related WRC decision → related ISB section
- [ ] 5.5 `05_gov_ie_law_corpus.py` — 6 cells (covers ALL gov.ie sub-departments):
  1. Department index (16 departments from GovIEDepartment enum)
  2. Press releases per department (timeline)
  3. Publications catalogue (filterable by dept + year)
  4. Statutory references in gov.ie press (top-N)
  5. Cross-source: gov.ie press → related WRC decision / CIB article / ISB section
  6. Search box (semantic over the full gov.ie corpus)
- [ ] 5.6 `06_unified_cross_source_query.py` — 4 cells:
  1. Single search box (queries all 6 sources: injuries_ie + courts_ie + wrc + citizensinfo + gov_ie + irish_statute_book)
  2. Per-source hit count breakdown
  3. Joined result table (source, title, url, snippet, statutes_cited)
  4. Drill-down: click a row → view full text + BAML-extracted fields

All 6 notebooks:
- Have PEP 723 inline deps (`marimo>=0.13`, `duckdb>=1.0`, `ibis-framework[duckdb]>=9.0`, `altair>=5.0`, `polars>=0.20`)
- Read from `md:oideachais.law.ie.*` via `duckdb.connect("md:oideachais")`
- Fall back to `:memory:` DuckDB with empty schema when `md:oideachais` is unreachable (matches `05_mathematics_analysis.py:38-54` pattern)
- Use `nb_utils.connect_md_oideachais()` for graceful fallback
- Never hardcode secrets

## Phase 6 — Validation + quality gates

- [ ] 6.1 Run `openspec validate 2026-07-06-ireland-legal-pipeline --strict` — must pass before commit
- [ ] 6.2 Run `mise run lint` — no errors
- [ ] 6.3 Run `mise run py:typecheck` — no errors
- [ ] 6.4 Run `mise run turbo typecheck` — no errors
- [ ] 6.5 Run `dg list components` — confirms 5 new L1 + 1 new L2 + 1 new L3 + 5 new L4 defs are registered
- [ ] 6.6 Run `mise run upstream:conformance` — IrelandLegalEmbedding v1 App passes R1–R4
- [ ] 6.7 Run `bun run ccc:index && bun run ccc:search "ireland legal pipeline"` — confirms the new spec + the 5 per-source DLT modules are indexed
- [ ] 6.8 Manual smoke: `marimo run cianfhoghlaim/notebooks/12_ireland_law/03_wrc_decision_search.py` renders without error