# Tasks: Mirror cianfhoghlaim 5-layer defs shape to cianchosaint

## Phase 0 — Mirror init

- [ ] 0.1. Copy `/Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs/__init__.py` to `/Users/cianmacandeisigh/dev/cianchosaint/orchestration/defs/__init__.py`
- [ ] 0.2. Verify `dg --directory /Users/cianmacandeisigh/dev/cianchosaint list defs` now returns ≥1 def (the licence_enforcement_sensor)

## Phase 1 — 5-layer dirs

- [ ] 1.1. Create `cianchosaint/orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,5_agent_ops}/`
- [ ] 1.2. Add `__init__.py` in each

## Phase 2 — Validation

- [ ] 2.1. `openspec validate 2026-09-13-cianchosaint-orchestration-init-v1 --strict` exits 0
- [ ] 2.2. `cd /Users/cianmacandeisigh/dev/cianchosaint && dg list defs --module orchestration.defs` returns the expected defs

## Phase 3 — Commit + push

- [ ] 3.1. `cd /Users/cianmacandeisigh/dev/cianchosaint && git add orchestration/defs/`
- [ ] 3.2. `cd /Users/cianmacandeisigh/dev/cianchosaint && git commit -m "feat(orchestration): mirror cianfhoghlaim 5-layer defs shape"`
- [ ] 3.3. `cd /Users/cianmacandeisigh/dev/cianchosaint && git push origin main`
