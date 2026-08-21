# 2026-08-22 — mise monorepo mode + subproject split (bonneagar + agents)

## Why

We **are** a monorepo (the repo has `bonneagar/`, `agents/`, and other first-class subprojects) but our `mise.toml` is monolithic — it pretends subprojects don't exist. The mise 2026.5+ release line shipped first-class monorepo support:

- `monorepo_root = true` (settings flag)
- `[monorepo] config_roots = [...]` (list of subproject paths)
- `MISE_MONOREPO_ROOT` env var (per subproject)
- `MISE_PROJECT_ROOT` precedence fix (subproject `task.config_root` wins over root)
- `[monorepo.task_defaults.<name>]` (root task defaults by name)
- `extends = "template:name"` (subproject task inheritance)

Today we have 0 of these. Enablement would let us:

1. **Subproject tasks** — `bonniegar/` gets its own `mise.toml` with IaC-specific tasks (`devops:health`, `devops:plan`, etc.); `agents/` gets its own with fleet-specific tasks (`ml:agents:smoke`, `ml:agents:audit`, etc.). These tasks don't pollute the root `mise tasks` listing.

2. **Inheritance** — subprojects inherit the root's `[tools]`, `[env]`, `[settings]`, and `[task_templates]` automatically. No duplication.

3. **Path resolution** — `MISE_PROJECT_ROOT` correctly scopes subproject tasks to their `mise.toml` (not the cwd). Today's `bonneagar/iac/commands/*.ts` resolves secrets against the root, which works but is fragile.

## What changes

1. **`mise.toml`** — add `[settings] monorepo_root = true` + `[monorepo] config_roots = ["bonneagar", "agents"]`

2. **`bonneagar/mise.toml`** (NEW) — IaC subproject:
   - Moves `devops:health`, `devops:plan`, `devops:bootstrap`, `devops:bootstrap-pangolin-client`, `devops:deploy`, `devops:teardown` here (using `extends` for shared config)
   - Inherits tools `[dagger]`, `[pulumi]`, `[infisical]`, `[oci]`, etc. from root

3. **`agents/mise.toml`** (NEW) — Agent-fleet subproject:
   - Moves `ml:agents:smoke`, `ml:agents:audit`, `ml:agents:reproduce` here
   - Inherits `python = "3.13"`, `[env]` from root

4. **Back-compat aliases** — every moved task retains its old name as alias for 1 release cycle

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-19-domain-driven-mise-task-catalog-v1` (the previous refactor established the 6 namespaces)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `mise tasks --all` shows BOTH root tasks AND `//devops:*` AND `//ml:agents:*` tasks
2. `cd agents && mise run ml:agents:smoke` works (subproject task resolution)
3. `cd bonneagar && mise run devops:health` works
4. `cd bonneagar && mise run ml:agents:smoke` works (root task still accessible from subproject)
5. Root `mise.toml` shrinks by ~20% (moved tasks out)
6. All old task names still work as aliases
7. `openspec validate --all --strict` exits 0

## Out of scope

- Splitting `web/` as a subproject (would require reorganizing the turbo.json workspaces)
- Splitting `orchestration/` as a subproject (would require separating the Dagster code-location)
- Splitting `dlt_sources/`, `baml_src/`, `meaisinfhoghlaim/`, etc. (not yet ready for monorepo treatment)
- `[monorepo.task_defaults.<name>]` (root task defaults) — that's a follow-up

## Rollback plan

Single commit. The root `mise.toml` changes are additive (just adding 2 settings keys). The new subproject mise.toml files are pure additions. Worst case: revert and the root stays monolithic.
