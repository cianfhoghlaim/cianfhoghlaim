# Change: sync-skills-from-docs

## Why

The `docs/{lance,dlt,dagster,cocoindex,baml}/` subtree is **85 MiB of
mirror material** (1,800+ files) that has drifted out of sync with the
authoritative skills at `.agents/skills/{lancedb,dlt,dagster,cocoindex,baml}/`.
Three concrete problems result:

1. **CocoIndex v0 skill, v1 code.** The `cocoindex` skill documents the
   v0 flow-builder DSL (`@cocoindex.flow_def`, `data_scope`, `.row()`,
   `cocoindex.sources.X`, `cocoindex.targets.X`). The project's own
   `sruth/oideachais/cocoindex_flows/*.py` and every rewritten example in
   `docs/cocoindex/` use the v1 API (`@coco.fn`, `coco.App`,
   `ContextKey`, `mount_table_target`, `mount_each`,
   `Annotated[NDArray, EMBEDDER]`). Agents reading the skill hallucinate
   the v0 DSL. The `cocoindex-v1-migration` spec is the source of truth
   for the v1 surface; the skill must match.
2. **BAML skill is a 9-line stub.** The `baml` skill carries only the 3
   project rules; the 4 example projects in `docs/baml/` introduce
   four major patterns (dynamic schemas, runtime evals, auto-retry,
   multimodal vision) that are not documented anywhere in the skill.
3. **The dlt, dagster, and lancedb skills are router-only / basics-only.**
   Each skill has solid surface but is missing the project-specific
   patterns surfaced in the docs subdirs (lancedb time-travel, dlt
   `lancedb_adapter`, dagster `DuckLakeResource`, etc.).

## What Changes

- **Replace** `.agents/skills/cocoindex/SKILL.md` (852 lines, v0) and
  its 4 v0 references (`flow_patterns.md`, `custom_functions.md`,
  `cli_operations.md`, `api_operations.md`) with a v1 SKILL.md (~400
  lines) + 13 new v1 reference files. Add a `v0-to-v1-migration.md`
  reference so an agent that has read old code can translate.
- **Expand** `.agents/skills/baml/SKILL.md` from 9 lines to ~300 lines
  + 6 new reference files (dynamic-schemas, runtime-evals, auto-retry,
  multimodal-vision, streaming-and-typebuilder, clients-and-retries).
  Deprecate the two 1,000+ line upstream BoundaryML reference files.
- **Expand** `.agents/skills/dlt/SKILL.md` from 28 lines to ~120 lines
  (router + decision tree + project recipes + reference index) + 13
  new reference files (destinations-lancedb, destinations-cognee-memgraph,
  destinations-graphiti, performance-optimisation, dagster-dlt-assets,
  openapi-generator, deploy-gcp-*, deploy-modal, sqlmesh-init,
  dlt-transformations, crawl4ai-dlt-summary). Link the 3 existing
  orphan references (`dlthub.md`, `dlthub-codebase-analysis.md`,
  `dlt-baml-orpc-mcp-typesafe-pipeline-analysis.md`) so they are no
  longer orphans. Fix the path bug: `dlt_sources` lives at
  `sruth/oideachais/dlt_sources/`, not `sruth/oideachais/data_platform/dlt_sources/`.
- **Expand** `.agents/skills/lancedb/SKILL.md` (bump version `>=0.26.0`)
  with 30+ advanced patterns + 10 new reference files
  (time-travel-rag, embed-functions-registry, advanced-rag-patterns,
  multimodal-fat-tables, lancedb-cloud, lance-namespace-and-iceberg,
  ibis-integration, typescript-modern-api, lance-ray-distributed,
  lance-vs-iceberg, geospatial-fts). Update the TypeScript section to
  use the modern `search()` API (replacing the deprecated
  `vectorSearch()`).
- **Expand** `.agents/skills/dagster/SKILL.md` (keep the 84-line
  skeleton) with 5 new reference files synthesised from the
  `docs/dagster/integrations/` subdirs: `integrations/dagster-ducklake/INDEX.md`,
  `integrations/dagster-sqlmesh/INDEX.md`,
  `integrations/dagster-dlt/parallel-github.md`,
  `deployment/docker-self-hosted.md`,
  `orchestration/kcg-cocoindex-graphiti.md`.
- **Delete** the 5 docs subdirectories after the skills are
  updated: `docs/lance/` (18M), `docs/dlt/` (9.9M), `docs/dagster/`
  (5.3M), `docs/cocoindex/` (48M), `docs/baml/` (3.6M). The misfiled
  `docs/baml/2025-12-09-git-worktrees/` (no `baml_src/`, no Python —
  a 32-line markdown on parallel agent infra) is also removed.

