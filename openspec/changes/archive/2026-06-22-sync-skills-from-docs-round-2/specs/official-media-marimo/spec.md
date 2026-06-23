# Spec Delta: official-media-marimo

## ADDED Requirements

### Requirement: Marimo on Cloudflare deployment (KCG)

The system SHALL use the marimo-on-Cloudflare Workers + Container
pattern as the canonical deployment for production marimo
dashboards in the official-media surface.

#### Scenario: Worker + Container deploys

- **GIVEN** the canonical Dockerfile + wrangler.jsonc + Durable
  Object pattern from `.agents/skills/marimo/references/deployment-cloudflare.md`
- **WHEN** the official-media mission-control marimo is deployed
- **THEN** the marimo UI SHALL be served from a `*.workers.dev`
  URL
- **AND** the Container SHALL be reachable at TCP 8080 for
  marimo's internal RPC

### Requirement: Streamlit-compatible layout in marimo

The system SHALL support a multi-column `mo.ui.tabs({...})` layout
in the official-media mission control so the page renders
correctly for both narrow and wide viewports.

#### Scenario: Tab layout renders

- **GIVEN** a marimo cell with
  `mo.ui.tabs({"Candidates": ..., "Skimmer": ..., "HMGCC": ...})`
- **WHEN** the user opens the dashboard on a 1024×768 viewport
- **THEN** the tabs SHALL be visible as a horizontal tab bar
- **AND** selecting a tab SHALL switch the content area without
  a full page reload

## REMOVED Requirements

(None.)
