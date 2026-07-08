## ADDED Requirements

### Requirement: 5 Irish legal DLT sources

The system SHALL ingest 5 Irish legal / operational-law DLT sources via
`cianfhoghlaim/dlt/british_isles/ireland/law/`:

1. `injuries_ie.py` — Personal Injuries Assessment Board (PIAB) process + forms
2. `courts_ie.py` — Courts Service forms + Judgements.ie + fees + Rules of Court
3. `workplace_relations.py` — Workplace Relations Commission (WRC) decisions + procedures
4. `citizensinformation.py` — Citizens Information Board (CIB) rights/entitlements articles
5. `gov_ie_law.py` — Irish Government (all sub-departments) press + publications

The system SHALL emit `nation="ie"`, `domain="law"`, `entity=<source_slug>`
on every row (per the oideachais-pipeline Asset Key Convention).

The system SHALL honour `USE_LOCAL_SCRAPES=true` to fall back to
`stedding/ingest_queue/<source>/` when the network is unavailable.

#### Scenario: All 5 sources registered

- **WHEN** a developer lists `cianfhoghlaim/dlt/british_isles/ireland/law/`
- **THEN** the 5 new files exist
- **AND** `__init__.py` exports all 5 source modules

#### Scenario: Each source uses merge + primary_key

- **WHEN** a source is materialised twice (e.g. once daily)
- **THEN** the second run merges into the first rather than replacing
- **AND** `primary_key=["url"]` deduplicates rows

#### Scenario: Network fallback works

- **WHEN** the network is unavailable AND `USE_LOCAL_SCRAPES=true`
- **THEN** the source reads from `stedding/ingest_queue/<source>/`
- **AND** produces the same row count as a live crawl (within tolerance)

### Requirement: PIAB source coverage (injuries.ie)

The system SHALL crawl `https://www.injuries.ie/eng/` covering:
- The PIAB process pages (how to apply, what to expect, timelines)
- The PIAB forms catalogue (Application forms A/B, consent forms, medical
  report forms)
- The PIAB news/updates page
- The "about PIAB" / "permission to seek judicial review" / "Section 14
  notice" pages (the central personal-injury litigation gate)

The system SHALL partition by `(entity_type, page_kind)` where
`entity_type ∈ {page, form}`.

#### Scenario: PIAB process pages crawled

- **WHEN** the `injuries_ie` source is materialised
- **THEN** at least 5 process pages exist in
  `oideachais.law.ie.piab_pages`

#### Scenario: PIAB forms catalogue

- **WHEN** the `injuries_ie` source is materialised
- **THEN** at least 2 PIAB forms exist in `oideachais.law.ie.piab_forms`

#### Scenario: Permission-to-sue page is extracted

- **WHEN** the user searches the BGE-M3 embeddings for "permission to
  seek judicial review injuries board"
- **THEN** the relevant PIAB page is returned with score > 0.75

### Requirement: Courts Service source coverage (courts.ie)

The system SHALL crawl `https://www.courts.ie/` covering:
- The 4 court levels (District / Circuit / High / Supreme / Court of Appeal)
- The court forms catalogue (district_court_forms, circuit_court_forms,
  high_court_forms, supreme_court_forms)
- The Judgements.ie database (~30,000 published decisions)
- The Court Fees schedules (per-court fee codes)
- The Rules of Court (PDF library per jurisdiction)

The system SHALL emit 4 resources: `forms`, `judgements`, `fees`, `rules`.

#### Scenario: High Court forms indexed

- **WHEN** the `courts_ie` source is materialised
- **THEN** at least 20 High Court forms exist in `oideachais.law.ie.courts_forms`
- **AND** the `court_level = "high"` filter returns >= 20 rows

#### Scenario: Judgements.ie database crawled

- **WHEN** the `courts_ie.judgements` resource is materialised
- **THEN** at least 100 judgements exist in `oideachais.law.ie.judgements`
- **AND** each row carries `neutral_citation`, `parties`, `judge`,
  `decision_date`, `statutes_cited[]`

