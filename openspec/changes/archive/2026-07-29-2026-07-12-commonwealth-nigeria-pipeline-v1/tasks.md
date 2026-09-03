# Tasks: 2026-07-12-commonwealth-nigeria-pipeline-v1

## 1. Federal tier (10 DLT sources)

- [ ] 1.1 Create `dlt/commonwealth/nga/__init__.py`
- [ ] 1.2 Create `dlt/commonwealth/nga/education/__init__.py`
- [ ] 1.3 Create `dlt/commonwealth/nga/education/federal_ministry_of_education.py`
- [ ] 1.4 Create `dlt/commonwealth/nga/education/nuc.py`
- [ ] 1.5 Create `dlt/commonwealth/nga/education/jamb.py`
- [ ] 1.6 Create `dlt/commonwealth/nga/education/nabteb.py`
- [ ] 1.7 Create `dlt/commonwealth/nga/education/nbc.py`
- [ ] 1.8 Create `dlt/commonwealth/nga/medicine/__init__.py`
- [ ] 1.9 Create `dlt/commonwealth/nga/medicine/fmhds.py`
- [ ] 1.10 Create `dlt/commonwealth/nga/medicine/ncdc.py`
- [ ] 1.11 Create `dlt/commonwealth/nga/medicine/nphcda.py`
- [ ] 1.12 Create `dlt/commonwealth/nga/law/__init__.py`
- [ ] 1.13 Create `dlt/commonwealth/nga/law/nass.py` (routed via
  `nigerialii.org` not `nigeria-law.org` per Phase 1 URL fix)
- [ ] 1.14 Create `dlt/commonwealth/nga/government/__init__.py`
- [ ] 1.15 Create `dlt/commonwealth/nga/government/customs.py`
- [ ] 1.16 Create 10 Dagster L1 defs.yaml files

## 2. State tier (37 sub-units × 5 domains = 185 DLT sources)

For each of 36 states + 1 FCT:

- [ ] 2.x Create `dlt/commonwealth/nga/states/<state_slug>/__init__.py`
- [ ] 2.x.1 Create the 5 per-domain DLT sources
- [ ] 2.x.2 Create the 5 per-domain Dagster L1 defs

## 3. BAML extensions

- [ ] 3.1 Create `baml/commonwealth/nga/federal.baml` with
  `ExtractNigerianFederalCurriculumSpec(federal_institution, language, text)`
- [ ] 3.2 Create `baml/commonwealth/nga/state.baml` with
  `ExtractNigerianStateCurriculumSpec(state_code, language, text)`
- [ ] 3.3 Create `baml/commonwealth/nga/_shared/nigeria_states.baml`
  with the 37-state code registry

## 4. CocoIndex v1 App

- [ ] 4.1 Create
  `cocoindex/nigeria_education_embedding.py`
- [ ] 4.2 Imports `from ._lifespan import shared_lifespan`
- [ ] 4.3 Embeds with `BAAI/bge-m3` (1024-d)
- [ ] 4.4 Partitions on `state_code + language`
- [ ] 4.5 Create the L3 defs.yaml

## 5. MotherDuck Dive + Flight

- [ ] 5.1 Create
  `motherduck/dives/nigeria_state_curriculum_matrix.py`
- [ ] 5.2 Create
  `motherduck/flights/nigeria_daily_sync_flight.py`
- [ ] 5.3 Append `nigeria_daily_sync_flight` to the flights
  `config.yaml` (cron `0 6 * * *`)

## 6. Spec deltas

- [ ] 6.1 ADDED Requirements on `commonwealth-pipeline/spec.md`
- [ ] 6.2 MODIFIED delta on `cross-region-pipeline/spec.md`
- [ ] 6.3 MODIFIED delta on `oideachais-pipeline/spec.md`

## 7. Validate

- [ ] 7.1 `openspec validate 2026-07-12-commonwealth-nigeria-pipeline-v1 --strict` passes
- [ ] 7.2 All 195 DLT sources AST-parse
- [ ] 7.3 All new defs.yaml YAML-parse
- [ ] 7.4 `dg check yaml` passes
- [ ] 7.5 `mise run lint:skills` still passes (53/53)

## 8. Commit + push

- [ ] 8.1 Single commit with message
  `feat(commonwealth): Nigeria pipeline — federal (10 sources) + 36 states + FCT (185 sources)`
- [ ] 8.2 `git push origin main`
