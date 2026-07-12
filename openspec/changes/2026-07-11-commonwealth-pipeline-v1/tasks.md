# Tasks: 2026-07-11-commonwealth-pipeline-v1

## 1. Create the umbrella spec

- [ ] 1.1 Create `openspec/specs/commonwealth-pipeline/spec.md`
- [ ] 1.2 Add the canonical DLT path contract Requirement
- [ ] 1.3 Add the 5 pilot countries Requirement
- [ ] 1.4 Add the per-nation curriculum extraction Requirement
- [ ] 1.5 Add the per-nation law extraction Requirement
- [ ] 1.6 Add the per-nation medicine extraction Requirement
- [ ] 1.7 Add the CocoIndex v1 + Dagster + MotherDuck Requirement

## 2. Per-country DLT sources

For each of the 5 pilot countries (`aus`, `can`, `nzl`, `ind`, `zaf`):

- [ ] 2.x.1 Create `dlt/commonwealth/<iso3>/__init__.py`
- [ ] 2.x.2 Create the 5 per-domain DLT source files
- [ ] 2.x.3 Create the 5 per-domain Dagster defs.yaml

## 3. BAML extraction schemas

For each of the 5 pilot countries:

- [ ] 3.x.1 Create `baml/commonwealth/<iso3>/education.baml`
- [ ] 3.x.2 Create `baml/commonwealth/<iso3>/law.baml`
- [ ] 3.x.3 Create `baml/commonwealth/<iso3>/medicine.baml`

## 4. CocoIndex v1 App

- [ ] 4.1 Create `cianfhoghlaim/cocoindex/commonwealth_education_embedding.py`
- [ ] 4.2 Imports `from ._lifespan import shared_lifespan`
- [ ] 4.3 Embeds with `BAAI/bge-m3`
- [ ] 4.4 Create the corresponding Dagster L3 defs.yaml

## 5. MotherDuck Dive + Flight

- [ ] 5.1 Create `cianfhoghlaim/motherduck/dives/commonwealth_curriculum_matrix.py`
- [ ] 5.2 Create `cianfhoghlaim/motherduck/flights/commonwealth_daily_sync_flight.py`
- [ ] 5.3 Append the flight to `config.yaml`

## 6. Spec deltas

- [ ] 6.1 ADDED Requirements on `commonwealth-pipeline/spec.md`
- [ ] 6.2 MODIFIED delta on `cross-region-pipeline/spec.md` adding a
  cross-reference
- [ ] 6.3 MODIFIED delta on `oideachais-pipeline/spec.md` adding a
  cross-reference

## 7. Validate

- [ ] 7.1 `openspec validate 2026-07-11-commonwealth-pipeline-v1 --strict` passes
- [ ] 7.2 `dg check yaml` passes on the new defs.yaml
- [ ] 7.3 `mise run lint:skills` still passes

## 8. Commit + push

- [ ] 8.1 Single commit with message
  `feat(commonwealth): Commonwealth of Nations pipeline (AUS / CAN / NZL / IND / ZAF)`
- [ ] 8.2 `git push origin main`
