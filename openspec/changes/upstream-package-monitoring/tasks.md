# Tasks: upstream-package-monitoring

> Implementation tasks for the `upstream-package-monitoring`
> OpenSpec change. Each task is small, testable, and traceable
> to a `## Requirements` block in `proposal.md`.

## 1. BAML schema additions

- [ ] 1.1 Create
  `sruth/sruth/oideachais/baml_src/upstream_monitoring.baml` with 3
  extraction functions and their Pydantic-style classes:
  - [ ] 1.1.1 `ExtractBlogPostMetadata(content: string, url: string) -> BlogPostMetadata`
    with fields `(title, author, published_at: datetime, package: enum, blog_post_type: enum, summary: string, affected_capabilities: list[string], code_examples: list[string], api_changes: list[string])`
  - [ ] 1.1.2 `ExtractCocoIndexApiChange(content: string, url: string) -> ApiChange`
    with fields `(symbol: string, old_signature: string, new_signature: string, severity: enum[BREAKING|MAJOR|MINOR|PATCH], migration_steps: list[string], example_code: string, changelog_url: string)`
  - [ ] 1.1.3 `ExtractPackageRelease(content: string, url: string) -> PackageRelease`
    with fields `(package: enum, version: string, release_date: datetime, breaking_changes: list[string], new_features: list[string], deprecations: list[string])`
  - [ ] 1.1.4 All 3 route through the canonical `ExtractEn`
    client from `sruth/sruth/oideachais/baml_src/clients.baml:243-251`
- [ ] 1.2 Run `mise run baml:generate` (or `cd sruth/oideachais
  && uv run baml-cli generate`) and verify
  `baml_client/upstream_monitoring.py` is created.
- [ ] 1.3 Confirm the new file is auto-picked-up by
  `baml_src/__init__.py` (no manual re-export needed if
  BAML glob includes `**/*.baml`).

## 2. CocoIndex v1 App: upstream blog monitor

- [ ] 2.1 Create
  `sruth/sruth/oideachais/cocoindex_flows/upstream_blog_monitor.py`
  with:
  - [ ] 2.1.1 Imports `shared_lifespan`, `LANCE_DB`, `EMBEDDER`,
    `RESOLVED_FILE_REGISTRY`, `LANCEDB_URI`, `EMBED_MODEL`,
    `EMBED_DIM` from `oideachais.cocoindex_flows._lifespan`.
    **No new ContextKeys declared** (R2 conformance rule).
  - [ ] 2.1.2 `@coco.lifespan` that wraps `shared_lifespan`
    and additionally provides a `KG_DB_UPSTREAM` ContextKey
    (`detect_change=False`) bound to a FalkorDB connection
    selected on graph `upstream_packages_graph`. The
    `KG_DB_UPSTREAM` ContextKey is exempt from R2 (declared in
    `tasks.md:§ 8`).
  - [ ] 2.1.3 `app_main` that mounts
    `localfs.walk_dir("stedding/upstream_blog_payloads/",
    recursive=True, live=True, refresh_interval=120s)` where
    `stedding/upstream_blog_payloads/` is the local mirror
    populated by the n8n workflow.
  - [ ] 2.1.4 Phase 1 `@coco.fn(memo=True) process_blog_payload`
    that runs `ExtractBlogPostMetadata` and emits an
    `UpstreamBlogChunk` dataclass row.
  - [ ] 2.1.5 Phase 2 `@coco.fn build_blog_graph` that declares
    `BlogPostNode` + `PackageNode` + `CapabilityNode` nodes
    and `PUBLISHED_BY` / `AFFECTS_CAPABILITY` /
    `MENTIONS_PACKAGE` edges into the
    `upstream_packages_graph` FalkorDB graph.
  - [ ] 2.1.6 LanceDB target `upstream_blog_chunks` with HNSW
    on `embedding` (vector_dim=1024, hnsw_drop_threshold=50).
  - [ ] 2.1.7
    `app = coco.App(coco.AppConfig(name="UpstreamBlogMonitor"),
    app_main)` at module level (R3 conformance rule).

## 3. CocoIndex v1 App: cocoindex v1 conformance

