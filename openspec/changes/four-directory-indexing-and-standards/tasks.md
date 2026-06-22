# Tasks: four-directory-indexing-and-standards

> Implementation tasks for the `four-directory-indexing-and-standards`
> OpenSpec change. Each task is small, testable, and traceable to a
> `## Requirements` block in `proposal.md`.

## 1. BAML schema additions

- [ ] 1.1 Create `baml_src/four_directory_indexing.baml` with
  `ExtractOpenSpecChange` and `ExtractLeabharlannCites` plus their
  Pydantic-style classes.
- [ ] 1.2 Run `baml-cli generate` (or `bun run baml:generate` once
  wired) and verify `baml_client/four_directory_indexing.py` is
  created.
- [ ] 1.3 Re-export the new functions from
  `baml_src/__init__.py` so `baml_client` can find them.

## 2. CocoIndex v1 App: openspec indexing

- [ ] 2.1 Create `oideachais/cocoindex_flows/openspec_indexing.py`
  with:
  - [ ] 2.1.1 ContextKeys `KG_DB`, `EMBEDDER` (BAAI/bge-m3),
    `BAML_CLIENT` (`detect_change=True`).
  - [ ] 2.1.2 `@coco.lifespan` that provides FalkorDB
    `ConnectionFactory(graph="docs_skills_graph")`, the embedder,
    and the BAML client. **Reuses the same FalkorDB graph as
    `docs_skills_consolidation.py`** so all four directory sources
    contribute to one graph.
  - [ ] 2.1.3 `app_main` that mounts
    `localfs.walk_dir("openspec/", live=True, refresh_interval=60s)`
    with includes `*.md`, `*.mdx`, `*.toml`, `*.yaml` and excludes
    `**/archive/**`, `**/.DS_Store`.
  - [ ] 2.1.4 Phase 1 `@coco.fn(memo=True) process_openspec_file`
    that runs `ExtractOpenSpecChange` and declares an
    `OpenSpecChange` node in FalkorDB + emits an `OpenSpecTriples`
    carrier.
  - [ ] 2.1.5 Phase 2 `@coco.fn build_openspec_graph` that declares
    `BLOCKS` / `BLOCKED_BY` / `MODIFIES_SPEC` edges from the
    consolidated triples.
  - [ ] 2.1.6 LanceDB target `openspec_chunks` with vector index on
    `embedding` (HNSW; `HNSW_DROP_THRESHOLD` honoured).
  - [ ] 2.1.7
    `app = coco.App(coco.AppConfig(name="OpenSpecIndex"), app_main)`
    at module level.
- [ ] 2.2 Re-export the new App in
  `oideachais/cocoindex_flows/__init__.py` as `openspec_app`.

## 3. CocoIndex v1 App: leabharlann↔openspec links

- [ ] 3.1 Create
  `oideachais/cocoindex_flows/leabharlann_openspec_links.py` with:
  - [ ] 3.1.1 ContextKeys `KG_DB`, `EMBEDDER`, `BAML_CLIENT`
    (`detect_change=True`).
  - [ ] 3.1.2 `@coco.lifespan` providing FalkorDB
    `ConnectionFactory(graph="docs_skills_graph")` (same graph as
    Step 2).
  - [ ] 3.1.3 `app_main` that mounts
    `localfs.walk_dir("leabharlann/", live=True, refresh_interval=120s)`
    with includes `*.md`, `*.mdx` (the directory's PDF corpus is
    handled by `leabharlann_embedding.py`; this App indexes the
    Markdown summaries already emitted by the 4 leabharlann dlt
    sources).
  - [ ] 3.1.4 Phase 1 `@coco.fn(memo=True) process_leabharlann_md`
    that runs `ExtractLeabharlannCites` and emits a `CitesRecord`.
  - [ ] 3.1.5 Phase 2 `@coco.fn build_link_graph` that declares
    `LEABHARLANN_CITES` edges from each `LeabharlannDoc` node to
    the corresponding `OpenSpecChange` node.
  - [ ] 3.1.6 LanceDB target `leabharlann_openspec_links` with
    vector index on `embedding`.
  - [ ] 3.1.7
    `app = coco.App(coco.AppConfig(name="LeabharlannOpenspecLinks"), app_main)`
    at module level.
- [ ] 3.2 Re-export in `oideachais/cocoindex_flows/__init__.py` as
  `leabharlann_openspec_links_app`.

## 4. Schema-mask + data-type standardisation

- [ ] 4.1 Create `oideachais/core/types.py` with:
  - [ ] 4.1.1 `Quadrant` enum: `OIDEACHAIS`, `MEISINFHOGHLAIM`,
    `TUATHA`, `CROILAR`, `SHARED`.
  - [ ] 4.1.2 `DocumentType` enum: `CURRICULUM`, `LEABHARLANN_PDF`,
    `LEABHARLANN_EPUB`, `LEABHARLANN_TAKEOUT`, `ZOTERO_PAPER`,
    `RESEARCH_BRIEF`, `OPENSPEC_CHANGE`, `SKILL_MD`, `DOCS_MD`,
    `BAML_SCHEMA`, `DAGSTER_ASSET`.
  - [ ] 4.1.3 `EmbeddingModel` enum: `BGE_M3`,
    `BGE_LARGE_EN_V1_5`, `TEXT_EMBED_3_LARGE`.
  - [ ] 4.1.4 `BgeM3 = "BAAI/bge-m3"` constant + an
    `embedding_model_string(EmbeddingModel)` helper.
