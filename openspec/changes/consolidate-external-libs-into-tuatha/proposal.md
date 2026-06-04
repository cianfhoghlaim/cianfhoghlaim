# Consolidate External Libraries into `tuatha/`

## Why

The Cianfhoghlaim monorepo currently has three external Python/TypeScript projects
sitting at inconsistent locations:

1. **`códeolas_codebase_indexing/`** — the publishable `codeolas` Python library
   (semantic code search, knowledge graph, MCP server, Dagster assets). 76 source
   files, 10K LOC, with massive internal duplication (6 pairs of near-identical files)
   and broken entry points in `pyproject.toml` pointing at non-existent
   `sruth.códeolas.*` paths.
2. **`crypteolas_formative_assessment/`** — the `github-intelligence` Python
   platform (DLT, CocoIndex, Cognee, Marimo) for GitHub data ingestion and DeFi
   protocol research. ~50 source files + a 600-file vendored DSPy tree that is
   never imported, plus 2 pairs of duplicate marimo notebooks. 17 of its
   sub-package names collide with existing `tuatha/` packages (different content
   for the Celtic MMO).
3. **`tuatha/tuatha_1/`** — the `fibo` Python + TanStack Start + Gradio demo app
   ("Crypteolas Demo") with 12 hard imports pointing at the external
   `crypteolas.*` namespace (which is not a registered workspace source) and a
   missing `package.json` / `tsconfig.json` / `src/lib/` skeleton.

A prior `monorepo-restructure-v2` change (see `openspec/changes/monorepo-restructure-v2/`)
moved the old `códeolas/` and `tuatha/formative_education_cryptocurrency/` paths
out of the way and re-rooted them at the working-tree locations above, but did
not finish the consolidation into `tuatha/`. This change completes the work:
all three external packages become sub-packages of the `tuath` uv workspace
member, the deployment pipeline learns about all three code-locations, and
nothing is lost.

## What Changes

### Directory moves

- **Move** `códeolas_codebase_indexing/` → `tuatha/codeolas/`
- **Move** `crypteolas_formative_assessment/` → `tuatha/crypteolas/`
- **Move** `tuatha/tuatha_1/` → `tuatha/apps/crypteolas_demo/`

### `codeolas` cleanup (aggressive dedup)

- **Drop** the duplicate `generators/arch_generator.py` (verbatim copy of `arch.py`).
- **Drop** the duplicate `storage/lance.py` (keep `lance_catalog.py` which has
  the `EmbeddingModel` enum + dataclass-aware formatting).
- **Drop** the duplicate `flows/` directory (keep `cocoindex_flows/` which is
  the registered CocoIndex flow variant).
- **Drop** the duplicate `pipelines/` directory (keep `dagster_assets/` which
  imports from `cocoindex_flows`).
- **Drop** the duplicate `mcp/` directory (keep `mcp_server/` with the typed
  `Tool` dataclass registry; `mcp/` only has a Datadog-traced variant).
- **Drop** the entire dead `agents/` tree (all stubs raise `NotImplementedError`).
- **Drop** the per-member `uv.lock` (root will regenerate).
- **Rewrite** all `sruth.códeolas.*` imports → `codeolas.*` (~25 sites, 12 files).
- **Fix** `tests/test_generators.py` by adding a stub `generators/changelog.py`
  with a `ChangelogGenerator` class.
- **Fix** `tests/test_research.py` hard-coded path `/Users/cliste/dev/cianfhoghlaim`
  → `os.environ.get("REPO_PATH", os.getcwd())`.
- **Fix** `tests/test_multilang_chunking.py` path resolution to use
  `Path(__file__).parent / "core" / "analyzer.py"`.
- **Fix** `pyproject.toml` entry points:
  - `codeolas = "codeolas.cli:main"`
  - `codeolas-mcp = "codeolas.mcp_server.server:main"`
  - Dagster `codeolas = "codeolas.dagster_assets.definitions:defs"`
- **Update** `compose.yaml` / `compose.dev.yaml` volume binds to new sub-path.
- **Update** `.forgejo/workflows/ci.yaml` and `release.yaml` path filters
  (`codeolas/**` → `tuatha/codeolas/**`).
- **Document** all dropped duplicates in `tuatha/codeolas/STATUS.md`.

### `crypteolas` cleanup (drop DSPy, dedup notebooks)

- **Drop** the entire `dspy/` directory (~600 vendored files, never imported).
- **Drop** `notebooks/01_github_explorer.py` (keep `01_github_api_explorer.py`).
- **Drop** `notebooks/04_defi_dashboard.py` (keep `04_unified_dashboard.py`).
- **Drop** the per-member `uv.lock` (root will regenerate).
- **Drop** ephemeral `.tmp_dagster_home_*/` directories.
- **Rewrite** all `from crypteolas.X import Y` → `from tuatha.crypteolas.X import Y`
  (17 files, ~50 sites).
- **Resolve** dead `sruth.crypteolas.*` and `sruth.shared.*` imports in
  `agent_os/main.py`, `agents/adk/architecture_agent.py`,
  `dagster_assets/components/__init__.py`, `dagster_assets/lakekeeper_examples.py`
  with thin local shims or documented stubs in `STATUS.md`.
- **Fix** `tests/test_knowledge_graph.py` to point at the real file names
  (`cognee/static_knowledge`, `graphiti/temporal_graph`).
- **Add** TODO comment in `wrangler.toml` explaining the missing
  `workers/index.ts`.
- **Document** all drops, shims, and TODOs in `tuatha/crypteolas/STATUS.md`.
- **Relocate** all `*.md` docs to `tuatha/crypteolas/docs/` for tidiness.

### `tuatha/apps/crypteolas_demo` cleanup (flatten + stub TS)

- **Flatten** the `fibo` namespace: rewrite `from fibo.X import Y` →
  `from X import Y` in `definitions.py`, `defs/__init__.py`, `pipelines/__init__.py`,
  `pipelines/defs/*.py`.
- **Rewrite** the broken `__init__.py` (it imports `from agents.crypto_agents`
  and `from agents.mcp_tools` which don't exist; the files are at the package
  root) to import from `.crypto_agents` and `.mcp_tools` directly and
  re-export the public surface.
- **Rewrite** `pyproject.toml`: `name = "fibo"` → `name = "crypteolas_demo"`,
  `root_module = "fibo"` → `root_module = "crypteolas_demo"`.
- **Reconcile** the 12 `from crypteolas.X import Y` imports inside
  `tuatha_1/` — point them at the new `tuatha.crypteolas.*` workspace source.
- **Drop** the `agno` service from `docker-compose.yaml` (the
  `build.context: "../../../.."` + `dockerfile: demo/Dockerfile.agno` is
  broken; the existing `tuatha/agents/orchestrator.py` covers the
  orchestration need).
- **Create stub** `package.json` and `tsconfig.json` for the TanStack Start
  app so `bun install` and `bun run typecheck` work.
- **Create stubs** for the 12 missing `src/lib/*` modules (auth, x402,
  copilot, query, web3, mcp) — each with TODO and minimal type signature.
- **Create stub** `models/{colpali,qwen_vlm,fibo_mlx}.py` so
  `defs/curriculum/resources.py`, `defs/fibo_generation/resources.py`, and
  `ui/components/image_preview.py` can at least import successfully (raise
  `NotImplementedError` at runtime).
- **Update** `scéimre/generators.baml` `output_dir = "../baml_client"` →
  `"./baml_client"` (keeps the demo self-contained; doesn't pollute the
  main `tuatha/baml_client/`).
- **Update** `Dockerfile` `pnpm-lock.yaml*` references to `bun.lock*`.
- **Document** every stub and gap in `tuatha/apps/crypteolas_demo/STATUS.md`.

### BAML reconciliation (one combined `baml_client/`)

- **Rename** `tuatha/baml_src/clients.baml` → `tuatha/baml_src/tuatha_clients.baml`.
- **Update** all references in `tuatha/baml_src/*.baml` files to use the renamed
  generator.
- **Generate** one combined `tuatha/baml_client/` from
  `tuatha/baml_src/` + `tuatha/crypteolas/baml_src/`.
- The crypteolas_demo app gets its own isolated `tuatha/apps/crypteolas_demo/baml_client/`
  from `scéimre/`.

### Deployment wiring

- **Update** root `pyproject.toml` `[tool.uv.workspace] members` to add
  `"tuatha/codeolas"`, `"tuatha/crypteolas"`, `"tuatha/apps/crypteolas_demo"`.
- **Update** root `dg.toml` to include the new code-locations.
- **Update** `tuatha/pyproject.toml` `[tool.hatch.build.targets.wheel] packages`
  to add `codeolas`, `crypteolas` (plus the 5 existing sub-packages that were
  missing: `asset_generation`, `dlt_utils`, `fibo_generation`, `tests`, `demo`).
- **Add** missing dependencies to `tuatha/pyproject.toml`: `tree-sitter`,
  `tree-sitter-languages`, `langfuse`, `ddtrace`, `tiktoken`, `mcp`, `agno`,
  `cocoindex`, `dlt[lancedb,duckdb]`, `dlthub`, `cognee`, `marimo`,
  `ibis-framework[duckdb]`, `graphiti-core`, `falkordb`, `crawl4ai`,
  `firecrawl-py`, `dagster-embedded-elt`.
- **Update** `tuatha/dg.toml` to add two new `[[project]]` blocks for the
  `crypteolas` and `crypteolas_demo` code-locations.
- **Update** root `package.json` `workspaces` to add
  `"tuatha/apps/crypteolas_demo"`.
- **Update** `mise.toml` to add `dagster:tuath`, `dagster:crypteolas`,
  `dagster:crypteolas_demo`, `test:codeolas`, `test:crypteolas`,
  `test:crypteolas_demo` aliases.
- **No changes** to `turbo.json` — its task graph already covers everything.

### Follow-up issue (out of scope)

- **File** a follow-up issue for the four pre-existing broken
  `sruth.shared.*` imports in `tuatha/dlt_sources/geospatial/{gaeltacht_boundaries,
  welsh_language_areas, gaelic_communities}.py` and
  `tuatha/storage/serial_executor.py`. The plan for that follow-up: simplify
  the `sruth.shared.*` abstraction entirely, inline HTTP clients per-source
  (or use the existing `tuatha/http_utils/` layer), avoid external shared
  packages, and keep code directed at fitting in with the existing
  `tuatha/dlt_sources/geospatial/` assets.

## Impact

| Surface | Before | After |
|:--|:--|:--|
| Top-level dirs | 3 (códeolas_codebase_indexing, crypteolas_formative_assessment, tuatha/tuatha_1) | 0 (all consolidated into tuatha/) |
| codeolas source files | 76 (with 6 duplicate pairs) | 64 (deduped) |
| codeolas public imports | Broken (point to non-existent `sruth.códeolas.*`) | Working (`codeolas.*`) |
| crypteolas source files | ~50 + 600 vendored DSPy | ~50 (DSPy dropped) |
| crypteolas notebooks | 6 (2 duplicate pairs) | 4 (deduped) |
| Crypteolas_demo TS app | Cannot build (no package.json) | Can install + typecheck (stubs) |
| Dagster code-locations | 1 (tuath) | 3 (tuath, crypteolas, crypteolas_demo) |
| UV workspace members | 5 | 8 |
| bun workspaces | 3 | 4 |
| Hatch wheel packages | 7 (out of sync with reality) | 12 (correct) |
| OpenSpec changes in flight | 0 (this is the new one) | 1 |

## Validation

- [ ] `uv sync` succeeds
- [ ] `bun install` succeeds
- [ ] `cd tuatha && uv run python -c "from codeolas import CodebaseAnalyzer"` works
- [ ] `cd tuatha && uv run python -c "from crypteolas.definitions import defs; print(len(defs.assets))"` works
- [ ] `cd tuatha/apps/crypteolas_demo && uv run python -c "from crypteolas_demo import CryptoResearchAgent"` works
- [ ] `cd tuatha && uv run pytest codeolas/tests/ crypteolas/tests/ -v` passes
- [ ] `cd tuatha/apps/crypteolas_demo && bun install && bun run typecheck` succeeds
- [ ] `bun run ccc:index` rebuilds the semantic index
- [ ] `bun run turbo typecheck && bun run turbo lint` passes
- [ ] `git status` shows the working tree ready to commit with all renames
- [ ] `git push` succeeds and `git status` shows "up to date with origin"
