# 2026-07-30-biep-v3-sct-wls-ni-v1 (REVISED — Phase A merge complete)

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

## Phase A merge (2026-08-13 follow-up)

Per the **2026-08-13-biep-v3-systematic-download-ireland-england-v1**
change, the 3 deferred jurisdictions have been **promoted to
proper per-jurisdiction directories** (replacing the original
multi-jurisdiction placeholder approach). The original
`sct_wls_ni/education/` directory is now a **re-export shim** that
delegates to the per-jurisdiction proper directories:

| Old (this change) | New (per-jurisdiction) |
|:--|:--|
| `dlt_sources/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py` | (re-export shim — preserved for backward compat) |
| | `dlt_sources/british_isles/scotland/education/scotland_jurisdiction_pipeline.py` (NEW canonical home) |
| | `dlt_sources/british_isles/wales/education/wales_jurisdiction_pipeline.py` (NEW canonical home) |
| | `dlt_sources/british_isles/northern_ireland/education/northern_ireland_jurisdiction_pipeline.py` (NEW canonical home) |

The per-jurisdiction proper directories also got full Dagster assets
(per the Phase B follow-up) + per-jurisdiction BAML Extract*
functions (per the Phase C follow-up).

## What was changed (this change)

### 1. Three new BAML subject-taxonomy files (deferred from this change to Phase C)

- `baml_src/british_isles/scotland/education/subject_taxonomy.baml` —
  `SCQFSubject` (~50 entries) + `SCQFLevel` enum (National 5 + Higher +
  Advanced Higher) + `ExtractScotlandSyllabus` BAML function
- `baml_src/british_isles/wales/education/subject_taxonomy.baml` —
  `WJECSubject` (~80 entries) + `WJECLevel` enum (GCSE + A-Level + AS
  Level + Welsh Baccalaureate) + `ExtractWalesSyllabus` BAML function.
  Welsh-medium subjects flagged via the language field (cy = Cymraeg)
- `baml_src/british_isles/northern_ireland/education/subject_taxonomy.baml` —
  `CCEASubject` (~35 entries) + `CCEALevel` enum (GCSE + A-Level + AS
  Level) + `ExtractNIExamPaper` BAML function. Includes `IRISH` +
  `IRISH_LANGUAGE` (the Gaeltacht overlay)

### 2. The 3 generic per-jurisdiction DLT pipelines (now in the per-jurisdiction proper directories)

- `dlt_sources/british_isles/scotland/education/scotland_jurisdiction_pipeline.py` —
  `ScotlandJurisdictionPipeline` (150 cohorts: 50 SCQF × 3 levels)
- `dlt_sources/british_isles/wales/education/wales_jurisdiction_pipeline.py` —
  `WalesJurisdictionPipeline` (160 cohorts: 80 WJEC × 2 levels)
- `dlt_sources/british_isles/northern_ireland/education/northern_ireland_jurisdiction_pipeline.py` —
  `NorthernIrelandJurisdictionPipeline` (70 cohorts: 35 CCEA × 2 levels)

The original `dlt_sources/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py`
is now a **re-export shim** that delegates to the per-jurisdiction
proper directories (preserves backward compat with the BIEP v3
orchestration assets that import from it).

### 3. The 3 generic per-jurisdiction Dagster assets files (Phase B follow-up)

- `orchestration/defs/2_materials/scotland_education/scotland_assets.py` —
  3 generic Scotland assets + 3 asset checks + 50 per-subject backfill jobs
- `orchestration/defs/2_materials/wales_education/wales_assets.py` —
  3 generic Wales assets + 3 asset checks + 80 per-subject backfill jobs
- `orchestration/defs/2_materials/northern_ireland_education/northern_ireland_assets.py` —
  3 generic NI assets + 3 asset checks + 35 per-subject backfill jobs

### 4. Extended registry loader (this change)

`dlt/british_isles/_cross/registry_loader.py` gets new
`load_scotland_subjects()` + `load_wales_subjects()` +
`load_northern_ireland_subjects()` functions (the 380-row seed).
Updated in the Phase A follow-up to use per-jurisdiction BAML functions
(`b.ExtractScotlandSyllabus` / `b.ExtractWalesSyllabus` /
`b.ExtractNIExamPaper`).

## Dependencies

```yaml
Blocked by: 2026-07-29-biep-v3-england-full-coverage-v1
Blocked by (soft): 2026-07-26-biep-v3-root-namespace-rename-v1
                  2026-07-27-biep-v3-canonical-registry-v1
                  2026-07-28-biep-v3-ireland-full-coverage-v1
                  2026-08-13-biep-v3-systematic-download-ireland-england-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-30-biep-v3-sct-wls-ni-v1 --strict` passes
- `cd baml_src && uv run baml-cli generate` succeeds cleanly
- `python3 -c "from dlt.british_isles._cross.registry_loader import seed_registry; print(seed_registry())"`
  returns counts: `scotland >= 150`, `wales >= 160`, `northern_ireland >= 70`
- The companion notebook Tab 2 (Nation comparison) shows
  `scotland >= 150, wales >= 160, northern_ireland >= 70`
- `dg list assets | grep -E "scotland_(documents_ingested|extractions|embeddings)"` lists 3 assets
- `dg list assets | grep -E "wales_(documents_ingested|extractions|embeddings)"` lists 3 assets
- `dg list assets | grep -E "northern_ireland_(documents_ingested|extractions|embeddings)"` lists 3 assets
- `dg list assets | grep -E "sct_wls_ni_(scotland|wales|northern_ireland)_(documents|extractions|embeddings)"` lists 9 assets
  (the old re-export shim names still work)
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1/v2 LC spec; extended by Phases 2 + 3 + 4
- `openspec/changes/2026-07-29-biep-v3-england-full-coverage-v1/` — Phase 3
- `openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/` — Phase 5
- `openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/` —
  the umbrella change that drove the Phase A merge
- `baml_src/british_isles/england/education/curriculum_syllabus.baml` —
  the canonical `ExtractUKQualSpec` reused here
- `baml_src/british_isles/scotland/education/subject_taxonomy.baml` —
  the per-jurisdiction `ExtractScotlandSyllabus` (new in Phase C)
- `dlt_sources/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py` —
  the re-export shim (preserved for backward compat)
- `dlt_sources/british_isles/scotland/education/scotland_jurisdiction_pipeline.py` —
  the canonical per-jurisdiction home (new in Phase A)
- `orchestration/defs/2_materials/scotland_education/scotland_assets.py` —
  the canonical per-jurisdiction Dagster assets (new in Phase B)
- `.agents/skills/dlt/SKILL.md` — the DLT conventions
