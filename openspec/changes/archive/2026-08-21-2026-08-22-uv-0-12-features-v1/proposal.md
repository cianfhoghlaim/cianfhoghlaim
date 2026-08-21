# 2026-08-22 — uv 0.12 features (lock --refresh + tree --json + format)

## Why

Latest uv is 0.12.5 (we run 0.11.21). The 0.12.x line added 3 notable features
that are direct improvements to our workflow:

- **`uv lock --refresh`** — refresh the lockfile (vs. just `uv lock` which uses cached resolution)
- **`uv tree --format=json`** — JSON output for tool integration (was `--json` in 0.11, became `--format=json` in 0.12)
- **`uv format`** — Rust-managed Python formatter (complements ruff format, uses Python 3.13+)

The previous refactor (`2026-08-22-uv-audit-and-check-previews-v1`) added `core:uv:audit` + `core:uv:check`. This change adopts the 0.12 lock + tree + format features.

## What changes

1. **`mise.toml`** — add 5 new tasks in the `core` namespace:

   - `core:uv:lock:refresh` (alias `uv:lock:refresh`) — `uv lock --refresh` (re-resolve from scratch)
   - `core:uv:lock:upgrade` (alias `uv:lock:upgrade`) — `uv lock --upgrade` (upgrade all packages)
   - `core:uv:lock:upgrade-package` (alias `uv:lock:upgrade-package`) — `uv lock --upgrade-package <name>`
   - `core:uv:tree:json` (alias `uv:tree:json`) — `uv tree --format=json` (uv 0.12+)
   - `core:uv:format` (alias `uv:format`) — `uv format` (Python formatter, uv 0.12+)

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-22-uv-audit-and-check-previews-v1` (extends the uv domain)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `mise run core:uv:lock:refresh` exits 0
2. `mise run core:uv:lock:upgrade` exits 0 (or warns if no upgrades available)
3. `mise run core:uv:tree:json` exits 0 and emits JSON
4. `mise run core:uv:format --check` exits 0
5. `openspec validate --all --strict` exits 0

## Out of scope

- Upgrading uv itself to 0.12.x (the tasks work in 0.11.21+; the `--format=json` flag is 0.12+)
- Adding the lock --refresh to a CI gate (separate change)
- Migrating to PEP 803 (abi3t) builds (separate change)

## Rollback plan

Single commit. Revert via `git revert` if any task fails. The tasks are additive.
