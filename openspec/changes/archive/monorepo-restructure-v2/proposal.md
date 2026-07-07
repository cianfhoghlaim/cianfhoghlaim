# Monorepo Restructure v2 — Polyglot bun + uv + turbo

## Why

The root `package.json` and `pyproject.toml` have drifted into broken states that block developer onboarding and CI:

1. **Root `package.json` referenced six `sruth/*` paths that no longer exist** (the repo was restructured into `sruth/oideachais/`, `sruth/tuatha/`, `códeolas_codebase_indexing/`, etc. but the root scripts were not updated).
2. **24 root dependencies are unused** — TanStack, Convex, Hono, Pulumi, Vite, etc. are properly declared in nested packages but pollute the root lockfile.
3. **Root `pyproject.toml` was a 251-line verbatim duplicate of `sruth/oideachais/pyproject.toml`** — no uv workspace, no shared tooling.
4. **Secret-bootstrap scripts were hidden in `scripts/infisical/`** with their own `package.json` and `bun.lock` — they belong at the root.
5. **`turbo.json` was minimal** (4 tasks, no `test`, no `dagster`, no `ccc:index`, no `spec:validate`) and referenced a Next.js output cache that we never use.
6. **`mise.toml` still pointed at the old `sruth/oideachas/`, `sruth/tuath/`, `sruth/teanga/` dagster code-locations**.
7. **`AGENTS.md` and `README.md` did not document** the bun workspace model, the uv workspace model, the turbo pipeline, the `bun run secrets:init` workflow, or the `bun run ccc:search` / `bun run spec:validate` developer loop.

This change brings the root manifests and developer docs in line with the actual post-restructure directory layout, makes the secret-bootstrap scripts a first-class part of the root toolchain, and gives the repo a single source of truth (`turbo.json` + `mise.toml`) for cross-language task orchestration.

## What Changes

- **Add** bun workspaces to the root `package.json` (`sruth/oideachais/web`, `sruth/oideachais/mcp/filesystem`, `sruth/tuatha/ui`).
- **Add** uv workspace to the root `pyproject.toml` (members: `oideachais`, `tuatha`, `códeolas_codebase_indexing`, `infrastructure/browser`, `sruth/oideachais/mcp/mcpo`).
- **Add** root-level scripts: `setup`, `secrets:env`, `secrets:init`, `secrets:sync`, `komodo:sync`, `pangolin:check`, `locket:exec`, `ccc:init`, `ccc:index`, `ccc:search`, `spec:list`, `spec:validate`, `spec:archive`.
- **Move** `scripts/infisical/{init-vault.ts, create-env.ts}` → `scripts/` and patch their `process.cwd()`-relative paths (was `../../`, now `./`).
- **Delete** `scripts/infisical/` directory entirely.
- **Remove** the 24 unused root dependencies from `package.json`.
- **Remove** the 6 broken `dev:oideachas/codeolas/scoil/gaois/tuath/tionscnamh` scripts.
- **Remove** the 3 broken `docs:dev/build/serve` scripts (no `docs-site/` exists).
- **Remove** the 2 broken `dagger:*` scripts (no `bonneagar/dagger/` exists).
- **Rewrite** `turbo.json` with the full task graph (`postinstall`, `build`, `dev`, `typecheck`, `lint`, `format`, `test`, `clean`, `dagster`, `ccc:index`, `spec:validate`) and explicit `globalEnv` for `INFISICAL_*`, `BROWSERBASE_*`, `FIRECRAWL_*`, `MOTHERDUCK_*`, `GOOGLE_VERTEX_*`, `GEMINI_*`, `DAGSTER_HOME`, `LOCKET_*`, `KOMODO_*`, `PANGOLIN_*`.
- **Patch** `mise.toml`: drop every `cd sruth/*` task, add `turbo`, `ccc:init/index/search`, `secrets:env/init/sync`, `locket:exec`, `komodo:sync`, `pangolin:check`, `openspec:list/validate/archive` aliases.
- **Add** missing top-level sections to `AGENTS.md` (Monorepo Topology, Secrets Bootstrap, Codebase Indexing & Spec-Driven Development) and patch the existing "Strict Secret Hydration" reference from `scripts/infisical/init-vault.ts` to `scripts/init-vault.ts`.
- **Add** Quickstart and Monorepo Topology sections to `README.md`.
- **Migrate** `sruth/bonneagar/stacks/tools/stirling-pdf/` → `infrastructure/stacks/stirling-pdf/` and delete the now-empty `sruth/` directory.
- **Add** ASCII-named `[tool.uv.sources]` entries (`codeolas`, `sruth-browser`, `oideachais`, `tuath`) to all member `pyproject.toml` files (TOML forbids non-ASCII unquoted keys, so `códeolas` becomes `codeolas`).
- **Add** a real `package.json` to `sruth/tuatha/ui/` (was missing — only a stale `bun.lock` remained) and add a `name` field to `sruth/oideachais/mcp/filesystem/package.json` (was missing — bun rejected it).

## Impact

| Surface | Before | After |
|:--|:--|:--|
| Root `package.json` size | 63 lines, 24 unused deps, 12 broken scripts | 75 lines, 2 deps, 30 working scripts |
| Root `pyproject.toml` size | 259 lines, duplicate of oideachais | 142 lines, workspace shell |
| Workspace members | 0 (no `workspaces` field) | 3 bun + 5 uv |
| Secret-bootstrap discoverability | Hidden in `scripts/infisical/` | Root `bun run secrets:init` |
| `turbo.json` tasks | 4 | 11 |
| `mise.toml` tasks | 21 (3 broken) | 36 (all working) |
| Stale `sruth/` references | 8 | 0 |
| `bun install` | failed (no workspaces, missing name fields) | succeeds (790 packages) |
| `uv sync` | succeeded for individual members only | succeeds for whole monorepo (469 packages, single lockfile) |
| Secret-sync runtime | hidden 3-level-nested bun script | root-level bun script, runs end-to-end, seeds 24 secrets |

## Out of scope

- Pinning `'latest'` versions in `sruth/oideachais/web/package.json` and `sruth/tuatha/ui/package.json` — deferred to a follow-up change.
- Renaming `códeolas_codebase_indexing/` back to `códeolas/` — directory name is the user's choice; only the workspace `members` path was updated to match.
- Cleaning the pre-existing `.infisical.env` entries that point at the non-existent `aleyum` environment — that is a data-quality issue for the secrets template, not a manifest issue.
- Modifying the 60+ Komodo stacks in `infrastructure/stacks/`.
- Modifying `opencode.json` / `.opencode.yaml` agent and MCP server configuration.
