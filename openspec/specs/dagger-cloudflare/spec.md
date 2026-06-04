# Cloudflare Deployment Capability

## Overview

Deployment automation for Cloudflare Pages and Workers with build integration and live log streaming.

| Feature | Description |
|---------|-------------|
| Pages Deployment | Static site deployment via Wrangler |
| Worker Deployment | Edge function deployment |
| Log Streaming | Real-time worker logs |
| Project Management | List and manage deployments |

## Requirements

### Requirement: Pages Deployment

The system SHALL deploy static sites to Cloudflare Pages.

#### Scenario: Deploy Pages
- **GIVEN** source directory and project name
- **WHEN** `deployPages()` is executed
- **THEN** site is deployed to Cloudflare Pages

#### Scenario: Deploy Docs
- **GIVEN** docs source directory
- **WHEN** `deployDocs()` is executed
- **THEN** documentation is built and deployed to Pages

### Requirement: Worker Deployment

The system SHALL deploy edge functions to Cloudflare Workers.

#### Scenario: Deploy Worker
- **GIVEN** source directory and worker name
- **WHEN** `deployWorker()` is executed
- **THEN** worker is deployed to Cloudflare

### Requirement: Project Management

The system SHALL list and manage Cloudflare projects.

#### Scenario: List Projects
- **WHEN** `listProjects()` is executed
- **THEN** all Pages projects are returned

#### Scenario: List Workers
- **WHEN** `listWorkers()` is executed
- **THEN** all deployed workers are returned

### Requirement: Log Streaming

The system SHALL stream worker logs for debugging.

#### Scenario: Tail Worker
- **GIVEN** worker name
- **WHEN** `tailWorker()` is executed
- **THEN** live logs are streamed to output

## API Reference

| Function | Parameters | Returns |
|----------|------------|---------|
| `deployPages()` | source, projectName | string |
| `deployDocs()` | source | string |
| `deployWorker()` | source, workerName | string |
| `listProjects()` | - | string |
| `listWorkers()` | - | string |
| `tailWorker()` | workerName | string |

## Implementation References

| Component | Path |
|-----------|------|
| Main Module | `infrastructure/dagger/src/web/__init__.py (calls bonny.cloudflare_deploy_pages) or infrastructure/dagger/ts_submodules/bonneagar/src/cloudflare.ts` |

## Related Specs

- [dagger-ci](../dagger-ci/spec.md) - CI orchestration
