# Spec Deltas for `consolidate-external-libs-into-tuatha`

This change modifies the existing `tuatha-deployment` capability and adds three
new capabilities: `codeolas`, `crypteolas`, and `crypteolas-demo`.

---

## `specs/tuatha-deployment/spec.md`

## MODIFIED Requirements

### Requirement: Hatch wheel packages list
The `tuatha/pyproject.toml` `[tool.hatch.build.targets.wheel] packages` SHALL include
every sub-package with an `__init__.py` plus every published library. The list
SHALL be updated whenever new sub-packages are added.

#### Scenario: After consolidation
- **WHEN** `tuatha/pyproject.toml` is read
- **THEN** `packages` contains: `dlt_sources`, `dagster_assets`, `cocoindex_flows`,
  `knowledge_graph`, `agents`, `api`, `storage`, `asset_generation`, `dlt_utils`,
  `fibo_generation`, `tests`, `demo`, `codeolas`, `crypteolas`.

### Requirement: Dagster code-locations
The `tuatha/dg.toml` SHALL register every Dagster code-location hosted in
the `tuath` workspace member. The Dagster UI SHALL load all registered
code-locations from a single process.

#### Scenario: Three code-locations registered
- **WHEN** `dagster dev -m dagster_assets.definitions` is started from `tuatha/`
- **THEN** the UI shows three code-locations: `tuath`, `crypteolas`, `crypteolas_demo`.

### Requirement: Bun workspaces
The root `package.json` `workspaces` field SHALL list every TypeScript workspace
in the monorepo. The crypteolas demo app's TanStack Start skeleton SHALL be
registered so `bun install` resolves it.

#### Scenario: bun install succeeds
- **WHEN** `bun install` is run from the repo root
- **THEN** four workspaces resolve: `oideachais-web`, `oideachais-mcp-filesystem`,
  `tuatha-ui`, `tuatha-apps-crypteolas-demo`.

## ADDED Requirements

### Requirement: BAML clients.baml uniqueness
Every `baml_src/` directory SHALL have a uniquely-named `clients.baml` (or
equivalent) generator file. Two packages SHALL NOT both export a `clients.baml`
that generates to the same `baml_client/` directory.

#### Scenario: tuatha baml_src and crypteolas baml_src
- **WHEN** both `tuatha/baml_src/clients.baml` and `tuatha/crypteolas/baml_src/clients.baml`
  are present
- **THEN** `tuatha/baml_src/clients.baml` SHALL be renamed to `tuatha_clients.baml`
  to avoid the collision, and one combined `tuatha/baml_client/` SHALL be
  generated.

### Requirement: Followup issue filed
A follow-up GitHub/Forgejo issue SHALL be filed for the pre-existing broken
`sru th.shared.*` imports in `tuatha/dlt_sources/geospatial/` and
`tuatha/storage/serial_executor.py`. This change SHALL NOT fix those imports.

#### Scenario: Issue exists
- **WHEN** the followup is searched for by title
- **THEN** an issue titled "Followup: simplify sruth.shared.* abstraction in
  tuatha/dlt_sources/geospatial/ and tuatha/storage/" exists with the full
  plan inline.
