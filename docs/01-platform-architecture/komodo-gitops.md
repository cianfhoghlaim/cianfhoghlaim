---
title: "Komodo GitOps — Deployment Orchestration & Resource Management"
domain: architecture
status: stable
description: "Complete Komodo deployment orchestration covering Core/Periphery architecture, GitOps workflows, Resource Sync, Procedures, Actions, Ansible integration, and recursive deployment"
supersedes:
  - docs/bonneagar/KOMODO_COMPLETE_GUIDE.md
  - docs/bonneagar/komodo.md
  - docs/bonneagar/komodo-deployment.md
  - docs/bonneagar/komodo-api-summary.md
  - docs/bonneagar/komodo-openapi-research.md
  - docs/bonneagar/comparing-approaches-pangolin-registration-komodo-deployment.md
  - docs/bonneagar/deploying-komodo-periphery-pangolin-private-access-lancedb-stack.md
  - docs/bonneagar/extending-komodo-pr-deploy-pangolin-integration-komodo-actions.md
  - docs/bonneagar/deploy.md
  - docs/bonneagar/Release Komodo v2.0.0-dev-102 · moghtech_komodo.md
  - docs/bonneagar/Pigsty, Mathesar, Komodo Deployment Outline.md
entities:
  - KomodoCore
  - KomodoPeriphery
  - GitOps
  - ResourceSync
related_skills:
  - .agents/skills/komodo/SKILL.md
  - .agents/skills/stack-ops/SKILL.md
  - .agents/skills/pangolin/SKILL.md
ccc_query_hints:
  - "komodo deployment workflow"
  - "gitops resource sync"
  - "how to deploy with komodo"
  - "komodo core periphery architecture"
  - "komodo procedures and actions"
  - "recursive deployment komodo"
last_reviewed: 2026-06-06
---

# Komodo GitOps — Deployment Orchestration

Komodo is an open-source container orchestration platform by Moghtech. It provides GitOps-driven deployment management with a web UI, API, and CLI — syncing Docker Compose stacks from Git repositories across multiple servers.

## Architecture: Core/Periphery

```
┌─────────────────────────────────────────────────────────────┐
│                    KOMODO CORE                               │
│         Web UI + API + State Management                      │
│                    (Port 9120)                               │
└─────────────────────────────────────────────────────────────┘
        ↓                    ↓                    ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  PERIPHERY   │   │  PERIPHERY   │   │  PERIPHERY   │
│  (Server A)  │   │  (Server B)  │   │  (Server C)  │
│  Port 8120   │   │  Port 8120   │   │  Port 8120   │
└──────────────┘   └──────────────┘   └──────────────┘
        ↓                    ↓                    ↓
   [Docker]            [Docker]            [Docker]
   [Stacks]            [Stacks]            [Stacks]
```

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

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Core initiates to Periphery | Periphery can be behind NAT |
| Passkey authentication | Simple shared-secret model |
| Stateless Periphery | Easy deployment, no local persistence |
| MongoDB backend | Document store for complex configs |

## Resource Types

All resources in Komodo share common traits: unique name/ID, tagging, permission controls, audit logging.

| Resource | Description |
|----------|-------------|
| **Server** | Connection to Periphery agent with monitoring |
| **Deployment** | Single Docker container deployment |
| **Stack** | Docker Compose project (UI, Host, or Git-based) |
| **Build** | Automated Docker image builds from Git |
| **Builder** | Build capacity (Server or AWS instances) |
| **Repo** | Git repository for script execution |
| **Procedure** | Multi-stage orchestration (parallel + sequential) |
| **Action** | TypeScript automation with full API access |
| **Resource Sync** | GitOps declarative infrastructure |
| **Alerter** | Notification routing system |
| **Template** | Reusable resource configurations |

## GitOps Workflow

```
1. Commit compose.yaml changes to Forgejo
2. Webhook fires to Komodo Core
3. Core detects divergence between desired and actual state
4. Periphery pulls new images, restarts containers
5. State reconciled automatically
```

### Webhook Configuration

```
POST https://komodo.cianfhoghlaim.ie/api/webhook/git
Headers: X-Komodo-Secret: <webhook-secret>
```

### Stack-Specific Triggers

```yaml
triggers:
  - paths: ["sruth/oideachais/**"]
    stack: education-pipeline
```

