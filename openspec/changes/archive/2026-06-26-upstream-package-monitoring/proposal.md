# Change: upstream-package-monitoring

> **Companion to `four-directory-indexing-and-standards/`.** That change
> covers the four on-disk documentation directories (`docs/`,
> `.agents/skills/`, `leabharlann/`, `openspec/`). This change covers
> the **upstream** documentation surface — the four package blogs /
> docs sites whose capability boundaries KCG depends on:
> **motherduck**, **dlthub**, **lancedb**, **cocoindex**.

## Why

The Cianfhoghlaim stack stands on the shoulders of four upstream
packages that ship weekly:

| Package | Surfaced via | Update cadence |
|:--|:--|:--|
| `motherduck` | `oideachais.storage`, `oideachais.cognify_rules` | weekly blog posts |
| `dlthub` | `oideachais.dlt_sources.*`, `oideachais.dlt_utils.*` | weekly blog posts |
| `lancedb` | `oideachais.cocoindex_flows.*` (embedder + storage) | weekly blog posts + Lance Format releases |
| `cocoindex` | `oideachais.cocoindex_flows.*` (v1 Apps), `meaisínfhoghlaim.cocoindex_eval` | weekly doc commits + v1.x patches |

**Problem 1: silent capability drift.** When `lancedb` ships Lance
Blob V2, Lance Format v2.2, or `motherduck` ships DuckLake 1.0, the
relevant change is announced on the blog — and only on the blog.
`docs/cocoindex/examples/text_embedding_lancedb/main.py` referenced
by the archived `leabharlann-cocoindex-v1` change is now stale; the
v1.0.7 release refactored the `coco.App` / `@coco.fn` /
`@coco.lifespan` API in ways the platform's `cocoindex_flows/`
modules do not yet fully reflect (`culture_heritage_embedding.py`
still wraps in `@coco.flow(scope="global")` + `coco.index_flow(...)`
— the v0-style hybrid).

**Problem 2: no conformance enforcement.** Eleven v1 CocoIndex Apps
exist (the 3 leabharlann + `docs_skills` + `codebase_indexing` +
`api_indexing` + `filesystem_indexing` + `storage_indexing` +
`config_indexing` + `unified_embedding` + `culture_heritage`).
Only 2 of them (`leabharlann_embedding.py`,
`culture_heritage_embedding.py`) delegate to the shared
`_lifespan.py:shared_lifespan`. The other 9 re-declare
`@coco.lifespan` and 3 ContextKeys each — direct violation of
REFACTORING.md item 12. There is no automated check.

**Problem 3: no canonical place for upstream content.** Blog posts
disappear into browser tabs. `codeolas/STATUS.md` can mention
"motherduck supports DuckLake 1.0" but the underlying source URL +
BAML-extracted metadata + chunked embedding + graph link all live
nowhere. The previous `archive/2026-06-16-state-of-art-5-workspaces`
change did firecrawl-blog-fetch once but the artefacts were
one-shot, not a steady-state pipeline.

**Problem 4: change-detection skill stops at 3 layers.** The
`change-detection` skill enumerates DLT incremental cursor + Dagster
sitemap-hash sensor + ChangeDetection.io. It is silent on
**Firecrawl monitors**, the canonical primitive for a blog/changelog
that has no sitemap or whose changelog URL pattern is too deep to
sweep cleanly with curl.

## What Changes

### Layer 4 of `change-detection`: Firecrawl monitors

- **4 Firecrawl monitor configs** at
  `infrastructure/firecrawl/monitors/upstream_packages/`:
  - `motherduck_blog.yml` — 1 page watch
    `https://motherduck.com/blog/` + `--goal` filtering meaningful
    vs marketing noise (webinars, hiring, podcast appearances)
  - `dlthub_blog.yml` — 1 page watch
    `https://dlthub.com/blog` + `--goal` filtering source-context
    additions, ADE-bench / Cortex Code integration updates
  - `lancedb_blog.yml` — 1 page watch
    `https://www.lancedb.com/blog/` + `--goal` filtering Lance
    Format / Lance Blob / multimodal releases
  - `cocoindex_docs.yml` — multi-page watch on
    `https://cocoindex.io/docs/skill.md`, `/getting_started/*`,
    `/advanced_topics/*`, `/connectors/*`, plus `llms-full.txt` —
    `--goal` filtering API-surface changes that affect
    `coco.App`, `@coco.fn`, `@coco.lifespan`, `coco.auto_refresh`,
    or the FalkorDB connector

- Each monitor: 30-min `scheduleText`, `judgeEnabled=true`, webhook
  → `n8n.cianfhoghlaim.ie/webhook/upstream-blog`.

- **1 n8n workflow** at
  `infrastructure/stacks/n8n/workflows/upstream-blog-monitor.json` (alongside
  the 6 seeded `team-*.json` workflows): webhook → parse Firecrawl
  `monitor.page` payload → POST to DLT incremental source →
  enqueue Dagster `upstream_blog_monitor_ingest` run via GraphQL.

### 3 new CocoIndex v1 Apps

Each app imports `shared_lifespan` + the 3 shared ContextKeys
(`LANCE_DB`, `EMBEDDER`, `RESOLVED_FILE_REGISTRY`) from
`oideachais.cocoindex_flows._lifespan` per REFACTORING.md item 12.
No app re-declares a lifespan.

- **`sruth/oideachais/cocoindex_flows/upstream_blog_monitor.py`** —
  consumes the DLT landing table produced by the n8n workflow.
  - `app = coco.App(coco.AppConfig(name="UpstreamBlogMonitor"), app_main)`
  - `@coco.lifespan` delegates to `shared_lifespan`
  - `@coco.fn(memo=True) ingest_blog_post` runs
    BAML `ExtractBlogPostMetadata` → emits
    `(BlogPostNode, BlogPostChunk)` rows
  - `@coco.fn build_blog_graph` declares the `BlogPostNode` +
    `AFFECTS_PACKAGE` edges into the NEW FalkorDB graph
    `upstream_packages_graph` (separate from `docs_skills_graph`)
  - LanceDB target `upstream_blog_chunks` with HNSW on
    `embedding` (`BAAI/bge-large-en-v1.5` per
    `_lifespan.py:70`)

- **`sruth/oideachais/cocoindex_flows/cocoindex_v1_conformance.py`** —
  static linter wrapped as a Dagster `asset_check`. Enforces 4
  rules on every v1 CocoIndex App:
  - **R1** imports `shared_lifespan` from
    `oideachais.cocoindex_flows._lifespan`
  - **R2** declares no new `coco.ContextKey` without a documented
    purpose (exempt `LANCE_DB`, `EMBEDDER`,
    `RESOLVED_FILE_REGISTRY` from `_lifespan` + the 2 new keys
    `KG_DB_UPSTREAM`, `BAML_CLIENT_UPSTREAM` declared in this
    change)
  - **R3** declares `app = coco.App(coco.AppConfig(name=...),
    app_main)` at module level (NOT `@coco.flow` + `coco.index_flow`
    v0-style wrapper)
  - **R4** has at least one `@coco.fn(memo=True)` decorator on a
    processing function
  - Exposes a `ConformanceReport` dataclass + a
    `run_conformance_check(repo_root: pathlib.Path) -> ConformanceReport`
    entrypoint. Dagster `asset_check` wraps the call.

- **`sruth/oideachais/cocoindex_flows/upstream_api_surface.py`** —
  watches the 4 cocoindex docs URLs (same as
  `cocoindex_docs.yml` monitor, but the App is the canonical
  in-pipeline view). BAML `ExtractCocoIndexApiChange` → emits
  `(ApiChangeNode, ApiChangeChunk)` rows + declares `AFFECTS_APP`
  edges from each change to the v1 App it touches (matched by
  the symbol name in `text`). `upstream_breaking_change_sensor`
  fires a Slack alert on any edge where `severity = "BREAKING"`.

### 1 new DLT incremental source

