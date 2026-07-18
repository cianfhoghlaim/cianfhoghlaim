# Cross-repo-sync: 2026-08-11-biep-v3-lakehouse-population-v1

Per the openspec AGENTS.md convention, this change touches only the
`cianfhoghlaim` repo. The lakehouse stack deploy is via Komodo
(bienneses data-plane); IaC lives in the same repo at `bonneagar/`.

## Affected repos

- `cianfhoghlaim` (this repo) — DLT + DuckDB + CocoIndex + BAML +
  Dagster + MotherDuck + notebooks
- `bonnegar` (separate repo, not in this worktree) — IaC stack
  catalogue + Komodo deploys. NO IaC changes required for this change
  (local Postgres fallback stays).

## Commit plan

### Commit 1 (cianfhoghlaim) — Lakehouse population operational

The work is largely operational, but the commit may include:

1. `scripts/refactor-biep-notebooks.py --write` output (replaces
   `md:oideachais` → `md:cianfhoghlaim` in ~25 notebooks).
2. Any new operational scripts (e.g., `scripts/smoke-test-lakehouse.sh`).
3. Documentation updates in `docs/lakehouse/smoke-test-2026-08-11.md`.

## Order of operations

1. `2026-08-10-biep-v3-preflight-bug-fixes-v1` must archive first
   (this change's blocker).
2. Commit 1 (cianfhoghlaim) lands on
   `openspec/2026-07-25-refactor-batch-v1` branch.
3. `openspec validate 2026-08-11-biep-v3-lakehouse-population-v1 --strict`
   passes.
4. Operational deploy runs:
   - `bun run preflight:arm-oci`
   - `km deploy stack lakehouse-bunchloch --action=up`
   - `mise run biep:v3:lakehouse:smoke-test`
   - `mise run biep:v3:registry:seed`
   - 4 jurisdiction pipelines via `dg launch`
   - 8 CocoIndex flows via `dg launch`
   - 4 BIEP v3 MotherDuck Flights via `dg launch`
   - Notebook namespace sweep via `bun run scripts/refactor-biep-notebooks.py --write`
5. Push to `origin/openspec/2026-07-25-refactor-batch-v1`.
6. Archive: `openspec archive 2026-08-11-biep-v3-lakehouse-population-v1 --yes`.

## Push targets

- `origin/openspec/2026-07-25-refactor-batch-v1` (the wave branch)

## PlanetScale follow-up (NOT in this batch)

Per the user's audit decision, the Phase B.0 PlanetScale hard switch is
deferred. When ready, the follow-up change would be:
`2026-08-12-biep-v3-planetscale-hard-switch-v1` (separate openspec
change, separate commit, separate archive).