## Stack Configuration

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

### Git-Based Stack

```toml
[[stack]]
name = "my-application"
description = "Deployed from Git"

[stack.config]
server = "main-server"
repo = "username/my-app-repo"
git_account = "github-account"
branch = "main"
file_paths = ["docker-compose.yml"]

[stack.config.environment]
NODE_ENV = "production"
APP_VERSION = "${APP_VERSION}"
DB_PASSWORD = "${DB_PASSWORD}"
```

## Recursive Deployment

Komodo manages its own Periphery agents as Stacks:

1. **Initial State**: Admin manually installs Periphery on server
2. **Adoption**: Define Periphery's docker-compose.yaml in Git, create Stack in Core
3. **Handover**: Komodo instructs running Periphery to "redeploy yourself"
4. **Graceful Replacement**: Docker pulls new image, stops old container, starts new one

**Critical**: The `/etc/komodo` directory contains the agent's unique ID. Losing it causes the agent to appear as a new server in Core.

## Resource Sync (Infrastructure as Code)

Resource Syncs reproduce Periphery state from TOML definitions:

```bash
# Export current server state as TOML
komodo resource get-server-toml <server-name>

# Create Managed Resource Sync from TOML
# Execute Sync to re-create stacks
```

### Repository Structure

```
komodo-infra/
├── stacks/
│   ├── frontend.toml
│   ├── backend.toml
│   └── database.toml
├── deployments/
│   └── monitoring.toml
├── procedures/
│   ├── deploy-all.toml
│   └── update-all.toml
├── actions/
│   └── custom-automation.toml
└── sync.toml
```

### Sync Configuration

```toml
[[resource_sync]]
name = "komodo-infrastructure"
description = "All infrastructure as code"

[resource_sync.config]
repo = "username/komodo-infra"
git_account = "github-account"
branch = "main"
resource_path = [
  "stacks/*.toml",
  "deployments/*.toml",
  "procedures/*.toml",
  "actions/*.toml"
]
managed = true
files_on_stack = false
git_provider = "github"
```

### Use Cases

- Migrating between agent types (systemd ↔ container)
- Disaster recovery
- Server provisioning
- Environment replication

## Procedures & Actions

### Multi-Stage Procedure

```toml
[[procedure]]
name = "deploy-full-stack"
description = "Deploy all services in correct order"

# Stage 1: Pull all repositories (parallel)
[[procedure.config.stages]]
[[procedure.config.stages.executions]]
operation = "PullRepo"
params = { repo = "frontend-repo" }

[[procedure.config.stages.executions]]
operation = "PullRepo"
params = { repo = "backend-repo" }

# Stage 2: Build images (parallel, after Stage 1)
[[procedure.config.stages]]
[[procedure.config.stages.executions]]
operation = "RunBuild"
params = { build = "frontend-build" }

[[procedure.config.stages.executions]]
operation = "RunBuild"
params = { build = "backend-build" }

# Stage 3: Deploy stacks (after Stage 2)
[[procedure.config.stages]]
[[procedure.config.stages.executions]]
operation = "DeployStack"
params = { stack = "frontend-stack" }

[[procedure.config.stages.executions]]
operation = "DeployStack"
params = { stack = "backend-stack" }
```

### TypeScript Action

```typescript
// Action: sync-environment-branches
const targetBranch = ARGS.branch || "main";
const dryRun = ARGS.dryRun || false;

// Pre-initialized 'komodo' client available
const stacks = await komodo.read("ListStacks", {});

for (const stack of stacks) {
  const config = await komodo.read("GetStack", { stack: stack.name });

  if (config.config.repo && config.config.branch !== targetBranch) {
    if (!dryRun) {
      await komodo.write("UpdateStack", {
        name: stack.name,
        config: { ...config.config, branch: targetBranch }
      });
      await komodo.execute("DeployStack", { stack: stack.name });
    }
  }
}
```

## TypeScript SDK

```typescript
import { KomodoClient } from "komodo_client";

const client = KomodoClient({
  url: "https://komodo.example.com",
  type: "api-key",
  params: {
    key: "your-api-key",
    secret: "your-api-secret"
  }
});

// Read operations
const stacks = await client.read("ListStacks", {});
const deployment = await client.read("GetDeployment", { deployment: "my-app" });

// Execute operations
await client.execute("DeployStack", { stack: "frontend" });
await client.execute("RunBuild", { build: "my-app-build" });

// Write operations
await client.write("UpdateStack", {
  name: "frontend",
  config: { /* updated configuration */ }
});
```