- **`sruth/oideachais/dlt_sources/domains/cross/upstream/blog_post.py`**
  — reads n8n-webhook payloads from an S3-compatible Garage bucket
  `oideachais-upstream-webhooks/` (the n8n workflow drops raw
  payloads there). Incremental cursor on `payload["metadata"]["first_seen_at"]`.
  Writes to `oideachais.upstream_blog_posts` table in DuckLake.

  Note: `dlt_sources/domains/cross/` does not yet exist — this
  change creates it. `lateralise-dlt-sources-to-domains/` already
  proposes `domains/education/{nation}/` + `domains/{medicine,law,
  culture}/{nation}/`; the new `cross/` subdirectory follows
  the same naming convention for sources that span domains
  (upstream monitoring, change detection, cross-corpus KG).

### 5 new Dagster assets + 1 sensor

- **`sruth/oideachais/dagster_defs/assets/upstream_monitoring_assets.py`**:
  - `upstream_blog_monitor_ingest` — runs the DLT source on
    Garage bucket delta
  - `upstream_blog_chunk_and_tag` — runs `cocoindex update
    oideachais.cocoindex_flows.upstream_blog_monitor`
  - `upstream_blog_graph_publish` — `asset_check` that verifies
    `upstream_packages_graph` has the expected node count
  - `cocoindex_v1_conformance_check` — runs
    `cocoindex_v1_conformance.run_conformance_check`; blocks the
    asset group on any R1/R2/R3/R4 violation
  - `upstream_api_surface_publish` — runs the API-surface App,
    writes a per-package `ApiChange` report to
    `docs/upstream/api-changes/{package}.md`
  - Sensor `upstream_breaking_change_sensor` — fires on any
    `ApiChangeNode` with `severity="BREAKING"`; routes to Slack
    `#upstream-breaking-changes`

### 4 new task aliases

In `mise.toml` and `package.json`:

- `bun run upstream:blog` → `uv run cocoindex update oideachais.cocoindex_flows.upstream_blog_monitor`
- `bun run upstream:blog:live` → `uv run cocoindex update -L oideachais.cocoindex_flows.upstream_blog_monitor`
- `bun run upstream:conformance` → `uv run dagster asset materialize --select cocoindex_v1_conformance_check`
- `bun run upstream:api-surface` → `uv run cocoindex update oideachais.cocoindex_flows.upstream_api_surface`

### 1 new BAML file

- **`sruth/oideachais/baml_src/upstream_monitoring.baml`** with 3
  extraction functions, all routing through `ExtractEn` from
  `baml_src/clients.baml`:
  - `ExtractBlogPostMetadata(content, url) -> BlogPostMetadata`
    — fields: `(title, author, published_at, package,
    blog_post_type, summary, affected_capabilities[], code_examples[],
    api_changes[])`
  - `ExtractCocoIndexApiChange(content, url) -> ApiChange`
    — fields: `(symbol, old_signature, new_signature, severity,
    migration_steps[], example_code, changelog_url)`
  - `ExtractPackageRelease(content, url) -> PackageRelease` —
    fields: `(package, version, release_date, breaking_changes[],
    new_features[], deprecations[])`

### MODIFIED `schema-type-standardization` spec

Adds 2 new enum types at `sruth/oideachais/core/types.py`:

- `Package` enum: `MOTHERDUCK`, `DLTHUB`, `LANCEDB`, `COCOINDEX`
- `BlogPostType` enum: `ANNOUNCEMENT`, `TUTORIAL`, `BENCHMARK`,
  `CASE_STUDY`, `RELEASE_NOTES`, `API_DOC`

(Existing `Quadrant`, `DocumentType`, `EmbeddingModel` enums from
`four-directory-indexing-and-standards/specs/schema-type-standardization/spec.md`
stay as-is.)

### Lifespan migrations (REFACTORING.md item 12 enforcement precondition)

- `codebase_indexing.py` — replace its own `@coco.lifespan`
  (lines 485-495 + 585-599 per the prior read) with a
  `shared_lifespan` delegation.
- `docs_skills_consolidation.py` — replace its own
  `@coco.lifespan` (lines 384-405) + rename ContextKey
  `docs_skills_lance_db` → `oideachais_lance_db` (already exported
  by `_lifespan.py`).
- `culture_heritage_embedding.py` — migrate from the non-canonical
  `@coco.flow(scope="global")` + `coco.index_flow(...)` wrapper
  to the canonical `coco.App` + `@coco.fn` pattern + delegate
  `@coco.lifespan` to `shared_lifespan`. (`culture_heritage_embedding.py:130-155`
  currently wraps a function instead of declaring `app = coco.App(...)`
  at module level.)
