# Infrastructure Stacks Capability

## Overview

65+ storage, utility, engineering, machine learning, and infrastructure Docker Compose stacks managed via Komodo for the Cianfhoghlaim platform. Organized into 5 categories with standardized Pangolin routing, Locket secret injection, and Infisical secret management.

| Feature | Description |
|---------|-------------|
| Storage Stacks | Vector, graph, relational databases, lakehouse, AI memory |
| Engineering Stacks | Dev tooling, API gateways, MCP servers |
| ML Stacks | Training infrastructure, LLM serving |
| Infrastructure Stacks | Pangolin control plane, Komodo, Pocket ID |
| Tools Stacks | Productivity, media, development utilities |

## Requirements

### Requirement: Stack Standardization

The system SHALL enforce that every web-facing stack includes four standard files.

#### Scenario: Complete Stack
- **GIVEN** a stack directory under `infrastructure/stacks/<category>/<name>/`
- **WHEN** deploying via Komodo
- **THEN** the stack SHALL have `compose.yaml`, `pangolin.yaml`, `sidecar.yaml`, and `secrets.env`

#### Scenario: Backend-Only Stack
- **GIVEN** a stack that requires no web routing
- **WHEN** deploying via Komodo
- **THEN** `pangolin.yaml` MAY be omitted

### Requirement: Storage Stacks

The system SHALL deploy database and data infrastructure for the lakehouse architecture.

#### Scenario: Lakehouse Stack
- **GIVEN** lakehouse stack with Garage S3, Postgres, Lakekeeper, and Lance Namespace sidecar
- **WHEN** stack deploys via Komodo
- **THEN** S3 API (3900), Postgres (5433), Iceberg REST catalog (8181), and Lance sidecar (8182) are accessible

#### Scenario: AI Memory Stacks
- **GIVEN** Cognee and Graphiti stacks
- **WHEN** stacks deploy
- **THEN** knowledge graph and temporal memory services are available

#### Scenario: Vector Database Stacks
- **GIVEN** LanceDB, Qdrant, and FalkorDB stacks
- **WHEN** stacks deploy
- **THEN** vector search infrastructure is accessible

### Requirement: Engineering Stacks

The system SHALL deploy developer tooling and API infrastructure.

#### Scenario: LiteLLM Gateway
- **GIVEN** LiteLLM stack with Postgres and Prometheus
- **WHEN** stack deploys
- **THEN** LLM proxy is accessible on port 4000

#### Scenario: Crawl4AI
- **GIVEN** Crawl4AI stack
- **WHEN** stack deploys
- **THEN** web crawling API is accessible for curriculum ingestion

### Requirement: Infrastructure Stacks

The system SHALL deploy the Pangolin Convergence control plane.

#### Scenario: Pangolin Stack
- **GIVEN** pangolin stack with Traefik, Gerbil, Pocket ID, TinyAuth, and CrowdSec
- **WHEN** stack deploys
- **THEN** WireGuard VPN (51820/udp), HTTPS (443), HTTP (80), and TinyAuth (8443) are available

#### Scenario: Komodo Stack
- **GIVEN** Komodo stack with MongoDB
- **WHEN** stack deploys
- **THEN** Komodo UI is accessible at port 9120

## Infrastructure (Control Plane) Stacks

| Stack | Image(s) | Key Ports |
|-------|----------|-----------|
| pangolin | `fosrl/pangolin:postgresql-latest`, `postgres:17`, `traefik:v3.4.0`, `pocket-id:latest`, `tinyauth:v4`, `crowdsec:latest` | 51820/udp, 443, 80, 8443 |
| komodo | `ghcr.io/moghtech/komodo-core:2`, `mongo:latest` | 9120 |
| pocket-id | `ghcr.io/pocket-id/pocket-id` | 1411 |
| dozzle | Container log viewer | Internal |
| DnsServer | Local DNS resolution | Internal |

## Storage Stacks

| Stack | Purpose | Key Ports |
|-------|---------|-----------|
| garage | CRDT S3-compatible object storage | 3900-3904 |
| lakehouse | Lakekeeper Iceberg catalog + Lance Namespace + Garage + Postgres | 3900-3904, 5433, 8181-8182 |
| lakehouse-oci | OCI variant of lakehouse | 5433, 8181-8182 |
| dagster | Pipeline orchestration (custom image) | 3335 |
| langfuse | LLM observability (Postgres + ClickHouse + Redis + MinIO) | 3000 |
| mlflow | ML experiment tracking (Postgres + MinIO) | 5000 |
| forgejo | Git forge (Postgres) | 3000, 2222 |
| forgejo-runner | CI/CD runner | — |
| memgraph | Graph database (MAGE + Lab UI) | 7687, 7444, 3000 |
| falkordb | Vector+graph hybrid | 6379, 3000 |
| qdrant | Vector database | 6333, 6334 |
| lancedb | LanceDB data viewer | 8080 |
| agent-os | 4 custom services: oideachais, crypteolas, browser, aleyum | 7771-7774 |
| browser | Browser automation (Skyvern + Postgres + Garage) | 3001, 3100, 8001, 11235 |
| confluent | Kafka UI (kafka+zookeeper commented out) | 9080 |
| graphiti | Temporal knowledge graph | Internal |
| cognee | AI memory system | Internal |
| convex | Real-time backend | Cloud |
| lakefs | Data versioning | Internal |
| lakekeeper | Iceberg catalog (standalone) | Internal |
| mathesar | Database UI | Internal |
| nimtable | Analytics table viewer | Internal |
| olake-ui | CDC replication UI | Internal |
| beszel | System monitoring | Internal |
| kafka | Standalone Kafka | Internal |
| r2 | Cloudflare R2 bridge | Internal |

### Documentation-Only Stacks (secrets configured, no local compose)

| Stack | Purpose |
|-------|---------|
| motherduck | MotherDuck cloud analytics |
| planetscale | MySQL-compatible cloud DB |
| pydantic-gateway | Pydantic AI gateway |
| logfire | Pydantic observability |

## Engineering Stacks

| Stack | Purpose | Key Ports |
|-------|---------|-----------|
| litellm | LLM proxy gateway (Postgres + Prometheus) | 4000, 5432, 9090 |
| crawl4ai | Web crawling API | 11235 |
| coder | Cloud development environment | Internal |
| windmill | Workflow automation | Internal |
| MCPJungle | MCP server collection | Internal |
| DevDocs | API documentation aggregator | Internal |
| networking-toolbox | Network diagnostic tools | Internal |

## Machine Learning Stacks

| Stack | Purpose |
|-------|---------|
| cognee | AI memory (ML variant) |
| graphiti | Temporal graphs (ML variant) |
| langfuse | LLM observability (ML variant) |
| lmnr | Language model observability |
| olake | CDC replication |

## Tools Stacks (17)

Productivity: `actual`, `blinko`, `linkwarden`, `presenton`, `stirling-pdf`
Media: `audiobookshelf`, `kapowarr`, `pinchflat`, `rybbit`
Development: `changedetection`, `enclosed`, `pastemax`, `perplexica`, `skyvern`, `LetterFeed`, `romm`, `mailcow-dockerized`

## Stack Configuration Standard

| File | Purpose | Required |
|------|---------|----------|
| `compose.yaml` | Docker service definitions | Yes |
| `pangolin.yaml` | Traefik routing + TinyAuth config | For web-facing |
| `sidecar.yaml` | Locket container for Infisical injection | Yes |
| `secrets.env` | Infisical URI references for stack | Yes |

## Implementation References

| Component | Path |
|-----------|------|
| All Stacks | `infrastructure/stacks/` |
| Gold Standard | `infrastructure/stacks/GOLD_STANDARD.md` |
| Stack README | `infrastructure/stacks/README.md` |

## Related Specs

- [infrastructure](../infrastructure/spec.md) — Pangolin convergence, secrets, Komodo GitOps
- [data-pipeline](../data-pipeline/spec.md) — Pipeline orchestration
