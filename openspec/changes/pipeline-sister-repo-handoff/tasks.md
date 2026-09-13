# Tasks: pipeline-sister-repo-handoff

## 1. Sister-handoff inventory + canonical surface (per `cianchosaint-handoff-v1` ✓ Complete)

- [x] **H1.1** Verify the filesystem inventory of all 6 sister repos (cianchosaint + ciandlithe + ciancheiltis + tuatha + gemini-hackathon + biiep-hackathon-public)
- [x] **H1.2** Write `openspec/specs/sister-shared/spec.md` (5 Requirements)
- [x] **H1.3** Write `openspec/specs/cianfhoghlaim/spec.md` (4 Requirements)
- [x] **H1.4** Cross-repo refactor: rename `kcg_subapp_manifest.yaml` → `cianfhoghlaim_subapp_manifest.yaml`
- [x] **H1.5** Cross-repo refactor: replace `kings_college_galway/kcg` references with `cianfhoghlaim`
- [x] **H1.6** Cleanup residuals in `bonneagar/stacks/`, `leabharlann/`, `openspec/plans/`
- [x] **H1.7** Archive `cianchosaint-handoff-v1` under this umbrella

## 2. cianchosaint 5-layer defs mirror (per `2026-09-13-cianchosaint-orchestration-init-v1`)

- [x] **H2.1** Mirror the cianfhoghlaim `Definitions` loader to `cianchosaint/orchestration/defs/__init__.py`
- [x] **H2.2** Create the 5 empty layer namespaces in `cianchosaint/orchestration/defs/`
  - [x] `1_ingestion/`
  - [x] `2_materials/`
  - [x] `3_model_lifecycle/`
  - [x] `4_asset_generation/`
  - [x] `5_agent_ops/`
- [x] **H2.3** Relocate `licence_enforcement_sensor.py` from the old top-level to `2_materials/`
- [ ] **H2.4** Bring cianchosaint's Dagster 1.13+ on par with cianfhoghlaim (enables `dg list defs` parity)
- [ ] **H2.5** Add per-sensor assets to the 5 layer namespaces (the 7 sensors from the original change proposal)
- [ ] **H2.6** Verify `dg list defs` returns 5 layer namespaces from the cianchosaint working tree
- [ ] **H2.7** Archive `2026-09-13-cianchosaint-orchestration-init-v1` under this umbrella

## 3. Sister-repo consumers (each shipped as its own openspec change)

- [ ] **H3.1** `openspec/changes/ciandlithe-sister-handoff-v1/` — materialise the sister-shared spec into ciandlithe (downstream: cross-repo consumer)
- [ ] **H3.2** `openspec/changes/ciancheiltis-sister-handoff-v1/` — materialise into ciancheiltis
- [ ] **H3.3** `openspec/changes/tuatha-sister-handoff-v1/` — materialise into tuatha
- [ ] **H3.4** `openspec/changes/gemini-hackathon-sister-handoff-v1/` — materialise into gemini-hackathon

## 4. Verification

- [ ] Run `openspec validate pipeline-sister-repo-handoff --strict` — pass
- [ ] Run `openspec validate --all --strict` — pass
- [ ] Verify cianchosaint's `dg list defs` returns 5 layer namespaces

## Verification

```bash
cd ~/dev/cianchosaint
openspec validate pipeline-sister-repo-handoff --strict
dg list defs
```
