# Infrastructure Overview

Cianfhoghlaim infrastructure is managed through modular Docker stacks with unified secrets and routing.

## Components

| Component | Purpose |
|-----------|---------|
| **Stacks** | 19 Docker Compose services |
| **Pangolin** | Identity-aware VPN + Traefik |
| **Komodo** | Container orchestration |
| **Locket** | 1Password secret injection |
| **Pulumi** | IaC for OCI/Hetzner |
| **Dagger** | CI/CD pipelines |

## Stack Architecture

Each stack follows a standard structure:

```
stacks/<name>/
├── compose.yaml     # Docker Compose (standalone)
├── blueprint.yaml   # Pangolin routing
├── secrets.env      # Locket template
└── sidecar.yaml     # Locket sidecar mode
```

## Available Stacks

| Stack | Description | Port |
|-------|-------------|------|
| autobase | PostgreSQL cluster | 8082 |
| beszel | Server monitoring | 8090 |
| cognee | AI memory/knowledge | 8001 |
| dozzle | Container logs | 8080 |
| falkordb | Graph database | 3000 |
| garage | S3 storage | 3900 |
| graphiti | Knowledge graph MCP | 8000 |
| lakefs | Data versioning | 8000 |
| lancedb | Vector database | 8080 |
| langfuse | LLM observability | 3000 |
| memgraph | Graph database | 3000 |
| mlflow | ML tracking | 5000 |
| qdrant | Vector search | 6333 |

## Quick Start

```bash
# Development mode
./scripts/stack.sh langfuse up -d

# Production (with Locket secrets)
LOCKET_ENABLED=1 ./scripts/stack.sh langfuse up -d

# Sync routing blueprints
./scripts/sync-blueprints.sh
```

## Related Docs

- [Pangolin](./pangolin) - VPN and routing
- [Komodo](./komodo) - Container orchestration
- [Locket](./locket) - Secret management
- [Pulumi](./pulumi) - Infrastructure as Code
- [Dagger](./dagger) - CI/CD pipelines
