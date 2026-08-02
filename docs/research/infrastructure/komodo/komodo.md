# Komodo

Container orchestration and deployment management platform.

## Overview

Komodo provides a GitOps-style deployment platform for Docker containers:

- **Stack Management** - Compose-based service definitions
- **GitOps Workflows** - Deploy on git push
- **Multi-Server** - Manage containers across servers
- **Build Automation** - Automated container builds

## Dashboard

Access the Komodo dashboard at your configured URL to:

- View running containers and their status
- Trigger deployments manually
- View build logs and history
- Manage environment variables

## Stack Configuration

Stacks are defined in `bonneagar/komodo/stacks/`:

```yaml
# stack.yaml
name: education-pipeline
description: Oideachas data processing services

services:
  dagster:
    image: ghcr.io/cianfhoghlaim/dagster:latest
    build:
      context: sruth/oideachas
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}

  memgraph:
    image: memgraph/memgraph:latest
    volumes:
      - memgraph_data:/var/lib/memgraph
```

## Deployment

### Via Dashboard

1. Navigate to Stacks
2. Select target stack
3. Click "Deploy"

### Via CLI

```bash
# Install komodo CLI
npm install -g komodo_client

# Deploy a stack
komodo stack deploy education-pipeline
```

### Via API

```typescript
import { KomodoClient } from 'komodo_client';

const client = new KomodoClient({
  url: process.env.KOMODO_URL,
  apiKey: process.env.KOMODO_API_KEY,
});

await client.stacks.deploy('education-pipeline');
```

## Environment Management

Environment variables are managed securely:

```bash
# Set environment variable
komodo env set education-pipeline DATABASE_URL "postgres://..."

# List variables
komodo env list education-pipeline
```

For sensitive values, integrate with [Locket](./locket).

## Build Configuration

Automated builds on git push:

```yaml
# komodo.build.yaml
builds:
  dagster:
    repo: github.com/cianfhoghlaim/cianfhoghlaim
    branch: main
    path: sruth/oideachas
    dockerfile: Dockerfile
    triggers:
      - paths: ["sruth/oideachas/**"]
```

## Integration with Cianfhoghlaim

| Stack | Purpose | Services |
|-------|---------|----------|
| `education-pipeline` | Data processing | Dagster, workers |
| `graph-services` | Knowledge graph | Memgraph, FalkorDB |
| `docs` | Documentation | Docusaurus |

## Related

- [Dagger](./dagger) - CI/CD pipelines
- [Locket](./locket) - Secret management
- [Infrastructure Overview](./overview)
