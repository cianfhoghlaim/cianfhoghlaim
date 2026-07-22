# Upstream Package Monitoring Capability

## Purpose

`upstream-package-monitoring` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at:

- `cianfhoghlaim/cocoindex_flows/upstream_blog_monitor.py` —
  CocoIndex v1 App that ingests Firecrawl webhook payloads +
  publishes LanceDB chunks + FalkorDB graph nodes for the 4
  upstream packages
- `cianfhoghlaim/cocoindex_flows/upstream_api_surface.py` —
  CocoIndex v1 App that watches the cocoindex docs + llms-full.txt
  + extracts API-surface changes
- `cianfhoghlaim/cocoindex_flows/cocoindex_v1_conformance.py` —
  CocoIndex v1 App that enforces 4 conformance rules on every v1
  App (the enforcement layer for REFACTORING.md item 12)
- `cianfhoghlaim/dlt_sources/domains/cross/upstream/blog_post.py` —
  DLT incremental source from the n8n webhook bridge
- `cianfhoghlaim/dagster_defs/assets/upstream_monitoring_assets.py` —
  5 Dagster assets + 1 breaking-change sensor
- `cianfhoghlaim/baml_src/upstream_monitoring.baml` — 3
  BAML extraction functions (`ExtractBlogPostMetadata`,
  `ExtractCocoIndexApiChange`, `ExtractPackageRelease`)
- `infrastructure/firecrawl/monitors/upstream_packages/*.yml` —
  4 Firecrawl monitor configs (motherduck / dlthub / lancedb /
  cocoindex)
- `bonneagar/stacks/n8n/workflows/upstream-blog-monitor.json` — n8n
  workflow that bridges Firecrawl webhook → DLT → Dagster

See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

## Background

The Cianfhoghlaim stack stands on the shoulders of four upstream
packages that ship weekly: `motherduck` (DuckLake 1.0 + Cortex
Code handoff), `dlthub` (9,700+ source contexts + dltHub Pro),
`lancedb` (Lance Blob V2 + Lance Format v2.2), and `cocoindex`
(v1.0.7 + FalkorDB connector + `coco.auto_refresh`). Without a
canonical place to ingest, extract, embed, and graph-link their
weekly releases, the platform drifts silently from upstream
best practice. This capability is the steady-state ingestion
pipeline that closes that gap and serves as the enforcement
layer for CocoIndex v1 conformance (REFACTORING.md item 12).

## Requirements

### Requirement: Upstream Blog Monitor

The system SHALL expose a CocoIndex v1 App at
`cianfhoghlaim.cocoindex_flows.upstream_blog_monitor` (named
`UpstreamBlogMonitor` in `coco.AppConfig`) that ingests Firecrawl
webhook payloads for blog posts from the four upstream packages
(motherduck / dlthub / lancedb / cocoindex), extracts structured
metadata via BAML `ExtractBlogPostMetadata`, and publishes both
LanceDB chunks and FalkorDB graph nodes + edges.

#### Scenario: First-run materialisation

- **GIVEN** a Firecrawl monitor webhook has fired for a new
  motherduck blog post
- **WHEN** the payload lands in
  `stedding/upstream_blog_payloads/` and `uv run cocoindex update
  cianfhoghlaim.cocoindex_flows.upstream_blog_monitor` runs
- **THEN** the App SHALL emit at least one `UpstreamBlogChunk`
  row to LanceDB table `upstream_blog_chunks` (HNSW index on
  `embedding`)
- **AND** the App SHALL declare one `BlogPostNode` +
  one `PackageNode` (with `package=MOTHERDUCK`) + at least one
  `PUBLISHED_BY` edge in FalkorDB graph
  `upstream_packages_graph`
- **AND** the `id` column of each LanceDB row SHALL be
  deterministic (derived from `(url_sha256, content_sha256)` via
  `IdGenerator()`)

#### Scenario: 100-row batch minimum

- **GIVEN** the App is processing 250 new blog posts
- **WHEN** it calls `lancedb.mount_table_target`
- **THEN** the App SHALL batch upserts in groups of ≥ 100 rows
  per the embedding-pipeline skill minimum
- **AND** if a batch exceeds 50 vector changes since the last
  update, the App SHALL drop and rebuild the HNSW index
  (HNSW-DROP-THRESHOLD=50)

#### Scenario: R2 conformance exemption declaration

