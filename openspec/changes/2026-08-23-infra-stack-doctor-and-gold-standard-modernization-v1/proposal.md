# 2026-08-23 — Stack doctor + GOLD_STANDARD modernization (2 new tasks)

## Why

The repo has **99 Docker Compose stacks** at `bonneagar/stacks/*/` (was 93, then 94; new stacks added by recent changes). The 6-file GOLD_STANDARD pattern (compose.yaml + sidecar.yaml + secrets.env + pangolin.yaml + blueprint.yaml + .env.example) was introduced 2026-07 but several stacks have drifted from it.

The `scripts/stack-doctor.sh` (13 KB, comprehensive) already detects drift. We just don't have CI gates that fail on drift or surface the drift count.

This change adds 2 tasks that expose the stack-doctor audit + drift-report functionality as first-class mise tasks.

## What changes

### 2 new mise tasks in `mise.toml`

| Task | What it does |
|:--|:--|
| `devops:stack:gold-standard-audit` | Runs the existing `scripts/stack-doctor.sh --strict` and fails CI if any stack is missing any of the 6 GOLD_STANDARD files |
| `devops:stack:drift-report` | Runs `scripts/stack-doctor.sh` in report mode and prints a per-stack drift summary (which files are missing for which stacks) |

### 1 doc update

`bonneagar/AGENTS.md`: add a "Stack modernization" section documenting the 99 stacks + the GOLD_STANDARD audit workflow.

## Dependencies

- **Blocked by:** none
- **Affected repos:** cianfhoghlaim only
- **Out of scope:** fixing the drift (per-stack modernization is a separate change per stack)

## Acceptance criteria

1. Both tasks exist in `mise.toml`
2. `devops:stack:gold-standard-audit` exits 1 if any stack is missing any of the 6 GOLD_STANDARD files
3. `devops:stack:drift-report` exits 0 always (informational)
4. `bonneagar/AGENTS.md` includes the new "Stack modernization" section
5. `openspec validate 2026-08-23-infra-stack-doctor-and-gold-standard-modernization-v1 --strict` exits 0

## Rollback plan

- Remove the 2 tasks from `mise.toml`
- Revert the docs update
- No code changes; no API changes; no migration