- [ ] 3.1 Create
  `sruth/sruth/oideachais/cocoindex_flows/cocoindex_v1_conformance.py`
  with:
  - [ ] 3.1.1 Imports `shared_lifespan` from
    `oideachais.cocoindex_flows._lifespan` (R1 conformance rule).
  - [ ] 3.1.2 A `ConformanceReport` dataclass
    `(app_name, r1_pass, r2_pass, r3_pass, r4_pass,
    violations: list[str], checked_at: datetime)`.
  - [ ] 3.1.3 A `run_conformance_check(repo_root: pathlib.Path)
    -> ConformanceReport` function that walks every
    `sruth/sruth/oideachais/cocoindex_flows/*.py` file (except
    `__init__.py`, `_lifespan.py`, `_v0_archive/`) and applies
    the 4 rules:
    - **R1**: AST contains `from ._lifespan import` AND
      `shared_lifespan` referenced
    - **R2**: no `coco.ContextKey[` declaration outside
      `_lifespan.py` AND any `coco.ContextKey[` declaration
      in the file has a sibling `# R2-exempt: <reason>` comment
    - **R3**: AST contains `coco.App(coco.AppConfig(`
    - **R4**: AST contains `@coco.fn(`
  - [ ] 3.1.4
    `app = coco.App(coco.AppConfig(name="CocoIndexV1Conformance"),
    app_main)` at module level. The `app_main` reads the
    `ConformanceReport` from a sibling asset and re-runs the
    check on every change to `cocoindex_flows/*.py`.

## 4. CocoIndex v1 App: upstream api surface

- [ ] 4.1 Create
  `sruth/sruth/oideachais/cocoindex_flows/upstream_api_surface.py`
  with:
  - [ ] 4.1.1 Imports `shared_lifespan`, `LANCE_DB`, `EMBEDDER`,
    `RESOLVED_FILE_REGISTRY` from
    `oideachais.cocoindex_flows._lifespan`.
  - [ ] 4.1.2 `@coco.lifespan` wraps `shared_lifespan` and
    additionally provides `KG_DB_UPSTREAM` (same as § 2) +
    `BAML_CLIENT_UPSTREAM` ContextKey
    (`detect_change=False`) bound to the BAML client instance
    from `upstream_monitoring.baml`.
  - [ ] 4.1.3 `app_main` mounts the 4 cocoindex docs URLs
    via `localfs.read_url` (or a S3-cached mirror) +
    `llms-full.txt`; refresh_interval=3600s (1 hour).
  - [ ] 4.1.4 Phase 1 `@coco.fn(memo=True) extract_api_change`
    that runs `ExtractCocoIndexApiChange` and emits an
    `ApiChangeChunk` row.
  - [ ] 4.1.5 Phase 2 `@coco.fn build_api_change_graph` that
    declares `ApiChangeNode` + `V1AppNode` nodes and `AFFECTS_APP`
    edges from each `ApiChangeNode` to the matching `V1AppNode`
    (matched by symbol name in `text`).
  - [ ] 4.1.6 LanceDB target `upstream_api_chunks` with HNSW.
  - [ ] 4.1.7
    `app = coco.App(coco.AppConfig(name="UpstreamApiSurface"),
    app_main)` at module level.

## 5. Lifespan migrations (REFACTORING.md item 12 enforcement precondition)

- [ ] 5.1 In
  `sruth/sruth/oideachais/cocoindex_flows/codebase_indexing.py`:
  - [ ] 5.1.1 Replace its own `@coco.lifespan` (the one at the
    top-level `codebase_app`) with a delegation to
    `shared_lifespan` from `_lifespan`.
  - [ ] 5.1.2 Remove any local `LANCE_DB` / `EMBEDDER` /
    `RESOLVED_FILE_REGISTRY` ContextKey declarations; import
    them from `_lifespan` instead.