- **GIVEN** the App declares an additional ContextKey
  `KG_DB_UPSTREAM` bound to a FalkorDB connection
- **WHEN** the `cocoindex_v1_conformance` App audits the file
- **THEN** the audit SHALL recognise the `# R2-exempt: ...`
  comment as a valid exemption
- **AND** the conformance report SHALL record the exemption
  reason verbatim

### Requirement: CocoIndex v1 Conformance

The system SHALL expose a CocoIndex v1 App at
`cianfhoghlaim.cocoindex_flows.cocoindex_v1_conformance` (named
`CocoIndexV1Conformance`) that implements a static linter
enforcing 4 conformance rules on every v1 CocoIndex App under
`cianfhoghlaim/cocoindex_flows/`, and SHALL expose a
`ConformanceReport` dataclass + a
`run_conformance_check(repo_root)` entrypoint usable as a Dagster
`asset_check`.

#### Scenario: R1 — shared lifespan delegation

- **GIVEN** a v1 CocoIndex App at
  `cianfhoghlaim/cocoindex_flows/<name>.py`
- **WHEN** `run_conformance_check` is invoked
- **THEN** the App SHALL be flagged as R1-FAILING if the AST
  does NOT contain `from ._lifespan import` AND a reference to
  the symbol `shared_lifespan`
- **AND** the App SHALL be flagged as R1-PASSING otherwise

#### Scenario: R2 — no new ContextKeys without exemption

- **GIVEN** a v1 CocoIndex App declares a `coco.ContextKey[`
  outside of `_lifespan.py`
- **WHEN** `run_conformance_check` is invoked
- **THEN** the App SHALL be flagged as R2-FAILING unless the
  declaration has a sibling comment starting with
  `# R2-exempt:` followed by a non-empty reason
- **AND** the canonical ContextKeys `LANCE_DB`, `EMBEDDER`,
  `RESOLVED_FILE_REGISTRY` from `_lifespan.py` SHALL be
  R2-exempt by default (no comment required when imported
  from `_lifespan`)
- **AND** the additional ContextKeys `KG_DB_UPSTREAM` and
  `BAML_CLIENT_UPSTREAM` SHALL be R2-exempt when declared in
  the 3 new Apps with a `# R2-exempt:` comment

#### Scenario: R3 — canonical v1 pattern

- **GIVEN** a v1 CocoIndex App
- **WHEN** `run_conformance_check` is invoked
- **THEN** the App SHALL be flagged as R3-PASSING if the AST
  contains the substring `coco.App(coco.AppConfig(` at module
  scope (NOT inside a function body)
- **AND** the App SHALL be flagged as R3-FAILING if the AST
  instead contains the v0-style hybrid
  `@coco.flow(scope="global")` + `coco.index_flow(...)`
  wrapper (which `culture_heritage_embedding.py` previously
  used and which this change migrates away from)

#### Scenario: R4 — at least one @coco.fn

- **GIVEN** a v1 CocoIndex App
- **WHEN** `run_conformance_check` is invoked
- **THEN** the App SHALL be flagged as R4-PASSING if the AST
  contains at least one `@coco.fn(` decorator
- **AND** the App SHALL be flagged as R4-FAILING otherwise

#### Scenario: ConformanceReport shape

- **GIVEN** `run_conformance_check(repo_root)` has been
  invoked
- **WHEN** the caller receives the return value
- **THEN** the return SHALL be a `ConformanceReport` dataclass
  with fields `(app_name, r1_pass, r2_pass, r3_pass, r4_pass,
  violations: list[str], checked_at: datetime)`
- **AND** `violations` SHALL contain one human-readable string
  per failed rule per App (e.g. `"codebase_indexing.py: R1
  FAIL — no `from ._lifespan import`"`)

### Requirement: Upstream API Surface Monitor

The system SHALL expose a CocoIndex v1 App at
`cianfhoghlaim.cocoindex_flows.upstream_api_surface` (named
`UpstreamApiSurface`) that watches the canonical CocoIndex v1
docs URLs (`/docs/skill.md`, `/docs/getting_started/quickstart`,
`/docs/advanced_topics/live_component`, `/docs/connectors/falkordb`,
plus `llms-full.txt`), extracts API-surface changes via BAML
`ExtractCocoIndexApiChange`, declares `ApiChangeNode` +
`V1AppNode` graph nodes + `AFFECTS_APP` edges, and SHALL
trigger the `upstream_breaking_change_sensor` Dagster sensor
within 5 minutes whenever a `severity="BREAKING"` change is
detected.

