# Tasks: 2026-07-11-european-union-official-language-pipeline-v1

## 1. Create the umbrella spec

- [ ] 1.1 Create `openspec/specs/european-union-official-language-pipeline/spec.md`
- [ ] 1.2 Add the 24-language Requirement (1 Requirement + 1 Scenario)
- [ ] 1.3 Add the EUR-Lex ingestion Requirement (1 Requirement + 1 Scenario)
- [ ] 1.4 Add the Eurydice / Cedefop education Requirement (1 Requirement + 1 Scenario)
- [ ] 1.5 Add the EMA / ECDC medicine Requirement (1 Requirement + 1 Scenario)
- [ ] 1.6 Add the Eurostat statistics Requirement (1 Requirement + 1 Scenario)
- [ ] 1.7 Add the Publications Office + Europa portal Requirement (1 Requirement + 1 Scenario)

## 2. DLT sources under `dlt/european_union/`

- [ ] 2.1 Create `dlt/european_union/_shared/__init__.py`
- [ ] 2.2 Create `dlt/european_union/_shared/eu_languages.py` (the 24-language registry)
- [ ] 2.3 Create `dlt/european_union/_shared/eu_institutions.py` (the institution registry)
- [ ] 2.4 Create `dlt/european_union/_shared/cache_layout.py` (the `stedding/ingest_queue/eu/<institution>/` cache)
- [ ] 2.5 Create `dlt/european_union/eur_lex/__init__.py`
- [ ] 2.6 Create `dlt/european_union/eur_lex/regulations.py`
- [ ] 2.7 Create `dlt/european_union/eur_lex/directives.py`
- [ ] 2.8 Create `dlt/european_union/eur_lex/decisions.py`
- [ ] 2.9 Create `dlt/european_union/eur_lex/treaties.py`
- [ ] 2.10 Create `dlt/european_union/eur_lex/cjeu_case_law.py`
- [ ] 2.11 Create `dlt/european_union/publications_office/__init__.py`
- [ ] 2.12 Create `dlt/european_union/publications_office/eu_publications.py`
- [ ] 2.13 Create `dlt/european_union/publications_office/cellar_documents.py`
- [ ] 2.14 Create `dlt/european_union/education/__init__.py`
- [ ] 2.15 Create `dlt/european_union/education/eurydice.py`
- [ ] 2.16 Create `dlt/european_union/education/cedefop.py`
- [ ] 2.17 Create `dlt/european_union/education/school_education_gateway.py`
- [ ] 2.18 Create `dlt/european_union/medicine/__init__.py`
- [ ] 2.19 Create `dlt/european_union/medicine/ema_medicines_register.py`
- [ ] 2.20 Create `dlt/european_union/medicine/ecdc_surveillance.py`
- [ ] 2.21 Create `dlt/european_union/medicine/european_health_data_space.py`
- [ ] 2.22 Create `dlt/european_union/statistics/__init__.py`
- [ ] 2.23 Create `dlt/european_union/statistics/eurostat.py`
- [ ] 2.24 Create `dlt/european_union/government/__init__.py`
- [ ] 2.25 Create `dlt/european_union/government/europa_portal.py`
- [ ] 2.26 Create `dlt/european_union/government/commission_press.py`
- [ ] 2.27 Create `dlt/european_union/government/parliament_documents.py`
- [ ] 2.28 Create `dlt/european_union/government/council_documents.py`
- [ ] 2.29 Every DLT source honours `USE_LOCAL_SCRAPES=true`
- [ ] 2.30 Every DLT source emits rows tagged with `region`,
  `institution`, `language`, `document_type`, `source_url`,
  `content_hash`, and the canonical DuckLake namespace

## 3. BAML extraction schemas under `baml/european_union/`

