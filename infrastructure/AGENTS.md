# Infrastructure - AI Agent Instructions

## Overview

Infrastructure contains deployment configurations, infrastructure-as-code, and service orchestration for the Cianfhoghlaim platform implementing Pangolin Convergence Architecture (two-tier: OCI ARM1 control plane + MacBook M4 workload host).

## Directory Structure

| Directory | Purpose | Technology |
|-----------|---------|------------|
| `stacks/storage/` | Foundational substrates (S3, catalogs, version control) | Docker Compose |
| `stacks/infrastructure/` | Control plane (Pangolin, Komodo, Pocket ID, Forgejo, Pulumi, R2, MotherDuck, PlanetScale) | Docker Compose |
| `stacks/engineering/` | Dev tooling + gateways + services (LiteLLM, llama-swap, Coder, Dagster, Convex, Pipecat) | Docker Compose |
| `stacks/machine_learning/` | AI services (Cognee, Graphiti, Langfuse, MLflow, LanceDB, Qdrant, Memgraph, FalkorDB, RisingWave) | Docker Compose |
| `stacks/tools/` | Productivity and media utilities | Docker Compose |
| `stacks/browser/` | Browser automation stacks | Docker Compose |
| `komodo/` | Komodo configuration and profiles | Komodo |
| `pangolin/` | Pangolin setup documentation | Markdown |
| `infisical/` | Local Infisical dev server | Docker Compose |
| `pulumi/` | Cloud infrastructure | Pulumi IaC |
| `ansible/` | Server configuration | Ansible |
| `scripts/` | Utility scripts | Shell/TypeScript |

### Categorisation philosophy (after Phase 0 reorganisation)

