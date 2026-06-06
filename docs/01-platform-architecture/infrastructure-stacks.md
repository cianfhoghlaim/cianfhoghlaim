---
title: "Infrastructure Stacks — Docker Compose Architecture & Patterns"
domain: architecture
status: stable
description: "Complete Docker Compose stack architecture covering 89 stacks, network topology, health checks, restart policies, storage architecture, and multi-network isolation patterns"
supersedes:
  - docs/bonneagar/DOCKER_COMPOSE_ARCHITECTURE.md
  - docs/bonneagar/DOCKER_COMPOSE_QUICKSTART.md
  - docs/bonneagar/DOCKER_COMPOSE_REFERENCE.md
  - docs/bonneagar/docker-compose-patterns.md
  - docs/bonneagar/compose.yaml
  - docs/bonneagar/docker-compose(1).yaml
  - docs/bonneagar/Docker Compose Setup for Data Tools.md
  - docs/bonneagar/Docker Provider.md
entities:
  - DockerComposeStacks
  - NetworkTopology
  - StorageArchitecture
related_skills:
  - .agents/skills/docker-compose/SKILL.md
  - .agents/skills/stack-ops/SKILL.md
  - .agents/skills/komodo/SKILL.md
ccc_query_hints:
  - "docker compose stack architecture"
  - "how are the 89 stacks organized"
  - "docker network topology"
  - "port allocation map"
  - "service dependency graph"
  - "health check patterns"
last_reviewed: 2026-06-06
---

# Infrastructure Stacks — Docker Compose Architecture

The Cianfhoghlaim platform runs **89 Docker Compose stacks** across multiple servers (arm1-oci, bunchloch MacBook M4, cax41-hetzner). Every stack follows consistent patterns for compose files, sidecar secrets, Pangolin routing, and Komodo deployment.

## Stack Categories

```
infrastructure/stacks/
├── storage/           # Database and object storage
│   ├── garage/        # S3-compatible object storage
│   ├── minio/         # MLFlow artifact storage
│   └── postgres/      # PostgreSQL instances
├── engineering/       # Developer tools
│   ├── n8n/           # Workflow automation
│   ├── forgejo/       # Git + PyPI + OCI registry
│   ├── semaphore/     # Ansible UI
│   └── netbox/        # DCIM/IPAM source of truth
├── ml/                # Machine learning
│   ├── dagster/       # Data orchestration
│   ├── litellm/       # LLM API gateway
│   ├── langfuse/      # LLM observability
│   ├── mlflow/        # Model tracking
│   └── cognee/        # Knowledge graph engine
├── tools/             # Team tools
│   ├── vikunja/       # Task management
│   └── cal-diy/       # Scheduling
├── browser/           # Browser automation
│   ├── crawl4ai/      # Web scraping
│   └── browserbase/   # CDP browser sessions
└── infrastructure/    # Self-managed infra
    ├── komodo/        # Core + Periphery
    ├── pangolin/      # Zero-trust gateway
    └── infisical/     # Secret vault
```

## Standard Stack Structure

Every stack directory follows this pattern:

```
infrastructure/stacks/<category>/<service>/
├── compose.yaml       # Service definition (Docker Compose)
├── sidecar.yaml       # Locket secret injection sidecar
├── pangolin.yaml      # Pangolin routing configuration
└── blueprint.yaml     # Access rules (roles, auth)
```

### compose.yaml — Service Definition

```yaml
services:
  dagster:
    image: ghcr.io/cianfhoghlaim/dagster:latest
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - dagster_data:/opt/dagster/dagster_home
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/graphql"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - shared-network
```

### sidecar.yaml — Locket Secrets

Every stack that needs secrets includes a Locket sidecar:

```yaml
services:
  locket:
    image: ghcr.io/bpbradley/locket:latest
    restart: unless-stopped
    command: ["--provider=infisical", "--mode=watch"]
    environment:
      - INFISICAL_CLIENT_ID=${INFISICAL_CLIENT_ID}
      - INFISICAL_CLIENT_SECRET=${INFISICAL_CLIENT_SECRET}
    volumes:
      - type: tmpfs
        target: /run/secrets/locket
    healthcheck:
      test: ["CMD", "locket", "healthcheck"]
      interval: 10s
      timeout: 5s
      retries: 3
```

### pangolin.yaml — Routing Rules

```yaml
# blueprint.yaml (Pangolin declarative config)
version: "1"
resources:
  - name: vikunja
    type: private
    upstream: http://vikunja:3456
    auth: pocket_id
    roles: [member]
  - name: grafana
    type: private
    upstream: http://grafana:3000
    auth: pocket_id
    roles: [admin]
```

## Network Topology

### Isolated Networks

```yaml
networks:
  forgejo_network:
    driver: bridge
    internal: true
  dagster_network:
    driver: bridge
    internal: true
  mlflow-network:
    driver: bridge
    internal: true
  pangolin:
    driver: bridge
```

### Shared Network (Inter-Stack Communication)

```yaml
networks:
  shared-network:
    driver: bridge
    name: cianfhoghlaim-shared
    external: true
```

### Multi-Network Isolation Pattern

```yaml
networks:
  frontend:
    driver: bridge      # Public-facing
  backend:
    driver: bridge
    internal: true       # Internal services only
  database:
    driver: bridge
    internal: true       # Most restricted

services:
  traefik:
    networks: [frontend]
  litellm:
    networks: [frontend, backend]
  dagster:
    networks: [backend, database]
  postgres:
    networks: [database]
```

## Port Allocation Map

| Range | Purpose | Examples |
|-------|---------|----------|
| 3000-3001 | Web UIs | Forgejo (3000), Dagster (3001), Langfuse (3000), Pangolin API (3001) |
| 4000-4999 | APIs | LiteLLM (4000) |
| 5000-5999 | Databases | MLFlow (5000), PostgreSQL (5432) |
| 6300-6379 | Search/Cache | Qdrant (6333), Dragonfly (6379) |
| 7687-7444 | Graphs | Memgraph (7687) |
| 8000-8999 | Gateways | Supabase Kong (8000), Infisical (8080), Termix (8080) |
| 9000-9001 | Object Storage | MinIO (9000), Garage S3 (3900) |
| 9120 | Komodo Core | Orchestration control plane |
| 51820/udp | WireGuard | Pangolin Gerbil tunnel |
| 11235+ | Special | Crawl4AI |

## Service Dependency Graph

### Tier 0 — Standalone (No Dependencies)

- Dragonfly (Redis-compatible cache)
- Qdrant (Vector database)
- Termix (Web terminal)
- Pangolin (Network configuration)
- Komodo Periphery (Infrastructure agent)

### Tier 1 — Database-Dependent

- Forgejo → PostgreSQL
- Supabase → PostgreSQL + external services
- LiteLLM → PostgreSQL
- Langfuse → PostgreSQL
- MLFlow → PostgreSQL + MinIO
- Memgraph (graph DB, optional PostgreSQL extension)

### Tier 2 — Multi-Service Dependent

- Cognee → PostgreSQL + Memgraph + Dragonfly + LanceDB + LLM API
- Dagster → PostgreSQL + Forgejo + GitHub + Docker socket
- Crawl4AI → LLM API keys
- Agno → PostgreSQL (pgvector)

## Health Check Patterns

### Database Health Checks

```yaml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 10s
    timeout: 5s
    retries: 5

memgraph:
  healthcheck:
    test: ["CMD", "mgconsole", "--eval", "RETURN 1"]

dragonfly:
  healthcheck:
    test: ["CMD", "redis-cli", "PING"]
```

### Application Health Checks

```yaml
dagster:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3000/graphql"]
    interval: 30s

litellm:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:4000/health"]

pangolin:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3001/api/health"]
```

### Dependency Chain Pattern

```yaml
services:
  app:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      locket:
        condition: service_healthy
      minio:
        condition: service_started
```

## Restart Policies

| Policy | Use Case |
|--------|----------|
| `unless-stopped` | All production services (default) |
| `always` | Critical infrastructure (Komodo, Pangolin, Infisical) |
| `on-failure` | Batch jobs, build runners |
| `no` | One-shot init containers |

## Storage Architecture

### Relational (SQL)

| Database | Purpose |
|----------|---------|
| Supabase PostgreSQL | Auth tables, storage metadata, user data |
| Forgejo PostgreSQL | Repositories, users, issues, packages |
| Dagster PostgreSQL | Runs, events, assets, schedules |
| Langfuse PostgreSQL | Projects, traces, spans, observations |
| LiteLLM PostgreSQL | API keys, models, usage logs |
| MLFlow PostgreSQL | Experiments, runs, metrics/params |

### Graph (NoSQL)

| Database | Purpose |
|----------|---------|
| Memgraph | Knowledge graphs, entity relationships, computed properties |
| Neo4j | Curriculum prerequisite graph, temporal relationships |
| Cognee (Kuzu embedded) | Entity relationship extraction |

### Vector (Embeddings)

| Database | Purpose |
|----------|---------|
| Qdrant | Text embeddings, document chunks, semantic search indexes |
| LanceDB | Vector embeddings for curriculum content |
| LanceDB Cloud | Production vector search |

### Key-Value (Cache)

| Database | Purpose |
|----------|---------|
| Dragonfly (Redis-compatible) | Session cache, embedding cache, temporary data |

### Object Storage (Blob)

| Store | Purpose |
|-------|---------|
| MinIO | MLFlow artifacts, model files, datasets |
| Garage S3 | General object storage, backups, archives |
| Cloudflare R2 | Raw PDFs, images, public assets |

## Environment-Specific Overrides

### Development Override

```yaml
# compose.dev.yaml
services:
  postgres:
    ports:
      - "5432:5432"        # Expose for local tools
  litellm:
    environment:
      - LITELLM_LOG_LEVEL=DEBUG
```

### Production Override

```yaml
# compose.prod.yaml
services:
  postgres:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
  litellm:
    deploy:
      replicas: 2
```

### Usage

```bash
# Development
docker compose -f compose.yaml -f compose.dev.yaml up

# Production
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

## Deployment Order

### Phase 1: Infrastructure Foundation
- Dragonfly (cache), Qdrant (vector), Memgraph (graph)
- No dependencies, can start in parallel

### Phase 2: Core Services
- PostgreSQL instances (Forgejo, Supabase, Dagster, LiteLLM, Langfuse, MLFlow)
- Wait for PG health checks

### Phase 3: Orchestration & Observability
- Dagster (needs Forgejo ready for package registry)
- Cognee (needs all DBs and LLM keys)
- LiteLLM, Langfuse

### Phase 4: Data Processing
- Crawl4AI (needs LLM keys)
- Agno (needs PostgreSQL)

### Phase 5: Advanced
- Garage S3, Pangolin, Komodo
- Verify: `curl http://localhost:3001` (Dagster), `curl http://localhost:4000/health` (LiteLLM)

## Shared Tmpfs for Secrets

```yaml
volumes:
  secrets:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: "size=1m,mode=0700"

services:
  locket:
    volumes:
      - secrets:/run/secrets/locket
  app:
    volumes:
      - secrets:/run/secrets/locket:ro
    depends_on:
      locket:
        condition: service_healthy
```

## Mac-Specific: Host Network Access

For services needing host network on Mac (Docker Desktop):

```yaml
services:
  local-llm-client:
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - LLM_API_BASE=http://host.docker.internal:8081/v1
```

## Quick Health Verification

```bash
# Supabase
curl http://localhost:8000/rest/v1

# Dagster
curl http://localhost:3001

# LiteLLM
curl http://localhost:4000/health

# Komodo Core
curl http://localhost:9120

# Pangolin
curl http://localhost:3001/api/health
```