- `leabharlann_embedding.py` — audit confirmed it already uses
  `shared_lifespan`; no change required.

### `__init__.py` export update

`sruth/oideachais/cocoindex_flows/__init__.py:33-145` currently exports
only 5 Apps (leabharlann_*, docs_skills_*, codebase_*). This change
adds the 6 missing Apps (`api_indexing`, `filesystem_indexing`,
`storage_indexing`, `config_indexing`, `unified_embedding`,
`culture_heritage_embedding`) + the 3 new Apps
(`upstream_blog_monitor_app`, `upstream_api_surface_app`,
`cocoindex_v1_conformance_app`) = 14 exports.

Also: fix the stale docstring at
`sruth/oideachais/cocoindex_flows/__init__.py:1-26` (claims
`curriculum_embedding_v1` + `research_embedding_v1` exist — they
do not on disk) and the docstring at
`sruth/oideachais/cocoindex_flows/_lifespan.py:1-16` (claims "9 v1
Apps" — actual disk count is 10 .py files + leabharlann's 3
sub-Apps = 12 Apps; with this change it becomes 15).

### 8 skill updates

- `.agents/skills/cocoindex/SKILL.md` — add v1.0.7 reference,
  v0→v1 mapping table, `coco.lifespan` + `ContextKey` patterns,
  FalkorDB connector ref, `coco.auto_refresh` (new in v1.0.7)
- `.agents/skills/oideachais-cocoindex-v1/SKILL.md` — add the 3
  new Apps to registry (12 → 15), 4-rule conformance contract,
  `_lifespan.py` reference
- `.agents/skills/change-detection/SKILL.md` — extend from 3
  layers to 4 (Firecrawl monitor = layer 4 for blog/changelog
  without sitemaps); wire `upstream_blog_monitor` +
  `upstream_api_surface` as layer-4 exemplars
- `.agents/skills/upstream-mirrors/SKILL.md` — add Firecrawl
  monitor as upstream-drift detection layer for the 11 KCG mirror
  summaries
- `.agents/skills/lancedb/SKILL.md` — note Lance Blob V2 + Lance
  Format v2.2 (50% storage reduction vs Parquet, 68× faster blob
  reads, multimodal first-class); 4 storage modes (Inline / Packed
  / Dedicated / External)
- `.agents/skills/motherduck/SKILL.md` — note DuckLake 1.0 (data
  inlining + data clustering + bucket partitioning + variant
  types); 3 hosting options (managed / BYOB / DuckLake)
- `.agents/skills/dlt/SKILL.md` — note dltHub Pro (9,700+ source
  contexts, Cortex Code handoff, ADE-Bench 65% vs Claude Code 58%);
  validate strict-secret-hydration mandate (the "without the
  workbench, the agent leaked credentials" finding directly
  confirms our Infisical + mise + Locket flow)
- `.agents/skills/firecrawl-cli/SKILL.md` — add `firecrawl monitor`
  recipes + the `--goal` judge pattern (already partly documented)

### 2 AGENTS.md updates

- `sruth/sruth/oideachais/AGENTS.md` — add `oideachais-cocoindex-v1` to
  the priority 8-skills quick-reference (currently missing —
  confirmed by re-read 2026-06-25)
