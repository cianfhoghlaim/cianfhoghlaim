# Cross-Repo Sync Plan

This change touches **a single repo** (`cianfhoghlaim/`) — no cross-repo
sync is required.

## Repos involved

| Repo | Worktree | Files changed | Branch | Push target |
|:--|:--|:--|:--|:--|
| `cianfhoghlaim` | `~/dev/kings_college_galway` | 28 files (5 new AGENTS.md, 78 new `openspec/specs/<name>/AGENTS.md`, 1 new `scripts/lint_drift_docs.py`, 1 new `scripts/sync/spec_agents.py`, 4 new spec deltas, 1 updated `scripts/sync/all.sh`, 2 new CI workflows, root `AGENTS.md` + `mise.toml` + `openspec/AGENTS.md` numbers fixed) | (current) | `origin` (post-`git pull --rebase`) |

## Repos NOT involved

| Repo | Reason |
|:--|:--|
| `leabharlann` (separate repo, 3.4 GB corpus) | No code change in this change; the `leabharlann` worktree is untouched |
| `bonneagar` (IaC subdirectory, post-v7 part of this repo) | Touched only via the 89-stacks number fix in `AGENTS.md` (no IaC files modified) |

## Pre-commit gates

1. `openspec validate 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 --strict` — must exit 0
2. `mise run lint:drift-docs` — must exit 0 (the new lint catches future drift)
3. `mise run sync:all` — must exit 0 (the 7-layer orchestrator wires correctly)
4. `git status` must show ≤30 changed files (per the change boundary in `tasks.md`)

## Post-commit verification

- `git push origin` (per the agent-protocol Habit #4)
- `git status` shows "up to date with origin/main"
- `gh run watch` (or the Forgejo equivalent) on the 2 new CI workflows
- All 4 sibling changes still validate strictly (`2026-07-29-complete-remaining-model-registry-migrations-v1`, `2026-08-15-retroactive-pre-v7-cleanup-v1`)