- [ ] 5.2 In
  `sruth/sruth/oideachais/cocoindex_flows/docs_skills_consolidation.py`:
  - [ ] 5.2.1 Replace its own `@coco.lifespan` (the one at the
    top-level `docs_skills_app`) with a delegation to
    `shared_lifespan`.
  - [ ] 5.2.2 Rename the local `docs_skills_lance_db` ContextKey
    → `oideachais_lance_db` (the canonical name from
    `_lifespan.py:53`). Update all references within the file.
- [ ] 5.3 In
  `sruth/sruth/oideachais/cocoindex_flows/culture_heritage_embedding.py`:
  - [ ] 5.3.1 Migrate from the non-canonical
    `@coco.flow(scope="global")` + `coco.index_flow(...)`
    wrapper (lines 130-155 per the prior read) to the canonical
    `app = coco.App(coco.AppConfig(name="CultureHeritageEmbedding"),
    app_main)` + `@coco.fn(memo=True)` pattern.
  - [ ] 5.3.2 Replace its own `@coco.lifespan` (lines 137-142)
    with a delegation to `shared_lifespan`.
  - [ ] 5.3.3 Confirm the CLI entry point
    (`python -m oideachais.cocoindex_flows.culture_heritage_embedding update`)
    still works with the new module-level `app`.
- [ ] 5.4 In
  `sruth/sruth/oideachais/cocoindex_flows/leabharlann_embedding.py`:
  - [ ] 5.4.1 Audit confirmed it already delegates to
    `shared_lifespan`. No change required.

## 6. __init__.py export update

- [ ] 6.1 In
  `sruth/sruth/oideachais/cocoindex_flows/__init__.py`:
  - [ ] 6.1.1 Fix the stale docstring at lines 1-26 (claims
    `curriculum_embedding_v1` + `research_embedding_v1` exist —
    they do not on disk).
  - [ ] 6.1.2 Add exports for the 6 missing Apps that already
    exist on disk but are not re-exported:
    `api_indexing`, `filesystem_indexing`, `storage_indexing`,
    `config_indexing`, `unified_embedding`,
    `culture_heritage_embedding`. Each gets a `try/except
    ImportError` guard matching the existing pattern at
    lines 33-145.
  - [ ] 6.1.3 Add exports for the 3 new Apps from this change:
    `upstream_blog_monitor`, `upstream_api_surface`,
    `cocoindex_v1_conformance`.
  - [ ] 6.1.4 Add the new exports to `__all__`.
- [ ] 6.2 In
  `sruth/sruth/oideachais/cocoindex_flows/_lifespan.py`:
  - [ ] 6.2.1 Fix the stale "9 v1 Apps" docstring at lines 1-16.
    Replace with the canonical count = 12 (current) → 15
    (after this change lands).

## 7. Schema-mask + data-type standardisation (extension)

- [ ] 7.1 In
  `sruth/sruth/oideachais/core/types.py` (created by
  `four-directory-indexing-and-standards/` § 4):
  - [ ] 7.1.1 Add `Package` enum:
    `(MOTHERDUCK, DLTHUB, LANCEDB, COCOINDEX)`
  - [ ] 7.1.2 Add `BlogPostType` enum:
    `(ANNOUNCEMENT, TUTORIAL, BENCHMARK, CASE_STUDY,
    RELEASE_NOTES, API_DOC)`
  - [ ] 7.1.3 Confirm `Quadrant`, `DocumentType`, `EmbeddingModel`
    enums from the parent change are still present.
- [ ] 7.2 Re-export both enums from
  `sruth/codeolas/core/types.py` for the publishable wheel.

## 8. DLT incremental source

- [ ] 8.1 Create
  `sruth/sruth/oideachais/dlt_sources/domains/cross/__init__.py`
  (empty marker file for the new `cross/` subdirectory).
- [ ] 8.2 Create
  `sruth/sruth/oideachais/dlt_sources/domains/cross/upstream/__init__.py`
  (empty marker file for the new `upstream/` subdirectory).
