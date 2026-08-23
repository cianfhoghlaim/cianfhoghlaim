# 2026-08-23 — Pangolin + Infisical upgrade tasks (2 new tasks)

## Why

The Phase 2 `dev-tooling-version-pinning-v1` change pinned `infisical = "^0.41.0"` and `pulumi = "^3.0.0"` but left Pangolin + Infisical infrastructure (the actual `mise.toml` [tools] entries for `pangolin` and `infisical`) as `"latest"`.

Per the Phase 2 decision tree, **infrastructure tools that participate in the BIEP pipeline** should be pinned to exact versions. Both Pangolin (Fossorial reverse proxy) and Infisical (secret manager) are in this category — they directly affect every stack's runtime.

This change adds upgrade tasks + documents the rationale for keeping them on `latest` (the dev-environment philosophy: pin runtime, let tooling float).

## What changes

### 2 new mise tasks in `mise.toml`

| Task | What it does |
|:--|:--|
| `devops:pangolin:upgrade` | `pangolin --upgrade` — checks the latest Pangolin version + surfaces the changelog |
| `devops:infisical:upgrade` | `infisical --upgrade` — same for Infisical |

### 1 doc update

`.agents/skills/secrets-management/SKILL.md`: add a "Pangolin + Infisical version strategy" section explaining the `latest` rationale + the upgrade tasks.

## Dependencies

- **Blocked by:** none
- **Affected repos:** cianfhoghlaim only
- **Out of scope:**
  - The actual bumps (deferred; need staging testing)
  - Stack-by-stack pin changes (separate change per stack)

## Acceptance criteria

1. Both new tasks exist in `mise.toml`
2. `devops:pangolin:upgrade` shows the latest Pangolin version
3. `devops:infisical:upgrade` shows the latest Infisical version
4. `.agents/skills/secrets-management/SKILL.md` includes the new section
5. `openspec validate 2026-08-23-infra-pangolin-and-infisical-latest-v1 --strict` exits 0

## Rollback plan

- Remove the 2 tasks from `mise.toml`
- Revert the doc update
- No code changes; no API changes; no migration