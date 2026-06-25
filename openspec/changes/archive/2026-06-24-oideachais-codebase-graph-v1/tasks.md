# Tasks: oideachais-codebase-graph-v1

## 1. OpenSpec change scaffolding
- [x] Create change directory.
- [x] Write `proposal.md`.
- [x] Write `tasks.md` (this file).
- [x] Write 1 spec delta (oideachais-pipeline).
- [x] Validate `--strict`.

## 2. Port language detection (codeolas → oideachais)
- [x] `git mv codeolas/chunking/languages.py sruth/oideachais/cocoindex_flows/chunking/languages.py`
- [x] Update `sruth/oideachais/cocoindex_flows/codebase_indexing.py` to import the new module
- [x] Add `EXTENSION_TO_LANGUAGE` + `get_supported_languages` to the public exports

## 3. Expand codebase_indexing.py with 7-node / 7-edge model
- [x] Add `CodeNodeType` enum (7 members)
- [x] Add `CodeEdgeType` enum (7 members)
- [x] Add `CodeNode` + `CodeEdge` dataclasses
- [x] Add `_LANG_AST_NODE_TYPES` mapping (11 languages)
- [x] Add `_ast_extract_nodes_and_edges()` function
- [x] Add `_ast_walk()` recursive helper
- [x] Add `_extract_name()` helper
- [x] Add `detect_language_for_path()` public function
- [x] Add `_make_graph_app()` + `codebase_graph_app`
- [x] Add `search_code_graph()` public function
- [x] Add `LANCEDB_GRAPH_TABLE` config

## 4. 3 new Dagster assets
- [x] Create `sruth/oideachais/dagster_defs/assets/codebase_assets.py`
- [x] `codebase_chunks` asset (group_name="codebase")
- [x] `codebase_code_graph` asset (deps on codebase_chunks)
- [x] `codebase_architecture_docs` asset (deferred placeholder)

## 5. Skills updated
- [x] `.agents/skills/ccc/SKILL.md` — update v1 reference to include the 3 new Dagster assets
- [x] `.agents/skills/cocoindex/SKILL.md` — update v1 pattern with 7-node / 7-edge model

## 6. sruth/oideachais/STATUS.md updated
- [x] §3 (CocoIndex v0 vs v1 status) — mark `codebase_chunks` + `codebase_code_graph` as v1
- [x] §4 (Dagster asset catalogue) — add the 3 new assets to the `codebase` group

## 7. Verify
- [ ] `openspec validate oideachais-codebase-graph-v1 --strict`
- [ ] `git status --short` is reasonable (~5 files: 1 new, 1 move, 1-2 modifications)
- [ ] `python -c "from oideachais.cocoindex_flows import codebase_indexing; print(codebase_indexing.CodeNodeType.FILE)"` works (syntax check)

## 8. Archive
- [ ] `openspec archive oideachais-codebase-graph-v1 --yes`

## 9. Land the plane
- [ ] `git add` only the relevant changes (avoid the pre-existing .gitignore, .infisical.env, stirling-pdf, cocoindex_flows, untracked top-level docs, etc.)
- [ ] `git commit -m "..."`
- [ ] `git push`
