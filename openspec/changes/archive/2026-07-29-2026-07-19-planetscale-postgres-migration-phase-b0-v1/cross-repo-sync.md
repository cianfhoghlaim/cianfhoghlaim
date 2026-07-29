# cross-repo-sync — planetscale-postgres-migration-phase-b0-v1

This change touches **2 repos**: `cianfhoghlaim` (the openspec change + tests) + `bonneagar` (the IaC code + 3 stack swaps).

## Repo 1: cianfhoghlaim (this repo)

Branch: `feat/2026-07-19-planetscale-postgres-migration-phase-b0-v1`
Push target: `origin`

| Commit # | Phase | Message |
|--:|---|---|
| 1 | Phase 0–3 | `openspec(changes): planetscale-postgres-migration-phase-b0-v1 — Lakekeeper + Convex + Dagster → PlanetScale PG (3 stacks, hard switch + env swap, ~8h)` |

## Repo 2: bonneagar (separate worktree)

Branch: `feat/2026-07-19-planetscale-postgres-migration-phase-b0-v1`
Push target: `archive-bonneagar`

| Commit # | Message |
|--:|---|
| 1 | `iac(planetscale): LCP resolver + read-only DB verifier + 3 stack swaps (lakekeeper hard switch + convex hard switch + dagster env swap only)` |

## Order of operations

1. **First** push cianfhoghlaim (the openspec change validates + merges).
2. **Then** push bonneagar (the IaC code + stack swaps land).
3. **Then** open a draft PR for operator review.
4. **Then** (after operator approval + pre-requisites confirmed) merge.
5. **Then** archive the openspec change: `bun run spec:archive 2026-07-19-planetscale-postgres-migration-phase-b0-v1 --yes`.

## Why this order

The openspec change archives AFTER both repos land. The PR review surface is small (~13 files total) but spans 2 repos. Operators can review them as a single PR if the repos are mirrored via git, or as 2 PRs if not.

## Hard constraints

- **The cianfhoghlaim branch MUST NOT be merged** until the bonneagar branch is reviewed + merged (the IaC code is what implements the openspec change)
- **The operator's pre-requisites MUST be complete** before the IaC deploy (create 2 databases + 3 Infisical secrets)
- **Lakekeeper + Convex are HARD SWITCHED** — no fallback at the container layer; rollback is `git revert` + PlanetScale PITR
- **Dagster is ENV-SWAPPED ONLY** — the local `dagster-postgres` container stays; full retirement happens in Phase B.1