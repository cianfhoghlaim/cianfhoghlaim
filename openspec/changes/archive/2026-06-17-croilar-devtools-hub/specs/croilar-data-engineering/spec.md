# Spec Delta: `croilar-data-engineering`

## ADDED Requirements

### Requirement: Convex Web-Stack Observability Tables

The system SHALL maintain 9 new Convex tables that inventory the monorepo's web stack.

#### Scenario: tanstackRoutes is populated by the analyzer

- **WHEN** `sruth/croilar/scripts/analyze-web-stack.ts` runs
- **THEN** each TanStack route file under `sruth/tuatha/ui/src/routes/`, `sruth/oideachais/apps/web/src/routes/`, `sruth/oideachais/dashboard/src/routes/`, `sruth/croilar/apps/{web,portal}/src/routes/` SHALL become a row in `tanstackRoutes`
- **AND** `project` SHALL be one of `tuatha | oideachais | croilar | meaisinfhoghlaim`
- **AND** `isServer`, `hasLoader`, `hasAuth` SHALL reflect the file's actual content (regex match)

#### Scenario: convexFunctions is populated by the analyzer

- **WHEN** the analyzer walks every `convex/*.ts` in the 4 projects
- **THEN** each exported `query | mutation | action | internalQuery | internalMutation | internalAction` SHALL become a row in `convexFunctions`
- **AND** `kind` SHALL be the actual kind (e.g. `internalAction` for `internalAction({...}, ...)`)
- **AND** `lines` SHALL be the line count of the function body

#### Scenario: cloudflareResources is populated by the analyzer

- **WHEN** the analyzer walks every `wrangler.toml` in the 4 projects
- **THEN** each `[site]` / `[[r2_buckets]]` / `[[kv_namespaces]]` / `[[d1_databases]]` / `[[durable_objects.bindings]]` block SHALL become a row in `cloudflareResources`
- **AND** `kind` SHALL be one of `worker | pages | r2 | kv | d1 | durable_object`

#### Scenario: bamlSchemas is populated by the analyzer

- **WHEN** the analyzer walks every `baml_src/*.baml` in the 4 projects
- **THEN** each `.baml` file SHALL become a row in `bamlSchemas`
- **AND** `classCount`, `functionCount`, `enumCount` SHALL match the actual counts

#### Scenario: testRuns table is ready (ingest deferred)

- **WHEN** the table is created
- **THEN** the `ingest` mutation SHALL accept `{project, suite, branch, commit, passed, failed, skipped, durationMs, startedAt, finishedAt, failureDetails?}` and write a row
- **AND** the table SHALL be empty until the CI integration (deferred) starts calling it
- **AND** `getLatest` SHALL return the most recent row per `project`

#### Scenario: convexFunctionCalls is populated by the action middleware

- **WHEN** any `loggedAction` wrapper in `sruth/croilar/convex/_middleware.ts` runs
- **THEN** a row SHALL be inserted with `{function, kind: "action", project, args, durationMs, ok, error?, calledAt}`
- **AND** `args` SHALL be JSON-stringified and truncated to 1024 bytes
- **AND** `ok = false` AND `error` populated on exception
- **AND** a fresh `tail` query SHALL return the most recent N rows

#### Scenario: convexMetrics table is populated by a periodic scrape

- **WHEN** `refreshConvexMetrics` cron fires every 5 minutes
- **THEN** p50, p95, qps, and error_rate over the last 5 minutes SHALL be computed from `convexFunctionCalls`
- **AND** written as `scope = "global"` rows

#### Scenario: marimoNotebooks is populated by the analyzer

- **WHEN** the analyzer walks every `notebooks/**/*.py` and `marimo/**/*.py`
- **THEN** each notebook SHALL become a row in `marimoNotebooks`
- **AND** `slug` SHALL be the path relative to the notebooks root with `.py` stripped
- **AND** `cellCount` SHALL match the count of `marimo.App(...).cell` calls

#### Scenario: glanceConfig is the version history

- **WHEN** `glance_config.regenerate` action runs
- **THEN** a new row SHALL be inserted with `{version: prev + 1, yaml, pageCount, widgetCount, generatedAt, generatedBy}`
- **AND** `getCurrent` SHALL return the row with the highest `version`

### Requirement: Action-Call Middleware

The system SHALL provide a `loggedAction` helper in `sruth/croilar/convex/_middleware.ts` that wraps every Convex action invocation and records to `convexFunctionCalls`.

