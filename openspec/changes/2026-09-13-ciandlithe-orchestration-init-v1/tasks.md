# Tasks: Bootstrap ciandlithe orchestration skeleton

## Phase 0 — Scaffold

- [ ] 0.1. Create `ciandlithe/orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,5_agent_ops}/`
- [ ] 0.2. Copy cianfhoghlaim's `orchestration/defs/__init__.py` to ciandlithe's

## Phase 1 — Validate

- [ ] 1.1. `cd /Users/cianmacandeisigh/dev/ciandlithe && dg list defs --module orchestration.defs` returns empty (expected — no assets yet)
- [ ] 1.2. `openspec validate 2026-09-13-ciandlithe-orchestration-init-v1 --strict` exits 0

## Phase 2 — Commit + push

- [ ] 2.1. `cd /Users/cianmacandeisigh/dev/ciandlithe && git add orchestration/`
- [ ] 2.2. `cd /Users/cianmacandeisigh/dev/ciandlithe && git commit -m "feat(orchestration): bootstrap 5-layer defs scaffold (sister-handoff-v1 §4 drift #4)"`
- [ ] 2.3. `cd /Users/cianmacandeisigh/dev/ciandlithe && git push origin main`
