# Tasks: 2026-07-15-eu-pilot-upgrade-v1

## 1. OpenSpec scaffolding

- [ ] 1.1 Create `openspec/changes/2026-07-15-eu-pilot-upgrade-v1/`
- [ ] 1.2 Write `proposal.md` + `tasks.md` + spec deltas
- [ ] 1.3 `openspec validate 2026-07-15-eu-pilot-upgrade-v1 --strict` passes

## 2. Ukraine per-subject depth (7 subjects)

- [ ] 2.1 Create `dlt/european_nations/ukr/education/subjects/__init__.py`
- [ ] 2.2 Create 7 per-subject DLT sources:
  - mathematics.py, chemistry.py, biology.py, physics.py, language.py, computing_science.py, ukrainian_language.py
- [ ] 2.3 Update `dlt/european_nations/ukr/education/__init__.py`
- [ ] 2.4 Create 7 Dagster L1 defs under
  `orchestration/defs/1_ingestion/european_nations/ukr/education/subjects/<subject>/defs.yaml`
- [ ] 2.5 Create 1 L3 def at
  `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_ukr_education/defs.yaml`
- [ ] 2.6 Create per-subject CocoIndex v1 App or extend the existing one
- [ ] 2.7 Update BAML files (education/law/medicine) with per-subject extraction functions
- [ ] 2.8 Create 7 cache fixtures

## 3. The 5 other EU pilots (FRA / DEU / POL / ESP / ITA)

For each country `<iso3>`:

- [ ] 3.<iso3>.1 Create `dlt/european_nations/<iso3>/education/subjects/__init__.py`
- [ ] 3.<iso3>.2 Create 6 per-subject DLT sources
- [ ] 3.<iso3>.3 Update `dlt/european_nations/<iso3>/education/__init__.py`
- [ ] 3.<iso3>.4 Create 6 L1 Dagster defs
- [ ] 3.<iso3>.5 Create 1 L3 CocoIndex v1 def
- [ ] 3.<iso3>.6 Create per-subject CocoIndex v1 App
- [ ] 3.<iso3>.7 Update BAML with per-subject extraction functions
- [ ] 3.<iso3>.8 Create 6 cache fixtures

## 4. British Isles fill-in (WLS / EN / NI)

For each of WLS / EN / NI:

- [ ] 4.<nation>.1 Create `dlt/british_isles/<nation>/education/subjects/physics/physics.py`
- [ ] 4.<nation>.2 Create `dlt/british_isles/<nation>/education/subjects/physics/__init__.py`
- [ ] 4.<nation>.3 Create `dlt/british_isles/<nation>/education/subjects/biology/biology.py`
- [ ] 4.<nation>.4 Create `dlt/british_isles/<nation>/education/subjects/biology/__init__.py`
- [ ] 4.<nation>.5 Create 2 L1 Dagster defs (physics + biology)
- [ ] 4.<nation>.6 Create 2 cache fixtures

## 5. Spec deltas

- [ ] 5.1 MODIFIED delta on `european-nations-ukraine-pipeline/spec.md`
  declaring the Ukraine per-subject depth (7 subjects including
  ukrainian_language)
- [ ] 5.2 MODIFIED delta on `british-isles-education-pipeline/spec.md`
  declaring the per-subject completeness contract (physics +
  biology required for WLS/EN/NI)
- [ ] 5.3 MODIFIED delta on `oideachais-pipeline/spec.md`
  cross-referencing the change

## 6. Validate

- [ ] 6.1 `openspec validate 2026-07-15-eu-pilot-upgrade-v1 --strict` passes
- [ ] 6.2 All Python files AST-parse
- [ ] 6.3 All Dagster defs.yaml YAML-parse
- [ ] 6.4 All BAML files parse
- [ ] 6.5 `dg check yaml` passes
- [ ] 6.6 `mise run lint:skills` still passes (53/53)

## 7. Commit + push

- [ ] 7.1 Single commit with message
  `feat(eu-pilot): per-subject depth upgrade — Ukraine (7 subjects incl. ukrainian_language) + FRA/DEU/POL/ESP/ITA + WLS/EN/NI physics+biology fill-in`
- [ ] 7.2 `git push origin pick-4-biep-v1`
