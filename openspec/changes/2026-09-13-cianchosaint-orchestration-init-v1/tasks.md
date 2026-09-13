# Tasks: Mirror cianfhoghlaim 5-layer defs shape to cianchosaint

## Phase 0 — Mirror init

- [x] 0.1. Copy `/Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs/__init__.py` to `/Users/cianmacandeisigh/dev/cianchosaint/orchestration/defs/__init__.py`
- [ ] 0.2. Verify `dg --directory /Users/cianmacandeisigh/dev/cianchosaint list defs` now returns ≥1 def (the licence_enforcement_sensor)

  **Status:** SKIPPED — `dg` CLI is not installed in the cianchosaint
  venv (the project's `motherduck>=0.10.0` constraint conflicts with
  the only available motherduck==0.0.0). The cianchosaint repo has no
  working venv at `.venv/bin/dg`. Per the user prompt: "may not have
  `dg` available — if not, skip".

## Phase 1 — 5-layer dirs

- [x] 1.1. Create `cianchosaint/orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,5_agent_ops}/`
- [x] 1.2. Add `__init__.py` in each

## Phase 2 — Validation

- [x] 2.1. `openspec validate 2026-09-13-cianchosaint-orchestration-init-v1 --strict` exits 0
- [ ] 2.2. `cd /Users/cianmacandeisigh/dev/cianchosaint && dg list defs --module orchestration.defs` returns the expected defs

  **Status:** SKIPPED — same reason as 0.2 (no `dg` binary available
  in the cianchosaint environment). The structural change (5-layer
  dirs + __init__.py + licence_enforcement_sensor.py alongside) is
  in place; `dg` will pick it up once the project resolves its
  motherduck dep conflict.

## Phase 3 — Commit + push

- [x] 3.1. `cd /Users/cianmacandeisigh/dev/cianchosaint && git add orchestration/defs/`
- [x] 3.2. `cd /Users/cianmacandeisigh/dev/cianchosaint && git commit -m "feat(orchestration): mirror cianfhoghlaim 5-layer defs shape"`
- [x] 3.3. `cd /Users/cianmacandeisigh/dev/cianchosaint && git push origin main`
