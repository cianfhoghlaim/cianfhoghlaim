# 2026-07-28-biep-v3-ireland-full-coverage-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Phases 0 + 1 merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Generic Ireland DLT pipeline

- [ ] Create `dlt/british_isles/ireland/education/ireland_jurisdiction_pipeline.py`
  with `ireland_jurisdiction_pipeline()` factory
- [ ] Test: `python3 -c "from dlt.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline; p, s = ireland_jurisdiction_pipeline(); print(p, s)"`
  (assumes the lakehouse stack is running)

## Stage 2 — Generic Ireland Dagster assets

- [ ] Create `orchestration/defs/2_materials/ireland_education/__init__.py`
- [ ] Create `orchestration/defs/2_materials/ireland_education/generic_ireland_assets.py`
  with 3 generic assets + 1 asset_check
- [ ] Test: `dg list assets | grep ireland_` lists the 4 new entries

## Stage 3 — Extend registry loader

- [ ] Update `dlt/british_isles/_cross/registry_loader.py:load_ireland_subjects()`
  to return the FULL 134+ row seed (64 LC + 18 JC + 16 short courses + 36 CBAs)
- [ ] Update `load_england_subjects()` to return the FULL Phase 3 seed
  (43 GCSE + 49 A-Level × 3 boards) — this is forward-loaded for Phase 3
- [ ] Test: `python3 -c "from dlt.british_isles._cross.registry_loader import seed_registry; print(seed_registry())"`
  returns counts >= 134 for Ireland

## Stage 4 — Companion notebook verification

- [ ] Run `marimo edit notebooks/18_cianfhoghlaim_subject_registry.py`
  and verify Tab 2 (Nation comparison) shows the new Ireland row count

## Stage 5 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-07-28-biep-v3-ireland-full-coverage-v1/specs/british-isles-education-pipeline/spec.md`
- [ ] Run `openspec validate 2026-07-28-biep-v3-ireland-full-coverage-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-28-biep-v3-ireland-full-coverage-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/cianfhoghlaim-ireland-pipeline.md` with the migration notes
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol