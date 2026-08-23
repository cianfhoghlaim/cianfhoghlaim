# Cross-Repo Sync Plan

This change touches **only** the `cianfhoghlaim` repo. The
`bonneagar/` IaC subdir is a subdirectory of this repo (post-v7
flattening), so the IaC test gate (`mise run devops:validate-stacks`)
runs in this repo's CI. The `leabharlann/` corpus repo is
unaffected.

## Commit order

Single repo. Single commit per task per the
`concurrent-write-safety-v1` protocol.

```bash
# After every task:
git status -- <path/to/file>
git diff -- <path/to/file>
git add <path/to/file>
git commit -m "media-intel-research-v1: <T1.x> <description>"
git push origin <branch>
```

## Branch

`feature/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1`

(Conventional `feature/YYYY-MM-DD-<change-id>` branch per
`bonneagar/AGENTS.md` § Branching.)

## Push target

`origin` (the default remote for this repo per `git remote -v`).

## PR

Open at the end of Phase 1 (T1.1 - T1.10) for early review.
The full change lands as a single PR with 3 phases worth of
commits.

## Out-of-scope repos

- `leabharlann/` — separate repo, no changes from this change
- `bonneagar/` is a SUBDIRECTORY of this repo, not a separate
  repo (post-v7); the IaC test gate runs in this repo's CI

## CI gate pre-merge

```bash
# Local
openspec validate 2026-08-23-tuatha-media-intel-gameplay-capture-research-v1 --strict
mise run openspec:validate-all
mise run lint:drift-docs
mise run lint:registry
mise run devops:validate-stacks
mise run lint
mise run py:typecheck
mise run turbo typecheck
bun run ccc:index
```

## CI gate on PR

Same as local. The `.github/workflows/` + Forgejo mirror
configurations invoke the same mise tasks.

## Archive gate (post-deploy)

```bash
# After the 5 parent pending changes archive
openspec archive 2026-08-23-tuatha-media-intel-gameplay-capture-research-v1 --yes
```

## Cross-repo sync convention compliance

Per `openspec/AGENTS.md` § Cross-repo sync convention:

- Single-repo change → this file is included for clarity
- Topo ordering: 5 parent pending changes must archive first
- No new branches in leabharlann
- No IaC test prerequisite from bonneagar (post-v7 subdir)
