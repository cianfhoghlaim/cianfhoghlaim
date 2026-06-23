# Tasks: sync-skills-from-docs

## 1. Create OpenSpec change scaffolding

- [x] Create `openspec/changes/sync-skills-from-docs/` directory tree.
- [x] Write `proposal.md` (context, what/why, scope, impact, success
      criteria, rollback).
- [x] Write `tasks.md` (this file).
- [x] Write 5 spec deltas (one per affected spec).
- [x] Run `openspec validate sync-skills-from-docs --strict`.

## 2. Rewrite `cocoindex` skill (v0 → v1)

- [x] Delete `.agents/skills/cocoindex/SKILL.md` (852 lines, v0).
- [x] Delete `.agents/skills/cocoindex/references/flow_patterns.md`
      (478 lines, v0).
- [x] Delete `.agents/skills/cocoindex/references/custom_functions.md`
      (467 lines, v0).
- [x] Delete `.agents/skills/cocoindex/references/cli_operations.md`
      (v0).
- [x] Delete `.agents/skills/cocoindex/references/api_operations.md`
      (v0).
- [x] Create new `SKILL.md` (~400 lines, v1).
- [x] Create `references/v0-to-v1-migration.md` (the v0→v1
      translation table).
- [x] Create `references/baml-extraction.md` (BAML in CocoIndex v1).
- [x] Create `references/knowledge-graph-build.md` (3-phase KG build).
- [x] Create `references/live-updates.md` (live mode pattern).
- [x] Create `references/fastapi-server.md` (FastAPI server pattern).
- [x] Create `references/multimodal-image-search.md` (CLIP / ColPali).
- [x] Create `references/rust-port.md` (Rust port reference).

## 3. Expand `baml` skill (9 lines → ~300 + 6 refs)

- [x] Update `.agents/skills/baml/SKILL.md` to add 4 new pattern
      sections (dynamic schemas, runtime evals, auto-retry,
      multimodal vision) + BAML syntax features + project conventions
      + anti-patterns. Preserve the 3 existing rules verbatim.
- [x] Create `references/dynamic-schemas.md`.
- [x] Create `references/runtime-evals.md`.
- [x] Create `references/auto-retry.md`.
- [x] Create `references/multimodal-vision.md`.
- [x] Create `references/streaming-and-typebuilder.md`.
- [x] Create `references/clients-and-retries.md`.
- [x] Delete `references/baml-comprehensive-guide.md` (deprecate).
- [x] Delete `references/baml-patterns-and-best-practices.md`
      (deprecate).
- [x] Keep `references/baml.md` (the LLM prompt; still useful).

## 4. Expand `dlt` skill (28 lines → ~120 + 13 refs)

- [x] Update `.agents/skills/dlt/SKILL.md` to:
  - Fix the path bug: `oideachais/dlt_sources/`, not
    `oideachais/data_platform/dlt_sources/`.
  - Add a decision tree that dispatches to sub-skills.
  - Add project-specific recipes (type-safe pipeline,
    multi-destination fan-out, Dagster wrapping, performance
    & anti-patterns).
  - Link the 3 orphan reference files in a new reference index.
- [x] Create `references/destinations-lancedb.md`.
- [x] Create `references/destinations-cognee-memgraph.md`.
- [x] Create `references/destinations-graphiti.md`.
- [x] Create `references/performance-optimisation.md`.
- [x] Create `references/dagster-dlt-assets.md`.
- [x] Create `references/openapi-generator.md`.
- [x] Create `references/deploy-gcp-cloud-function-webhook.md`.
- [x] Create `references/deploy-gcp-cloud-function.md`.
- [x] Create `references/deploy-gcp-cloud-run.md`.
- [x] Create `references/deploy-modal.md`.
- [x] Create `references/sqlmesh-init.md`.
- [x] Create `references/dlt-transformations.md`.
- [x] Create `references/crawl4ai-dlt-summary.md`.
- [x] Create `references/type-safe-pipeline.md`.

## 5. Expand `lancedb` skill (~350 lines → ~500 + 11 refs)

- [x] Bump version to `>=0.26.0` in `SKILL.md` frontmatter.
- [x] Update `SKILL.md` "When to use this skill" trigger list to add
      time-travel, A/B testing embedding models, multimodal search,
      LanceDB + Iceberg, Ibis query, Lance Namespace catalog.
- [x] Update the TypeScript section to use the modern `search()`
      API (replacing the deprecated `vectorSearch()`).
