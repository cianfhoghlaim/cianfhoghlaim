# `croilar-self-hosted-portal` capability spec

## Purpose

`croilar-self-hosted-portal` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.


The internal platform dashboard for the Croílár portfolio — stacks, data pipelines, monitoring, MCP gateway, and image registry — gated behind multi-tenant auth.

## Requirements

### Requirement: Stack Health Dashboard
The system SHALL display live health status for all croilar Docker Compose stacks via the Komodo API.

#### Scenario: All stacks show health
- **WHEN** an authenticated user opens `/portal/stacks`
- **THEN** a grid of stack cards SHALL render with status (running/stopped/error), container count, and uptime

### Requirement: Data Pipeline Status
The system SHALL display live Dagster pipeline status via the Dagster GraphQL API.

#### Scenario: Asset grid renders
- **WHEN** an authenticated user opens `/portal/data/pipelines`
- **THEN** a grid SHALL render all 15+ assets grouped by persona

### Requirement: Monitoring Dashboard
The system SHALL embed live Prometheus, Grafana, and Loki views for infrastructure observability.

#### Scenario: Grafana dashboard embeds
- **WHEN** an authenticated user opens `/portal/monitoring`
- **THEN** the page SHALL render an iframe pointing at the Grafana instance with a croilar-specific dashboard

### Requirement: MCP Gateway Status
The system SHALL display the status of all 13 MCP servers in the project.

#### Scenario: Server status grid
- **WHEN** an authenticated user opens `/portal/mcp-gateway`
- **THEN** a grid SHALL render each MCP server with status (online/offline), last call latency, and error count

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