- [ ] 8.3 Create
  `sruth/sruth/oideachais/dlt_sources/domains/cross/upstream/blog_post.py`
  with:
  - [ ] 8.3.1 A `blog_post_source(storage_root: pathlib.Path = ...)`
    factory that returns a DLT `@resource` iterator.
  - [ ] 8.3.2 Reads `*.jsonl` payloads from
    `${storage_root}/upstream_blog_payloads/` where each
    payload is the JSON body POSTed by the n8n workflow.
  - [ ] 8.3.3 Incremental cursor on
    `payload["metadata"]["first_seen_at"]` (ISO 8601
    timestamp) using the `add_incremental` helper from
    `.agents/skills/add-incremental-loading/SKILL.md`.
  - [ ] 8.3.4 Schema fields:
    `(blog_post_id, url, title, author, package,
    blog_post_type, summary, first_seen_at, published_at,
    raw_markdown)` matching the BAML `BlogPostMetadata`
    class plus `raw_markdown` (the unprocessed Firecrawl
    payload).
  - [ ] 8.3.5 Default destination: `ducklake` (per
    `oideachais-storage/SKILL.md` — writes to DuckLake on
    Garage S3 + Postgres catalog; reads via `md:oideachais`).

## 9. Dagster assets + sensor

- [ ] 9.1 Create
  `sruth/sruth/oideachais/dagster_defs/assets/upstream_monitoring_assets.py`
  with 5 assets + 1 sensor:
  - [ ] 9.1.1 `upstream_blog_monitor_ingest` — runs the DLT
    source from § 8. Materialises `oideachais.upstream_blog_posts`
    rows in DuckLake. Partitioned by `published_at` (daily).
  - [ ] 9.1.2 `upstream_blog_chunk_and_tag` — runs
    `uv run cocoindex update
    oideachais.cocoindex_flows.upstream_blog_monitor`. Depends
    on `upstream_blog_monitor_ingest`.
  - [ ] 9.1.3 `upstream_blog_graph_publish` — `asset_check`
    that verifies the `upstream_packages_graph` FalkorDB
    graph has the expected node count. Depends on
    `upstream_blog_chunk_and_tag`.
  - [ ] 9.1.4 `cocoindex_v1_conformance_check` — runs
    `cocoindex_v1_conformance.run_conformance_check`. Blocks
    the asset group on any R1/R2/R3/R4 violation. Materialises
    a `conformance_status` asset + a `conformance_report`
    asset materialisation with the latest
    `ConformanceReport` JSON.
  - [ ] 9.1.5 `upstream_api_surface_publish` — runs
    `uv run cocoindex update
    oideachais.cocoindex_flows.upstream_api_surface`. Writes
    a per-package Markdown report to
    `sruth/sruth/oideachais/docs/upstream/api-changes/{package}.md`.
  - [ ] 9.1.6 Sensor `upstream_breaking_change_sensor` —
    runs every 5 minutes. Queries the
    `upstream_packages_graph` FalkorDB graph for any
    `ApiChangeNode` with `severity="BREAKING"` created
    since the last sensor tick. Routes to Slack
    `#upstream-breaking-changes` via the existing
    `infrastructure/scripts/slack_webhook.py` helper.
- [ ] 9.2 Register all 6 in
  `sruth/sruth/oideachais/dagster_defs/assets/__init__.py`
  by appending to `all_assets` (line 173).

## 10. Task aliases

- [ ] 10.1 In `mise.toml`, add:
  - [ ] 10.1.1 `[tasks."upstream:blog"]` →
    `uv run cocoindex update oideachais.cocoindex_flows.upstream_blog_monitor`
  - [ ] 10.1.2 `[tasks."upstream:blog:live"]` →
    `uv run cocoindex update -L oideachais.cocoindex_flows.upstream_blog_monitor`
  - [ ] 10.1.3 `[tasks."upstream:conformance"]` →
    `uv run dagster asset materialize --select cocoindex_v1_conformance_check`
  - [ ] 10.1.4 `[tasks."upstream:api-surface"]` →
    `uv run cocoindex update oideachais.cocoindex_flows.upstream_api_surface`
- [ ] 10.2 Mirror the same 4 scripts in `package.json` under
  the `scripts` key.
- [ ] 10.3 Confirm `bun run upstream:blog` and
  `bun run upstream:conformance` work end-to-end.

## 11. Firecrawl monitors