- [ ] 4.2 Re-export from `codeolas/core/types.py` for the
  publishable wheel (so `crypteolas`, `tuath`, and the cocoindex
  flows can all import from one place).
- [ ] 4.3 Sweep `oideachais/`, `meaisinfhoghlaim/`, `tuatha/`,
  `codeolas/`, `baml_src/`, `infrastructure/` for hard-coded
  `"BAAI/bge-m3"` strings and replace with
  `os.environ.get("CODEOLAS_EMBED_MODEL", BgeM3)`.
- [ ] 4.4 Sweep the same trees for `Document`, `Chunk`,
  `Language`, `Quadrant` duplicates and replace with the canonical
  enums. Emit a migration report to
  `docs/refactor/schema-type-standardization-report.md`.

## 5. Dagster assets

- [ ] 5.1 Create `oideachais/dagster_defs/assets/openspec_assets.py`
  with 3 assets:
  - [ ] 5.1.1 `openspec_chunk_and_tag` (wraps `cocoindex update`
    batch).
  - [ ] 5.1.2 `openspec_graph_publish` (verifies FalkorDB
    node/edge counts via `asset_check`).
  - [ ] 5.1.3 `openspec_live` (sensor-launched, runs
    `cocoindex update -L`).
- [ ] 5.2 Add `leabharlann_openspec_links_build` to the same file
  (or a sibling).
- [ ] 5.3 Register the 4 assets in
  `oideachais/dagster_defs/definitions.py` under a new
  `four_directory_indexing` asset group.

## 6. Task aliases

- [ ] 6.1 In `mise.toml`, add `[tasks."openspec:index"]`,
  `[tasks."openspec:index:live"]`, `[tasks."leabharlann:links"]`,
  `[tasks."leabharlann:links:live"]`.
- [ ] 6.2 Mirror the same scripts in `package.json`.
- [ ] 6.3 Confirm `bun run openspec:index` and
  `bun run leabharlann:links` work end-to-end.

## 7. Deprecate legacy chunkhound MCP

- [ ] 7.1 In `.opencode.yaml`, comment out the `chunkhound` MCP
  entry. Add a comment pointing at the v1 App:
  `oideachais.cocoindex_flows.codebase_indexing.codebase_app`.
- [ ] 7.2 In `openspec/specs/chunkhound-code-search/spec.md`, add a
  MODIFIED Requirement that designates the v1 App as the canonical
  implementation. Do NOT delete the spec — leave it in place until
  2026-07-15.
- [ ] 7.3 Open a follow-up issue for the 2026-07-15 hard-removal.

## 8. Skill updates

- [ ] 8.1 In `.agents/skills/ccc/SKILL.md`, add a "See also:
  four-directory-indexing-and-standards" section with a link to
  the two new CocoIndex v1 Apps.
- [ ] 8.2 In `.agents/skills/cocoindex/SKILL.md`, add the 2 new
  Apps to the inventory.
- [ ] 8.3 In `.agents/skills/dlt/SKILL.md`, add a note that the 4
  leabharlann dlt sources are the upstream of
  `leabharlann_embedding.py`.

## 9. Verification

- [ ] 9.1 `mise run format && mise run lint && mise run py:typecheck`
  — all green.
- [ ] 9.2 `baml-cli generate` — exits 0.
- [ ] 9.3
  `uv run cocoindex update oideachais/cocoindex_flows/openspec_indexing.py`
  — materialises ≥ 1 row per openspec spec.
- [ ] 9.4
  `uv run cocoindex update oideachais/cocoindex_flows/leabharlann_openspec_links.py`
  — materialises ≥ 50 cite edges on first run.
- [ ] 9.5 `mise dagster:oideachais` — `openspec_graph_publish`
  asset check passes.
- [ ] 9.6
  `uv run python -c 'from falkordb import FalkorDB; g = FalkorDB().select_graph("docs_skills_graph"); print(g.query("MATCH (n:OpenSpecChange) RETURN count(n)").result_set)'`
  — returns ≥ 10.
- [ ] 9.7 `openspec validate four-directory-indexing-and-standards --strict`
  — exits 0.

## 10. Land the plane

- [ ] 10.1 `git add -A && git commit` with a Conventional Commit
  message.
- [ ] 10.2 `git pull --rebase && git push`.
- [ ] 10.3 `git status` shows "up to date with origin".
- [ ] 10.4 Open follow-up issues for: chunkhound hard-removal
  (2026-07-15), Cognee cognify of the new edges, RAGAS eval
  asset, doc canonical-of-originals migration tracker.

## Reference

- OpenSpec change:
  `openspec/changes/four-directory-indexing-and-standards/`
- Sister change:
  `openspec/changes/docs-skills-consolidation-pipeline/`
- v1 reference patterns:
  `docs/cocoindex/code_embedding/main.py`,
  `docs/cocoindex/docs_to_knowledge_graph/main.py`,
  `oideachais/cocoindex_flows/leabharlann_embedding.py`
- OpenSpec workflow: `openspec/AGENTS.md`
- Dagster definitions: `oideachais/dagster_defs/definitions.py`
