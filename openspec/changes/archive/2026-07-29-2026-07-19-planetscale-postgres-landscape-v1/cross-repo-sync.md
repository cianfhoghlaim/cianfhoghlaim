# cross-repo-sync — planetscale-postgres-landscape-v1

This change touches a **single repo only** — `cianfhoghlaim`.

The IaC half (Phase B + C follow-up changes) will live on the
`bonneagar/` worktree. Those changes don't exist yet, so no
`bonneagar` commit plan is needed here.

## Repo 1: cianfhoghlaim (this repo)

Branch: `feat/2026-07-19-planetscale-postgres-landscape-v1`
Push target: `origin`

| Commit # | Phase | Message |
|--:|---|---|
| 1 | Phase 0–4 | `openspec(changes): planetscale-postgres-landscape-v1 — text-only analysis (1 NEW umbrella spec + 17 MODIFIED deltas + 1 ADR + 1 proposal + 1 tasks)` |

## Repo 2: bonneagar (separate worktree)

**No commits this change.** The IaC migration work (Phase B + C) is deferred
to separate, future openspec changes:

- `2026-07-XX-planetscale-postgres-migration-phase-b-v1` — `bonneagar/stacks/<stack>/compose.yaml` deltas
- `2026-07-XX-planetscale-mysql-sunset-v1` — Bytebase migration scripts + `PLANETSCALE_*_URL` env hooks

## Order of operations

1. **First** push the cianfhoghlaim commit (the single analysis commit).
2. **Then** open a draft PR for operator review.
3. **Then** (after operator approval) open the Phase B + C branches.

## Why this change is text-only

The operator's choice was: **Full landscape analysis FIRST**.
This means:

- ✅ A canonical umbrella spec (`planetscale-postgres-data-strategy`)
- ✅ A 28-row per-stack decision matrix
- ✅ 17 MODIFIED spec deltas (cross-references)
- ✅ 1 ADR recording the technical rationale
- ❌ No stack `compose.yaml` mutations
- ❌ No `bonneagar/` worktree commits
- ❌ No Python / TypeScript code changes

The actual Postgres / D1 / FerretDB migrations happen in the Phase B + C + Komodo follow-up changes.
