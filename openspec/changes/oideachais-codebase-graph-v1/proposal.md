# Change: oideachais-codebase-graph-v1

## Why

Phase 1 of the 6-phase refactor plan. The user asked to:
1. **Expand the `oideachais/cocoindex_flows/codebase_indexing.py` v1 App** with the 7-node / 7-edge code-graph patterns from `codeolas/cocoindex_flows/file_graph.py`
2. **Port the 29+ language detection** from `codeolas/chunking/languages.py` to `oideachais/cocoindex_flows/chunking/languages.py`
3. **Add 3 Dagster assets** to `oideachais/dagster_defs/assets/codebase_assets.py` (code_chunks, code_graph, architecture_docs) that drive the v1 App
4. **Update the ccc and cocoindex skills** to reflect the v1 patterns

The v1 App (round 7+8) is the canonical codebase indexer. The legacy `ccc` CLI is on a 30-day deprecation window (round 7). The `codeolas` standalone subdir has duplicate CocoIndex code that the v1 code now subsumes. Per the user's plan answer, **the v1 code stays in oideachais/**, and **codeolas/ stays as a standalone subdir for now** (with this change being a port, not a deletion).

## What Changes

### Port the language detection table
- `codeolas/chunking/languages.py` (82 lines, 29 languages) → `oideachais/cocoindex_flows/chunking/languages.py` via `git mv`
- The `EXTENSION_TO_LANGUAGE` dict + `detect_language` + `get_supported_languages` are now part of the canonical oideachais CocoIndex flow
- The `codebase_indexing.py` flow imports `EXTENSION_TO_LANGUAGE` + `get_supported_languages` from the new module

### Expand `oideachais/cocoindex_flows/codebase_indexing.py` with the 7-node / 7-edge model
- 7 `CodeNodeType`: `FILE`, `FUNCTION`, `CLASS`, `METHOD`, `MODULE`, `INTERFACE`, `VARIABLE` (ported from `codeolas/cocoindex_flows/file_graph.py:NodeType`)
- 7 `CodeEdgeType`: `CONTAINS`, `IMPORTS`, `CALLS`, `EXTENDS`, `IMPLEMENTS`, `USES`, `DEFINES` (ported from `codeolas/cocoindex_flows/file_graph.py:EdgeType`)
- 11-language Tree-sitter AST node type mapping (Python, TypeScript, JavaScript, TSX, JSX, Rust, Go, Java, Kotlin, Ruby, Swift)
- `_ast_extract_nodes_and_edges()` — the canonical Tree-sitter extraction function (ported from `codeolas/cocoindex_flows/file_graph.py:extract_relationships_from_ast`)
- New v1 App `CodebaseGraph` — writes to 2 new LanceDB tables `codebase_graph` + `codebase_graph_edges`
- New search helper `search_code_graph()` for the graph table

### 3 new Dagster assets in `oideachais/dagster_defs/assets/codebase_assets.py`
- `codebase_chunks` — materialises the v1 `CodebaseIndex` App (group_name="codebase")
- `codebase_code_graph` — materialises the v1 `CodebaseGraph` App, deps on `codebase_chunks`
- `codebase_architecture_docs` — `.arch.md` generation, deferred to a later round (returns `status: deferred` for now)
- All 3 ported from `codeolas/dagster_assets/code_assets.py` (group_name="codeolas" → "codebase")

### Skills updated
- `.agents/skills/ccc/SKILL.md` — the deprecation banner remains; the v1 App reference is updated to include the 3 new Dagster assets
- `.agents/skills/cocoindex/SKILL.md` — the v1 pattern is updated to include the 7-node / 7-edge model + the 29+ language table

## Impact

- **Affected specs (1)**: `oideachais-pipeline` (the canonical capability spec for the lakehouse) — adds 1 MODIFIED Requirement for the v1 codebase indexer
- **Affected code**: only `oideachais/cocoindex_flows/`, `oideachais/dagster_defs/assets/`, `.agents/skills/ccc/`, `.agents/skills/cocoindex/`
- **Affected skills (2)**: ccc + cocoindex
- **Disk delta**: 0 (no new files outside the existing dirs; `languages.py` is a `git mv`)

## Success criteria

- `openspec validate oideachais-codebase-graph-v1 --strict` passes
- `oideachais/cocoindex_flows/codebase_indexing.py` exports `CodeNodeType` (7 members) + `CodeEdgeType` (7 members) + `CodeNode` + `CodeEdge`
- `oideachais/cocoindex_flows/chunking/languages.py` exists with `EXTENSION_TO_LANGUAGE` (29+ entries) + `get_supported_languages()` (returns 29+ names)
- `oideachais/dagster_defs/assets/codebase_assets.py` exists with 3 assets: `codebase_chunks`, `codebase_code_graph`, `codebase_architecture_docs`
- `oideachais/STATUS.md` §3 is updated to mark `codebase_chunks` + `codebase_code_graph` as v1 (was v0 / unwired)
- `oideachais-pipeline/spec.md` has 1 MODIFIED Requirement for the v1 codebase indexer

## Rollback

Skills-only. Rollback = `git revert` this commit. No data, code, or runtime state is affected (the v0 codeolas/ code still works as a fallback).
