# Tasks: 2026-07-11-americas-california-pipeline-v1

## 1. Create the umbrella spec

- [ ] 1.1 Create `openspec/specs/americas-california-pipeline/spec.md`
- [ ] 1.2 Add the canonical DLT path contract Requirement
- [ ] 1.3 Add the California sub-state Requirement
- [ ] 1.4 Add the Brazil / Mexico / Venezuela national Requirement
- [ ] 1.5 Add the institutional OAS / PAHO / IDB / CELAC Requirement
- [ ] 1.6 Add the per-jurisdiction curriculum extraction Requirement
- [ ] 1.7 Add the CocoIndex v1 + Dagster + MotherDuck Requirement

## 2. Per-jurisdiction DLT sources

For each of the 5 jurisdictions (`us_ca`, `bra`, `mex`, `ven`,
`official`):

- [ ] 2.x.1 Create `dlt/americas/<jurisdiction>/__init__.py`
- [ ] 2.x.2 Create the 5 per-domain DLT source files (or 4 for the
  institutional layer)
- [ ] 2.x.3 Create the 5 per-domain Dagster defs.yaml

## 3. BAML extraction schemas

For each of the 4 national jurisdictions (`us_ca`, `bra`, `mex`,
`ven`):

- [ ] 3.x.1 Create `baml/americas/<jurisdiction>/education.baml`
- [ ] 3.x.2 Create `baml/americas/<jurisdiction>/law.baml`
- [ ] 3.x.3 Create `baml/americas/<jurisdiction>/medicine.baml`

Plus:

- [ ] 3.5 Create `baml/americas/_shared/jurisdiction.baml`
- [ ] 3.6 Create `baml/americas/__init__.baml`

## 4. CocoIndex v1 App

- [ ] 4.1 Create
  `cocoindex/americas_california_education_embedding.py`
- [ ] 4.2 Imports `from ._lifespan import shared_lifespan`
- [ ] 4.3 Embeds with `BAAI/bge-m3`
- [ ] 4.4 Create the corresponding Dagster L3 defs.yaml

## 5. MotherDuck Dive + Flight

- [ ] 5.1 Create
  `motherduck/dives/americas_state_standards_crosswalk.py`
- [ ] 5.2 Create
  `motherduck/flights/americas_daily_sync_flight.py`
- [ ] 5.3 Append the flight to `config.yaml`

## 6. Spec deltas

- [ ] 6.1 ADDED Requirements on `americas-california-pipeline/spec.md`
- [ ] 6.2 MODIFIED delta on `cross-region-pipeline/spec.md` adding a
  cross-reference
- [ ] 6.3 MODIFIED delta on `oideachais-pipeline/spec.md` adding a
  cross-reference

## 7. Validate

- [ ] 7.1 `openspec validate 2026-07-11-americas-california-pipeline-v1 --strict` passes
- [ ] 7.2 `dg check yaml` passes on the new defs.yaml
- [ ] 7.3 `mise run lint:skills` still passes

## 8. Commit + push

- [ ] 8.1 Single commit with message
  `feat(americas): Americas regional pipeline (US-CA / BRA / MEX / VEN + OAS/PAHO/IDB/CELAC)`
- [ ] 8.2 `git push origin main`
