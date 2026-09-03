---
name: komodo
description: Expert assistance for Komodo infrastructure management platform. Use when users need Docker container orchestration, GitOps workflows, build automation, or multi-server deployments.
---

# Komodo - Infrastructure Management Platform

**Version:** 2.2.0 | **Last Updated:** 2026-06-29

## Overview

Komodo is an open-source Docker infrastructure management platform:

- **Core/Periphery Architecture**: Central server with lightweight agents
- **GitOps**: Declarative infrastructure as code
- **Resource Types**: Stacks, Deployments, Builds, Procedures, Actions
- **Automation**: TypeScript actions, multi-stage procedures
- **Monitoring**: Built-in alerting and health checks

**Documentation**: https://komo.do/docs

## When to Use This Skill

Activate when users need:

- "Deploy Docker containers with Komodo"
- "Set up GitOps workflow"
- "Create deployment automation"
- "Manage multi-server infrastructure"
- "Configure CI/CD with Komodo"

## Core Concepts

### 1. Architecture

```
┌─────────────────────────────────────────────┐
│            Komodo Core                       │
│  (REST API, WebSocket, Web UI - port 9120)  │
└─────────────────┬───────────────────────────┘
                  │ Passkey Authentication
       ┌──────────┼──────────┐
       ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│Periphery │ │Periphery │ │Periphery │
│ Server 1 │ │ Server 2 │ │ Server 3 │
│  :8120   │ │  :8120   │ │  :8120   │
└──────────┘ └──────────┘ └──────────┘
```

### 2. Resource Types

| Resource | Purpose |
|----------|---------|
| **Server** | Connection to Periphery agent |
| **Stack** | Docker Compose project |
| **Deployment** | Single container deployment |
| **Build** | Docker image builds from Git |
| **Procedure** | Multi-stage orchestration |
| **Action** | TypeScript automation |
| **Resource Sync** | GitOps declarative infra |

### 3. Stack Configuration (TOML)

```toml
[[stack]]
name = "my-application"
description = "Production application stack"

[stack.config]
server = "main-server"
repo = "username/my-app"
git_account = "github-account"
branch = "main"
file_paths = ["docker-compose.yml"]

[stack.config.environment]
NODE_ENV = "production"
APP_VERSION = "${APP_VERSION}"
DB_PASSWORD = "${DB_PASSWORD}"

[[stack.config.labels]]
environment = "production"
app = "my-application"

[[stack.config.after]]
"database-stack"
```

### 4. Deployment Configuration

```toml
[[deployment]]
name = "api-service"
description = "API service deployment"

[deployment.config]
server = "main-server"
build = "api-build"
network = "host"

[deployment.config.environment]
PORT = "3000"
DB_HOST = "${DB_HOST}"

[[deployment.config.volumes]]
host = "/data/api"
container = "/app/data"

[deployment.config.restart]
policy = "unless-stopped"

[deployment.config.auto_update]
enabled = true
```

### 5. Build Configuration

```toml
[[build]]
name = "my-app-build"
description = "Build Docker image from Git"

[build.config]
repo = "username/my-app"
git_account = "github-account"
branch = "main"
builder = "main-server-builder"
docker_account = "dockerhub-account"

[build.config.build_args]
NODE_VERSION = "20"

[build.config.image]
name = "username/my-app"
tag = "latest"
```

### 6. Procedure (Multi-Stage Automation)

```toml
[[procedure]]
name = "deploy-full-stack"
description = "Deploy all services"

# Stage 1: Pull repos (parallel)
[[procedure.config.stages]]
[[procedure.config.stages.executions]]
operation = "PullRepo"
params = { repo = "frontend-repo" }

[[procedure.config.stages.executions]]
operation = "PullRepo"
params = { repo = "backend-repo" }

# Stage 2: Build images (parallel, waits for Stage 1)
[[procedure.config.stages]]
[[procedure.config.stages.executions]]
operation = "RunBuild"
params = { build = "frontend-build" }

[[procedure.config.stages.executions]]
operation = "RunBuild"
params = { build = "backend-build" }

# Stage 3: Deploy stacks
[[procedure.config.stages]]
[[procedure.config.stages.executions]]
operation = "DeployStack"
params = { stack = "frontend-stack" }

# Stage 4: Cleanup
[[procedure.config.stages]]
[[procedure.config.stages.executions]]
operation = "PruneSystem"
params = { server = "main-server" }
```

### 7. Action (TypeScript Automation)

```typescript
// Action: sync-environment-branches
const targetBranch = ARGS.branch || "main"
const dryRun = ARGS.dryRun || false

// Pre-initialized 'komodo' client available
const stacks = await komodo.read("ListStacks", {})

const updates = []

for (const stack of stacks) {
  const config = await komodo.read("GetStack", { stack: stack.name })

  if (config.config.repo && config.config.branch !== targetBranch) {
    updates.push({ name: stack.name, oldBranch: config.config.branch })

    if (!dryRun) {
      await komodo.write("UpdateStack", {
        name: stack.name,
        config: { ...config.config, branch: targetBranch }
      })
      await komodo.execute("DeployStack", { stack: stack.name })
    }
  }
}

return { message: dryRun ? "Dry run" : "Completed", updates }
```

### 8. Resource Sync (GitOps)

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
git_provider = "github"
```

### 9. TypeScript SDK Usage

```typescript
import { KomodoClient } from 'komodo_client'

const client = KomodoClient({
  url: "https://komodo.example.com",
  type: "api-key",
  params: {
    key: "your-api-key",
    secret: "your-api-secret"
  }
})

// Read operations
const stacks = await client.read("ListStacks", {})
const deployment = await client.read("GetDeployment", {
  deployment: "my-app"
})

