# 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify A1 + B1 merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Create the 4 missing Component classes

- [ ] Create `orchestration/components/biep_subject_component.py` with the
  `BIEPSubjectComponent` class — 5-layer convention (ingestion +
  extraction + embedding + cognify + agent_ops)
- [ ] Create `orchestration/components/junior_cycle_subject_component.py`
- [ ] Create `orchestration/components/england_board_subject_component.py`
- [ ] Create `orchestration/components/england_cross_board_comparator_component.py`

## Stage 2 — Create the 5 registry-change sensors

- [ ] Create `orchestration/sensors/ncca_registry_sensor.py`
- [ ] Create `orchestration/sensors/sqa_registry_sensor.py`
- [ ] Create `orchestration/sensors/wjec_registry_sensor.py`
- [ ] Create `orchestration/sensors/ccea_registry_sensor.py`
- [ ] Create `orchestration/sensors/jcq_registry_sensor.py`

## Stage 3 — Implement the 2-axis `scope × year` partition

- [ ] Edit `orchestration/partitions_v2.py` — add the canonical
  `scope` × `year` partition definition
- [ ] Add a helper `scope_from_registry_row(jurisdiction, stage, subject_slug, board, qualification_level, language)`
  that builds the canonical `<jurisdiction>__<stage>__<subject_slug>__<board>__<qualification_level>__<language>` key

## Stage 4 — Wire `EnsembledExtractor.extract()` into the 4 generic asset modules

- [ ] Edit
  `orchestration/defs/2_materials/ireland_education/generic_ireland_assets.py:117-133`
  — replace the `+0` placeholder with a real
  `EnsembledExtractor().extract(pdf_path=..., baml_function=...)` call
- [ ] Edit
  `orchestration/defs/2_materials/england_education/generic_england_assets.py:101-113`
  — same
- [ ] Edit
  `orchestration/defs/2_materials/sct_wls_ni_education/generic_sct_wls_ni_assets.py:65-82`
  — same
- [ ] Edit
  `orchestration/defs/2_materials/crown_dependencies_education/generic_crown_dependencies_assets.py:65-78`
  — same

## Stage 5 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1/specs/dagster-5-layer-component-architecture/spec.md`
- [ ] Run `openspec validate 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol