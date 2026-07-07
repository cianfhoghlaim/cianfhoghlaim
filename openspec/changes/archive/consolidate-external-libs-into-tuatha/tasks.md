# Tasks — Consolidate External Libraries into `sruth/tuatha/`

## Phase 0 — Pre-Move

- [x] 1. Create `openspec/changes/consolidate-external-libs-into-sruth/tuatha/{proposal.md, tasks.md, specs/}`.
- [x] 2. Inspect in-progress git state: 765 modified/deleted files (prior rename of `códeolas/` → `códeolas_codebase_indexing/`, move of `sruth/tuatha/formative_education_cryptocurrency/` → `crypteolas_formative_assessment/`, deletion of root `baml_src/`). Treat the working tree as the source of truth and proceed.

## Phase 1 — `codeolas` (Aggressive Dedup)

- [ ] 3. `mv códeolas_codebase_indexing sruth/tuatha/codeolas`
- [ ] 4. `rm sruth/tuatha/codeolas/uv.lock`
- [ ] 5. `rm sruth/tuatha/codeolas/generators/arch_generator.py` (dup of `arch.py`)
- [ ] 6. `rm sruth/tuatha/codeolas/storage/lance.py` (dup of `lance_catalog.py`)
- [ ] 7. `rm -rf sruth/tuatha/codeolas/flows` (dup of `cocoindex_flows/`)
- [ ] 8. `rm -rf sruth/tuatha/codeolas/pipelines` (dup of `dagster_assets/`)
- [ ] 9. `rm -rf sruth/tuatha/codeolas/mcp` (dup of `mcp_server/`)
- [ ] 10. `rm -rf sruth/tuatha/codeolas/agents` (all dead stubs)
- [ ] 11. Rewrite all `sruth.códeolas.*` → `codeolas.*` imports (~25 sites, 12 files)
- [ ] 12. Update `sruth/tuatha/codeolas/pyproject.toml` entry points: `codeolas.cli:main`, `codeolas.mcp_server.server:main`, `codeolas.dagster_assets.definitions:defs`
- [ ] 13. Add stub `sruth/tuatha/codeolas/generators/changelog.py` with `ChangelogGenerator` class (for `test_generators.py`)
- [ ] 14. Fix `tests/test_research.py` hard-coded `/Users/cliste/dev/cianfhoghlaim` path
- [ ] 15. Fix `tests/test_multilang_chunking.py` path resolution
- [ ] 16. Update `sruth/tuatha/codeolas/compose.yaml` and `compose.dev.yaml` volume binds
- [ ] 17. Update `sruth/tuatha/codeolas/.forgejo/workflows/{ci,release}.yaml` path filters
- [ ] 18. Create `sruth/tuatha/codeolas/STATUS.md` documenting all dropped duplicates

## Phase 2 — `crypteolas` (Drop DSPy, Dedup Notebooks, BAML Rename)

- [ ] 19. `mv crypteolas_formative_assessment sruth/tuatha/crypteolas`
- [ ] 20. `rm sruth/tuatha/sruth/crypteolas/uv.lock`
- [ ] 21. `rm -rf sruth/tuatha/sruth/crypteolas/.tmp_dagster_home_*` (ephemeral)
- [ ] 22. `rm -rf sruth/tuatha/sruth/crypteolas/dspy` (~600 vendored files, never imported)
- [ ] 23. `rm sruth/tuatha/sruth/crypteolas/notebooks/01_github_explorer.py` (dup of `01_github_api_explorer.py`)
- [ ] 24. `rm sruth/tuatha/sruth/crypteolas/notebooks/04_defi_dashboard.py` (dup of `04_unified_dashboard.py`)
- [ ] 25. BAML rename: `mv sruth/tuatha/baml_src/clients.baml sruth/tuatha/baml_src/tuatha_clients.baml`
- [ ] 26. Update all `sruth/tuatha/baml_src/*.baml` references to use `tuatha_clients.baml` generator
- [ ] 27. Rewrite all `from crypteolas.X import Y` → `from tuatha.crypteolas.X import Y` (17 files, ~50 sites)
- [ ] 28. Resolve dead `sruth.crypteolas.*` and `sruth.shared.*` imports with thin local shims or documented stubs
- [ ] 29. Fix `tests/test_knowledge_graph.py` to point at real file names (`cognee/static_knowledge`, `graphiti/temporal_graph`)
- [ ] 30. Add TODO comment to `sruth/tuatha/sruth/crypteolas/wrangler.toml` about missing `workers/index.ts`
- [ ] 31. Relocate all `*.md` docs to `sruth/tuatha/sruth/crypteolas/docs/`
- [ ] 32. Create `sruth/tuatha/sruth/crypteolas/STATUS.md` documenting drops, shims, and TODOs

## Phase 3 — `apps/crypteolas_demo` (Flatten + Stub TS)