#### Scenario: First-run extraction

- **GIVEN** a new CocoIndex v1.x patch has shipped and the
  `cocoindex_docs.yml` Firecrawl monitor has fired
- **WHEN** `uv run cocoindex update
  cianfhoghlaim.cocoindex_flows.upstream_api_surface` runs
- **THEN** the App SHALL emit at least one `ApiChangeChunk` row
  to LanceDB table `upstream_api_chunks`
- **AND** the App SHALL declare one `ApiChangeNode` +
  one `V1AppNode` (matched by symbol name in `text`) +
  one `AFFECTS_APP` edge in FalkorDB graph
  `upstream_packages_graph`

#### Scenario: Breaking-change sensor routing

- **GIVEN** an `ApiChangeNode` has been declared with
  `severity="BREAKING"` and the
  `upstream_breaking_change_sensor` runs every 5 minutes
- **WHEN** the sensor polls the
  `upstream_packages_graph` FalkorDB graph
- **THEN** the sensor SHALL emit one Slack message to
  `#upstream-breaking-changes` per detected breaking change
- **AND** the message SHALL include the
  `(symbol, old_signature, new_signature, migration_steps,
  changelog_url)` payload
- **AND** the sensor SHALL NOT re-alert on the same
  `(symbol, version)` tuple within a 24-hour window

#### Scenario: Per-package Markdown report

- **GIVEN** the `upstream_api_surface_publish` Dagster asset
  has run for all 4 packages
- **WHEN** the caller inspects
  `cianfhoghlaim/docs/upstream/api-changes/{package}.md`
- **THEN** the file SHALL contain a Markdown table with
  columns `(symbol, severity, old_signature, new_signature,
  changelog_url, migration_steps)` for the 30 most recent
  `ApiChangeNode` entries per package
- **AND** the file SHALL be regenerated on every asset run
  (idempotent overwrite, no append)

### Requirement: Canonical Package Enum

The system SHALL expose a canonical `Package` enum at
`cianfhoghlaim.core.types.Package` with the values `MOTHERDUCK`,
`DLTHUB`, `LANCEDB`, `COCOINDEX`, re-exported from
`codeolas.core.types` for the publishable wheel. The enum SHALL
be the single source of truth for the four upstream packages
whose blog posts / docs / changelogs the platform's upstream
monitoring pipeline watches.

#### Scenario: Single import surface

- **GIVEN** a CocoIndex v1 App or a Dagster asset that needs to
  tag an artefact by upstream package
- **WHEN** the module imports `Package`
- **THEN** the import SHALL resolve to the canonical enum at
  `cianfhoghlaim.core.types.Package`
- **AND** no module SHALL redeclare a local `Package` enum

#### Scenario: BAML client enforcement

- **GIVEN** the BAML function
  `ExtractBlogPostMetadata(content, url) -> BlogPostMetadata` in
  `baml_src/upstream_monitoring.baml`
- **WHEN** the function returns
- **THEN** the `package` field SHALL be typed as
  `cianfhoghlaim.core.types.Package` (not a string)
- **AND** the BAML client SHALL reject any value not in the
  enum at validation time

### Requirement: Canonical BlogPostType Enum

The system SHALL expose a canonical `BlogPostType` enum at
`cianfhoghlaim.core.types.BlogPostType` with the values
`ANNOUNCEMENT`, `TUTORIAL`, `BENCHMARK`, `CASE_STUDY`,
`RELEASE_NOTES`, `API_DOC`, re-exported from
`codeolas.core.types` for the publishable wheel. The enum SHALL
be the single source of truth for the classification of upstream
blog posts by the `ExtractBlogPostMetadata` BAML function.

#### Scenario: BAML client enforcement

- **GIVEN** the BAML function
  `ExtractBlogPostMetadata(content, url) -> BlogPostMetadata` in
  `baml_src/upstream_monitoring.baml`
- **WHEN** the function returns
- **THEN** the `blog_post_type` field SHALL be typed as
  `cianfhoghlaim.core.types.BlogPostType` (not a string)
- **AND** the BAML client SHALL reject any value not in the
  enum at validation time
- **AND** the Firecrawl monitor `--goal` strings for each of
  the 4 packages SHALL mention at least 3 of the 6 enum values
  so the LLM judge can classify accurately