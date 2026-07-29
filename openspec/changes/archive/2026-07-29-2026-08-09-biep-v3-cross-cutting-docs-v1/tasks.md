# 2026-08-09-biep-v3-cross-cutting-docs-v1 — Tasks

## Pre-implementation
- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1

## Stage 1 — cross-repo-sync.md
- [ ] Add `cross-repo-sync.md` to 4 openspec changes (P0 + P1 + P2 + this P3)

## Stage 2 — 4 spec deltas
- [ ] Add `specs/{spec}/spec.md` to the 4 jurisdiction pipeline changes

## Stage 3 — Mise task aliases
- [ ] Add `biep:v3:lakehouse:smoke-test` to `mise.toml`
- [ ] Add `biep:v3:registry:seed`
- [ ] Add `biep:v3:marimo:wasm:export`
- [ ] Add `biep:v3:test-runs:ingest`

## Stage 4 — Docs
- [ ] Create `docs/lakehouse/smoke-test-2026-08-06.md`
- [ ] Create `docs/baml/biiep-v3-client-canon.md`
- [ ] Create `docs/dagster/group-name-underscore-migration.md`

## Stage 5 — Spec delta + validation
- [ ] Write spec delta to `openspec/changes/2026-08-09-biep-v3-cross-cutting-docs-v1/specs/infrastructure-stacks/spec.md`
- [ ] `openspec validate 2026-08-09-biep-v3-cross-cutting-docs-v1 --strict`
- [ ] Commit + push
- [ ] Archive after merge

## Post-implementation
- [ ] File any remaining bugs
- [ ] Run `./scripts/sync_agent_docs.sh`