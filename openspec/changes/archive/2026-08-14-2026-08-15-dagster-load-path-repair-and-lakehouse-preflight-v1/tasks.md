# Tasks: Dagster load-path repair + lakehouse preflight

This change ships in **5 phases**. Each phase is one PR. The order
matches the dependency chain — phases with `- [ ]` that depend on a
prior phase SHALL NOT start until the prior phase merges.

## Phase A — Openspec change scaffold (this PR)

- [ ] **A.1** Verify the canonical URI form is `infisical://dev-baile/<svc>/<key>` (no changes needed; this is a docs-only openspec change)
- [ ] **A.2** Inventory the 18 unreachable YAML files (`find orchestration/defs -name '*.yaml' -not -name 'defs.yaml' -not -name '*.planned'` + `1_ingestion/` walk)
- [ ] **A.3** Write `openspec/changes/2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1/{proposal.md, tasks.md}` (this file)
- [ ] **A.4** Write 3 spec delta files at `openspec/changes/2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1/specs/{dagster-5-layer-component-architecture, british-isles-education-pipeline-v3, infrastructure-stacks}/spec.md`
- [ ] **A.5** Run `openspec validate 2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1 --strict` and confirm exit 0

## Phase B — Dagster load-path repair (1 PR, depends on A)

- [ ] **B.1** Write `orchestration/defs/1_ingestion/_layer/defs.yaml` (DefsFolderComponent mount)
- [ ] **B.2** Write `orchestration/defs/1_ingestion/law/_layer/defs.yaml` (DefsFolderComponent mount)
- [ ] **B.3** Write `orchestration/defs/1_ingestion/law/ie/_layer/defs.yaml` (DefsFolderComponent mount)
- [ ] **B.4** Write `orchestration/defs/1_ingestion/curriculum/lc6/_layer/defs.yaml` (DefsFolderComponent mount)
- [ ] **B.5** Rename 6 L1 LC6 sources: `1_ingestion/curriculum/lc6/{english,geography,chemistry,gaeilge,mathematics,computer_science}.yaml` → `defs.yaml`
- [ ] **B.6** Rename 6 L2 grading sources: `2_materials/grading/{english,geography,chemistry,gaeilge,mathematics,computer_science}.yaml` → `defs.yaml`
- [ ] **B.7** Rename 1 L2 OCR ensemble source: `2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble.yaml` → `defs.yaml`
- [ ] **B.8** Write 4 L2 subdir mount points: `2_materials/embedding_pivot/_layer/defs.yaml`, `2_materials/england_education/comparators/_layer/defs.yaml`, `2_materials/england_education/aqa/_layer/defs.yaml`, `2_materials/lc_extraction/lc_subjects/_layer/defs.yaml`
- [ ] **B.9** Run `dg check yaml` and confirm exit 0 (or run `bun run scripts/ccc_v1_search.py` if dg is unavailable)

## Phase C — L3 deferred-asset gates (1 PR, depends on B)

- [ ] **C.1** Add `automation_condition: Manual()` default to `orchestration/components/kcg_cognify_component.py:KCGCognifyComponent`
- [ ] **C.2** Add `automation_condition: Manual()` default to `orchestration/components/kcg_cognify_component.py:CognifyIngestSensorsComponent`
- [ ] **C.3** Add `automation_condition: Manual()` default to `orchestration/components/layer3_model_lifecycle.py:CelticFederatedOcrComponent`
- [ ] **C.4** Verify that the 3 Component defaults are settable (Dagster 1.13+ allows `AutomationCondition` on the @asset or the asset definition)

## Phase D — Lakehouse preflight (1 PR, depends on B)

- [ ] **D.1** Write `scripts/lakehouse_preflight.py` (CLI probe — 5 endpoints + 12 databases + 8 buckets + cognify status)
- [ ] **D.2** Write `scripts/audit_lakehouse_buckets.py` (urllib3-based Garage admin API helper)
- [ ] **D.3** Write `notebooks/24_lakehouse_preflight.py` (marimo dashboard — same probes as a 5-column grid)
- [ ] **D.4** Add `mise run lakehouse:preflight` task to `mise.toml`
- [ ] **D.5** Run `python3 scripts/lakehouse_preflight.py` locally (expected: `skipped` for cognify since the cognify stack is intentionally not deployed on the dev box)

## Phase E — Validate + commit + push (1 PR, depends on B+C+D)

- [ ] **E.1** Run `openspec validate 2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1 --strict` — confirm exit 0
- [ ] **E.2** Run `mise run cic:stack-doctor --strict --check-grammar` — confirm zero mixed stacks
- [ ] **E.3** Run `mise run lint:registry --strict` — confirm zero hardcoded model strings
- [ ] **E.4** Run `mise run lint:drift-docs` — confirm the spec drift count decreases (or stays the same; the companion change will handle the pyproject drift)
- [ ] **E.5** Commit + push (40+ file diff over 3 logical commits: B renames + B/C/D new files + preflight bundle, OR one squash commit)
- [ ] **E.6** Open the companion change `2026-08-15-update-dagster-5-layer-spec-for-v7-flattening-v1` (separate openspec change for the pyproject drift)

## Phase F — Bring up the lakehouse + run BIEP M0 (post-archive, the operational phase)

- [ ] **F.1** Bring up the lakehouse: `cd bonneagar/stacks/lakehouse && docker compose -f compose.yaml -f sidecar.yaml up -d`
- [ ] **F.2** Run `mise run lakehouse:preflight` — confirm all 5 required endpoints are healthy
- [ ] **F.3** Bring up Dagster locally: `mise run dagster:dev`
- [ ] **F.4** Open the Dagster UI (http://localhost:3000) — confirm the Assets tab now shows:
  - 1_ingestion/law/ie/{piab,court_rules,legal_aid,courts,judgements} (5 new)
  - 1_ingestion/curriculum/lc6/{english,geography,chemistry,gaeilge,mathematics,computer_science} (6 new)
  - 2_materials/grading/{english,geography,chemistry,gaeilge,mathematics,computer_science} (6 new)
  - 2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble (1 new)
  - 3_model_lifecycle/cognify/* — marked manual-only badge
- [ ] **F.5** Run `mise run biep:v3:m0` — confirm the BIEP foundation unblock completes (lakehouse smoke + BAML codegen + registry seed + Lance namespace creation)
- [ ] **F.6** Run `mise run biep:v3:m1` — confirm the Ireland LC pipeline runs (12 cohorts, EN+GA; 3 asset checks pass)

## Phase F+ — Post-archive notes (after archive)

- [ ] Update `.agents/skills/dagster/SKILL.md` with a "Load-path convention" subsection (the `_layer/defs.yaml` + `defs.yaml` mounting rule)
- [ ] Update `.agents/skills/centralized-registry/SKILL.md` to mention the `automation_condition: manual` pattern for cognify-deferred assets
- [ ] Run `mise run sync:all` to refresh the sync-reports
