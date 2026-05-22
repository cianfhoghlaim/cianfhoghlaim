# Bonneagar (Infrastructure) - AI Agent Instructions

## Overview

Bonneagar (Irish: "infrastructure") contains deployment configurations, infrastructure-as-code, and service orchestration for the cianfhoghlaim platform.

## Directory Structure

| Directory | Purpose | Technology |
|-----------|---------|------------|
| `storage/` | Database and storage stacks | Docker Compose |
| `komodo/` | Container orchestration | Komodo |
| `pangolin/` | VPN and network access | Pangolin/WireGuard |
| `locket/` | Secret management | Infisical/Vault |
| `pulumi/` | Cloud infrastructure | Pulumi IaC |
| `dagger/` | CI/CD pipelines | Dagger |
| `ansible/` | Server configuration | Ansible |
| `forgejo/` | Git hosting | Forgejo |
| `api_specs/` | API specifications | OpenAPI |
| `uirlisí/` | CLI tools | TypeScript/Bun |
| `op/` | Infisical integration | Infisical CLI |
| `scripts/` | Utility scripts | Shell/TypeScript |

## Stack Categories

### Database Stacks (`storage/`)

| Stack | Purpose | Port |
|-------|---------|------|
| `lancedb/` | Vector database | N/A (embedded) |
| `memgraph/` | Graph database | 7687 |
| `qdrant/` | Vector search | 6333 |
| `duckdb/` | Analytics database | N/A (embedded) |
| `falkordb/` | Graph + vector | 6379 |
| `risingwave/` | Streaming SQL | 4566 |

### ML/AI Stacks (`storage/`)

| Stack | Purpose | Port |
|-------|---------|------|
| `mlflow/` | ML experiment tracking | 5000 |
| `langfuse/` | LLM observability | 3000 |
| `ollama/` | Local LLM inference | 11434 |
| `litellm/` | LLM proxy | 4000 |

### Observability Stacks (`storage/`)

| Stack | Purpose | Port |
|-------|---------|------|
| `grafana/` | Dashboards | 3000 |
| `prometheus/` | Metrics | 9090 |
| `loki/` | Logs | 3100 |

## Standard Stack Structure

Each stack SHOULD follow this structure:

```
bonneagar/storage/<stack>/
├── docker-compose.yml      # Main compose file
├── docker-compose.dev.yml  # Development overrides
├── .env.example           # Environment template
├── README.md              # Stack documentation
├── config/                # Configuration files
│   └── *.yaml
└── data/                  # Persistent data (gitignored)
```

## Critical Constraints

### Docker Compose Best Practices

```yaml
# CORRECT: Health checks and restart policies
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

# WRONG: Missing health checks and persistence
# services:
#   database:
#     image: postgres:16  # No restart, no health, no volume!
```

### Secret Management

**NEVER commit secrets to git.** Use:

1. **Infisical CLI (`op/`):**
   ```bash
   infisical secrets get "infisical://vault/item/field"
   ```

2. **Environment files:**
   ```bash
   # .env.example (committed)
   DATABASE_URL=postgresql://user:password@host:5432/db

   # .env (gitignored, actual values)
   DATABASE_URL=postgresql://prod_user:$ECRET@prod-host:5432/db
   ```

3. **Pulumi secrets:**
   ```typescript
   const dbPassword = new pulumi.Config().requireSecret("dbPassword");
   ```

### Network Configuration

All stacks should use the shared network for inter-service communication:

```yaml
services:
  app:
    networks:
      - cianfhoghlaim

networks:
  cianfhoghlaim:
    external: true
```

Create the network once:
```bash
docker network create cianfhoghlaim
```

## Deployment Workflow

### 1. Local Development

```bash
# Start a stack
cd bonneagar/storage/<stack>
cp .env.example .env
# Edit .env with local values
docker-compose up -d

# View logs
docker-compose logs -f

# Stop stack
docker-compose down
```

### 2. Production Deployment

Using Komodo (`komodo/`):

```bash
# Deploy stack to production
komodo deploy <stack>

# Check status
komodo status <stack>

# View logs
komodo logs <stack> -f
```

### 3. Infrastructure Changes

Using Pulumi (`pulumi/`):

```bash
cd bonneagar/pulumi/<project>

# Preview changes
pulumi preview

# Apply changes
pulumi up

# Destroy resources (CAREFUL!)
pulumi destroy
```

## Stack-Specific Documentation

### LanceDB (`storage/lancedb/`)

Embedded vector database for semantic search:
- No Docker required (Python library)
- Use `merge_insert` for idempotent writes
- Follows MVCC for multi-process safety

See `.claude/CONSTRAINTS.md` for critical usage patterns.

### Memgraph (`storage/memgraph/`)

Graph database for curriculum relationships:
- Cypher query language
- Port 7687 (Bolt protocol)
- Used for prerequisite chains, topic relationships

```bash
docker-compose -f bonneagar/storage/memgraph/docker-compose.yml up -d
```

### Qdrant (`storage/qdrant/`)

High-performance vector search:
- REST API on port 6333
- gRPC on port 6334
- Supports multi-vector search (ColPali)

### Pangolin (`pangolin/`)

VPN and secure network access:
- WireGuard-based tunneling
- Zero-trust network access
- Used for secure database access

### Komodo (`komodo/`)

Container orchestration and deployment:
- GitOps workflow
- Multi-server deployments
- Integrated with Forgejo

## Common Operations

### Starting All Required Stacks

```bash
# Create network
docker network create cianfhoghlaim

# Start databases
docker-compose -f bonneagar/storage/memgraph/docker-compose.yml up -d
docker-compose -f bonneagar/storage/qdrant/docker-compose.yml up -d

# Start ML services
docker-compose -f bonneagar/storage/mlflow/docker-compose.yml up -d
docker-compose -f bonneagar/storage/ollama/docker-compose.yml up -d

# Start observability
docker-compose -f bonneagar/storage/grafana/docker-compose.yml up -d
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

### Backup Operations

```bash
# Backup Memgraph
docker exec memgraph mgconsole -c "CREATE SNAPSHOT;"

# Backup Qdrant
curl -X POST "http://localhost:6333/collections/curriculum/snapshots"

# Backup DuckDB (file copy)
cp data/*.duckdb backups/
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Container won't start | Port conflict | Check `docker ps` and `lsof -i :<port>` |
| Network unreachable | Missing network | Run `docker network create cianfhoghlaim` |
| Out of disk space | Data accumulation | Run `docker system prune -a` |
| Permission denied | Volume ownership | Check UID/GID in compose file |
| Stack won't connect | Network isolation | Ensure same Docker network |

## Adding New Stacks

1. Create directory structure:
   ```bash
   mkdir -p bonneagar/storage/<stack>/{config,data}
   ```

2. Create docker-compose.yml with:
   - Health checks
   - Restart policies
   - Named volumes
   - Network configuration

3. Create .env.example with all required variables

4. Add to this AGENTS.md with port and purpose

5. Test locally before adding to Komodo

## Resources

- **Docker Compose Docs:** https://docs.docker.com/compose
- **Pulumi Docs:** https://www.pulumi.com/docs
- **Komodo Docs:** https://komo.do/docs
- **Pangolin Docs:** https://pangolin.dev
- **Infisical CLI:** https://developer.infisical.com/docs/cli
