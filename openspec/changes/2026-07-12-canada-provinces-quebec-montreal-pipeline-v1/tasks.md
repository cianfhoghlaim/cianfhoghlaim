# Tasks: 2026-07-12-canada-provinces-quebec-montreal-pipeline-v1

## 1. Per-province DLT scaffolds (13 provinces × 5 domains = 65 files)

For each of `on`, `qc`, `bc`, `ab`, `sk`, `mb`, `ns`, `nb`, `pe`,
`nl`, `nt`, `nu`, `yt`:

- [ ] 1.x Create
  `dlt/commonwealth/can/<prov>/__init__.py`
- [ ] 1.x.1 Create `dlt/commonwealth/can/<prov>/education/<ministry>.py`
- [ ] 1.x.2 Create `dlt/commonwealth/can/<prov>/law/<legislation>.py`
- [ ] 1.x.3 Create `dlt/commonwealth/can/<prov>/medicine/<health_authority>.py`
- [ ] 1.x.4 Create `dlt/commonwealth/can/<prov>/statistics/<stats_office>.py`
- [ ] 1.x.5 Create `dlt/commonwealth/can/<prov>/government/<gov_portal>.py`
- [ ] 1.x.6 Create
  `orchestration/defs/1_ingestion/commonwealth/can/<prov>/<domain>/defs.yaml`

## 2. Quebec + Montreal deep education cluster

- [ ] 2.1 Create `dlt/commonwealth/can/qc/education/mees.py`
- [ ] 2.2 Create `dlt/commonwealth/can/qc/education/cssdm.py`
- [ ] 2.3 Create `dlt/commonwealth/can/qc/education/emsb.py`
- [ ] 2.4 Create `dlt/commonwealth/can/qc/education/lbpsb.py`
- [ ] 2.5 Create `dlt/commonwealth/can/qc/education/mcgill_universities.py`
- [ ] 2.6 Create 5 Dagster L1 defs.yaml for Quebec education

## 3. BAML extensions

- [ ] 3.1 Create `baml/commonwealth/can/quebec/education.baml` with
  `BilingualTextQuebec` + `ExtractQuebecEducationDocument`
- [ ] 3.2 Create `baml/commonwealth/can/quebec/montreal_education.baml`
  with `MontrealSchoolBoardRecord` + `ExtractMontrealSchoolBoardDocument`
- [ ] 3.3 Create `baml/commonwealth/can/_shared/province.baml` with
  the generic `ExtractCanadianProvinceDocument(province, language, text)`

## 4. CocoIndex v1 App

- [ ] 4.1 Create
  `cocoindex/quebec_montreal_education_embedding.py`
  (1 App for the 5 Quebec education sources + 4 Montreal
  universities)
- [ ] 4.2 Imports `from ._lifespan import shared_lifespan`
- [ ] 4.3 Embeds with `BAAI/bge-m3` (1024-d multilingual)
- [ ] 4.4 Partitions on `language ∈ ("fr", "en")` (FR default)
- [ ] 4.5 Create
  `orchestration/defs/3_model_lifecycle/cocoindex_v1/quebec_montreal_education/defs.yaml`

## 5. MotherDuck Dive + Flight

- [ ] 5.1 Create
  `motherduck/dives/quebec_montreal_curriculum_matrix.py`
  (bilingual cross-language matrix)
- [ ] 5.2 Create
  `motherduck/flights/canada_daily_sync_flight.py`
- [ ] 5.3 Append `canada_daily_sync_flight` to
  `motherduck/flights/config.yaml` (cron `0 6 * * *`)

## 6. Spec deltas

- [ ] 6.1 ADDED Requirements on `commonwealth-pipeline/spec.md` for
  the 13 provinces + the Quebec deep cluster
- [ ] 6.2 MODIFIED delta on `cross-region-pipeline/spec.md`
- [ ] 6.3 MODIFIED delta on `oideachais-pipeline/spec.md`

## 7. Validate

- [ ] 7.1 `openspec validate 2026-07-12-canada-provinces-quebec-montreal-pipeline-v1 --strict` passes
- [ ] 7.2 71 DLT sources (65 provincial + 6 Quebec/Montreal) AST-parse
- [ ] 7.3 All new defs.yaml files YAML-parse
- [ ] 7.4 `dg check yaml` passes
- [ ] 7.5 `mise run lint:skills` still passes (53/53)

## 8. Commit + push

- [ ] 8.1 Single commit with message
  `feat(commonwealth): Canada provinces (13) + Quebec/Montreal deep bilingual education cluster`
- [ ] 8.2 `git push origin main`