- [ ] 11.1 Create
  `infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml`
  with: page=`https://motherduck.com/blog/`, scheduleText=
  `every 30 minutes`, goal=`Alert when a new blog post is published, an existing post's headline changes, or a new product capability (DuckLake, BYOB, Cortex Code integration) is announced. Ignore marketing-only changes, webinars, hiring posts, and podcast appearances.`, webhookUrl=`https://n8n.cianfhoghlaim.ie/webhook/upstream-blog?package=motherduck`.
- [ ] 11.2 Create `dlthub_blog.yml` (page=`https://dlthub.com/blog`,
  goal filtered to source-context additions + ADE-Bench /
  Cortex Code integration updates, package=dlthub).
- [ ] 11.3 Create `lancedb_blog.yml` (page=`https://www.lancedb.com/blog/`,
  goal filtered to Lance Format / Lance Blob / multimodal
  releases, package=lancedb).
- [ ] 11.4 Create `cocoindex_docs.yml` (pages=[`https://cocoindex.io/docs/skill.md`,
  `https://cocoindex.io/docs/getting_started/quickstart`,
  `https://cocoindex.io/docs/advanced_topics/live_component`,
  `https://cocoindex.io/docs/connectors/falkordb`,
  `https://cocoindex.io/llms-full.txt`], goal filtered to
  `coco.App`, `@coco.fn`, `@coco.lifespan`, `coco.auto_refresh`,
  FalkorDB connector API-surface changes, package=cocoindex).
- [ ] 11.5 Apply all 4 monitors via
  `firecrawl monitor create --body-file infrastructure/firecrawl/monitors/upstream_packages/<name>.yml`.
- [ ] 11.6 Confirm the monitors list at
  `firecrawl monitor list` shows 4 active monitors tagged
  with `upstream-packages` in the name.

## 12. n8n workflow

- [ ] 12.1 Create
  `engineering/n8n/workflows/upstream-blog-monitor.json` with:
  - [ ] 12.1.1 A `Webhook` node bound to
    `/webhook/upstream-blog` (path),
    `POST` (method), with query-param `package` filter
    matching the 4 packages.
  - [ ] 12.1.2 A `Function` node that validates the Firecrawl
    `monitor.page` payload schema (Zod-equivalent Python
    type-check; the Firecrawl v2 webhook contract is
    documented at `https://docs.firecrawl.dev/features/monitor`).
  - [ ] 12.1.3 An `S3` (Garage) node that writes the payload
    as a JSONL line to
    `s3://oideachais-upstream-webhooks/<package>/<YYYY-MM-DD>/<blog_post_id>.jsonl`
    (Garage S3 endpoint per `oideachais-storage/SKILL.md`).
  - [ ] 12.1.4 A `GraphQL` node that POSTs to
    `http://dagster:3335/graphql` with the
    `LAUNCH_PARTITION_BACKFILL_MUTATION` for the
    `upstream_blog_monitor_ingest` asset, partitioned by
    `published_at` (daily).
- [ ] 12.2 Import the workflow via
  `n8n import:workflow --input=engineering/n8n/workflows/upstream-blog-monitor.json`
  on the `n8n-init` one-shot container per
  `infrastructure/AGENTS.md`.

## 13. Skill updates

- [ ] 13.1 In
  `.agents/skills/cocoindex/SKILL.md`:
  - [ ] 13.1.1 Add a "CocoIndex v1.0.7 (last reviewed
    2026-06-23)" header at the top of the "When to load"
    table.
  - [ ] 13.1.2 Add the v0→v1 mapping table:
    `@cocoindex.flow_def`/`FlowBuilder` → `coco.App` +
    `@coco.fn`; `add_collector()`/`collect()`/`export()` →
    `declare_row`/`declare_file`;
    `cocoindex.sources/functions/targets.*` → connector APIs
    (`localfs.walk_dir`, `coco.ops.*`,
    `postgres.declare_table_target`).
  - [ ] 13.1.3 Add a section on `@coco.lifespan` + 3
    ContextKeys (`LANCE_DB`, `EMBEDDER`,
    `RESOLVED_FILE_REGISTRY`).
  - [ ] 13.1.4 Add a section on `coco.auto_refresh` (new in
    v1.0.7; replaces Dagster schedule for in-pipeline
    refreshes).
  - [ ] 13.1.5 Add a cross-link to the FalkorDB connector
    docs at
    `https://cocoindex.io/docs/connectors/falkordb`.