#### Scenario: Court fees and rules indexed

- **WHEN** the `courts_ie.fees` + `courts_ie.rules` resources are materialised
- **THEN** >= 10 fees exist in `oideachais.law.ie.court_fees`
- **AND** >= 5 rules exist in `oideachais.law.ie.court_rules`

### Requirement: WRC source coverage (workplacerelations.ie)

The system SHALL crawl `https://workplacerelations.ie/en/` covering:
- The published WRC Adjudication Decisions database (~6,000 decisions/yr)
- The complaint procedure pages (unfair dismissal, employment equality,
  payment of wages, working time, redundancy)
- The WRC forms catalogue
- The WRC news/updates page

The system SHALL emit 2 resources: `pages`, `decisions`.

#### Scenario: WRC decisions crawled

- **WHEN** the `wrc.decisions` resource is materialised
- **THEN** at least 50 WRC decisions exist in `oideachais.law.ie.wrc_decisions`
- **AND** each row carries `case_ref`, `decision_date`, `complaint_type`,
  `outcome`, `award_amount_eur`, `claimant`, `respondent`,
  `statutes_cited[]`

#### Scenario: WRC procedures indexed

- **WHEN** the `wrc.pages` resource is materialised
- **THEN** at least 5 procedure pages exist in `oideachais.law.ie.wrc_pages`
- **AND** each row carries `complaint_type`, `time_limits`, `hearing_steps`,
  `adr_options`

### Requirement: Citizens Information source coverage (citizensinformation.ie)

The system SHALL crawl `https://www.citizensinformation.ie/en/` covering:
- Justice / law topics
- Employment topics (rights at work, contracts, dismissals, equality)
- Social welfare (entitlements, appeals)
- Housing (tenancies, evictions)
- Health (medical cards, hospital charges, complaints)
- Consumer (rights, returns, warranties)
- Money and tax (entitlements, PRSI, USC)

The system SHALL emit 1 resource: `articles`.

#### Scenario: CIB articles crawled across categories

- **WHEN** the `citizensinfo` source is materialised
- **THEN** at least 200 articles exist in `oideachais.law.ie.citizensinfo_articles`
- **AND** >= 5 distinct categories appear in the `category` column
- **AND** >= 10 articles mention "appeal" in their text

### Requirement: gov.ie source coverage (all sub-departments)

The system SHALL crawl `https://www.gov.ie/en/` covering all
ministerial sub-departments: DoJ, DoH, DES, DBEI, DECC, DAFM, DTCAGSM,
DHLGH, DPER, DRCD, DT (Transport), DCYA (Children), and the Department
of Tourism, Culture, Arts, Gaeltacht, Sport and Media.

The system SHALL emit 1 resource: `pages` with sub-types `department`,
`publication`, `news`, `organisation`.

#### Scenario: gov.ie departments indexed

- **WHEN** the `gov_ie` source is materialised
- **THEN** at least 50 pages exist in `oideachais.law.ie.gov_ie_pages`
- **AND** >= 8 distinct departments appear in the `department` column

### Requirement: BAML extraction for the 5 sources

The system SHALL provide 9 BAML extraction functions in
`cianfhoghlaim/baml_src/processing/ireland_legal_extraction.baml`:

1. `ExtractPIABPage` → `PIABPage`
2. `ExtractCourtForm` → `CourtForm`
3. `ExtractJudgement` → `Judgement`
4. `ExtractCourtFee` → `CourtFee`
5. `ExtractCourtRule` → `CourtRule`
6. `ExtractWRCDecision` → `WRCDecision`
7. `ExtractWRCProcedure` → `WRCProcedure`
8. `ExtractCitizensInfoArticle` → `CitizensInfoArticle`
9. `ExtractGovIEPressRelease` → `GovIEPressRelease`

The system SHALL default to `litellm/gemini-2.5-flash` for all 9
functions (matches the `circular_extraction.baml` precedent).

The system SHALL re-use the `CaseCategory`, `Jurisdiction`, `TimelineEvent`,
`StatuteReference` enums/classes from `legal_case_profile.baml` via
BAML cross-file imports.

The system SHALL persist extracted rows to DuckLake tables
`oideachais.law.ie.<entity>_*` (per source).

#### Scenario: WRC decision BAML extraction

- **WHEN** a WRC decision HTML page is passed to `b.ExtractWRCDecision`
- **THEN** the returned `WRCDecision` carries all 8 fields:
  `case_ref`, `decision_date`, `complaint_type`, `outcome`,
  `award_amount_eur`, `claimant`, `respondent`, `statutes_cited`
- **AND** `statutes_cited` contains at least one `StatuteReference`

#### Scenario: Judgement BAML extraction

- **WHEN** a Judgements.ie HTML page is passed to `b.ExtractJudgement`
- **THEN** the returned `Judgement` carries `neutral_citation`, `parties`,
  `judge`, `decision_date`, `court_level`, `catchwords`, `holding`,
  `statutes_cited[]`
- **AND** `statutes_cited` is the canonical join key against
  `oideachais.education.ie.irish_statute_book.acts`

#### Scenario: Pydantic-mirror schema validation

- **WHEN** the BAML codegen runs (`mise run baml:generate`)
- **THEN** the generated Pydantic v2 classes mirror the BAML class shapes
- **AND** the L2 Dagster assets use the Pydantic-mirror for runtime
  validation before persisting to DuckLake

### Requirement: CocoIndex v1 BGE-M3 embeddings

The system SHALL provide a v1-conformant CocoIndex App at
`cianfhoghlaim/cocoindex/ireland_legal_embedding.py` with the
canonical R1–R4 conformance contract:

- R1: `from ._lifespan import shared_lifespan`
- R2: imports `ContextKeys` from `._lifespan`
- R3: `IrelandLegalEmbedding = coco.App(name="IrelandLegalEmbedding")` at module scope
- R4: ≥1 `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

The system SHALL embed the BAML-extracted content (9 tables) into
LanceDB tables named `oideachais.law.ie.<entity>` using
`BAAI/bge-m3` (1024 dims).

The system SHALL honour the 100-row batch minimum + the HNSW-DROP-THRESHOLD=50
rule from the `oideachais-cocoindex-v1` skill.

#### Scenario: CocoIndex v1 conformance

- **WHEN** `mise run upstream:conformance` runs
- **THEN** `IrelandLegalEmbedding` passes R1, R2, R3, R4

#### Scenario: LanceDB rows produced

- **WHEN** `dagster asset materialize --select '*ireland_legal*'` runs
  against a populated DuckLake
- **THEN** rows appear in `oideachais.law.ie.piab`,
  `oideachais.law.ie.courts`, `oideachais.law.ie.wrc`,
  `oideachais.law.ie.citizensinfo`, `oideachais.law.ie.gov_ie`
- **AND** each row's `embedding` is a valid BGE-M3 vector (1024-dim)

### Requirement: 5-layer Dagster orchestration

The system SHALL orchestrate the pipeline via the canonical 5-layer
architecture:

- L1 ingestion: `orchestration/defs/1_ingestion/law/ie_{injuries_board,courts_service,workplace_relations,citizensinformation,ie_gov_ie}/defs.yaml` (5 new `CelticIngestionComponent` instantiations)
- L2 materials: `orchestration/defs/2_materials/legal_research/ireland_legal_extraction/` (1 `CelticMaterialsComponent` + 9 BAML extraction `@asset`s)
- L3 model-lifecycle: `orchestration/defs/3_model_lifecycle/cocoindex_v1/ireland_legal/` (1 `CelticModelLifecycleComponent`)
- L4 asset-generation: `orchestration/defs/4_asset_generation/marimo_dashboards/ireland_legal_{personal_injury,courts,wrc,citizensinfo,gov_ie}/` (5 new `CelticAssetGenerationComponent` instantiations)

#### Scenario: Full materialisation succeeds

- **WHEN** `dagster asset materialize --select '*ireland_legal*'` runs
- **THEN** all 5 L1 + 9 L2 + 1 L3 (CocoIndex v1) assets materialise without error

### Requirement: Asset checks

The system SHALL enforce the following `@asset_check`s on the new
sources:

- `piab_partition_count_min` (≥ 5 process pages + ≥ 2 forms)
- `courts_forms_count_min` (≥ 20 High Court forms + ≥ 20 Circuit Court forms)
- `judgements_citation_required` (every judgement row has a `neutral_citation`)
- `wrc_decision_award_required` (every decision row has `award_amount_eur` or explicit `outcome="non_monetary"`)
- `citizensinfo_category_diversity` (≥ 5 distinct categories in articles)
- `gov_ie_department_diversity` (≥ 8 distinct departments)
- `baml_extraction_latency_p95` (95th-percentile BAML extraction latency ≤ 30s per page)
- `lakehouse_row_count_min` (each of the 9 DuckLake tables has ≥ 10 rows)

#### Scenario: piab_partition_count_min passes

- **WHEN** the `piab_pages` + `piab_forms` tables are populated
- **THEN** the `piab_partition_count_min` `@asset_check` passes

### Requirement: 6 marimo notebooks (one per source + unified)

The system SHALL provide 6 marimo notebooks under
`cianfhoghlaim/notebooks/12_ireland_law/`:

1. `01_personal_injury_journey.py` — PIAB → High Court flow chart
2. `02_courts_index.py` — forms + judgements + fees + rules catalogue
3. `03_wrc_decision_search.py` — WRC decisions semantic search + citation lookup
4. `04_citizensinfo_rights.py` — rights/entitlements/appeals explorer
5. `05_gov_ie_law_corpus.py` — gov.ie ALL sub-departments archive
6. `06_unified_cross_source_query.py` — one box across all 6 sources (incl. ISB)

All 6 notebooks:
- Have PEP 723 inline deps (`marimo>=0.13`, `duckdb>=1.0`,
  `ibis-framework[duckdb]>=9.0`, `altair>=5.0`, `polars>=0.20`)
- Read from `md:oideachais.law.ie.*` via `duckdb.connect("md:oideachais")`
- Use DuckDB + Ibis (no pandas-only analytics)
- Fall back to `:memory:` DuckDB when `md:oideachais` is unreachable
- Never hardcode secrets

#### Scenario: Personal injury journey notebook renders

- **WHEN** `marimo run cianfhoghlaim/notebooks/12_ireland_law/01_personal_injury_journey.py`
  runs against a populated lakehouse
- **THEN** the 5 cells render charts with real data from
  `oideachais.law.ie.piab_pages`, `oideachais.law.ie.piab_forms`,
  `oideachais.law.ie.courts_forms`, and
  `oideachais.law.ie.citizensinfo_articles`

#### Scenario: WRC decision search notebook renders

- **WHEN** the user types "unfair dismissal redundancy payment" in the
  WRC notebook's search box
- **THEN** the notebook returns ≥ 1 WRC decision + ≥ 1 Citizens
  Information article + ≥ 1 Irish Statute Book section that are
  semantically relevant

#### Scenario: Unified cross-source query notebook renders

- **WHEN** the user types "personal injury" in the unified notebook's
  search box
- **THEN** the notebook returns hits from all 6 sources (PIAB, courts,
  WRC, citizensinfo, gov.ie, irish_statute_book)
- **AND** the per-source hit count breakdown chart shows the relative
  weight of each source

### Requirement: Cross-source statute linkage

The system SHALL link the BAML-extracted `statutes_cited` arrays
(from `Judgement`, `WRCDecision`, `CitizensInfoArticle`,
`GovIEPressRelease`) to the existing `irish_statute_book.acts` table
via the `LinkStatutesToActs` Dagster asset.

The system SHALL persist the linkage to
`oideachais.law.ie.statute_links` with columns
`(source, source_id, source_url, statute_name, matched_act_id,
match_confidence)`.

#### Scenario: WRC decision statute linkage

- **WHEN** a WRC decision cites the "Employment Equality Act 1998"
- **THEN** `LinkStatutesToActs` produces a row in
  `oideachais.law.ie.statute_links` with
  `source="wrc"`, `source_id=<decision case_ref>`,
  `statute_name="Employment Equality Act 1998"`,
  `matched_act_id="1998/0021/act"`, `match_confidence ≥ 0.9`

#### Scenario: Judgement statute linkage

- **WHEN** a Judgements.ie decision cites the "Civil Liability Act 1961"
- **THEN** `LinkStatutesToActs` produces a row with
  `source="courts"`, `matched_act_id="1961/0041/act"`,
  `match_confidence ≥ 0.9`

### Requirement: EN-only v1 (Irish GA deferred)

The system SHALL crawl only the English (`/en/`, `/eng/`) paths of the
5 sources in v1. Irish-language paths (e.g. `gort.coimisiúnna.ie`,
`citizensinformation.ie/ga/`, `gov.ie/ga/`) SHALL be deferred to v2.

#### Scenario: No /ga/ paths in v1

- **WHEN** the 5 sources are materialised in v1
- **THEN** no rows have `language="ga"`
- **AND** a `lang_detect` `@asset_check` confirms all rows are EN-only

#### Scenario: v2 Irish GA path is documented

- **GIVEN** the v2 change `2026-Q?-ireland-legal-pipeline-ga-coverage`
  is archived
- **WHEN** a developer reads the v1 spec
- **THEN** the spec's Cross-references section points at the v2 spec

### Requirement: Self-hosted Docker Dagster deploy

The system SHALL use the upstream self-hosted Docker pattern
(`docs/dagster/integrations/deploy/`) as the canonical Dagster
deploy topology (per the oideachais-pipeline spec), with the 4
services (dagster-postgres, dagster-user-code, dagster-webserver,
dagster-daemon). The 5 new L1 + 1 new L2 + 1 new L3 + 5 new L4
defs SHALL be discoverable by `dg list defs` after
`mise run dagster:oideachais`.

#### Scenario: Self-hosted stack picks up the new defs

- **WHEN** `docker compose -f infrastructure/stacks/dagster/compose.yaml up -d`
  runs
- **THEN** the Dagster UI SHALL be reachable at `http://localhost:3000`
- **AND** `dg list defs | grep ireland_legal` returns the 12 new entries