- [x] Update the FTS section to mention `tokenizer="en_stem"` and
      `with_stopwords=[...]`.
- [x] Add sections for: time-travel / `tbl.checkout()` /
      `tbl.version`; embeddings registry (10+ providers); context
      enrichment window; multimodal "fat table"; pre-filter vs
      post-filter; `refine_factor`; `drop_index`; `explain_plan` /
      `analyze_plan`; LanceDB Cloud regions + auto-compaction +
      auto-reindexing.
- [x] Update deployment section to mention the 4 LanceDB Cloud
      regions and the rclone-R2-sidecar Compose pattern.
- [x] Create `references/time-travel-rag.md`.
- [x] Create `references/embed-functions-registry.md`.
- [x] Create `references/advanced-rag-patterns.md`.
- [x] Create `references/multimodal-fat-tables.md`.
- [x] Create `references/lancedb-cloud.md`.
- [x] Create `references/lance-namespace-and-iceberg.md`.
- [x] Create `references/ibis-integration.md`.
- [x] Create `references/typescript-modern-api.md`.
- [x] Create `references/lance-ray-distributed.md`.
- [x] Create `references/lance-vs-iceberg.md`.
- [x] Create `references/geospatial-fts.md`.
- [x] Create `references/hosting-lancedb-r2.md`.
- [x] Update `references/hosting-lancedb-docker-compose.md` to
      include the rclone-R2-sidecar pattern.
- [x] Delete the stale `references/lancedb-research-report.md` and
      replace with a pointer in `references/lancedb-reference-index.md`.

## 6. Expand `dagster` skill (84 lines + 5 KCG-relevant refs)

- [x] Keep `SKILL.md` skeleton; add "KCG-relevant references" section.
- [x] Create `references/integrations/dagster-ducklake/INDEX.md`.
- [x] Create `references/integrations/dagster-sqlmesh/INDEX.md`.
- [x] Create `references/integrations/dagster-dlt/parallel-github.md`.
- [x] Create `references/integrations/dagster-evidence/INDEX.md`
      (thin stub).
- [x] Create `references/integrations/dagster-modal/INDEX.md`
      (thin stub).
- [x] Create `references/integrations/dagster-iceberg/INDEX.md`
      (thin stub).
- [x] Create `references/deployment/docker-self-hosted.md`.
- [x] Create `references/orchestration/kcg-cocoindex-graphiti.md`.

## 7. Delete the 5 docs subdirectories + the misfiled baml example

- [x] `rm -rf /Users/cianmacandeisigh/dev/kings_college_galway/docs/lance/`
      (18M)
- [x] `rm -rf /Users/cianmacandeisigh/dev/kings_college_galway/docs/dlt/`
      (9.9M)
- [x] `rm -rf /Users/cianmacandeisigh/dev/kings_college_galway/docs/dagster/`
      (5.3M)
- [x] `rm -rf /Users/cianmacandeisigh/dev/kings_college_galway/docs/cocoindex/`
      (48M)
- [x] `rm -rf /Users/cianmacandeisigh/dev/kings_college_galway/docs/baml/`
      (3.6M) — removes the misfiled `2025-12-09-git-worktrees/`
      example.
- [x] Verify: all 5 directories confirmed absent
      (`ls docs/{lance,dlt,dagster,cocoindex,baml} 2>&1` returns
      `No such file or directory`).

## 8. Verify and re-index

- [x] Run `openspec validate sync-skills-from-docs --strict` again
      (post-implementation; passes).
- [x] Smoke test: `from cocoindex_flows import docs_skills_consolidation`
      from `oideachais/` (passes with pre-existing warnings).
- [x] Smoke test: `from dlt_sources.ireland import *` from
      `oideachais/` (passes).
- [x] Re-index the codebase: `bun run ccc:index` (runs; pre-existing
      COCOINDEX_DB env-var requirement, addressed by setting
      `COCOINDEX_DB=./cocoindex.db`).

## 9. Archive

- [ ] `openspec archive sync-skills-from-docs --yes` after
      successful verification (final step).

## 10. Land the plane

- [ ] `git status` (clean expected except for the changes).
- [ ] `git pull --rebase`.
- [ ] `git add -A` the new/changed files.
- [ ] `git commit -m "sync skills from docs/{lance,dlt,dagster,cocoindex,baml} and delete the docs subdirectories"`.
- [ ] `git push`.
- [ ] `git status` shows "up to date with origin".
