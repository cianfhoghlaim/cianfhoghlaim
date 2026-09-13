# Tasks: Bootstrap ciandlithe orchestration skeleton

## Phase 0 — Scaffold

- [x] 0.1. Create `ciandlithe/orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,5_agent_ops}/`
- [x] 0.2. Copy cianfhoghlaim's `orchestration/defs/__init__.py` to ciandlithe's

## Phase 1 — Validate

- [x] 1.1. `cd /Users/cianmacandeisigh/dev/ciandlithe && dg list defs --module orchestration.defs` returns empty (expected — no assets yet)

  **Status:** SKIPPED — `dg` CLI is not installed in the ciandlithe
  environment (`uv run dg list defs ...` → "No such file or directory
  (os error 2)"). Equivalent structural verification via `importlib`
  succeeded: all 5 layer dirs + the parent `defs/__init__.py` are
  importable. When `dg` becomes available the empty-defs result is
  expected (only `__init__.py` files exist, no `@asset`-decorated
  functions).
- [x] 1.2. `openspec validate 2026-09-13-ciandlithe-orchestration-init-v1 --strict` exits 0

## Phase 2 — Commit + push

- [x] 2.1. `cd /Users/cianmacandeisigh/dev/ciandlithe && git add orchestration/`
- [x] 2.2. `cd /Users/cianmacandeisigh/dev/ciandlithe && git commit -m "feat(orchestration): bootstrap 5-layer defs scaffold (sister-handoff-v1 §4 drift #4)"`
- [x] 2.3. `cd /Users/cianmacandeisigh/dev/ciandlithe && git push origin 2026-08-27-kcg-rename-v1`
