# 2026-07-25-cocoindex-per-subject-dedup-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Change 1 (`nb-utils-ibis-first`) merged on `feat/iac-ify-arm1-oci-control-plane`
- [ ] Read the 7 per-subject CocoIndex Apps to confirm they share the
  R1–R4 v1 conformance pattern (per the audit)
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Create the parameterised flow

- [ ] Create `cocoindex_flows/subjects/lc_subject_embedding.py` (~250 LOC)
  - Single `coco.App(coco.AppConfig(name="lc_subject_embedding"))` at module scope
  - `@coco.function(lifespan=shared_lifespan)` decorator
  - `lancedb.mount_table_target(LANCE_DB, "oideachais.lc.<subject>.<level>_<lang>")`
  - Drives all 6 BIEP v1 LC subjects (mathematics, chemistry, geography,
    english, gaeilge, computer_science)
- [ ] Create `cocoindex_flows/subjects/lc_subject_config.yaml` with the 6 subject rows
- [ ] Verify the file passes `mise run cocoindex:v1-conformance`

## Stage 2 — Delete the 7 deprecated per-subject Apps

- [ ] DELETE `cocoindex_flows/subjects/chemistry_embedding.py`
- [ ] DELETE `cocoindex_flows/subjects/applied_mathematics_embedding.py`
- [ ] DELETE `cocoindex_flows/subjects/computer_science_embedding.py`
- [ ] DELETE `cocoindex_flows/subjects/english_embedding.py`
- [ ] DELETE `cocoindex_flows/subjects/geography_embedding.py`
- [ ] DELETE `cocoindex_flows/subjects/history_embedding.py`
- [ ] DELETE `cocoindex_flows/subjects/mathematics_embedding.py`
- [ ] KEEP `cocoindex_flows/subjects/cross_subject_competency_embedding.py`

## Stage 3 — Update Dagster defs

- [ ] Update `orchestration/defs/3_model_lifecycle/cocoindex_v1/lc_subjects/` defs
  to point at the new `lc_subject_embedding` app key
- [ ] Run `dg list code-locations` — confirm 2 apps registered

## Stage 4 — Update existing LanceDB producers

- [ ] Confirm the existing `oideachais.lc.<subject>.<level>_<lang>` tables
  are still populated by the new parameterised flow
- [ ] Document the migration in `docs/cocoindex/per-subject-dedup.md`

## Stage 5 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-07-25-cocoindex-per-subject-dedup-v1/specs/meaisinfhoghlaim-platform/spec.md`
  with the new `### Requirement: 8 per-subject CocoIndex Apps → 1 parameterised`
- [ ] Run `openspec validate 2026-07-25-cocoindex-per-subject-dedup-v1 --strict`
- [ ] Commit the change on a dedicated branch `openspec/2026-07-25-cocoindex-per-subject-dedup-v1`
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-25-cocoindex-per-subject-dedup-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol