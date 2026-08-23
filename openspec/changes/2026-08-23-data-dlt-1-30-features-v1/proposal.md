# 2026-08-23 — Adopt DLT 1.30 features (3 new tasks)

## Why

DLT 1.30.0 (Aug 2026) brought 3 new features that the Cianfhoghlaim
DLT pipeline surface should adopt:

- **`refresh` write_disposition**: supersedes `replace`; more efficient
  incremental updates
- **`dlt[hub]` plugin split**: separate package for dlthub features
  (deployment, observability); we already pin `dlt[duckdb,motherduck,filesystem]`
- **`pipeline.dataset()` single-schema default**: was multi-schema
  before; now single-schema unless `schema=` is passed

The previous round (`2026-08-21-2026-08-21-dlt-1.28.1-to-1.30.0-v1`) did
the actual bump. This change adds the **task surface** for using the
new features.

## What changes

### 3 new mise tasks in `mise.toml`

| Task | What it does |
|:--|:--|
| `data:dlt:refresh` | `dlt pipeline <name> refresh` — triggers an incremental refresh of a named pipeline (supplants `replace`) |
| `data:dlt:hub:install` | `uv add dlt[hub]` — adds the dlthub plugin to the current venv (for deployment workflows) |
| `data:dlt:hub:deploy` | `dlt deploy <pipeline> <destination>` — scaffolds the deployment manifest for a named pipeline (e.g., `github_actions`, `airflow`, `kubernetes`) |

### 1 doc update

`.agents/skills/dlt/SKILL.md`: add a "DLT 1.30+ new features" section
documenting the `refresh` write_disposition + the `dlt[hub]` split +
the new `pipeline.dataset()` defaults.

## Dependencies

- **Blocked by:** none
- **Soft-blocked by:** `2026-08-21-2026-08-21-dlt-1.28.1-to-1.30.0-v1` (the actual bump)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. All 3 new tasks exist in `mise.toml`
2. `data:dlt:refresh` runs the `dlt pipeline ... refresh` command
3. `data:dlt:hub:install` adds the dlthub plugin via `uv add dlt[hub]`
4. `data:dlt:hub:deploy` scaffolds a deployment manifest
5. `.agents/skills/dlt/SKILL.md` includes the new section
6. `openspec validate 2026-08-23-data-dlt-1-30-features-v1 --strict` exits 0

## Rollback plan

- Remove the 3 tasks from `mise.toml`
- Revert the skill update
- No data loss; the dlt bump itself stays (separate change)