## CLI Usage (`km`)

```bash
# List containers
km ps --down

# Deploy resources
km deploy-stack frontend
km run-build my-app-build
km deploy my-app-deployment

# Run automation
km run action sync-branches
km run procedure deploy-all-production

# Maintenance
km prune-system
km database backup

# Skip confirmations (CI/CD)
km deploy-stack frontend --yes
```

## Environment & Secrets

### Core Environment Variables

```bash
KOMODO_PASSKEY=random_secure_passkey
KOMODO_HOST=https://komodo.example.com
KOMODO_TITLE="Production Komodo"
KOMODO_INIT_ADMIN_USERNAME=admin
KOMODO_INIT_ADMIN_PASSWORD=secure_password
KOMODO_FIRST_SERVER=http://192.168.1.10:8120
KOMODO_RESOURCE_POLL_INTERVAL=3600
KOMODO_WEBHOOK_SECRET=webhook_secret
```

### Periphery Configuration

```toml
# periphery.toml
passkey = "matches_komodo_passkey"
port = 8120

[directories]
repo_dir = "/opt/komodo/repos"
stack_dir = "/opt/komodo/stacks"

[security]
allowed_ips = ["192.168.1.0/24"]
```

### Secret Injection via Locket

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

## Build Automation

```yaml
# komodo.build.yaml
builds:
  dagster:
    repo: github.com/cianfhoghlaim/cianfhoghlaim
    branch: main
    path: sruth/oideachais
    dockerfile: Dockerfile
    triggers:
      - paths: ["sruth/oideachais/**"]
```

## Backup & Restore

### Database Backup

```bash
# MongoDB
mongodump --uri="mongodb://komodo:pass@localhost:27017/komodo" --out=/backup

# PostgreSQL
pg_dump -U komodo komodo > /backup/komodo.sql
```

### State Backup (Disaster Recovery)

```bash
for server in $(komodo resource list-servers); do
  komodo resource get-server-toml $server > backup/${server}.toml
done
```

## Security Best Practices

### Network Security

- Always use reverse proxy for HTTPS (Caddy, Nginx, Traefik)
- Firewall Periphery port 8120: Only allow Core IP
- Use IP whitelisting in Periphery config
- Disable direct internet access to Core/Periphery ports
- Use VPN for remote access (Tailscale, WireGuard, Pangolin)

### Authentication

- Rotate API keys regularly
- Use OAuth/OIDC for team access
- Implement User Groups for permission management
- Follow principle of least privilege
- Enable user approval workflow

### Secrets

- Store secrets in Komodo Core config, not in compose files
- Use variable interpolation: `${SECRET_NAME}`
- Consider external secret management (Infisical, 1Password)
- Never commit secrets to Git

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent appears as new server | Check `/etc/komodo` volume persistence |
| Permission denied on volumes | Fix ownership with `chown` after agent migration |
| Webhook not triggering | Verify webhook secret and URL configuration |
| Stack deploy hangs | Check Periphery connectivity to Core (port 8120) |
| Periphery stops after SSH close | Use `loginctl enable-linger` for user sessions |

### Debug Commands

```bash
# Restart Periphery
systemctl restart komodo-periphery

# Check logs
journalctl -u komodo-periphery -f

# Test connectivity
curl http://periphery-host:8120/health

# Verify firewall
ufw status
```

## Integration with Cianfhoghlaim

| Stack | Purpose | Services |
|-------|---------|----------|
| `education-pipeline` | Data processing | Dagster, workers |
| `graph-services` | Knowledge graph | Memgraph, FalkorDB |
| `docs` | Documentation | Docusaurus |
| `infrastructure/komodo` | Self-management | Core, Periphery |
| `infrastructure/pangolin` | Zero-trust | Gateway, Newt |
| `infrastructure/infisical` | Secrets | Vault, API |

### Webhook Automation Flow

```
Developer Push → Forgejo → Dagger Build → Push Image → Komodo Webhook → Deploy
```