- **`stacks/infrastructure/`** — Control-plane services. Anything that other services depend on for routing/auth/identity/storage provisioning.
- **`stacks/engineering/`** — Service mesh + dev tooling + AI gateways. Things humans and agents interact with daily.
- **`stacks/machine_learning/`** — AI/ML-specific services: vector DBs, knowledge graphs, observability, streaming, training.
- **`stacks/storage/`** — Foundational substrates only: S3 (Garage), Iceberg (Lakekeeper), git (Forgejo runner, LakeFS).
- **`stacks/tools/`** — Productivity / media utilities (rarely tied to the platform's data flow).

## Stack Categories

### Infrastructure (Control Plane)

| Stack | Purpose | Key Ports |
|-------|---------|-----------|
| `pangolin/` | VPN + Traefik + Pocket ID + CrowdSec + TinyAuth | 51820/udp, 443, 80, 8443 |
| `komodo/` | Container orchestration and deployment | 9120 |
| `pocket-id/` | OIDC identity provider | 1411 |
| `dozzle/` | Container log viewer | Internal |
| `DnsServer/` | Local DNS resolution | Internal |

### Storage (Foundational Substrates)

| Stack | Purpose | Key Ports |
|-------|---------|-----------|
| `garage/` | CRDT S3-compatible object storage | 3900-3904 |
| `lakehouse/` | Lakekeeper catalog + Lance Namespace + Postgres + Garage | 3900-3904, 5433, 8181-8182 |
| `lakekeeper/` | Iceberg REST catalog | 8181 |
| `lakefs/` | Git-for-data on S3 (versioned lake) | 8000 |
| `forgejo-runner/` | GitHub Actions runner for Forgejo | Internal |
| `beszel/` | Server/Docker monitoring hub | 8090 |

### Infrastructure (Control Plane)

| Stack | Purpose | Key Ports |
|-------|---------|-----------|
| `pangolin/` | VPN + Traefik + Pocket ID + CrowdSec + TinyAuth | 51820/udp, 443, 80, 8443 |
| `komodo/` | Container orchestration and deployment | 9120 |
| `pocket-id/` | OIDC identity provider | 1411 |
| `dozzle/` | Container log viewer | Internal |
| `DnsServer/` | Local DNS resolution | Internal |
| `forgejo/` | Self-hosted Git forge (control-plane) | 3000, 2222 |
| `r2/` | Cloudflare R2 adapter | Internal |
| `motherduck/` | Cloud query engine | Internal |
| `planetscale/` | Postgres-compatible cloud DB | Internal |
| `monitoring/` | Prometheus + Grafana + Loki | 9090, 3000 |

### Engineering (Dev Tooling + Gateways + Services)

| Stack | Purpose | Key Ports |
|-------|---------|-----------|
| `litellm/` | LLM proxy gateway (Postgres + Prometheus) | 4000, 5432, 9090 |
| `mlx-omni/` | Apple Silicon MLX-format OpenAI server | 10240 |
| `invokeai/` | SDXL image generation | 9090 |
| `crawl4ai/` | Web crawling API | 11235 |
| `coder/` | Cloud development environment | Internal |
| `windmill/` | Workflow automation | Internal |
| `MCPJungle/` | MCP server manager | Internal |
| `DevDocs/` | Developer documentation UI | Internal |
| `n8n/` | Visual workflow automation | 5678 |
| `networking-toolbox/` | Network diagnostic tools | Internal |
| `dagster/` | Pipeline orchestration (engineering entry) | 3335 |
| `convex/` | Realtime backend for web | Internal |
| `pydantic-gateway/` | Pydantic AI gateway (LLM routing) | Internal |
| `mathesar/` | Postgres UI | Internal |
| `agent-os/` | AgentOS (Letta) | Internal |

### Machine Learning (AI Services)

| Stack | Purpose | Key Ports |
|-------|---------|-----------|
| `cognee/` | AI memory system (Neo4j, Memgraph, FalkorDB) | 8000 |
| `graphiti/` | Temporal knowledge graph | 8080 |
| `langfuse/` | LLM observability (v3) | 3000 |
| `lmnr/` | LMNR observability | Internal |
| `olake/` | ELT from MongoDB→warehouse | 8080 |
| `qdrant/` | Vector search | 6333, 6334 |
| `memgraph/` | Graph database (MAGE + Lab UI) | 7687, 7444, 3000 |
| `falkordb/` | Vector+graph hybrid | 6379, 3000 |
| `lancedb/` | LanceDB data viewer | 8080 |
| `mlflow/` | ML experiment tracking | 5000 |
| `logfire/` | Pydantic Logfire (Python tracing) | Internal |
| `nimtable/` | Iceberg catalog UI | Internal |

## Standard Stack Structure

Each stack under `infrastructure/stacks/<category>/<name>/` SHALL follow this structure:

```
stacks/<category>/<name>/
├── compose.yaml           # Docker service definitions
├── pangolin.yaml          # Traefik routing + TinyAuth (if web-facing)
├── sidecar.yaml           # Locket container for Infisical injection
├── secrets.env            # Infisical URI references
└── config/                # Configuration files
    └── *.yaml
```

## Critical Constraints

### Docker Compose Best Practices

```yaml
# CORRECT: Health checks, restart policies, named volumes
services:
  database:
    image: postgres:16
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### Secret Management

**NEVER commit secrets to git.** The `.env` file is gitignored. Secrets flow:

1. **Infisical vault** (`dev-baile`): Source of truth for all secrets
2. **`.infisical.env` template** (committed): Contains `infisical://dev-baile/...` references
3. **`mise` hooks**: Automatically run `infisical export` on directory entry, hydrating `.env`
4. **Locket sidecar**: Per-stack container that injects secrets at runtime

```bash
# Template format (.infisical.env - committed, no plaintext)
MOTHERDUCK_TOKEN=infisical://dev-baile/motherduck/token
FIRECRAWL_API_KEY=infisical://dev-baile/firecrawl/api_key

# Stack format (secrets.env - committed, no plaintext)
MOTHERDUCK_TOKEN=infisical://dev-baile/motherduck/token
```

**DO NOT manually create `.env` files.** Allow mise hooks and Locket to hydrate the environment.

### Network Configuration

All stacks use shared Docker network for inter-service communication:

```yaml
services:
  app:
    networks:
      - cianfhoghlaim

networks:
  cianfhoghlaim:
    external: true
```

## Deployment Workflow

### Local Development

```bash
# Stacks use Komodo for management. For direct Docker Compose:
cd infrastructure/stacks/storage/<stack>
docker compose up -d
docker compose logs -f
docker compose down
```

### Production Deployment (Komodo GitOps)

Komodo syncs from Forgejo and manages all stacks:

```bash
# Access Komodo UI
open https://komodo.cianfhoghlaim.ie

# Deploy/update a stack via Komodo UI or API
# Each stack has compose.yaml + pangolin.yaml + sidecar.yaml + secrets.env
```

### Infrastructure Changes (Pulumi)

```bash
cd infrastructure/pulumi/<project>
pulumi preview
pulumi up
```

## Key Infrastructure Services

### Garage (S3 Object Storage)
- CRDT-based S3-compatible object storage
- Ports: 3900 (S3 API), 3901 (admin), 3902 (web), 3903-3904 (rpc)
- Used by DuckLake for Parquet storage and LanceDB for vector data

### Lakehouse Stack
- Garage S3 → Lakekeeper Iceberg Catalog (8181) → Lance Namespace Sidecar (8182)
- Postgres (5433) for Lakekeeper catalog metadata
- Custom `lakehouse-lance-namespace:latest` sidecar registers LanceDB tables as Iceberg tables

### Pangolin (VPN + Routing)
- WireGuard-based tunneling (port 51820/udp)
- Traefik v3.4.0 reverse proxy
- Pocket ID OIDC + TinyAuth for SSO
- CrowdSec for intrusion detection

### Komodo (Container Orchestration)
- GitOps workflow synced from Forgejo
- Multi-server deployments (OCI + MacBook)
- Integrated with Pangolin for service routing

## Common Operations

### Starting Core Infrastructure

```bash
# Core control plane (Pangolin + Komodo + Pocket ID) managed via Komodo
# Individual stacks can be started via:
docker compose -f infrastructure/stacks/storage/garage/compose.yaml up -d
docker compose -f infrastructure/stacks/storage/lakehouse/compose.yaml up -d
```

### Health Checks

```bash
# Check all container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check specific service
docker inspect --format='{{.State.Health.Status}}' <container>

# View resource usage
docker stats --no-stream
```

### Adding New Stacks

1. Create directory structure:
   ```bash
   mkdir -p infrastructure/stacks/<category>/<name>
   ```
2. Create `compose.yaml` with health checks, restart policies, named volumes, and network config
3. Create `pangolin.yaml` for web-facing services (Traefik + TinyAuth routing)
4. Create `sidecar.yaml` for Locket secret injection
5. Create `secrets.env` with Infisical URI references
6. Add to this AGENTS.md with port and purpose
7. Commit and let Komodo sync deploy

## Resources

- **Pangolin Docs:** https://pangolin.dev
- **Komodo Docs:** https://komo.do/docs
- **Infisical Docs:** https://infisical.com/docs
- **Pulumi Docs:** https://www.pulumi.com/docs
