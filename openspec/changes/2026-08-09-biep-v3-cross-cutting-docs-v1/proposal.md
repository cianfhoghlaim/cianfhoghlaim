# 2026-08-09-biep-v3-cross-cutting-docs-v1

## Why

The P3 layer adds the cross-cutting concerns: docs + cross-repo sync +
mise task aliases. 4 items.

Lives in both `cianfhoghlaim` + `bonnegar` repos.

## What changes

### 1. `cross-repo-sync.md` for 4 affected openspec changes

Add `cross-repo-sync.md` to the 4 changes (P0 + P1 + P2 + this P3) that
touch both `bonnegar/` + `cianfhoghlaim/`. Each file documents the
commit plan for both repos.

### 2. 4 spec deltas

Add `specs/{spec}/spec.md` to the 4 jurisdiction pipeline changes
that don't already have one. ~20 LOC each = 80 LOC.

### 3. Mise task aliases

Add 4 new mise task aliases to `mise.toml`:
- `biep:v3:lakehouse:smoke-test`
- `biep:v3:registry:seed`
- `biep:v3:marimo:wasm:export`
- `biep:v3:test-runs:ingest`

### 4. Docs

Create 3 docs files:
- `docs/lakehouse/smoke-test-2026-08-06.md` — updated smoke test report
- `docs/baml/biiep-v3-client-canon.md` — the 3 canonical clients
- `docs/dagster/group-name-underscore-migration.md` — slash → underscore

## Dependencies

```yaml
Blocked by: 2026-08-08-biep-v3-production-readiness-v1
Affected repos: cianfhoghlaim + bonnegar
```

## Acceptance gates
- All 4 new mise tasks pass
- `cross-repo-sync.md` is present in the 4 affected openspec changes
- All 3 docs files exist + link to their respective code

## Cross-references
- `mise.toml` (the mise task catalogue)
- `docs/` (the docs surface)