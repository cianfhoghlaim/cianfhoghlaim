# 2026-08-22 — uv audit + uv check (adopt the new uv 0.11+ security gates)

## Why

We use `uv sync` + `uv run` extensively (50+ invocations across mise.toml, workflows, agents) but have **zero security audit** or **type-check** gates. The uv 0.11+ release line (Mar–Jul 2026) added two preview subcommands that are direct improvements over our current setup:

- **`uv audit`** (preview, 0.11.x) — scans `uv.lock` against the OSV database for known vulnerabilities. Supports `--ignore`/`--ignore-until-fixed`. The analogous feature in `bun audit` / `npm audit` has been catching vulns across the ecosystem for months; we get the same affordance for Python.
- **`uv check`** (preview, 0.11.18) — runs Astral's `ty` type checker. Complements our existing `mypy` gate (different engine, different rules).

Additionally, `UV_MALWARE_CHECK=1` (0.11.16+) is the new opt-in malware scan on `uv add`/`uv sync` — the Astral-recommended safety layer that the wider Python ecosystem (e.g. `simple-modern-uv`) adds to their CI gates.

## What changes

Add 4 new tasks to the `core` namespace in `mise.toml`:

1. `core:uv:audit` — the relaxed audit (informational)
2. `core:uv:audit:strict` — the CI gate (exits 1 on any known vuln)
3. `core:uv:check` — the `ty` type checker
4. `core:uv:audit-malware` — malware scan on uv add/sync

Wire `core:uv:audit:strict` + `core:uv:check` into the `core:lint` aggregate gate so the CI catches issues automatically.

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-19-domain-driven-mise-task-catalog-v1` (extends the namespace)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `mise run core:uv:audit:strict` exits 0 (no vulns in our `uv.lock` at the time of adoption)
2. `mise run core:uv:check` exits 0 (ty passes against our `.py` files)
3. `mise run core:uv:audit` exits 0 (informational)
4. `mise run core:uv:audit-malware` exits 0 (dry-run with `UV_MALWARE_CHECK=1`)
5. `mise run core:lint` still passes (the new gates added to `depends`)
6. `openspec validate --all --strict` exits 0

## Out of scope

- Migrating from `mypy` to `ty` entirely (different engines, different rules). The 2 coexist.
- Adding `uv audit` to `.github/workflows/ci.yaml` (separate change: workflow updates).
- Promoting `uv audit` from preview to required (that's an upstream uv decision).

## Rollback plan

Single commit. Revert via `git revert` if a task fails. The tasks are additive (no existing tasks removed).
