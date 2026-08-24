# Tasks: 2026-08-24-wave-0-cocoindex-module-path-repair-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/specs/cocoindex-v1-module-path-migration/spec.md`

## Phase 2: Module-path repair in defs.yaml (3 tasks)

- [ ] **T2.1**: Bucket A — Per-nation education embeddings (~55 files)
  - Apply sed across `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_*/defs.yaml`
  - Map `cianfhoghlaim.cocoindex.european_nations_<iso>_education_embedding` → `cianfhoghlaim.cocoindex_flows.european_nations._factory`
  - Verify with `grep -rln "cianfhoghlaim.cocoindex.european_nations_" orchestration/defs | wc -l` returns 0

- [ ] **T2.2**: Bucket B — LC subjects (~6 files)
  - Edit `orchestration/defs/3_model_lifecycle/cocoindex_v1/lc_subjects/defs.yaml` (and similar)
  - Map `cianfhoghlaim.cocoindex.{mathematics,chemistry,geography,english,gaeilge,computer_science}_embedding` → `cianfhoghlaim.cocoindex_flows.subjects.lc_subject_embedding`
  - Gaeilge maps to `cianfhoghlaim.cocoindex_flows.celtic.gaeilge_embedding` (special case)

- [ ] **T2.3**: Bucket C — Specialised Apps (~20 files)
  - Apply the per-App mapping from proposal § "Bucket C"
  - Verify with `grep -rln "cianfhoghlaim.cocoindex\." orchestration/defs | wc -l` returns 0

## Phase 3: Partition-name typo fix (2 tasks)

- [ ] **T3.1**: Edit `orchestration/partitions_v2.py:305-314`
  - Change `name="cianhoghlaim_scope"` → `name="cianfhoghlaim_scope"`
  - Update the comment to reflect that the typo is now fixed

- [ ] **T3.2**: Verify with `grep -rn "cianhoghlaim_scope" orchestration` returns 0

## Phase 4: AGENTS.md counts drift fix (3 tasks)

- [ ] **T4.1**: Update `orchestration/AGENTS.md` line 29
  - Change "199 assets + 31 jobs + 6 schedules + 16 sensors + 22 asset checks"
  - To actual counts: "~190 assets + 31 jobs + 6 schedules + 13 sensors + 22 asset checks"
  - Recount via `find orchestration/defs -name "defs.yaml" | wc -l` and
    `grep -rln "@dg.asset\|@dg.sensor\|@dg.schedule" orchestration --include="*.py" | wc -l`

- [ ] **T4.2**: Update `cocoindex_flows/AGENTS.md` counts
  - Verify number of v1 Apps (should be 87+)

- [ ] **T4.3**: Update `orchestration/AGENTS.md` line 20 — verify "833 Dagster assets" claim (this number is in `mise.toml` task descriptions, may also be stale)

## Phase 5: Verify CocoIndex pipeline end-to-end (4 tasks)

- [ ] **T5.1**: `uv run python -c "import cocoindex; print(cocoindex.__version__)"` returns `1.0.20`

- [ ] **T5.2**: `uv run python -c "from cocoindex_flows.celtic import gaeilge_embedding"` succeeds

- [ ] **T5.3**: `mise run sync:dagster` passes (no `cocoindex_v1_module_import_failed`)

- [ ] **T5.4**: `mise run lint:drift-docs` passes (AGENTS.md numbers match reality)

## Phase 6: Commit + push (2 tasks)

- [ ] **T6.1**: Stage only the Wave 0 files (NOT other in-progress files):
  - 85 modified `defs.yaml` files (module path repair)
  - `orchestration/partitions_v2.py` (typo fix)
  - `orchestration/AGENTS.md`, `cocoindex_flows/AGENTS.md` (counts)
  - 3 new openspec files (this change)

- [ ] **T6.2**: Commit with message + push

## Total: 17 tasks across 6 phases

Estimated effort: ~3 days (per the master plan's Wave 0 estimate).
