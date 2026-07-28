# 2026-07-31-biep-v3-crown-dependencies-v1 (REVISED — Phase A merge complete)

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

## Phase A merge (2026-08-13 follow-up)

Per the **2026-08-13-biep-v3-systematic-download-ireland-england-v1**
change, the 3 Crown Dependencies have been **promoted to proper
per-jurisdiction directories** (replacing the original multi-jurisdiction
placeholder approach). The original
`crown_dependencies/education/` directory is now a **re-export shim**
that delegates to the per-jurisdiction proper directories:

| Old (this change) | New (per-jurisdiction) |
|:--|:--|
| `dlt_sources/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py` | (re-export shim — preserved for backward compat) |
| | `dlt_sources/british_isles/jersey/education/jersey_jurisdiction_pipeline.py` (NEW canonical home) |
| | `dlt_sources/british_isles/guernsey/education/guernsey_jurisdiction_pipeline.py` (NEW canonical home) |
| | `dlt_sources/british_isles/isle_of_man/education/isle_of_man_jurisdiction_pipeline.py` (NEW canonical home) |

The per-jurisdiction proper directories also got full Dagster assets
(per the Phase B follow-up) + per-jurisdiction BAML Extract*
functions (per the Phase C follow-up).

## What was changed (this change)

### 1. Three new BAML subject-taxonomy files (deferred from this change to Phase C)

- `baml_src/british_isles/jersey/education/subject_taxonomy.baml` —
  `JerseySubject` (~30 entries) + `JerseyLevel` enum (GCSE + A-Level
  + IB + French Baccalauréat) + `ExtractJerseySyllabus` BAML function
- `baml_src/british_isles/guernsey/education/subject_taxonomy.baml` —
  `GuernseySubject` (~30 entries) + `GuernseyLevel` enum + `ExtractGuernseySyllabus` BAML function
- `baml_src/british_isles/isle_of_man/education/subject_taxonomy.baml` —
  `IsleOfManSubject` (~30 entries) + `IsleOfManLevel` enum + `ExtractIsleOfManSyllabus` BAML function

### 2. The 3 generic per-jurisdiction DLT pipelines (now in the per-jurisdiction proper directories)

- `dlt_sources/british_isles/jersey/education/jersey_jurisdiction_pipeline.py` —
  `JerseyJurisdictionPipeline` (120 cohorts: 30 × 4 levels)
- `dlt_sources/british_isles/guernsey/education/guernsey_jurisdiction_pipeline.py` —
  `GuernseyJurisdictionPipeline` (120 cohorts: 30 × 4 levels)
- `dlt_sources/british_isles/isle_of_man/education/isle_of_man_jurisdiction_pipeline.py` —
  `IsleOfManJurisdictionPipeline` (120 cohorts: 30 × 4 levels)

The original
`dlt_sources/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py`
is now a **re-export shim** that delegates to the per-jurisdiction
proper directories (preserves backward compat with the BIEP v3
orchestration assets that import from it).

### 3. The 3 generic per-jurisdiction Dagster assets files (Phase B follow-up)

- `orchestration/defs/2_materials/jersey_education/jersey_assets.py` —
  3 generic Jersey assets + 3 asset checks + 30 per-subject backfill jobs
- `orchestration/defs/2_materials/guernsey_education/guernsey_assets.py` —
  3 generic Guernsey assets + 3 asset checks + 30 per-subject backfill jobs
- `orchestration/defs/2_materials/isle_of_man_education/isle_of_man_assets.py` —
  3 generic IoM assets + 3 asset checks + 30 per-subject backfill jobs

### 4. Extended registry loader (this change + Phase A follow-up)

`dlt/british_isles/_cross/registry_loader.py` gets new
`load_jersey_subjects()` + `load_guernsey_subjects()` +
`load_isle_of_man_subjects()` functions (the 360-row seed).
Updated in the Phase A follow-up to use per-jurisdiction BAML functions
(`b.ExtractJerseySyllabus` / `b.ExtractGuernseySyllabus` /
`b.ExtractIsleOfManSyllabus`).

## Dependencies

```yaml
Blocked by: 2026-07-30-biep-v3-sct-wls-ni-v1
Blocked by (soft): 2026-07-26-biep-v3-root-namespace-rename-v1
                  2026-07-27-biep-v3-canonical-registry-v1
                  2026-07-28-biep-v3-ireland-full-coverage-v1
                  2026-07-29-biep-v3-england-full-coverage-v1
                  2026-08-13-biep-v3-systematic-download-ireland-england-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-31-biep-v3-crown-dependencies-v1 --strict` passes
- `cd baml_src && uv run baml-cli generate` succeeds cleanly
- `python3 -c "from dlt.british_isles._cross.registry_loader import seed_registry; print(seed_registry())"`
  returns counts: `jersey >= 120`, `guernsey >= 120`, `isle_of_man >= 120`
- The companion notebook Tab 3 (Crown Dependencies comparison) shows
  `jersey >= 120, guernsey >= 120, isle_of_man >= 120`
- `dg list assets | grep -E "jersey_(documents_ingested|extractions|embeddings)"` lists 3 assets
- `dg list assets | grep -E "guernsey_(documents_ingested|extractions|embeddings)"` lists 3 assets
- `dg list assets | grep -E "isle_of_man_(documents_ingested|extractions|embeddings)"` lists 3 assets
- `dg list assets | grep -E "crown_(jersey|guernsey|isle_of_man)_(documents|extractions|embeddings)"` lists 9 assets
  (the old re-export shim names still work)
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1/v2 LC spec; extended by Phases 2 + 3 + 4 + 5
- `openspec/changes/2026-07-29-biep-v3-england-full-coverage-v1/` — Phase 3
- `openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/` — Phase 4 (also revised in Phase A)
- `openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/` —
  the umbrella change that drove the Phase A merge
- `baml_src/british_isles/england/education/curriculum_syllabus.baml` —
  the canonical `ExtractUKQualSpec` (reused for England A-Level / GCSE)
- `baml_src/british_isles/jersey/education/subject_taxonomy.baml` —
  the per-jurisdiction `ExtractJerseySyllabus` (new in Phase C)
- `dlt_sources/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py` —
  the re-export shim (preserved for backward compat)
- `dlt_sources/british_isles/jersey/education/jersey_jurisdiction_pipeline.py` —
  the canonical per-jurisdiction home (new in Phase A)
- `orchestration/defs/2_materials/jersey_education/jersey_assets.py` —
  the canonical per-jurisdiction Dagster assets (new in Phase B)
- `.agents/skills/dlt/SKILL.md` — the DLT conventions