- [ ] 33. `mkdir -p sruth/tuatha/apps && mv sruth/tuatha/tuatha_1 sruth/crypteolas/apps/crypteolas_demo`
- [ ] 34. `rm sruth/crypteolas/apps/crypteolas_demo/uv.lock`
- [ ] 35. Rewrite `sruth/crypteolas/apps/crypteolas_demo/__init__.py` (re-exports `.crypto_agents` + `.mcp_tools` public surface)
- [ ] 36. Flatten the `fibo` namespace: rewrite `from fibo.X import Y` → `from X import Y` in `definitions.py`, `defs/__init__.py`, `pipelines/__init__.py`, `pipelines/defs/*.py`
- [ ] 37. Update `pyproject.toml`: `name = "fibo"` → `name = "crypteolas_demo"`, `root_module = "fibo"` → `root_module = "crypteolas_demo"`
- [ ] 38. Reconcile 12 `from crypteolas.X import Y` imports inside the demo → `from tuatha.crypteolas.X import Y`
- [ ] 39. Drop the `agno` service from `docker-compose.yaml` (broken build context; `sruth/tuatha/agents/orchestrator.py` covers orchestration)
- [ ] 40. Create stub `sruth/crypteolas/apps/crypteolas_demo/package.json` (Vinxi + React 19 + Wagmi deps)
- [ ] 41. Create stub `sruth/crypteolas/apps/crypteolas_demo/tsconfig.json`
- [ ] 42. Create stubs for the 12 missing `src/lib/*` modules (auth, x402, copilot, query, web3, mcp)
- [ ] 43. Create stub `models/{__init__,colpali,qwen_vlm,fibo_mlx}.py` (raise `NotImplementedError`)
- [ ] 44. Update `scéimre/generators.baml` `output_dir` → `"./baml_client"` (isolated)
- [ ] 45. Update `Dockerfile` `pnpm-lock.yaml*` → `bun.lock*`
- [ ] 46. Create `sruth/crypteolas/apps/crypteolas_demo/STATUS.md` documenting all stubs and gaps

## Phase 4 — Wire into Deployment

- [ ] 47. Update root `pyproject.toml` `[tool.uv.workspace] members` to add `"sruth/tuatha/codeolas"`, `"sruth/tuatha/crypteolas"`, `"sruth/crypteolas/apps/crypteolas_demo"`
- [ ] 48. Update root `dg.toml` to include all code-locations
- [ ] 49. Update `sruth/tuatha/pyproject.toml` `[tool.hatch.build.targets.wheel] packages` to add `codeolas`, `crypteolas` + the 5 existing-but-missing sub-packages
- [ ] 50. Add missing dependencies to `sruth/tuatha/pyproject.toml` (tree-sitter, langfuse, ddtrace, dlt[lancedb,duckdb], dlthub, cognee, marimo, ibis, graphiti-core, falkordb, crawl4ai, firecrawl-py, dagster-embedded-elt, etc.)
- [ ] 51. Update `sruth/tuatha/dg.toml` to add 2 new `[[project]]` blocks (crypteolas, crypteolas_demo)
- [ ] 52. Update root `package.json` `workspaces` to add `"sruth/crypteolas/apps/crypteolas_demo"`
- [ ] 53. Update `mise.toml` to add `dagster:tuath/sruth/crypteolas/crypteolas_demo` + `test:codeolas/sruth/crypteolas/crypteolas_demo` aliases

## Phase 5 — Validation

- [ ] 54. `uv sync` succeeds
- [ ] 55. `bun install` succeeds
- [ ] 56. `cd tuatha && uv run python -c "from codeolas import CodebaseAnalyzer; print('OK')"`
- [ ] 57. `cd tuatha && uv run python -c "from crypteolas.definitions import defs; print(len(defs.assets))"`
- [ ] 58. `cd sruth/crypteolas/apps/crypteolas_demo && uv run python -c "from crypteolas_demo import CryptoResearchAgent; print('OK')"`
- [ ] 59. `cd tuatha && uv run pytest codeolas/tests/ sruth/crypteolas/tests/ -v`
- [ ] 60. `cd sruth/crypteolas/apps/crypteolas_demo && bun install && bun run typecheck`
- [ ] 61. `bun run ccc:index` rebuilds the semantic index
- [ ] 62. `bun run turbo typecheck && bun run turbo lint`

## Phase 6 — Landing the Plane

- [ ] 63. `git pull --rebase`
- [ ] 64. `git add -A`
- [ ] 65. `git commit -m "refactor(tuatha): consolidate códeolas, crypteolas, crypteolas_demo"`
- [ ] 66. `git push`
- [ ] 67. `git status` shows "up to date with origin"

## Followup (file as separate issue, out of scope here)

- [ ] 68. File followup issue: simplify `sruth.shared.*` abstraction in `sruth/tuatha/dlt_sources/geospatial/{gaeltacht_boundaries,welsh_language_areas,gaelic_communities}.py` and `sruth/tuatha/storage/serial_executor.py`. Plan: inline HTTP clients per-source (or use `sruth/tuatha/http_utils/`), avoid external shared packages, keep code directed at fitting in with the existing `sruth/tuatha/dlt_sources/geospatial/` assets.
