# Cross-Repo Sync Plan

This change is a **single-repo change** (post-v7, the IaC subdirectory
`bonneagar/` lives inside this repo, and the sister `leabharlann` repo is
unaffected because no BAML files are shared between cianfhoghlaim and
leabharlann).

## Affected repos

- `cianfhoghlaim` — the only repo touched by this change

## Commit order

Single-repo: this change is committed and pushed to `cianfhoghlaim` only.

## Branch name

```text
2026-08-13-biep-v3-systematic-download-ireland-england-v1
```

## Push target

```text
origin/2026-08-13-biep-v3-systematic-download-ireland-england-v1 -> main
```

## Sister-repo notes

The `bonneagar` directory inside this repo is committed via the same
`main` branch — no separate push target. The `leabharlann` repo (separate
repo at `github.com/cianfhoghlaim/leabharlann`) is untouched by this change.

## Per-milestone archive cadence

This change CANNOT archive until M4 (the last milestone) archives. Per-milestone
archives are tracked via the `mise run biep:v3:m<N>:archive` task and
maintained as **sub-archives of this umbrella change** (not separate openspec
changes).

## Cross-repo sync final answer

**Single-repo change. No cross-repo sync required.** This file is included
for openspec convention compliance (per `openspec/AGENTS.md`).
