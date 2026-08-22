# motherduck-connections Specification

## Purpose
The MotherDuck connection surface registers the 5th web application surface (the analytics consumer) across the Cianfhoghlaim monorepo. It defines 1 invariant: the canonical MotherDuck connection registration contract covers 4 connection methods (Postgres endpoint + native DuckDB API + JDBC + MCP), the cascading-registry integration pattern (per the 2026-08-15-cascading-registry-integration-v1 change), the read-only service account convention, the access-token rotation policy, the Duckling instance size requirements per dataset size, and the read scaling policy.

## Requirements
### Requirement: motherduck-connections MUST register the 5th web surface

The system SHALL update `openspec/specs/motherduck-connections/spec.md`
to include the 5th web surface (`web/apps/cianfhoghlaim-web/control-panel/`)
in the canonical MotherDuck / lakehouse / DLT / BIEP web surface
inventory. The 5 surfaces are listed in `agentic-frontend-frameworks/spec.md`.

#### Scenario: motherduck-connections surfaces the BIEP + control-panel surfaces

- **GIVEN** the 5 web surfaces (4 existing + 1 new control-panel)
- **WHEN** the operator reads `motherduck-connections/spec.md`
- **THEN** the surface inventory lists:
  1. `web/apps/cianfhoghlaim-web/` (the public web app)
  2. `web/apps/tuatha-ui/` (the Túatha educational MMO frontend)
  3. `web/apps/croilar-web/` (the Croílár multi-persona portfolio)
  4. `web/apps/croilar-portal/` (the Croílár portfolio dashboard)
  5. `web/apps/cianfhoghlaim-web/control-panel/` (NEW: deployment control panel)

#### Scenario: motherduck-connections connects to the schema introspection helpers

- **GIVEN** the 5 schema helpers in `notebooks/_shared/schema.py`
- **WHEN** the MotherDuck stack needs to introspect the BIEP lakehouse
- **THEN** `schema_introspect_full(connect_md())` returns the union of
  DuckDB + LanceDB + BAML columns
- **AND** the deployment control panel Tab 3 "Datasets" displays this surface