### Requirement: DuckLake canonical schema

The system SHALL persist the BAML-extracted rows to DuckLake tables
under the `oideachais.law.ie.*` schema (per the oideachais-pipeline
single-DB schema convention). The 9 canonical DuckLake tables are:

- `oideachais.law.ie.piab_pages`
- `oideachais.law.ie.piab_forms`
- `oideachais.law.ie.courts_forms`
- `oideachais.law.ie.judgements`
- `oideachais.law.ie.court_fees`
- `oideachais.law.ie.court_rules`
- `oideachais.law.ie.wrc_pages`
- `oideachais.law.ie.wrc_decisions`
- `oideachais.law.ie.citizensinfo_articles`
- `oideachais.law.ie.gov_ie_pages`
- `oideachais.law.ie.statute_links`

#### Scenario: All 11 DuckLake tables exist

- **WHEN** a developer queries
  `SELECT table_name FROM information_schema.tables WHERE table_schema = 'law.ie'`
- **THEN** 11 rows are returned

#### Scenario: Schema is discoverable from a marimo notebook

- **WHEN** `marimo run cianfhoghlaim/notebooks/12_ireland_law/06_unified_cross_source_query.py`
  opens
- **THEN** `duckdb.connect("md:oideachais").sql("SHOW TABLES FROM oideachais.law.ie")`
  returns the 11 tables