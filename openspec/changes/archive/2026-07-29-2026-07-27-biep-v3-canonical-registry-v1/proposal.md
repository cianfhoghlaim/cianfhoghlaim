## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

# 2026-07-27-biep-v3-canonical-registry-v1

## Why

The BIEP v3 batch (per the 2026-07-26 refactor decision) requires a
canonical British Isles subject registry that:

1. Lives in DuckDB (the same lakehouse as the rest of the platform)
2. Drives **all** 8 jurisdiction pipelines (Ireland → England →
   Scotland/Wales/NI → Crown Dependencies) via one shared schema
3. Replaces the 6 drift-prone per-jurisdiction enums (`LeavingCertSubject`
   64 + `JuniorCycleSubjectSlug` 18 + `JuniorCycleSubject` 20 + `JCSubject`
   24 + `GCSEAQASubject` 43 + `ALevelAQASubject` 49)
4. Is rendered + editable via a 4-tab companion notebook
5. Carries cross-jurisdiction bridges (e.g. `gaeilge` ↔ `irish` ↔ N/A)

Today the codebase has 6 separate subject enums that disagree in size
(64 vs 18 vs 20 vs 24 vs 43 vs 49) and have no canonical mapping. The
BIEP v3 plan unifies them into one registry.

## What changes

### 1. New BAML schema

`baml_src/british_isles/_cross/biep_subject.baml` — the canonical
`BritishIslesSubject` class + 8 enums (Jurisdiction, EducationalStage,
AwardingBody, QualificationLevel, Language, CrossJurisdictionConcept,
RegistrySource, RegistryStatus) + 2 query functions.

### 2. New DuckDB migration

`dlt/common/migrations/2026-07-27-cianfhoghlaim-subject-registry.sql`
creates 3 tables:
- `cianfhoghlaim.education._registry.subjects`
- `cianfhoghlaim.education._registry.jurisdiction_overrides`
- `cianfhoghlaim.education._registry.cross_jurisdiction_bridges`

Seeds 12 cross-jurisdiction bridges (the 10 core concepts + Irish
Language + Business Studies).

### 3. New Python API

- `dlt/british_isles/_cross/registry_api.py` — pure-Python ibis-first
  API: `query_by_jurisdiction()`, `query_by_concept()`,
  `query_by_stage()`, `query_cross_jurisdiction_bridges()`, `insert_subject()`
- `dlt/british_isles/_cross/registry_loader.py` — official-source loaders
  + `seed_registry()` + `apply_migration()`

### 4. New 4-tab companion notebook

`notebooks/18_cianfhoghlaim_subject_registry.py` — 4 tabs:
1. Format doc (BAML schema + DuckDB table descriptions + canonical
   namespace shape)
2. Nation comparison (subject count by jurisdiction)
3. Bridge explorer (find a concept in any jurisdiction)
4. Drift detector (compare live registry vs official sites via
   ChangeDetection.io)

### 5. Spec delta

`openspec/specs/cross-region-pipeline/spec.md` — add a new requirement
mandating the canonical registry shape + the `cianfhoghlaim.education.<jurisdiction>.<stage>[.<board>].<subject>` namespace.

## Dependencies

```yaml
Blocked by: 2026-07-26-biep-v3-root-namespace-rename-v1
Blocked by (soft): none
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-27-biep-v3-canonical-registry-v1 --strict` passes
- `cd baml_src && uv run baml-cli generate` succeeds cleanly
- The 3 DuckDB tables exist after `apply_migration()` is run
- The companion notebook opens with all 4 tabs (format doc + nation
  comparison + bridge explorer + drift detector)
- `mise run lint:skills` still passes (53/53)
- The 12 seeded cross-jurisdiction bridges are queryable via
  `query_cross_jurisdiction_bridges()`
- `dg check yaml` passes
- Push target: `origin/main`

## Cross-references

- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract that gains the registry requirement
- `openspec/changes/2026-07-26-biep-v3-root-namespace-rename-v1/` — the
  prerequisite `oideachais` → `cianfhoghlaim` rename
- `openspec/changes/2026-07-28-biep-v3-ireland-full-coverage-v1/` —
  Phase 2, the first consumer of this registry
- `.agents/skills/dagster/SKILL.md` — the 5-layer component convention
  that the BIEP v3 jurisdiction pipelines will use
- `.agents/skills/ibis/SKILL.md` — the ibis-first contract that the
  registry API follows
- `.agents/skills/marimo/SKILL.md` — the marimo convention that the
  companion notebook follows