## Project rules PRESERVED (not changed)

- **BAML**: `.baml` files in `sruth/oideachais/baml_src/`; Zod-like
  constraints; schemas map to DuckLake tables in
  `sruth/oideachais/dlt_sources/ireland/`.
- **DLT**: DuckLake/DuckDB destination; `DLT_DISABLE_PLUGINS=true`
  during tests; relative imports (no `oideachais.data_platform...`);
  `USE_LOCAL_SCRAPES=true` offline fallback.
- **Dagster**: `ireland/curriculum/` MultiPartitions by
  `language + subject`; `USE_DUCKLAKE=true` for MotherDuck; no
  absolute namespaces.
- **LanceDB**: `>=0.26.0` (was `>=0.15.0`); HNSW for accuracy;
  MVCC-safe with circuit breaker.
- **CocoIndex**: every flow is a `coco.App` with `@coco.fn` and
  stable identity; memoize expensive ops; `ContextKey` for shared
  resources; `localfs.walk_dir(..., live=True)`; `mount_table_target`
  for LanceDB; `Annotated[NDArray, EMBEDDER]` for vector dimensions.

## Impact

- **Affected specs (5)**:
  - `oideachais-baml-schemas` — adds 8 new requirements
    (dynamic schemas, runtime evals, auto-retry, multimodal,
    streaming, TypeBuilder, multi-generator, named clients).
  - `oideachais-pipeline` — adds 5 new requirements
    (Dagster DuckLake resource, self-hosted Docker deploy, DLT
    parallel-asset factory, SQLMesh translator, KCG orchestration
    pattern).
  - `oideachais-semantic-search` — adds 8 new requirements
    (lancedb time-travel, embeddings registry, context-enrichment-window,
    multimodal fat table, modern TS API, LanceDB Cloud regions,
    Lance + Iceberg, Ibis + lance_scan, lance-ray, geospatial+FTS).
  - `oideachais-leabharlann` — adds 7 new requirements
    (v1 App conventions, mount_table_target, mount_each, ContextKey,
    Annotated[NDArray, EMBEDDER], detect_change, IdGenerator).
  - `oideachais-cognify-knowledge-graph` — adds 3 new requirements
    (BAML+TypeBuilder, DLT→Cognee→Memgraph fan-out, runtime evals
    + auto-retry loop).

- **Affected code**: none. The skills are documentation; the
  project's v1 code is already correct.

- **Affected skills** (5): `baml`, `cocoindex`, `dagster`, `dlt`,
  `lancedb`.

## Success criteria

- `openspec validate sync-skills-from-docs --strict` passes
  (twice — once at authoring, once at archive).
- The rewritten `cocoindex` skill uses v1 APIs only; no v0 symbols
  (`@cocoindex.flow_def`, `data_scope`, `.row()`, `add_collector()`,
  `cocoindex.sources.X`, `cocoindex.targets.X`,
  `cocoindex.functions.SplitRecursively`,
  `cocoindex.functions.SentenceTransformerEmbed`) appear in the
  SKILL.md or any reference file.
- The new `baml` skill documents the 4 new patterns (dynamic
  schemas, runtime evals, auto-retry, multimodal) and links
  `sruth/oideachais/baml_src/ocr_extraction.baml` as the in-repo OCR
  example for multimodal.
- The new `dlt` skill correctly cites `sruth/oideachais/dlt_sources/`
  (not `data_platform/dlt_sources/`) and links all 3 orphan
  reference files.
- The new `lancedb` skill uses the modern TypeScript API
  (`search()`, not `vectorSearch()`) and documents the
  `get_registry().get("openai")` pattern.
- The new `dagster` skill exposes 5 new KCG-relevant reference
  files.
- All 5 `docs/{lance,dlt,dagster,cocoindex,baml}/` subdirectories
  are removed (verified by `ls docs/lance` returning ENOENT).
- The `docs_skills_consolidation` CocoIndex v1 App (the upstream
  indexer) still loads cleanly; the rewritten skill content is
  picked up on the next live run.

## Rollback

The change is documentation-only. Rollback = restore the 5 docs
subdirectories from git (`git checkout HEAD~1 -- docs/lance docs/dlt
docs/dagster docs/cocoindex docs/baml`) and revert the skill files.
No data, code, or runtime state is affected.

## Out of scope

- Adding new v1 CocoIndex Apps (the project already has them).
- Migrating any BAML file to use `@@dynamic` or the TypeBuilder
  pattern (that's a follow-on refactor; the skill *enables* it
  but does not mandate it).
- Restructuring the `dlt` skill into a sub-skill dispatcher (the
  router pattern is preserved; the new content is added as
  references and a decision tree, not as new sub-skills).
