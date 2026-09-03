# Cross-Repo Sync Plan

This change touches **a single repo** (`cianfhoghlaim/`) — no cross-repo
sync is required.

## Repos involved

| Repo | Worktree | Files changed | Branch | Push target |
|:--|:--|:--|:--|:--|
| `cianfhoghlaim` | `~/dev/kings_college_galway` | Drift-remediation implementation + OpenSpec tracking files | (current) | `origin` (post-`git pull --rebase`) |

## Repos NOT involved

| Repo | Reason |
|:--|:--|
| `leabharlann` (separate repo, 3.4 GB corpus) | No code change in this change; the `leabharlann` worktree is untouched |
| `bonneagar` (IaC subdirectory, post-v7 part of this repo) | Touched only via the registry_audit `_AUDIT_DIRS` list (no IaC files modified) |

## Pre-commit gates

1. `openspec validate 2026-07-30-drift-remediation-everything-bagel-v1 --strict` — must exit 0
2. `mise run lint:drift-docs` — must exit 0 (the new lint catches future drift)
3. `mise run lint:registry` — must exit 0 (the audit-pattern gate; now covers `meaisinfhoghlaim/`)
4. `mise run sync:paths` post-`--fix` — must exit 0 (the 47 auto-fixable occurrences are cleaned)
5. `from orchestration.definitions import defs` — must not show `[skip]` warnings + the required schedules must be registered

## Post-commit verification

- `git push origin` (per the agent-protocol Habit #4)
- `git status` shows "up to date with origin/main"