// Execute operations
await client.execute("DeployStack", { stack: "frontend" })
await client.execute("RunBuild", { build: "my-app-build" })

// Write operations
await client.write("UpdateStack", {
  name: "frontend",
  config: { branch: "develop" }
})
```

### 10. CLI Commands

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

## Environment Configuration

### Core (.env)
```bash
KOMODO_PASSKEY=secure_random_passkey
KOMODO_HOST=https://komodo.example.com
KOMODO_TITLE="Production Komodo"

# Initial setup
KOMODO_INIT_ADMIN_USERNAME=admin
KOMODO_INIT_ADMIN_PASSWORD=secure_password
KOMODO_FIRST_SERVER=http://192.168.1.10:8120

# OAuth (optional)
KOMODO_GITHUB_OAUTH_ENABLED=true
KOMODO_GITHUB_OAUTH_ID=client_id
KOMODO_GITHUB_OAUTH_SECRET=client_secret
```

### Periphery (periphery.toml)
```toml
passkey = "matches_komodo_passkey"
port = 8120

[directories]
repo_dir = "/opt/komodo/repos"
stack_dir = "/opt/komodo/stacks"

[security]
allowed_ips = ["192.168.1.0/24"]
```

### Secrets Management (core.toml)
```toml
[secrets]
DB_PASSWORD = "secret_database_password"
API_KEY = "secret_api_key"

[variables]
APP_VERSION = "1.0.0"
ENVIRONMENT = "production"
```

## Best Practices

1. **Use Git-based Stacks**: Version control all compose files
2. **Variable Interpolation**: Use `${VARIABLE}` for secrets
3. **Managed Mode**: Let Komodo own resource state
4. **Stage Grouping**: Parallel operations in same stage
5. **Dry-run Actions**: Test with `dryRun=true`
6. **Webhook Secrets**: Configure KOMODO_WEBHOOK_SECRET
7. **IP Whitelisting**: Restrict Periphery access

## Troubleshooting

### Stack Fails to Deploy
1. Check Stack logs in Komodo UI
2. Verify Server connection
3. Check compose syntax: `docker compose config`
4. Verify environment variables

### Build Fails
1. Check Build logs
2. Verify Dockerfile exists
3. Test locally: `docker build -t test .`
4. Check registry credentials

### Periphery Unreachable
```bash
# Check service
systemctl status komodo-periphery

# Check connectivity
curl http://periphery-host:8120/health

# Check logs
journalctl -u komodo-periphery -f
```

### Webhook Not Triggering
1. Verify webhook URL
2. Check secret matches
3. Review Git provider delivery logs
4. Verify content-type: application/json

## Resources

- **Website**: https://komo.do
- **Documentation**: https://komo.do/docs
- **GitHub**: https://github.com/mbecker20/komodo
- **Discord**: discord.gg/DRqE8Fvg5c

## KCG integration (canonical)

The Cianfhoghlaim platform runs **88 stacks** across 5
categories (storage, engineering, ML, infrastructure, tools),
all managed via a single Komodo instance. The KCG patterns
that differ from the upstream docs above:

### 5-stage deploy procedure

```bash
# 1. Add the stack to mise.toml (optional — for mise-managed stacks)
echo '[env._.path]' >> mise.toml
echo '_.path = ["./bonneagar/stacks/<surface>/scripts"]' >> mise.toml

# 2. Register the stack in komodo
komodo resource sync --stack infrastructure/stacks/<surface>/<name>

# 3. Deploy
komodo deploy --stack <name> --env production

# 4. Wire Locket sidecar (see secrets-management skill)
komodo sidecar attach <name> --image ghcr.io/cianfhoghlaim/locket:latest

# 5. Wire Pangolin private resource (see pangolin skill)
komodo pangolin attach <name> --full-domain <name>.cianfhoghlaim.ie
```

### `mise run komodo:sync` integration

```toml
# mise.toml
[env._.path]
_.path = ["./scripts", "./infrastructure/stacks"]

[tasks."komodo:sync"]
run = "bun run scripts/komodo-sync.ts"
```

The `komodo:sync` task walks all 88 stacks, compares
compose.yaml + sidecar.yaml + secrets.env + pangolin.yaml
against the live Komodo state, and emits a diff.

### Resource Sync paths

| Stack | Live path | Resource Sync source |
|:--|:--|:--|
| `dagster` | `digraph-compose.cianfhoghlaim.ie` | `infrastructure/stacks/dagster` |
| `cognee` | `cognee.cianfhoghlaim.ie` | `infrastructure/stacks/cognee` |
| `n8n` | `n8n.cianfhoghlaim.ie` | `infrastructure/stacks/n8n` |

### KCG custom actions

- `stack:up <name>` — bring up a Compose stack
- `stack:down <name>` — bring down a Compose stack
- `stack:rebuild <name>` — rebuild and restart
- `stack:logs <name> [service]` — tail logs
- `stack:exec <name> <service> <cmd>` — exec into a service
- `mise:install` — hydrate the polyglot toolchain
- `infisical:export <name>` — export secrets to env

### Related skills

- `.agents/skills/stack-ops/SKILL.md` — the 6-file
  GOLD_STANDARD stack pattern that Komodo deploys
- `.agents/skills/secrets-management/SKILL.md` — the
  Locket sidecar that Komodo wires
- `.agents/skills/pangolin/SKILL.md` — the private
  resource topology that Komodo configures
- `.agents/skills/kubernetes/SKILL.md` — the scale-out
  trigger (K8s for multi-host)
- `.agents/skills/monorepo/SKILL.md` — bun + uv + turbo
