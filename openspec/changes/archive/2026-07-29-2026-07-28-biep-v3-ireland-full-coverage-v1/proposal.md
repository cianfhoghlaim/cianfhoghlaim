## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

# 2026-07-28-biep-v3-ireland-full-coverage-v1

## Why

Phase 1 shipped the canonical British Isles subject registry. This
Phase 2 wires Ireland (the first jurisdiction) onto the registry:

- Replaces ~100 per-subject DLT source files with **1 generic pipeline**
- Replaces per-subject Dagster assets with **3 generic assets**
- Loads **134+ Ireland cohorts** (64 LC + 18 JC + 16 short courses + 36 CBAs)
  into the registry via `load_ireland_subjects()`
- Writes the per-subject per-language cohorts to the canonical
  `cianfhoghlaim.education.ireland.<stage>.<subject>[.<variant>]` namespace

## What changes

### 1. New generic Ireland DLT pipeline

`dlt/british_isles/ireland/education/ireland_jurisdiction_pipeline.py` —
reads the registry, emits 134+ Ireland cohorts as a single
`ireland_ireland_subjects` DLT resource, writes to the canonical
`cianfhoghlaim.education.ireland.*` namespace.

### 2. New generic Ireland Dagster assets

`orchestration/defs/2_materials/ireland_education/generic_ireland_assets.py`
— 3 generic assets (1 ingestion + 1 extraction + 1 embedding) backed
by the registry. Follows the 5-layer group_name convention:

- `1_ingestion/education/ireland/documents` — `ireland_documents_ingested`
- `2_materials/education/ireland/extractions` — `ireland_extractions`
- `3_model_lifecycle/education/ireland/embeddings` — `ireland_embeddings`

Plus 1 asset_check: `ireland_extractions_ragas_check` (ragas_score >= 0.70).

### 3. Registry loader extended

`dlt/british_isles/_cross/registry_loader.py:load_ireland_subjects()`
returns the FULL 134+ row seed (64 LC × 3 levels × 2 langs + 18 JC ×
3 years × 2 langs + 16 short courses + 36 CBAs) instead of the Phase 1
4-subject baseline.

### 4. No per-subject DLT files created

The generic Ireland pipeline replaces all the per-subject
`dlt/british_isles/ireland/education/{ncca_<subject>,junior_cycle_subjects/<subject>_<lang>,junior_cycle_short_courses/<course>,junior_cycle_cbas/_factory,subjects/subjects/senior_cycle,leaving_cert}.py`
files. The old files remain in place for now (deprecated); they will be
deleted in a future cleanup change.

## Dependencies

```yaml
Blocked by: 2026-07-27-biep-v3-canonical-registry-v1
Blocked by (soft): 2026-07-26-biep-v3-root-namespace-rename-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-28-biep-v3-ireland-full-coverage-v1 --strict` passes
- `python3 -c "from dlt.british_isles._cross.registry_loader import seed_registry; print(seed_registry())"`
  returns counts >= 134 for Ireland
- The companion notebook `notebooks/18_cianfhoghlaim_subject_registry.py`
  shows 134+ rows for `jurisdiction='ireland'`
- `dg list assets | grep ireland_` lists 4 assets (3 + 1 check)
- `mise run lint:skills` still passes (53/53)
- `baml-cli generate` succeeds cleanly
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the parent BIEP v1/v2 LC spec; extended by Phase 2 to cover all 134+ Ireland cohorts
- `openspec/changes/2026-07-27-biep-v3-canonical-registry-v1/` —
  Phase 1, the registry Phase 2 reads from
- `openspec/changes/2026-07-29-biep-v3-england-full-coverage-v1/` —
  Phase 3, the next consumer of the same generic pipeline pattern
- `openspec/specs/cross-region-pipeline/spec.md` — the umbrella contract
  that the canonical registry follows
- `.agents/skills/dlt/SKILL.md` — the DLT conventions
- `.agents/skills/dagster/SKILL.md` — the 5-layer group_name convention