# Tasks: 2026-07-11-european-nations-ukraine-pipeline-v1

## 1. Create the umbrella spec

- [ ] 1.1 Create `openspec/specs/european-nations-ukraine-pipeline/spec.md`
- [ ] 1.2 Add the canonical DLT path contract Requirement (1 Requirement + 1 Scenario)
- [ ] 1.3 Add the 6 pilot countries Requirement (1 Requirement + 1 Scenario)
- [ ] 1.4 Add the per-nation curriculum extraction Requirement (1 Requirement + 1 Scenario)
- [ ] 1.5 Add the per-nation law extraction Requirement (1 Requirement + 1 Scenario)
- [ ] 1.6 Add the per-nation medicine extraction Requirement (1 Requirement + 1 Scenario)
- [ ] 1.7 Add the cross-nation CocoIndex v1 App Requirement (1 Requirement + 1 Scenario)
- [ ] 1.8 Add the MotherDuck Dive + Flight Requirement (1 Requirement + 1 Scenario)

## 2. Per-country DLT sources (30 total)

For each of the 6 pilot countries (`ukr`, `fra`, `deu`, `pol`, `esp`, `ita`):

- [ ] 2.x.1 Create `dlt/european_nations/<iso3>/__init__.py`
- [ ] 2.x.2 Create `dlt/european_nations/<iso3>/education/__init__.py`
- [ ] 2.x.3 Create `dlt/european_nations/<iso3>/education/<education_source>.py`
- [ ] 2.x.4 Create `dlt/european_nations/<iso3>/law/__init__.py`
- [ ] 2.x.5 Create `dlt/european_nations/<iso3>/law/<law_source>.py`
- [ ] 2.x.6 Create `dlt/european_nations/<iso3>/medicine/__init__.py`
- [ ] 2.x.7 Create `dlt/european_nations/<iso3>/medicine/<medicine_source>.py`
- [ ] 2.x.8 Create `dlt/european_nations/<iso3>/statistics/__init__.py`
- [ ] 2.x.9 Create `dlt/european_nations/<iso3>/statistics/<statistics_source>.py`
- [ ] 2.x.10 Create `dlt/european_nations/<iso3>/government/__init__.py`
- [ ] 2.x.11 Create `dlt/european_nations/<iso3>/government/<government_source>.py`

The mapping is in the proposal §2 table.

## 3. BAML extraction schemas (18 total)

For each of the 6 pilot countries:

- [ ] 3.x.1 Create `baml/european_nations/<iso3>/education.baml`
- [ ] 3.x.2 Create `baml/european_nations/<iso3>/law.baml`
- [ ] 3.x.3 Create `baml/european_nations/<iso3>/medicine.baml`

Plus:

- [ ] 3.7 Create `baml/european_nations/_shared/jurisdiction.baml`
- [ ] 3.8 Create `baml/european_nations/__init__.baml`

## 4. CocoIndex v1 Apps

- [ ] 4.1 Create `cocoindex/european_nations_education_embedding.py`
- [ ] 4.2 Create `cocoindex/european_nations_law_embedding.py`
- [ ] 4.3 Create `cocoindex/european_nations_medicine_embedding.py`
- [ ] 4.4 Each App imports `from ._lifespan import shared_lifespan`
- [ ] 4.5 Each App uses `BAAI/bge-m3`

## 5. Dagster L1 + L3 assets

- [ ] 5.1 Create `orchestration/defs/1_ingestion/european_nations/<iso3>/education/defs.yaml`
- [ ] 5.2 Create `orchestration/defs/1_ingestion/european_nations/<iso3>/law/defs.yaml`
- [ ] 5.3 Create `orchestration/defs/1_ingestion/european_nations/<iso3>/medicine/defs.yaml`
- [ ] 5.4 Create `orchestration/defs/1_ingestion/european_nations/<iso3>/statistics/defs.yaml`
- [ ] 5.5 Create `orchestration/defs/1_ingestion/european_nations/<iso3>/government/defs.yaml`
- [ ] 5.6 Create `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_education/defs.yaml`
- [ ] 5.7 Create `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_law/defs.yaml`
- [ ] 5.8 Create `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_medicine/defs.yaml`

## 6. MotherDuck Dive + Flight

- [ ] 6.1 Create `motherduck/dives/eu_nation_curriculum_matrix.py`
- [ ] 6.2 Create `motherduck/flights/eu_nation_daily_sync_flight.py`
- [ ] 6.3 Append `eu_nation_daily_sync_flight` to
  `motherduck/flights/config.yaml` with cron `0 6 * * *`

## 7. Cache + fixtures

- [ ] 7.1 Create `stedding/ingest_queue/european_nations/<iso3>/<domain>/<lang>/` placeholder cache directories
- [ ] 7.2 Create 1 placeholder Firecrawl-shaped JSON per (country, domain) pair

## 8. Spec deltas

- [ ] 8.1 ADDED Requirements on
  `european-nations-ukraine-pipeline/spec.md`
- [ ] 8.2 MODIFIED delta on `cross-region-pipeline/spec.md` adding a
  cross-reference to the new EU nations instance
- [ ] 8.3 MODIFIED delta on `oideachais-pipeline/spec.md` adding a
  cross-reference

## 9. Validate

- [ ] 9.1 `openspec validate 2026-07-11-european-nations-ukraine-pipeline-v1 --strict` passes
- [ ] 9.2 `dg check yaml` passes on all new defs.yaml
- [ ] 9.3 The cocoindex_v1_conformance App passes for the 3 new
  CocoIndex v1 Apps
- [ ] 9.4 `mise run lint:skills` still passes

## 10. Commit + push

- [ ] 10.1 Single commit with message
  `feat(eu-nations): European nations + Ukraine pipeline (UKR / FRA / DEU / POL / ESP / ITA)`
- [ ] 10.2 `git push origin main`
