# 2026-07-30-biep-v3-sct-wls-ni-v1

## Why

Phases 0-3 shipped the canonical registry + the Ireland + England
generic jurisdiction pipelines. This Phase 4 ships the parallel
generic pipelines for the remaining 3 "mainland" British Isles
jurisdictions:

- **Scotland** (SQA — Scottish Qualifications Authority)
- **Wales** (WJEC — Welsh Joint Education Committee)
- **Northern Ireland** (CCEA — Council for the Curriculum, Examinations
  and Assessment)

Covers **380 unique qualifications** (50 SQA × 3 + 80 WJEC × 2 + 35 CCEA × 2).

## What changes

### 1. Three new BAML subject-taxonomy files

- `baml_src/british_isles/scotland/education/subject_taxonomy.baml` —
  `SCQFSubject` (~50 entries) + `SCQFLevel` enum (National 5 + Higher +
  Advanced Higher)
- `baml_src/british_isles/wales/education/subject_taxonomy.baml` —
  `WJECSubject` (~80 entries) + `WJECLevel` enum (GCSE + A-Level + AS
  Level + Welsh Baccalaureate). Welsh-medium subjects flagged via the
  language field (cy = Cymraeg)
- `baml_src/british_isles/northern_ireland/education/subject_taxonomy.baml` —
  `CCEASubject` (~35 entries) + `CCEALevel` enum (GCSE + A-Level + AS
  Level). Includes `IRISH` + `IRISH_LANGUAGE` (the Gaeltacht overlay)

### 2. One generic multi-jurisdiction DLT pipeline

`dlt/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py` —
factory function `sct_wls_ni_jurisdiction_pipeline(jurisdiction)` that
selects one of the 3 jurisdictions. Reuses the same canonical
`ExtractUKQualSpec` BAML function from Phase 3.

### 3. One generic SCT + WLS + NI Dagster assets file

`orchestration/defs/2_materials/sct_wls_ni_education/generic_sct_wls_ni_assets.py` —
3 generic assets + 1 asset_check. The 3 assets each iterate over the
3 jurisdictions.

### 4. Extended registry loader

`dlt/british_isles/_cross/registry_loader.py` gets new
`load_scotland_subjects()` + `load_wales_subjects()` +
`load_northern_ireland_subjects()` functions (the 380-row seed).

## Dependencies

```yaml
Blocked by: 2026-07-29-biep-v3-england-full-coverage-v1
Blocked by (soft): 2026-07-26-biep-v3-root-namespace-rename-v1
                  2026-07-27-biep-v3-canonical-registry-v1
                  2026-07-28-biep-v3-ireland-full-coverage-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-30-biep-v3-sct-wls-ni-v1 --strict` passes
- `cd baml_src && uv run baml-cli generate` succeeds cleanly
- `python3 -c "from dlt.british_isles._cross.registry_loader import seed_registry; print(seed_registry())"`
  returns counts: `scotland >= 150`, `wales >= 160`, `northern_ireland >= 70`
- The companion notebook Tab 2 (Nation comparison) shows
  `scotland >= 150, wales >= 160, northern_ireland >= 70`
- `dg list assets | grep -E "sct_wls_ni_(scotland|wales|northern_ireland)"` lists 4 assets
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1/v2 LC spec; extended by Phases 2 + 3 + 4
- `openspec/changes/2026-07-29-biep-v3-england-full-coverage-v1/` — Phase 3
- `openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/` — Phase 5
- `baml_src/british_isles/england/education/curriculum_syllabus.baml` —
  the canonical `ExtractUKQualSpec` reused here
- `dlt/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py` —
  the new generic pipeline
- `.agents/skills/dlt/SKILL.md` — the DLT conventions