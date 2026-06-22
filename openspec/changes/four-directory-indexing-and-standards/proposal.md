# Change: four-directory-indexing-and-standards

> **Companion to `docs-skills-consolidation-pipeline/`.** That change
> covers `docs/` + `.agents/skills/`. This change adds the two missing
> directories (`leabharlann/`, `openspec/`) and adds the
> schema-mask + data-type standardisation capability that the user
> specifically called out. Both changes share the same Dagster asset
> group, the same BAML extraction client, and the same FalkorDB graph
> pattern, so we keep them in lockstep.

## Why

The user's prior plan was to index `docs/`, `.agents/skills/`, `leabharlann/`,
`openspec/` as a single four-directory sweep, then consolidate docs →
skills + OpenSpec, then deduplicate schema masks and data types. The
existing `docs-skills-consolidation-pipeline/` change covers the first
two directories but is silent on the other two, and it does not address
the schema-mask / data-type standardisation at all.

Three concrete problems result:

1. **LEABHARLANN chunks have no link into OpenSpec change history.** The
   `leabharlann_embedding.py` v1 App emits LanceDB rows + FalkorDB nodes
   for every PDF / Zotero / UoG document, but no edges join those nodes
   to the OpenSpec `Change` nodes. A query like "what changes touched
   the leabharlann?" cannot be answered without a manual grep.
2. **`openspec/` is itself not indexed.** `openspec/specs/*/spec.md` and
   `openspec/changes/*/proposal.md` are exactly the kind of artefact
   that should be in the docs_skills_chunks LanceDB table, but the v1
   App in `docs_skills_consolidation.py` only mounts `docs/` and
   `.agents/skills/`.
3. **Schema masks and data types are duplicated across quadrants.**
   `oideachais/`, `meaisinfhoghlaim/`, `tuatha/codeolas/`, and the
   CocoIndex v1 Apps each define their own `Document`, `Chunk`,
   `Embedding`, `Language`, `Quadrant` types. The embedding model
   string `"BAAI/bge-m3"` is hard-coded in 6+ files. There is no
   canonical place to change it.

## What Changes

- **New CocoIndex v1 App** `oideachais/cocoindex_flows/openspec_indexing.py`:
  - Mounts `localfs.walk_dir("openspec/", live=True, refresh_interval=60s)`
  - Phase 1 per-file: BAML `ExtractOpenSpecChange(content)` →
    `(change_id, status, quadrant, capability_specs, blocking_deps)`
  - Phase 2 graph: declare `OpenSpecChange` nodes + `BLOCKS` /
    `BLOCKED_BY` / `MODIFIES_SPEC` edges into the same
    `docs_skills_graph` FalkorDB graph used by
    `docs_skills_consolidation.py` (single source of truth for the
    cross-cutting graph)
  - LanceDB table `openspec_chunks` with HNSW on `embedding`
  - `app = coco.App(coco.AppConfig(name="OpenSpecIndex"), app_main)`

- **New CocoIndex v1 App** `oideachais/cocoindex_flows/leabharlann_openspec_links.py`:
  - Joins the existing `leabharlann_chunks` LanceDB rows with the new
    `OpenSpecChange` FalkorDB nodes via a `MODIFIES_LEABHARLANN_DOC` /
    `CITED_BY_LEABHARLANN_DOC` edge
  - Phase 1 per-PDF: BAML `ExtractLeabharlannCites(content)` →
    `list[(pdf_id, openspec_change_id, quote, page)]`
  - Phase 2 graph build: declare the edges
  - Re-uses the `docs_skills_graph` graph; adds a `LEABHARLANN_CITES`
    edge type

- **New capability spec** `openspec/specs/schema-type-standardization/spec.md`:
  - One canonical `EmbeddingModel` enum (`BAI_BGE_M3`, `BGE_LARGE_EN`,
    `OPENAI_TEXT_EMBED_3_LARGE`, …) at `codeolas/core/types.py`
  - One canonical `Quadrant` enum at
    `oideachais/core/types.py` (`OIDEACHAIS`, `MEISINFHOGHLAIM`,
    `TUATHA`, `CROILAR`, `SHARED`)
  - One canonical `DocumentType` enum at `oideachais/core/types.py`
    (the existing dlt sources all roll their own)
  - Replace the 6+ hard-coded `"BAAI/bge-m3"` strings with
    `os.environ["CODEOLAS_EMBED_MODEL"]` + the enum default