- [ ] 13.2 In
  `.agents/skills/oideachais-cocoindex-v1/SKILL.md`:
  - [ ] 13.2.1 Add the 3 new Apps
    (`upstream_blog_monitor_app`,
    `upstream_api_surface_app`,
    `cocoindex_v1_conformance_app`) to the registry
    (currently lists 11 → becomes 14; matches the disk
    reality of 12 existing Apps + 3 new).
  - [ ] 13.2.2 Add the 4-rule conformance contract with a
    cross-link to
    `sruth/sruth/oideachais/cocoindex_flows/cocoindex_v1_conformance.py`.
  - [ ] 13.2.3 Fix the stale "11 v1 Apps" claim in any
    summary.
  - [ ] 13.2.4 Add a "Pair this skill with" entry for
    `change-detection/SKILL.md` (the layer-4 extension lives
    there).
- [ ] 13.3 In
  `.agents/skills/change-detection/SKILL.md`:
  - [ ] 13.3.1 Extend the 3-layer pattern to 4 layers
    (add layer 4: Firecrawl monitor for blog/changelog
    without sitemaps).
  - [ ] 13.3.2 Wire `upstream_blog_monitor` +
    `upstream_api_surface` as layer-4 exemplars.
  - [ ] 13.3.3 Add the canonical
    `firecrawl monitor --page <url> --goal "..."` recipe.
- [ ] 13.4 In
  `.agents/skills/upstream-mirrors/SKILL.md`:
  - [ ] 13.4.1 Add a section "Firecrawl monitor as
    upstream-drift detection" with a cross-link to the
    4 monitor YAMLs.
- [ ] 13.5 In
  `.agents/skills/lancedb/SKILL.md`:
  - [ ] 13.5.1 Add a section "Lance Blob V2" (4 storage
    modes: Inline / Packed / Dedicated / External;
    multimodal first-class).
  - [ ] 13.5.2 Add a section "Lance Format v2.2" (50%+ storage
    reduction vs Parquet, 68× faster blob reads).
  - [ ] 13.5.3 Add a note that the canonical KCG embedder
    `BAAI/bge-large-en-v1.5` (1024-dim) is set via the
    `OIDEACHAIS_EMBED_MODEL` env var at
    `sruth/oideachais/cocoindex_flows/_lifespan.py:70`.
- [ ] 13.6 In
  `.agents/skills/motherduck/SKILL.md`:
  - [ ] 13.6.1 Add a section "DuckLake 1.0" launched
    2026-04-16: data inlining + data clustering + bucket
    partitioning + variant types.
  - [ ] 13.6.2 Re-affirm the 3 hosting options (managed /
    BYOB / DuckLake) with cross-links to
    `sruth/oideachais/dlt_utils/motherduck_options.py`.
- [ ] 13.7 In
  `.agents/skills/dlt/SKILL.md`:
  - [ ] 13.7.1 Add a section "dltHub Pro" launched 2026-04-14:
    9,700+ known source contexts, Cortex Code handoff,
    ADE-Bench 65% task success on Snowflake vs Claude Code
    58%.
  - [ ] 13.7.2 Validate the strict-secret-hydration mandate
    against the dltHub finding "without the workbench, the
    agent leaked credentials" — directly confirms our
    Infisical + mise + Locket flow.
- [ ] 13.8 In
  `.agents/skills/firecrawl-cli/SKILL.md`:
  - [ ] 13.8.1 Add a `firecrawl monitor` recipe with the
    `--goal` judge pattern (the existing docs already
    mention `firecrawl monitor`; add the `monitor run`,
    `monitor get`, `monitor checks` workflow).

## 14. AGENTS.md updates

- [ ] 14.1 In
  `sruth/sruth/oideachais/AGENTS.md`:
  - [ ] 14.1.1 Add `oideachais-cocoindex-v1` to the
    priority 8-skills quick-reference table at the top of
    the file (currently missing — confirmed by re-read
    2026-06-25).