- [ ] 3.1 Create `baml/european_union/_shared/eu_languages.baml`
- [ ] 3.2 Create `baml/european_union/_shared/eu_institutions.baml`
- [ ] 3.3 Create `baml/european_union/_shared/eu_document.baml`
- [ ] 3.4 Create `baml/european_union/eur_lex_extraction.baml`
- [ ] 3.5 Create `baml/european_union/ema_extraction.baml`
- [ ] 3.6 Create `baml/european_union/ecdc_extraction.baml`
- [ ] 3.7 Create `baml/european_union/eurydice_extraction.baml`
- [ ] 3.8 Create `baml/european_union/eurostat_extraction.baml`

## 4. CocoIndex v1 App

- [ ] 4.1 Create `cocoindex/european_union_official_embedding.py`
- [ ] 4.2 Imports `from ._lifespan import shared_lifespan` (R1–R4 conformance)
- [ ] 4.3 Reads from `dlt/european_union/` DuckLake tables
- [ ] 4.4 Embeds with `BAAI/bge-m3` (1024-d)
- [ ] 4.5 Writes to `oideachais.eu.official_chunks` LanceDB table

## 5. Dagster L1 + L2 + L3 assets

- [ ] 5.1 Create `orchestration/defs/1_ingestion/european_union/eur_lex/regulations/defs.yaml`
- [ ] 5.2 Create `orchestration/defs/1_ingestion/european_union/eur_lex/directives/defs.yaml`
- [ ] 5.3 Create `orchestration/defs/1_ingestion/european_union/eur_lex/cjeu_case_law/defs.yaml`
- [ ] 5.4 Create `orchestration/defs/1_ingestion/european_union/publications_office/eu_publications/defs.yaml`
- [ ] 5.5 Create `orchestration/defs/1_ingestion/european_union/education/eurydice/defs.yaml`
- [ ] 5.6 Create `orchestration/defs/1_ingestion/european_union/medicine/ema_medicines_register/defs.yaml`
- [ ] 5.7 Create `orchestration/defs/1_ingestion/european_union/medicine/ecdc_surveillance/defs.yaml`
- [ ] 5.8 Create `orchestration/defs/1_ingestion/european_union/statistics/eurostat/defs.yaml`
- [ ] 5.9 Create `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_union_official/defs.yaml`
- [ ] 5.10 Every L1 defs.yaml uses the `CelticIngestionComponent` with
  `region="european_union"` and `state_backed: true`

## 6. MotherDuck Dive + daily Flight

- [ ] 6.1 Create
  `motherduck/dives/eu_official_language_coverage.py`
- [ ] 6.2 Create
  `motherduck/flights/eu_official_daily_sync_flight.py`
- [ ] 6.3 Create
  `motherduck/flights/config.yaml` entry for
  `eu_official_daily_sync_flight` with cron `0 5 * * *`

## 7. Cache + fixtures

- [ ] 7.1 Create `stedding/ingest_queue/eu/<institution>/<lang>/` placeholder cache directories
- [ ] 7.2 Create 1 placeholder Firecrawl-shaped JSON per institution
  (so the smoke test returns 1 row per source)

## 8. Spec deltas

- [ ] 8.1 ADDED Requirements on
  `european-union-official-language-pipeline/spec.md` (7 Requirements)
- [ ] 8.2 MODIFIED delta on `cross-region-pipeline/spec.md` adding a
  cross-reference to the new EU institutional instance
- [ ] 8.3 MODIFIED delta on `oideachais-pipeline/spec.md` adding a
  cross-reference to the EU institutional pipeline

## 9. Validate

- [ ] 9.1 `openspec validate 2026-07-11-european-union-official-language-pipeline-v1 --strict` passes
- [ ] 9.2 `dg check yaml` passes on all new defs.yaml
- [ ] 9.3 The cocoindex_v1_conformance App passes
- [ ] 9.4 `mise run lint:skills` still passes

## 10. Commit + push

- [ ] 10.1 Single commit with message
  `feat(eu): EU institutional pipeline (24 official languages) — EUR-Lex / EMA / ECDC / Eurydice / Eurostat`
- [ ] 10.2 `git push origin main`
