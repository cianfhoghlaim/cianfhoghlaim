# `croilar-self-hosted-portal` capability spec — NEW

The internal platform dashboard for the Croílár portfolio — stacks, data pipelines, monitoring, MCP gateway, and image registry — gated behind multi-tenant auth.

## ADDED Requirements

### Requirement: Stack Health Dashboard
The system SHALL display live health status for all croilar Docker Compose stacks via the Komodo API.

#### Scenario: All stacks show health
- **WHEN** an authenticated user opens `/portal/stacks`
- **THEN** a grid of stack cards SHALL render with status (running/stopped/error), container count, and uptime
- **AND** each card SHALL be live-refreshed every 30 seconds

#### Scenario: Stack down detected
- **WHEN** a stack transitions to a stopped or error state
- **THEN** the card SHALL show a red status indicator and a "last seen" timestamp

### Requirement: Data Pipeline Status
The system SHALL display live Dagster pipeline status via the Dagster GraphQL API.

#### Scenario: Asset grid renders
- **WHEN** an authenticated user opens `/portal/data/pipelines`
- **THEN** a grid SHALL render all 15+ assets grouped by persona
- **AND** each asset SHALL show last materialization time, status, and a link to the Dagster UI

#### Scenario: Per-persona asset filter
- **WHEN** the user selects the "aleyum" persona filter
- **THEN** only aleyum-group assets SHALL be displayed

### Requirement: Monitoring Dashboard
The system SHALL embed live Prometheus, Grafana, and Loki views for infrastructure observability.

#### Scenario: Grafana dashboard embeds
- **WHEN** an authenticated user opens `/portal/monitoring`
- **THEN** the page SHALL render an iframe pointing at the Grafana instance with a croilar-specific dashboard
- **AND** Loki log viewer SHALL be accessible in a sibling tab

### Requirement: MCP Gateway Status
The system SHALL display the status of all 13 MCP servers in the project.

#### Scenario: Server status grid
- **WHEN** an authenticated user opens `/portal/mcp-gateway`
- **THEN** a grid SHALL render each MCP server with status (online/offline), last call latency, and error count
- **AND** each server SHALL be clickable to view request history

### Requirement: Image Registry
The system SHALL display ghcr.io container image tags and multi-arch build status.

#### Scenario: Tag list renders
- **WHEN** an authenticated user opens `/portal/image-registry`
- **THEN** the page SHALL list all croilar container images with latest tag, last build date, and multi-arch manifest status

### Requirement: Auth-Gated Access
The system SHALL require BetterAuth OIDC authentication for all portal routes.

#### Scenario: Unauthenticated user redirected
- **WHEN** an unauthenticated visitor navigates to any `/portal/*` route
- **THEN** they SHALL be redirected to the BetterAuth login page

#### Scenario: Authenticated author sees admin controls
- **WHEN** a member of the `croilar-admin` org signs in
- **THEN** all portal modules SHALL be accessible
- **AND** write-capable controls (refresh, restart, rebuild) SHALL be enabled

#### Scenario: Invited collaborator sees read-only view
- **WHEN** a member of the `croilar-collab` org signs in
- **THEN** portal modules SHALL be read-only
- **AND** write-capable controls SHALL be disabled or hidden
