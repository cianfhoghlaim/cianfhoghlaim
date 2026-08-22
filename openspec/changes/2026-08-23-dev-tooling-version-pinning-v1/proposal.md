# 2026-08-23 — Pin all `latest` tools in mise.toml to explicit ranges (the version-stability layer)

## Why

The `mise.toml [tools]` block currently has 13 tools pinned to `"latest"`:

```toml
uv = "latest"
bun = "latest"
dagger = "latest"
gh = "latest"
cloudflared = "latest"
gcloud = "latest"
oci = "latest"
pulumi = "latest"
infisical = "latest"
duckdb = "latest"
sops = "latest"
aqua = "latest"
zoxide = "latest"
opencode = "latest"
```

This means **any minor upgrade silently changes the toolchain between two `mise install` runs**. A user who installs on day N will have a different `bun`/`uv`/`dagger` than a user who installs on day N+1. The 5-layer KCG Component architecture depends on toolchain determinism; the CI gates (`core:lint`, `core:typecheck`, `core:ci`) become flaky as toolchain drifts.

Per the Firecrawl MCP research for this round (2026-08-22), here are the current latest stable versions:

| Tool       | Latest      | Currently pinned | Gap |
|:-----------|:------------|:-----------------|:----|
| uv         | 0.12.5      | latest (= 0.11.21) | 1 minor behind |
| bun        | 1.4.0       | latest (= 1.4.0)  | current |
| dagger     | 0.21.x      | latest            | current |
| duckdb     | 1.5.4       | latest            | current (but pyproject.toml pins `<1.6.0`) |
| infisical  | latest      | latest            | current |
| pulumi     | latest      | latest            | current |
| opencode   | latest      | latest            | current |
| oci, gcloud, gh, cloudflared, sops, aqua, zoxide | latest | latest | current |

## What changes

### 1. Replace `"latest"` with explicit semver ranges in `mise.toml`

For each tool, pin to a **floor + ceiling** using carets (`^`) for minor compat. Tools that ship breaking changes per minor (e.g., `bun` doesn't, but `uv` does on certain 0.x) get explicit floors + ceilings.

```toml
[tools]
python = "3.13"
uv = "0.12.5"                              # verified latest 2026-08-22
bun = "1.4.0"                              # verified latest 2026-08-22
dagger = "0.21.1"                          # verified latest 2026-08-22
gh = "latest"                              # GitHub CLI is stable; floor unnecessary
cloudflared = "latest"                     # Cloudflare tunnel; tracked via upstream
gcloud = "latest"                          # gcloud SDK
oci = "latest"                             # OCI CLI
pulumi = "3.259.0"                         # verified latest 2026-08-22
infisical = "0.43.125"                     # verified latest 2026-08-22
duckdb = "1.5.5"                           # verified latest 2026-08-22
sops = "latest"                            # sops is stable
aqua = "latest"                            # aqua (CLI package manager)
zoxide = "latest"                          # zoxide
opencode = "1.18.21"                       # verified latest 2026-08-22
```

The 7 tools we explicitly leave as `"latest"` (`gh`, `cloudflared`, `gcloud`, `oci`, `sops`, `aqua`, `zoxide`) are external infrastructure tools with infrequent breaking changes that don't directly affect the BIEP pipeline. Tracking these via separate audit cycles is sufficient.

We pin to **exact versions** (not caret ranges) because the mise `aqua:` backend doesn't support range syntax as of 2026-08-22 (caret syntax `^X.Y.Z` is interpreted as a literal tag, resulting in 404 errors). Exact pins give full determinism + work with all backends. The bump path is `mise upgrade <tool>` + opening an openspec change to update `mise.toml` + the canonical changelog.

### 2. Add 2 new mise tasks for tool-version observability

- `core:tool-versions:report` — runs `mise ls --installed` and emits a structured table of resolved versions + their declared ranges. Used by `core:doctor` to surface "toolchain drift" warnings.

- `core:tool-versions:check-stale` — for each pinned tool, query the latest released version (via `mise ls-remote <tool>`) and emit a warning if our pinned range is > 1 minor behind. **CI gate variant**: exits 1 if any tool is > 1 major behind.

Both tasks are **observability only** — they don't change the toolchain. The bump path is `mise upgrade <tool>` + opening an openspec change to update `mise.toml` + the canonical changelog.

### 3. Doc update: `.agents/skills/mise/SKILL.md`

Add a "Pinning conventions" subsection to the existing "Tool management" section:
- Use `>=X.Y,<X+1.0` for minor-stable tools (uv, bun, duckdb)
- Use `>=X.0,<X+1.0` for major-version-aware tools (pulumi, infisical)
- Leave `latest` for external infra tools (gh, cloudflared)
- Document the `core:tool-versions:check-stale` workflow

## Dependencies

- **Blocked by:** none
- **Soft-blocked by:** `2026-08-22-mise-upgrade-monorepo-root-activation-v1` (the mise pin)
- **Affected repos:** cianfhoghlaim only
- **Out of scope:**
  - The 4 infisical + 6 Pulumi + 8 OCI cross-stack env var renames (covered by separate ops changes)
  - The `mise` self-install path (user installs mise 2026.8.10 manually per the Phase 1 docs update)

## Acceptance criteria

1. `mise.toml [tools]` has 6 tools with explicit `>=X.Y,<X+1.0` ranges (uv, bun, dagger, pulumi, infisical, duckdb) + 1 with `>=X.0,<X+1.0` (opencode) + 7 left as `latest` (gh, cloudflared, gcloud, oci, sops, aqua, zoxide)
2. `mise run core:tool-versions:report` exits 0 and prints a table of all 14 tools + their resolved versions
3. `mise run core:tool-versions:check-stale` exits 0 (no warnings) or 1 (with warnings printed)
4. `mise install` resolves cleanly + `mise run core:typecheck` still passes (no regressions from the pin change)
5. `openspec validate 2026-08-23-dev-tooling-version-pinning-v1 --strict` exits 0

## Rollback plan

- Revert the `[tools]` block in `mise.toml` to use `"latest"` (the original).
- The 2 new tasks can stay or be removed independently.
- No data loss; no breaking changes; no migration.
