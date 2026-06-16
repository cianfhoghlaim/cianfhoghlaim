# Spec Delta: `croilar-devtools-hub` (NEW CAPABILITY)

## ADDED Requirements

### Requirement: Web-Stack Inventory

The system SHALL provide a single, queryable inventory of the monorepo's web stack.

#### Scenario: All 4 projects surface in the inventory

- **WHEN** the analyzer cron runs
- **THEN** the 9 Convex tables SHALL have at least one row per project that has a web app
- **AND** `meaisínfhoghlaim` SHALL be skipped with a warning (no web app yet)

#### Scenario: Routes are discoverable

- **WHEN** a developer asks the `croilar-mcp-devtools` MCP server `list_tanstack_routes`
- **THEN** the server SHALL return all routes from all 4 projects
- **AND** each route SHALL have a deep link to the source file

#### Scenario: Convex functions are discoverable

- **WHEN** a developer asks the MCP server `list_convex_functions`
- **THEN** the server SHALL return all functions from all 4 projects
- **AND** each function SHALL have a deep link to the source file

#### Scenario: Test results are queryable

- **WHEN** a developer asks the MCP server `get_test_results`
- **THEN** the server SHALL return the latest test run per project
- **AND** if no test runs have been ingested, the server SHALL return a clear "no data" response

### Requirement: Glance Auto-Generation

The system SHALL keep the Glance dashboard in sync with the Convex registry.

#### Scenario: Regenerator emits 5 pages

- **WHEN** `bun run croilar/scripts/regenerate-glance-config.ts` runs
- **THEN** the output SHALL contain 5 pages: `Home`, `tuatha`, `oideachais`, `croilar`, `meaisínfhoghlaim`
- **AND** each project page SHALL have at least: a search box, a routes widget, a Dagster assets widget, a test results widget

#### Scenario: Regenerator refuses to clobber manual edits

- **WHEN** the regenerator detects a manually-edited `glance.yml` (no `CROILAR_GENERATED_AT` header comment)
- **THEN** it SHALL refuse to overwrite unless `CROILAR_GLANCE_REGEN_FORCE=true`

#### Scenario: Komodo procedure triggers the regenerator

- **WHEN** the `croilar-glance-regenerate` Komodo procedure runs
- **THEN** it SHALL execute the regenerator and restart the Glance container
- **AND** the new `glance.yml` SHALL be committed to the repo

### Requirement: MCP Server

The system SHALL expose a `croilar-mcp-devtools` MCP server that Claude and other agents can use.

#### Scenario: MCP server tools

- **WHEN** the MCP server starts
- **THEN** it SHALL expose the following tools:
  - `list_convex_functions({project?})` — returns the Convex function inventory
  - `list_tanstack_routes({project?})` — returns the TanStack route inventory
  - `get_test_results({project?})` — returns the latest test runs
  - `get_glance_config()` — returns the current Glance YAML
  - `tail_logs({limit, project?})` — returns the most recent Convex function calls
  - `get_summary()` — returns a single composite summary of all 9 tables
  - `regenerate_glance()` — runs the Glance regenerator

#### Scenario: MCP server is registered in opencode.json

- **WHEN** `opencode.json` is loaded
- **THEN** it SHALL contain a `mcp.croilar-devtools` entry
- **AND** the entry SHALL be `enabled: true`

### Requirement: Auth Model

The new `/web` and `/notebooks` portal pages SHALL be gated behind `croilar-admin` org owner|admin role.

#### Scenario: AccessDenied component

- **WHEN** a user without the required role opens `/web` or `/notebooks`
- **THEN** the page SHALL render an `AccessDenied` component
- **AND** the underlying Convex queries SHALL also reject unauthorized callers

#### Scenario: Role query

- **WHEN** a user opens any page that requires a role check
- **THEN** the page SHALL call `useQuery(api.helpers.currentRole)` to get the current user's role
- **AND** the page SHALL render the content only if the role matches

### Requirement: Marimo Notebooks (new)

The system SHALL ship 3 new marimo notebooks that visualize the new observability tables.

#### Scenario: web_route_health

- **WHEN** a user opens `notebooks/streams/teaching/web_route_health.py`
- **THEN** the notebook SHALL connect to Convex and pull `tanstackRoutes` + `testRuns`
- **AND** it SHALL render a pass/fail grid per route per project

#### Scenario: convex_function_latency

- **WHEN** a user opens `notebooks/streams/teaching/convex_function_latency.py`
- **THEN** the notebook SHALL connect to Convex and pull `convexFunctionCalls`
- **AND** it SHALL render p50 and p95 latency per function

#### Scenario: baml_extraction_quality

- **WHEN** a user opens `notebooks/streams/teaching/baml_extraction_quality.py`
- **THEN** the notebook SHALL connect to Langfuse (via the LLM gateway) and pull BAML extraction traces
- **AND** it SHALL render confidence histograms per schema

### Requirement: Infisical Secret

The system SHALL require the `CROILAR_CONVEX_DEPLOY_KEY` environment variable to be set when running the analyzer.

#### Scenario: Missing deploy key

- **WHEN** the analyzer is run without `CROILAR_CONVEX_DEPLOY_KEY`
- **THEN** it SHALL exit non-zero with a clear error message
- **AND** the error message SHALL direct the user to the Infisical `dev-baile/croilar/convex/deploy_key` path