- **New Dagster asset group** `four_directory_indexing` registered in
  `oideachais/dagster_defs/definitions.py`:
  - `openspec_chunk_and_tag`, `openspec_graph_publish`,
    `openspec_live` (3 assets, mirror of the docs_skills trio)
  - `leabharlann_openspec_links_build` (1 asset)

- **Deprecation path** for the legacy `chunkhound` MCP and
  `.chunkhound.json` config — `.opencode.yaml` is reduced to
  commented-out lines pointing at the v1 App. Removal target:
  2026-07-15 (matches the existing `ccc` deprecation banner).

- **Task aliases** in `mise.toml` and `package.json`:
  - `bun run openspec:index` →
    `uv run cocoindex update oideachais.cocoindex_flows.openspec_indexing:OpenSpecIndex`
  - `bun run leabharlann:links` →
    `uv run cocoindex update oideachais.cocoindex_flows.leabharlann_openspec_links:LeabharlannOpenspecLinks`

- **BAML schema additions** in
  `baml_src/four_directory_indexing.baml`:
  - `ExtractOpenSpecChange(content)` →
    `(change_id, status, quadrant, capability_specs, blocking_deps)`
  - `ExtractLeabharlannCites(content)` →
    `list[(pdf_id, openspec_change_id, quote, page)]`
  - Re-use `ExtractDocSkillTag`, `ExtractTriples`, `ProposeConsolidation`
    from `baml_src/docs_skills_consolidation.baml`

## Impact

- **Affected specs:**
  - `data-pipeline` — adds 2 new CocoIndex v1 Apps
  - `knowledge-graph` — adds 2 new edge types
  - `chunkhound-code-search` — adds MODIFIED Requirements that
    designate `oideachais.cocoindex_flows.codebase_indexing` as the
    canonical implementation
  - NEW `schema-type-standardization` — see above
- **Affected code:**
  - `oideachais/cocoindex_flows/__init__.py` — re-export 2 new apps
  - `oideachais/dagster_defs/definitions.py` — register 4 new assets
  - `oideachais/core/types.py` — add `Quadrant`, `DocumentType`,
    `EmbeddingModel` enums (NEW module)
  - `meaisinfhoghlaim/agents/` + `oideachais/cocoindex_flows/*` —
    migrate 6+ hard-coded model strings to the enum
  - `baml_src/four_directory_indexing.baml` — new file
  - `codeolas/core/types.py` — re-export the new enums for the
    publishable wheel
  - `mise.toml` + `package.json` — 4 new task aliases
  - `.opencode.yaml` — comment out the `chunkhound` MCP entry
- **Affected agent skills:**
  - `.agents/skills/ccc/SKILL.md` — add cross-link to
    `openspec_indexing` App
  - `.agents/skills/cocoindex/SKILL.md` — add the 2 new Apps to the
    "See also" section
  - `.agents/skills/dlt/SKILL.md` — add a note that the 4 leabharlann
    dlt sources are the upstream of the leabharlann_embedding App
- **Affected CI:**
  - `mise run py:typecheck` covers the new Python modules
  - `mise run lint` covers the new BAML file
- **Affected workflows:**
  - `mise dagster:oideachais` now shows the
    `four_directory_indexing` asset group

## Non-Goals

- This change does **not** rewrite the canonical content of any
  OpenSpec spec or change. It only indexes, tags, and graph-links
  the existing material.
- This change does **not** remove the `_v0_archive/` legacy module
  in `oideachais/cocoindex_flows/`. The v0 archive stays on disk.
- This change does **not** cognify the new FalkorDB edges into
  Cognee. The graph is cognify-ready (entity-typed) and can be
  picked up by `infrastructure/scripts/cognee-ingest-docs.py --all`
  in a follow-up change.
- This change does **not** add a RAGAS eval asset for the new
  indices. That's a follow-up change once we have ≥ 7 days of
  stable runs to compare against.
- This change does **not** delete the legacy `chunkhound` MCP yet —
  it just points at the v1 App. Hard deletion is the
  `2026-07-15` follow-up.