- [ ] 14.2 In
  `openspec/AGENTS.md`:
  - [ ] 14.2.1 Add `oideachais-cocoindex-v1` to the
    priority 4-skills quick-reference table (currently
    missing).
  - [ ] 14.2.2 Add the new `upstream-package-monitoring`
    spec to the 32-spec catalogue (becoming spec #33) at
    the appropriate quadrant row.

## 15. Verification

- [ ] 15.1 `mise run format && mise run lint && mise run py:typecheck`
  — all green.
- [ ] 15.2 `mise run baml:generate` — exits 0.
- [ ] 15.3
  `uv run cocoindex update sruth/sruth/oideachais/cocoindex_flows/upstream_blog_monitor.py`
  — materialises ≥ 1 row on first run with a sample payload
  in `stedding/upstream_blog_payloads/`.
- [ ] 15.4
  `uv run cocoindex update sruth/sruth/oideachais/cocoindex_flows/upstream_api_surface.py`
  — materialises ≥ 1 `ApiChangeChunk` on first run.
- [ ] 15.5
  `uv run python -c "from sruth.oideachais.cocoindex_flows.cocoindex_v1_conformance import run_conformance_check; print(run_conformance_check(pathlib.Path('sruth/sruth/oideachais/cocoindex_flows')))"`
  — returns a `ConformanceReport` with `r1_pass=True,
  r2_pass=True, r3_pass=True, r4_pass=True` for all 15 Apps
  (after migrations in § 5).
- [ ] 15.6
  `mise run dagster:oideachais` — `cocoindex_v1_conformance_check`
  asset materialises successfully + `upstream_blog_graph_publish`
  asset check passes.
- [ ] 15.7
  `firecrawl monitor list` — shows the 4 active monitors.
- [ ] 15.8 Manual webhook smoke test: POST a sample
  `monitor.page` payload to
  `https://n8n.cianfhoghlaim.ie/webhook/upstream-blog?package=motherduck`
  → verify DLT incremental cursor advances + Dagster
  `upstream_blog_monitor_ingest` run completes + FalkorDB
  `BlogPostNode` count increments + Slack alert is NOT
  triggered (severity ≠ BREAKING).
- [ ] 15.9 `openspec validate upstream-package-monitoring
  --strict` — exits 0.

## 16. Land the plane

- [ ] 16.1 `git add -A && git commit` with a Conventional
  Commit message:
  `feat(upstream-package-monitoring): 3 v1 CocoIndex Apps + 4 Firecrawl monitors + n8n bridge + lifespan migrations`.
- [ ] 16.2 `git pull --rebase && git push`.
- [ ] 16.3 `git status` shows "up to date with origin".
- [ ] 16.4 Open follow-up issues for: Cognee cognify of the
  new FalkorDB edges; RAGAS eval asset once ≥ 7 days of
  stable runs exist; promote `upstream-package-monitoring`
  spec from oideachais quadrant to shared if other
  quadrants start consuming it.

## Reference

- OpenSpec change:
  `openspec/changes/upstream-package-monitoring/`
- Sister change (dependency):
  `openspec/changes/four-directory-indexing-and-standards/`
- Sister change (recommended dependency):
  `openspec/changes/refactor-quadrants-to-sruth/`
- Sister change (related):
  `openspec/changes/lateralise-dlt-sources-to-domains/`
- Sister change (related):
  `openspec/changes/extend-lakehouse-with-nimtable-olake-lancedb/`
- v1 reference patterns:
  `sruth/sruth/oideachais/cocoindex_flows/leabharlann_embedding.py:236-249`
  (canonical lifespan) +
  `sruth/sruth/oideachais/cocoindex_flows/_lifespan.py`
  (shared lifespan home)
- OpenSpec workflow: `openspec/AGENTS.md`
- Dagster definitions:
  `sruth/sruth/oideachais/dagster_defs/assets/__init__.py`
- CocoIndex v1 docs (canonical reference):
  `https://cocoindex.io/docs/skill.md`