- `openspec/AGENTS.md` — add `oideachais-cocoindex-v1` to the
  priority 4-skills quick-reference (currently missing); add the
  new `upstream-package-monitoring` spec to the 32-spec catalogue
  (becoming spec #33)

## Impact

- **Affected specs:**
  - NEW `upstream-package-monitoring` — 3 ADDED Requirements:
    UpstreamBlogMonitor, CocoIndexV1Conformance, UpstreamApiSurface
  - MODIFIED `schema-type-standardization` — adds `Package` +
    `BlogPostType` enum types
  - MODIFIED `oideachais-cocoindex-v1-migration` (if exists) —
    adds a `### Note: conformance enforcement` paragraph pointing
    at the new `cocoindex_v1_conformance` App
- **Affected code:**
  - `sruth/oideachais/cocoindex_flows/{upstream_blog_monitor,
    cocoindex_v1_conformance, upstream_api_surface}.py` — NEW
  - `sruth/oideachais/cocoindex_flows/{codebase_indexing,
    docs_skills_consolidation, culture_heritage_embedding}.py` —
    MODIFIED to use `shared_lifespan` + canonical v1 pattern
  - `sruth/oideachais/cocoindex_flows/__init__.py` — MODIFIED to
    export 14 Apps (currently 5)
  - `sruth/oideachais/cocoindex_flows/_lifespan.py` — MODIFIED to
    fix stale "9 v1 Apps" docstring
  - `sruth/oideachais/dagster_defs/assets/upstream_monitoring_assets.py`
    — NEW (5 assets + 1 sensor)
  - `sruth/oideachais/dagster_defs/assets/__init__.py` — MODIFIED to
    register the new asset group
  - `sruth/oideachais/dlt_sources/domains/cross/upstream/blog_post.py`
    — NEW
  - `sruth/oideachais/dlt_sources/domains/cross/__init__.py` — NEW
    (empty init for the new cross/ subdirectory)
  - `sruth/oideachais/core/types.py` — MODIFIED to add `Package` +
    `BlogPostType` enums
  - `sruth/oideachais/baml_src/upstream_monitoring.baml` — NEW
  - `infrastructure/firecrawl/monitors/upstream_packages/
    {motherduck,dlthub,lancedb,cocoindex}.yml` — NEW (4 files)
  - `infrastructure/stacks/n8n/workflows/upstream-blog-monitor.json` — NEW
  - `mise.toml` + `package.json` — MODIFIED (4 task aliases)
- **Affected agent skills:** 8 skills listed above
- **Affected CI:**
  - `mise run lint:skills` (validates the 8 updated skills)
  - `mise run lint:openspec` (validates this change)
  - `mise run py:typecheck` (covers new Python modules)
  - `mise run baml:generate` (regenerates BAML client for new
    extraction functions)
- **Affected workflows:**
  - `mise dagster:oideachais` — adds the `upstream_monitoring`
    asset group with 5 assets + 1 sensor
  - `n8n.cianfhoghlaim.ie` — adds 1 workflow that bridges
    Firecrawl webhook → DLT → Dagster

## Non-Goals

- This change does **not** rewrite the canonical content of any
  upstream blog post or doc page. It only ingests, extracts,
  embeds, and graph-links the existing material.
- This change does **not** migrate the v0 CocoIndex modules in
  `sruth/oideachais/cocoindex_flows/_v0_archive/` (those stay on disk).
- This change does **not** cognify the new FalkorDB edges into
  Cognee. The graph is cognify-ready (entity-typed `BlogPostNode`
  + `PackageNode` + `ApiChangeNode` + `CapabilityNode`) and can
  be picked up by `infrastructure/scripts/cognee-ingest-docs.py --all`
  in a follow-up change.
- This change does **not** add a RAGAS eval asset for the new
  indices. That's a follow-up change once we have ≥ 7 days of
  stable runs to compare against.
- This change does **not** add Firecrawl monitors for any package
  outside the 4 listed (motherduck / dlthub / lancedb / cocoindex).
  Adding browser-tools / babyagi / stagehand etc. is a follow-up.
- This change does **not** delete the `culture_heritage_embedding.py`
  v0-style wrapper — it migrates it to the canonical v1 pattern.
- This change does **not** touch `sruth/refactor-quadrants-to-sruth/`
  (still in flight, 0/134 tasks). It uses the new `sruth/sruth/oideachais/...`
  path conventions on the assumption that change will land first.

## Dependencies

- **Requires `four-directory-indexing-and-standards/` to merge
  first** — this change extends its `schema-type-standardization`
  spec. If that change is still in flight when this change is
  reviewed, the proposal.md reviewer should read both side by
  side and confirm the merged `sruth/oideachais/core/types.py` exports
  `Package` + `BlogPostType` enums without conflict.
- **Recommends `refactor-quadrants-to-sruth/` to merge first** —
  this change uses the new `sruth/sruth/oideachais/...` paths. If
  that change is still in flight when this change is reviewed,
  paths in `tasks.md` should be interpreted as the post-move
  locations.
