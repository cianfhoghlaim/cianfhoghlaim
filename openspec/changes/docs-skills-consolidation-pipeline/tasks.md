# Tasks: docs-skills-consolidation-pipeline

> Implementation tasks for the `docs-skills-consolidation-pipeline` OpenSpec change.
> Each task is small, testable, and traceable to a `## Requirements` block in `proposal.md`.

## 1. BAML schema

- [ ] 1.1 Create `baml_src/docs_skills_consolidation.baml` with `ExtractDocSkillTag`, `ExtractTriples`, `ProposeConsolidation`, plus their Pydantic-style classes.
- [ ] 1.2 Run `baml-cli generate` (or `bun run baml:generate` once wired) and verify `baml_client/docs_skills_consolidation.py` is created.

## 2. CocoIndex v1 App: docs-skills consolidation

- [ ] 2.1 Create `oideachais/cocoindex_flows/docs_skills_consolidation.py` with:
  - [ ] 2.1.1 ContextKeys `KG_DB`, `EMBEDDER` (BAAI/bge-m3), `BAML_CLIENT` (`detect_change=True`).
  - [ ] 2.1.2 `@coco.lifespan` that provides FalkorDB `ConnectionFactory(graph="docs_skills_graph")`, the embedder, and the BAML client.
  - [ ] 2.1.3 `app_main` that mounts two `localfs.walk_dir` sources (`docs/`, `.agents/skills/`) with `live=True, refresh_interval=30s`.
  - [ ] 2.1.4 Phase 1 `@coco.fn(memo=True) process_file` that runs `ExtractDocSkillTag` + `ExtractTriples` and declares a `DocSkill` node in FalkorDB + emits a `DocTriples` carrier.
  - [ ] 2.1.5 Phase 2 `@coco.fn build_graph` that declares `Concept` nodes + `RELATES_TO` / `TAGGED` / `CONSOLIDATED_INTO` edges from the consolidated triples.
  - [ ] 2.1.6 LanceDB target `docs_skills_chunks` with vector index on `embedding` (HNSW; `HNSW_DROP_THRESHOLD` honoured).
  - [ ] 2.1.7 `app = coco.App(coco.AppConfig(name="DocsSkillsConsolidation"), app_main)` at module level.
- [ ] 2.2 Re-export the new App in `oideachais/cocoindex_flows/__init__.py`.

## 3. Dagster wrapper

- [ ] 3.1 Create `oideachais/dagster_defs/assets/docs_skills_assets.py` with 6 assets:
  - [ ] 3.1.1 `docs_skills_manifest` (manifest, sha256 of `docs/` + `.agents/skills/`).
  - [ ] 3.1.2 `docs_skills_chunk_and_tag` (wraps `cocoindex update` batch).
  - [ ] 3.1.3 `docs_skills_graph_publish` (verifies FalkorDB node/edge counts via `asset_check`).
  - [ ] 3.1.4 `docs_skills_live` (sensor-launched, runs `cocoindex update -L`).
  - [ ] 3.1.5 `codebase_chunk_and_embed` (wraps the codebase v1 App).
  - [ ] 3.1.6 `codebase_live` (sensor-launched).
- [ ] 3.2 Register the 6 assets in `oideachais/dagster_defs/definitions.py` (in the `combined_assets` list).
- [ ] 3.3 Add a `DOCS_SKILLS_ASSETS` aggregator list so the new group is also exportable as a job.

## 4. CocoIndex v1 App: codebase index (ccc replacement)

- [ ] 4.1 Create `oideachais/cocoindex_flows/codebase_indexing.py` with:
  - [ ] 4.1.1 ContextKey `EMBEDDER` (BAAI/bge-m3, `detect_change=True`).
  - [ ] 4.1.2 `@coco.lifespan` providing the embedder.
  - [ ] 4.1.3 `app_main` mounting `localfs.walk_dir(repo_root, live=True, refresh_interval=60s)` with include patterns `*.py,*.rs,*.ts,*.tsx,*.go,*.md,*.mdx,*.toml` and excludes `**/.*,**/node_modules,**/__pycache__,**/.venv,**/target,**/dist,**/build,**/.cocoindex_code,**/docs/cocoindex,**/.turbo,**/stedding`.
  - [ ] 4.1.4 `RecursiveSplitter` chunking with `detect_code_language`.
  - [ ] 4.1.5 LanceDB target `codebase_chunks` with vector index on `embedding`.
  - [ ] 4.1.6 `app = coco.App(coco.AppConfig(name="CodebaseIndex"), app_main)` at module level.
- [ ] 4.2 Re-export the new App in `oideachais/cocoindex_flows/__init__.py`.
- [ ] 4.3 Add `oideachais/cocoindex_flows/cli.py` (or extend existing) with a `search_codebase(query: str, k: int = 10)` helper that loads the embedder, encodes the query, and runs a LanceDB ANN query against `codebase_chunks`.

## 5. Task aliases

- [ ] 5.1 In `mise.toml`, update `[tasks."ccc:index"]` to delegate to the v1 App. Add `[tasks."ccc:v1:index"]`, `[tasks."ccc:v1:search"]`, and `[tasks."docs:consolidate"]`.
- [ ] 5.2 In `package.json`, mirror the same scripts.
- [ ] 5.3 Confirm `bun run ccc:index` still works (backward-compat alias).

## 6. Skill updates

- [ ] 6.1 In `.agents/skills/ccc/SKILL.md`, prepend a deprecation banner: "v1 app at `oideachais/cocoindex_flows/codebase_indexing.py` is the new path; this CLI is in maintenance mode until 2026-07-15."
- [ ] 6.2 In `.agents/skills/cocoindex/SKILL.md`, add a "See also: docs-skills-consolidation" section with a link to the new App.

## 7. Verification

- [ ] 7.1 `mise run format && mise run lint && mise run py:typecheck` — all green.
- [ ] 7.2 `baml-cli generate` — exits 0.
- [ ] 7.3 `uv run cocoindex update oideachais/cocoindex_flows/docs_skills_consolidation.py` — materialises ≥ 1 row per category.
- [ ] 7.4 `uv run cocoindex update oideachais/cocoindex_flows/codebase_indexing.py` — materialises ≥ 100 rows on first run.
- [ ] 7.5 `mise dagster:oideachais` — `docs_skills_graph_publish` asset check passes.
- [ ] 7.6 `bun run ccc:v1:search "Dagster MultiPartition definition"` — returns ≥ 3 results.
- [ ] 7.7 `openspec validate docs-skills-consolidation-pipeline --strict` — exits 0.

## 8. Land the plane

- [ ] 8.1 `git add -A && git commit` with a Conventional Commit message.
- [ ] 8.2 `git pull --rebase && git push`.
- [ ] 8.3 `git status` shows "up to date with origin".
- [ ] 8.4 Open follow-up issues for: ccc deprecation removal (2026-07-15), Cognee cognify of `docs_skills_graph`, RAGAS eval asset for the new indices, doc canonical-of-originals migration tracker.

## Reference

- OpenSpec change: `openspec/changes/docs-skills-consolidation-pipeline/`
- Reference patterns: `docs/cocoindex/meeting_notes_graph_falkordb/main.py`, `docs/cocoindex/docs_to_knowledge_graph/main.py`, `docs/cocoindex/code_embedding/main.py`
- OpenSpec workflow: `openspec/AGENTS.md`
- Dagster definitions: `oideachais/dagster_defs/definitions.py`
