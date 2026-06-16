# Change: docs-skills-consolidation-pipeline

## Why

The `docs/` tree (45 MiB / 1,038 canonical files post `docs-restructuring`) and `.agents/skills/` (~60 skill folders) have grown without a single pipeline that **tags**, **deduplicates**, **embeds**, and **graph-links** them. Three concrete problems result:

1. **No machine-readable metadata.** Every ccc search and every agent-skill routing table re-parses frontmatter manually. Tagging, quadrant, and supersedes are inferred per call.
2. **No canonical-of-originals link.** The `docs-restructuring` change preserved 1,038 originals in `docs/archive/2026-06-06-*` and produced 36 canonicals, but no graph records the `(original, canonical)` relationship. A query that hits an archive copy cannot follow the link to the merged target.
3. **The codebase semantic index (`ccc`) is a separate CLI from the rest of the data lakehouse.** It is not a CocoIndex v1 App, not visible in the Dagster UI, and not on the same LanceDB HNSW index that the new leabharlann assets are landing on. The platform loses operational uniformity.

This change introduces a single CocoIndex v1 App (BAML-driven extraction, LanceDB chunks, FalkorDB knowledge graph) that walks `docs/` and `.agents/skills/`, plus a second v1 App that re-implements `ccc` on the same primitives.

## What Changes

- **New BAML schema** `baml_src/docs_skills_consolidation.baml`:
  - `ExtractDocSkillTag(content)` → `(category, quadrant, confidence)`
  - `ExtractTriples(content)` → `list[(subject, predicate, object)]`
  - `ProposeConsolidation(file_a, file_b)` → `ConsolidationGroup` (canonical path, member paths, reason)
- **New CocoIndex v1 App** `oideachais/cocoindex_flows/docs_skills_consolidation.py`:
  - Two sources: `localfs.walk_dir("docs/")` and `localfs.walk_dir(".agents/skills/")` with `live=True`
  - Phase 1 per-file: BAML tag + BAML triples, declares `DocSkill` nodes in FalkorDB
  - Phase 2 graph build: `Concept` nodes + `RELATES_TO` / `TAGGED` / `CONSOLIDATED_INTO` edges
  - Three targets: LanceDB `docs_skills_chunks` (vector index on `embedding`), FalkorDB graph `docs_skills_graph`, evidence sink in `infrastructure/scripts/ingest_evidence/`
- **New Dagster assets** `oideachais/dagster_defs/assets/docs_skills_assets.py`:
  - `docs_skills_manifest`, `docs_skills_chunk_and_tag`, `docs_skills_graph_publish`, `docs_skills_live` (sensor-launched)
  - `codebase_chunk_and_embed`, `codebase_live` for the ccc replacement
- **New CocoIndex v1 App** `oideachais/cocoindex_flows/codebase_indexing.py`:
  - Tree-sitter chunks for `.py`/`.rs`/`.ts`/`.tsx`/`.go`/`.md`/`.mdx`/`.toml`
  - Embeds with `BAAI/bge-m3` via `ContextKey(detect_change=True)`
  - LanceDB table `codebase_chunks`
  - Replaces `bun run ccc:index` (alias kept for 30 days)
- **Task alias updates** in `mise.toml` and `package.json`:
  - `bun run ccc:index` → `uv run cocoindex update oideachais/cocoindex_flows/codebase_indexing.py:CodebaseIndex`
  - `bun run docs:consolidate` → batch (catch-up) run of the new app
  - `bun run ccc:v1:search <q>` → new Python helper that queries `codebase_chunks`
- **Skill updates**:
  - `.agents/skills/ccc/SKILL.md` gains a 30-day deprecation banner pointing at the v1 app
  - `.agents/skills/cocoindex/SKILL.md` gains a "See also: docs-skills-consolidation" section

## Impact

- **Affected specs:**
  - `data-pipeline` — adds Tagging-Consolidation Index requirement
  - `knowledge-graph` — adds `docs_skills_graph` schema
  - `cocoindex-v1-migration` — adds 2 new Apps to the inventory
- **Affected code:**
  - `oideachais/cocoindex_flows/__init__.py` — re-exports 2 new apps
  - `oideachais/dagster_defs/definitions.py` — registers 6 new assets
  - `oideachais/pyproject.toml` — adds `pyfalkordb` to dependencies
  - `mise.toml` + `package.json` — 4 new / updated tasks
  - `.agents/skills/ccc/SKILL.md`, `.agents/skills/cocoindex/SKILL.md` — banner + cross-link
  - `baml_src/docs_skills_consolidation.baml` — new schema (regenerates `baml_client/`)
- **Affected agent skills:** all 60 skills that previously used `ccc` (search) now have a v1-native alternative; no skill needs to change unless it has a hard-coded `bun run ccc:index` shell-out (those should switch to `bun run ccc:v1:index`).
- **Affected CI:** none. `mise run py:typecheck` covers the new files; `mise run lint` covers the new markdown and Python.
- **Affected workflows:** `mise dagster:oideachais` now shows the new `docs_skills` and `codebase` asset groups in the UI; the existing `bun run ccc:index` keeps working for 30 days as an alias.

## Non-Goals

- This change does **not** retire the `_v0_archive/` legacy module in `oideachais/cocoindex_flows/`. The v0 archive stays on disk; the v1 migration is complete for the actively-used modules and that's the existing boundary.
- This change does **not** cognify the new FalkorDB graph into Cognee. The new graph is cognify-ready (entity-typed) and can be picked up by `infrastructure/scripts/cognee-ingest-docs.py --all` in a follow-up change.
- This change does **not** move or delete `docs/cocoindex/` (the upstream-example mirror). The user has indicated that directory will be removed in a separate housekeeping step.
- This change does **not** rewrite the canonical content of any doc or skill. It only reads, tags, embeds, and graph-links the existing material.
- This change does **not** add a RAGAS eval asset for the new indices. That's a follow-up change once we have ≥ 7 days of stable runs to compare against.
