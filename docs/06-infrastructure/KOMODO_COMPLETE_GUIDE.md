# Komodo — Complete Deployment Orchestration Guide

> **Merged From:** `docs/bonneagar/komodo/` (21 files)
> Consolidated: komodo.md, KCG_SUMMARY.md, Komodo Deployment and Workflow Integration.md, Komodo FAQ Tips and Tricks.md, Komodo Deployment Technical Outline.md, Procedures and Actions, Sync Resources, Configuring Webhooks, Backup and Restore, komodo_client API docs, ansible-role-komodo/, SKILL_CONTEXT.md, and root-level komodo-*.md files.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture: Core/Periphery](#architecture-coreperiphery)
3. [Installation & Bootstrap](#installation--bootstrap)
4. [Stack Configuration](#stack-configuration)
5. [GitOps Workflow](#gitops-workflow)
6. [Recursive Deployment](#recursive-deployment)
7. [Resource Sync](#resource-sync)
8. [Procedures & Actions](#procedures--actions)
9. [Webhooks](#webhooks)
10. [Environment & Secrets Management](#environment--secrets-management)
11. [Build Automation](#build-automation)
12. [TypeScript SDK](#typescript-sdk)
13. [Ansible Integration](#ansible-integration)
14. [Backup & Restore](#backup--restore)
15. [FAQ & Troubleshooting](#faq--troubleshooting)
16. [Integration with Cianfhoghlaim](#integration-with-cianfhoghlaim)

---

## Overview

Komodo is an open-source container orchestration platform by Moghtech. It provides GitOps-driven deployment management with a web UI, API, and CLI — syncing Docker Compose stacks from a Git repository across multiple servers.

**Key capabilities:**
- **GitOps sync**: Watches Forgejo repositories and applies compose.yaml + sidecar.yaml on change
- **Multi-server**: One Komodo Core manages Periphery agents on all physical hosts
- **Pangolin integration**: All stacks automatically register as private Pangolin resources
- **Locket sidecar**: Secrets injected via Infisical at runtime, never in compose files

### In the Cianfhoghlaim Stack

Komodo is the deployment engine for all 89 Docker Compose stacks in `infrastructure/stacks/`. Every stack change committed to Forgejo is automatically synced and deployed to the correct server (arm1-oci, cax41-hetzner, or bunchloch MacBook).

---

## Architecture: Core/Periphery

### Komodo Core: The State Engine

Centralized control plane responsible for:
- **State Reconciliation**: Polls Git repos for changes, calculates diffs between desired and actual state
- **API & Webhooks**: Processes Git provider webhooks for instant deployment on commit
- **Database**: Supports MongoDB, FerretDB, and PostgreSQL
- **UI**: Web dashboard for stack management, build logs, and telemetry

### Komodo Periphery: The Privileged Agent

Lightweight Rust binary on every managed server:
- **Docker Socket Control**: Mounts `/var/run/docker.sock` for container lifecycle management
- **System Telemetry**: Mounts `/proc` for CPU, memory, disk metrics
- **Secure Connectivity**: Communication via shared secret (`KOMODO_PASSKEY`) + optional mTLS
- **Default port**: 8120

---

## Installation & Bootstrap

### Periphery Agent (Systemd)

```bash
# Install via official script
curl -fsSL https://komo.do/install | bash

# Or manually
cargo install komodo_periphery
```

### Periphery Agent (Docker)

```yaml
services:
  periphery:
    image: ghcr.io/moghtech/komodo-periphery:latest
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /etc/komodo:/etc/komodo
      - /proc:/proc:ro
    environment:
      - KOMODO_PASSKEY=${PASSKEY}
    ports:
      - "8120:8120"
```

### Systemd Customization (Drop-in)

```bash
systemctl edit periphery.service
```

```ini
[Service]
Environment="PERIPHERY_ROOT_DIRECTORY=/home/myUser/komodo"
Environment="PERIPHERY_DISABLE_TERMINALS=true"
```

```bash
systemctl daemon-reload
systemctl restart periphery.service
```

---

## Stack Configuration

Stacks are defined in Git repositories and managed via Komodo Core.

### Basic Stack Definition

```yaml
# compose.yaml
services:
  dagster:
    image: ghcr.io/cianfhoghlaim/dagster:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
  memgraph:
    image: memgraph/memgraph:latest
    volumes:
      - memgraph_data:/var/lib/memgraph
```

### Stack with Sidecar (Locket Secrets)

```yaml
# sidecar.yaml (merged at deploy time)
services:
  locket:
    image: ghcr.io/bpbradley/locket:latest
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
```

---

## GitOps Workflow

1. **Commit** compose.yaml changes to Forgejo
2. **Webhook** fires to Komodo Core
3. **Core** detects divergence between desired and actual state
4. **Periphery** pulls new images, restarts containers
5. **State** reconciled automatically

### Repository Structure

```
infrastructure/stacks/
├── engineering/
│   ├── n8n/
│   │   ├── compose.yaml
│   │   ├── sidecar.yaml
│   │   └── pangolin.yaml
│   └── forgejo/
├── tools/
│   ├── vikunja/
│   └── cal-diy/
└── infrastructure/
    ├── komodo/
    ├── pangolin/
    └── infisical/
```

---

## Recursive Deployment

Komodo can manage its own Periphery agents as Stacks:

1. **Initial State**: Admin manually installs Periphery on server
2. **Adoption**: Define Periphery's docker-compose.yaml in Git, create Stack in Core
3. **Handover**: Komodo instructs running Periphery to "redeploy yourself"
4. **Graceful Replacement**: Docker pulls new image, stops old container, starts new one. Persisted volumes (`/etc/komodo`) maintain agent identity.

**Critical**: The `/etc/komodo` directory contains the agent's unique ID. Losing it causes the agent to appear as a new server in Core.

---

## Resource Sync

Resource Syncs reproduce Periphery state from TOML definitions:

```bash
# Export current server state as TOML
komodo resource get-server-toml <server-name>

# Create Managed Resource Sync from TOML
# Execute Sync to re-create stacks on the server
```

**Use cases:**
- Migrating between agent types (systemd ↔ container)
- Disaster recovery
- Server provisioning

---

## Procedures & Actions

Komodo Procedures define multi-step workflows:

```yaml
procedures:
  - name: deploy-all
    steps:
      - action: deploy-stack
        target: education-pipeline
      - action: deploy-stack
        target: graph-services
      - action: deploy-stack
        target: docs
```

---

## Webhooks

### Git Provider Webhooks

Configure Forgejo/GitHub/GitLab to POST to Komodo Core on push events:

```
POST https://komodo.cianfhoghlaim.ie/api/webhook/git
Headers: X-Komodo-Secret: <webhook-secret>
```

### Stack-Specific Webhooks

Trigger specific stacks on path-filtered changes:

```yaml
triggers:
  - paths: ["sruth/oideachas/**"]
    stack: education-pipeline
```

---

## Environment & Secrets Management

### Environment Variables

```bash
# Via CLI
komodo env set education-pipeline DATABASE_URL "postgres://..."

# Via UI: Stack → Environment tab
```

### Secret Injection (Locket Sidecar)

Secrets are never stored in compose files. The Locket sidecar pattern:

```yaml
services:
  app:
    depends_on:
      locket:
        condition: service_healthy
    volumes:
      - type: tmpfs
        target: /run/secrets/locket
    environment:
      - DATABASE_URL_FILE=/run/secrets/locket/DATABASE_URL

  locket:
    image: ghcr.io/bpbradley/locket:latest
    command: ["--provider=infisical", "--mode=watch"]
```

---

## Build Automation

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

---

## TypeScript SDK

```typescript
import { KomodoClient } from "@komodo/client";

const client = new KomodoClient({
  url: process.env.KOMODO_URL,
  apiKey: process.env.KOMODO_API_KEY,
});

// Deploy a stack
await client.stacks.deploy('education-pipeline');

// List servers
const servers = await client.resources.listServers();

// Get build logs
const logs = await client.builds.getLogs(buildId);
```

---

## Ansible Integration

Community Ansible roles for Periphery agent management:

- **mbecker (official)**: `github.com/moghtech/komodo/discussions/220`
- **bpbradley**: `github.com/bpbradley/ansible-role-komodo`

Use for automated Periphery updates across fleet.

---

## Backup & Restore

### Database Backup

```bash
# MongoDB
mongodump --uri="mongodb://komodo:pass@localhost:27017/komodo" --out=/backup

# PostgreSQL
pg_dump -U komodo komodo > /backup/komodo.sql
```

### State Backup

Export all Resource TOMLs for disaster recovery:

```bash
for server in $(komodo resource list-servers); do
  komodo resource get-server-toml $server > backup/${server}.toml
done
```

---

## FAQ & Troubleshooting

### Can Komodo Core update itself?

Yes. If using systemd Periphery, re-deploy Core stack without issue. For Docker agents, keep Periphery and Core in different stacks.

### Periphery stops after closing SSH?

If installed with `--user`, use `loginctl enable-linger` to persist sessions.

### Migrating between agent types

1. Export Resource TOML from current agent
2. Install new agent type
3. Migrate configuration (env vars → config.toml or drop-in)
4. Execute Resource Sync to restore state
5. Fix file ownership with `chown` if switching root ↔ user

### Common Issues

| Issue | Solution |
|-------|----------|
| Agent appears as new server | Check `/etc/komodo` volume persistence |
| Permission denied on volumes | Fix ownership with `chown` after agent migration |
| Webhook not triggering | Verify webhook secret and URL configuration |
| Stack deploy hangs | Check Periphery connectivity to Core (port 8120) |

---

## Integration with Cianfhoghlaim

| Stack | Purpose | Services |
|-------|---------|----------|
| `education-pipeline` | Data processing | Dagster, workers |
| `graph-services` | Knowledge graph | Memgraph, FalkorDB |
| `docs` | Documentation | Docusaurus |
| `infrastructure/komodo` | Self-management | Core, Periphery |
| `infrastructure/pangolin` | Zero-trust | Gateway, Newt |
| `infrastructure/infisical` | Secrets | Vault, API |

### Related Tools

- **Pangolin** — Zero-trust networking (all stacks exposed as private resources)
- **Locket** — Secret injection sidecar (every stack uses `sidecar.yaml`)
- **Dagger** — CI/CD pipelines that trigger Komodo deployments
- **Infisical** — Source of truth for all secrets
