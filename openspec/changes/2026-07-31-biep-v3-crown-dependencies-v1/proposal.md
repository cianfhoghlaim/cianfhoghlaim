# 2026-07-31-biep-v3-crown-dependencies-v1

## Why

Phases 0-4 shipped the canonical registry + the Ireland, England, Scotland,
Wales, and Northern Ireland generic jurisdiction pipelines. This Phase 5
ships the final 3 Crown Dependencies:

- **Jersey** (States of Jersey Education Department — English GCSE +
  French Baccalauréat hybrid)
- **Guernsey** (States of Guernsey Education Services — English GCSE +
  A-Level)
- **Isle of Man** (Department of Education, Sport and Culture — English
  GCSE + A-Level)

Covers **~360 unique qualifications** (30 subjects × 4 levels × 3
jurisdictions). Completes the BIEP v3 8-jurisdiction rollout.

## What changes

### 1. Three new BAML subject-taxonomy files

- `baml_src/british_isles/jersey/education/subject_taxonomy.baml` —
  `JerseySubject` (~30 entries) + `JerseyLevel` enum (GCSE + A-Level
  + IB + French Baccalauréat)
- `baml_src/british_isles/guernsey/education/subject_taxonomy.baml` —
  `GuernseySubject` (~30 entries) + `GuernseyLevel` enum
- `baml_src/british_isles/isle_of_man/education/subject_taxonomy.baml` —
  `IsleOfManSubject` (~30 entries) + `IsleOfManLevel` enum

### 2. Generic Crown Dependencies DLT pipeline

`dlt/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py` —
factory function `crown_dependencies_jurisdiction_pipeline(jurisdiction)`.

### 3. Generic Crown Dependencies Dagster assets

`orchestration/defs/2_materials/crown_dependencies_education/generic_crown_dependencies_assets.py` —
3 generic assets + 1 asset_check. Each asset iterates over the 3
jurisdictions.

### 4. Extended registry loader

`dlt/british_isles/_cross/registry_loader.py` gets new
`load_jersey_subjects()` + `load_guernsey_subjects()` +
`load_isle_of_man_subjects()`.

## Dependencies

```yaml
Blocked by: 2026-07-30-biep-v3-sct-wls-ni-v1
Blocked by (soft): 2026-07-26-biep-v3-root-namespace-rename-v1
                  2026-07-27-biep-v3-canonical-registry-v1
                  2026-07-28-biep-v3-ireland-full-coverage-v1
                  2026-07-29-biep-v3-england-full-coverage-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-31-biep-v3-crown-dependencies-v1 --strict` passes
- `cd baml_src && uv run baml-cli generate` succeeds cleanly
- `python3 -c "from dlt.british_isles._cross.registry_loader import seed_registry; print(seed_registry())"`
  returns counts: `jersey >= 90, guernsey >= 90, isle_of_man >= 90`
- The companion notebook Tab 2 (Nation comparison) shows all 8
  jurisdictions with non-zero row counts
- `dg list assets | grep crown_dependencies_` lists 4 assets
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1/v2 LC spec; extended by Phases 2 + 3 + 4 + 5 to cover
  **all 8 British Isles jurisdictions**
- `openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/` — Phase 4
- `openspec/changes/2026-07-26-biep-v3-root-namespace-rename-v1/` — Phase 0
- `openspec/changes/2026-07-27-biep-v3-canonical-registry-v1/` — Phase 1
- `dlt/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py` —
  the new generic pipeline
- `orchestration/defs/2_materials/crown_dependencies_education/generic_crown_dependencies_assets.py` —
  the new generic Dagster assets
- `.agents/skills/dlt/SKILL.md` — the DLT conventions