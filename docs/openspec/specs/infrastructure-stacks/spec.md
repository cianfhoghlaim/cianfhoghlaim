# Infrastructure Stacks Capability

## Overview

25+ storage and utility Docker Compose stacks managed via Komodo for the Cianfhoghlaim platform.

| Feature | Description |
|---------|-------------|
| Database Stacks | Vector, graph, relational databases |
| Observability | Monitoring and logging |
| AI Memory | Knowledge graph and cognition |
| Utilities | Development tools and services |

## Requirements

### Requirement: Database Stacks

The system SHALL deploy database infrastructure for data pipelines.

#### Scenario: Deploy LanceDB
- **GIVEN** LanceDB stack configuration
- **WHEN** stack deploys via Komodo
- **THEN** vector database is accessible

#### Scenario: Deploy Memgraph
- **GIVEN** Memgraph stack configuration
- **WHEN** stack deploys
- **THEN** graph database is accessible at `memgraph.cianfhoghlaim.ie`

#### Scenario: Deploy FalkorDB
- **GIVEN** FalkorDB stack configuration
- **WHEN** stack deploys
- **THEN** vector+graph hybrid is accessible

### Requirement: Observability Stacks

The system SHALL deploy monitoring and observability infrastructure.

#### Scenario: Deploy MLflow
- **GIVEN** MLflow stack configuration
- **WHEN** stack deploys
- **THEN** experiment tracking is accessible

#### Scenario: Deploy Langfuse
- **GIVEN** Langfuse stack configuration
- **WHEN** stack deploys
- **THEN** LLM observability is accessible

### Requirement: AI Memory Stacks

The system SHALL deploy AI memory and cognition infrastructure.

#### Scenario: Deploy Cognee
- **GIVEN** Cognee stack configuration
- **WHEN** stack deploys
- **THEN** AI memory system with MCP is accessible

#### Scenario: Deploy Graphiti
- **GIVEN** Graphiti stack configuration
- **WHEN** stack deploys
- **THEN** temporal reasoning is available

### Requirement: Utility Stacks

The system SHALL deploy development utilities.

#### Scenario: Deploy Forgejo
- **GIVEN** Forgejo stack configuration
- **WHEN** stack deploys
- **THEN** Git forge is accessible at `git.cianfhoghlaim.ie`

## Storage Stacks

| Stack | Purpose | Access |
|-------|---------|--------|
| autobase | PostgreSQL management | Internal |
| beszel | System monitoring | Internal |
| cognee | AI memory | `cognee-mcp.cianfhoghlaim.ie` |
| convex | Real-time backend | Cloud |
| dozzle | Container logs | Internal |
| dragonflydb | Redis alternative | Internal |
| falkordb | Vector+graph | `falkordb.cianfhoghlaim.ie` |
| forgejo | Git forge | `git.cianfhoghlaim.ie` |
| garage | S3 storage | Internal |
| graphiti | Temporal graphs | Internal |
| lakefs | Data versioning | Internal |
| lakehouse | Iceberg tables | Internal |
| lakekeeper | Iceberg catalog | Internal |
| lancedb | Vector database | Internal |
| langfuse | LLM observability | Internal |
| mathesar | Database UI | Internal |
| memgraph | Graph database | `memgraph.cianfhoghlaim.ie` |
| mlflow | ML tracking | Internal |
| qdrant | Vector database | `qdrant.cianfhoghlaim.ie` |

## Utility Stacks (`uirlisí/`)

| Category | Stacks |
|----------|--------|
| Productivity | actual, blinko, karakeep, kimai, linkwarden, mealie, paperless, presenton, stirling-pdf |
| Media | audiobookshelf, calibre, kapowarr, kavita, komga, moonlight, mylar3, pinchflat, sunshine |
| Gaming | drop, ludusavi, romm |
| Development | coder, chartdb, changedetection, enclosed, excalidraw |

## Komodo Stack Configurations

| Config File | Target |
|-------------|--------|
| `hetzner-databases.toml` | Database services |
| `hetzner-devtools.toml` | Development tools |
| `macbook-analytics.toml` | Local analytics |
| `macbook-media.toml` | Local media |
| `oci-control-plane.toml` | OCI control plane |
| `oci-devtools.toml` | OCI dev tools |
| `uirlisi-devtools.toml` | Utility dev tools |
| `uirlisi-scraping.toml` | Web scraping |

## Implementation References

| Component | Path |
|-----------|------|
| Storage Stacks | `bonneagar/storage/` |
| Utility Stacks | `bonneagar/uirlisí/` |
| Komodo Configs | `bonneagar/komodo/stacks/` |

## Related Specs

- [dagger-komodo](../dagger-komodo/spec.md) - Komodo SDK
- [dagger-gitops](../dagger-gitops/spec.md) - GitOps deployment