#### Scenario: Middleware records every call

- **WHEN** a `loggedAction(fn, {function, project})` wrapper is invoked
- **THEN** it SHALL call `fn` and re-throw on exception
- **AND** it SHALL insert a `convexFunctionCalls` row regardless of success/failure (in `finally`)
- **AND** the row SHALL include `durationMs = Date.now() - t0`

#### Scenario: Middleware is opt-in

- **WHEN** a Convex action does NOT use the `loggedAction` wrapper
- **THEN** it SHALL still work correctly, but no `convexFunctionCalls` row SHALL be created for it
- **AND** the existing `pipelines.refreshAll`, `stacks.refreshAll`, `mcp.refreshAll`, `registry.refreshAll` SHALL be migrated to use `loggedAction` in this change

### Requirement: Dagster Schedules

The system SHALL schedule the analyzer and metric refresh on appropriate cadences.

#### Scenario: Six new cron entries (added)

- **WHEN** the analyzer cron schedule is added to `sruth/croilar/convex/crons.ts`
- **THEN** the following 6 new entries SHALL be present:
  - `syncTanstackRoutes` every 6h
  - `syncConvexFunctions` every 12h
  - `syncCloudflareResources` every 6h
  - `syncBamlSchemas` daily
  - `syncMarimoNotebooks` every 12h
  - `refreshConvexMetrics` every 5m
- **AND** each SHALL be idempotent (re-running the same `refreshAll` action on unchanged files produces the same data)

#### Scenario: Existing cron schedule (preserved)

- **WHEN** the existing 4 cron entries (syncStacks, syncPipelines, syncMcpServers, syncContainerImages) run
- **THEN** they SHALL continue to function unchanged

## ADDED Requirements

### Requirement: Analyzer Bun Script

The system SHALL ship `sruth/croilar/scripts/analyze-web-stack.ts` as a Bun script that walks the monorepo and posts aggregates to Convex.

#### Scenario: Walk succeeds for the 3 present projects

- **WHEN** `bun run sruth/croilar/scripts/analyze-web-stack.ts` is executed from the repo root
- **THEN** the analyzer SHALL walk `sruth/tuatha/`, `sruth/oideachais/`, `sruth/croilar/`
- **AND** it SHALL skip `meaisínfhoghlaim/` (no web app yet) with a warning
- **AND** it SHALL POST the resulting 5 tables (tanstackRoutes, convexFunctions, cloudflareResources, bamlSchemas, marimoNotebooks) to the Convex HTTP endpoint
- **AND** authentication SHALL use the `CROILAR_CONVEX_DEPLOY_KEY` from `.env` (loaded from Infisical)

#### Scenario: Walk is idempotent

- **WHEN** the analyzer is run twice in a row
- **THEN** the second run SHALL produce the same set of rows (modulo `lastCommit` / `lastCompiled` / `lastExported` timestamps)
- **AND** no duplicate rows SHALL appear

#### Scenario: Project-scope flag

- **WHEN** the analyzer is invoked with `--project tuatha` (or `oideachais` | `croilar` | `meaisinfhoghlaim`)
- **THEN** it SHALL walk only that project
- **AND** it SHALL exit 0 with a single-line summary

## MODIFIED Requirements

### Requirement: Dagster Asset Catalog

The system SHALL continue to emit 9+ stream-driven Dagster assets (music, teaching, cv, research).

#### Scenario: No regression

- **WHEN** `mise turbo build dagster` runs
- **THEN** the asset catalog SHALL still include `music__spotify`, `music__soundcloud`, `music__labels`, `music__artwork`, `teaching__github`, `teaching__linkedin`, `teaching__researchgate`, `cv__cv`, `cv__filesystem`

### Requirement: BAML Extraction Schemas

The system SHALL continue to compile the 9 BAML schemas.

#### Scenario: No regression

- **WHEN** `bun run baml-cli compile` runs
- **THEN** the compiler SHALL still emit TypeScript + Python client code from `sruth/croilar/baml/{artwork_analysis, cv_extraction, identity_verification, linkedin_profile_extraction, researchgate_extraction, style_transfer, teaching_extraction, generators, clients}.baml`

### Requirement: DuckLake Cross-DB Read

The system SHALL continue to read from the existing DuckLake catalog.

#### Scenario: No regression

- **WHEN** `oideachais_assets_embedded` or `meaisinfhoghlaim_assets_embedded` materializes
- **THEN** Dagster SHALL continue to query the DuckLake catalog and embed the result
