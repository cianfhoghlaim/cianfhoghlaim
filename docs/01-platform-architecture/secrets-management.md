---
title: "Secrets Management — Infisical, Locket & Three-Way Secret Contract"
domain: architecture
status: stable
description: "Complete secrets management covering the three-way contract (Infisical → .infisical.env → .env), Locket sidecar injection, mise hooks, provider configuration, and security model"
supersedes:
  - docs/bonneagar/SECRETS_MANAGEMENT_GUIDE.md
  - docs/bonneagar/infisical.md
  - docs/bonneagar/Configuration File.md
  - docs/bonneagar/integrating-1password-cli-connect-komodo-ansible-deployment.md
  - docs/bonneagar/integrating-1password-cli-komodo-ansible-deployment.md
  - docs/bonneagar/Get started with a 1Password Connect server _ 1Password Developer.md
  - docs/bonneagar/where-to-install-1password-cli-op.md
  - docs/bonneagar/SETUP.md
entities:
  - Infisical
  - Locket
  - SecretContract
  - DevBaile
  - MiseHooks
related_skills:
  - .agents/skills/stack-ops/SKILL.md
  - .agents/skills/komodo/SKILL.md
ccc_query_hints:
  - "how are secrets managed"
  - "three-way secret contract"
  - "locket sidecar injection"
  - "infisical vault configuration"
  - "how to add a new secret"
  - ".infisical.env template"
last_reviewed: 2026-06-06
truth: partial

---

# Secrets Management — Infisical, Locket & Three-Way Contract

Secrets management in the Cianfhoghlaim stack follows a strict **three-way contract**. Never hand-edit `.env` files.

## Three-Way Secret Contract

```
┌──────────────────────┐
│  Infisical Vault      │  ← Source of truth (dev-baile environment)
│  (arm1-oci)           │     Self-hosted on the control plane
└──────────┬───────────┘
           │ infisical://dev-baile/<folder>/<key>
           ↓
┌──────────────────────┐
│  .infisical.env       │  ← Template (committed to Git)
│  (URI references)     │     Only contains infisical:// references
└──────────┬───────────┘
           │ mise hook / locket inject
           ↓
┌──────────────────────┐
│  .env                 │  ← Hydrated runtime (gitignored)
│  (actual values)      │     Written by mise or Locket, never committed
└──────────────────────┘
```

### Two Hydration Paths

| Path | When | How |
|------|------|-----|
| **Local dev** | `cd` into project | `mise` directory hook → `infisical export` |
| **Production** | Container startup | Locket sidecar → `locket run --mode=watch` |

## Infisical — The Vault

### Overview

Infisical is the **self-hosted** secret management platform providing:

- Central vault for API keys, database passwords, configuration secrets
- REST API and CLI for secret retrieval
- Project-scoped environments (`dev-baile`, staging, production)
- Folder-based organization by service
- Machine identity authentication (Universal Auth)

### Folder Organization

```
dev-baile/
├── litellm/
│   ├── OPENAI_API_KEY
│   └── ANTHROPIC_API_KEY
├── dagster/
│   ├── DATABASE_URL
│   └── DAGSTER_SECRET
├── firecrawl/
│   └── FIRECRAWL_API_KEY
├── browserbase/
│   └── BROWSERBASE_API_KEY
├── pangolin/
│   ├── PANGOLIN_DOMAIN
│   └── WIREGUARD_KEYS
└── komodo/
    ├── KOMODO_PASSKEY
    └── PERIPHERY_PASSKEY
```

### Machine Identity Authentication

```bash
# Environment variables for automated access
INFISICAL_CLIENT_ID=<machine-identity-client-id>
INFISICAL_CLIENT_SECRET=<machine-identity-client-secret>
```

### CLI Usage

```bash
# Interactive login
infisical login

# Machine identity (Universal Auth)
infisical login --method=universal-auth \
  --client-id=<client-id> \
  --client-secret=<client-secret>

# Export all secrets for an environment
infisical export --env=dev-baile --format=dotenv > .env

# Get a specific secret
infisical secrets get OPENAI_API_KEY --env=dev-baile --folder=/litellm

# List all secrets
infisical secrets list --env=dev-baile

# Run command with secrets injected
infisical run --env=prod -- npm start

# Set secrets
infisical secrets set API_KEY=xxx DATABASE_URL=xxx
```

### SDK Usage

**Node.js:**

```typescript
import { InfisicalSDK } from '@infisical/sdk';

const client = new InfisicalSDK();
await client.auth().universalAuth.login({
  clientId: process.env.INFISICAL_CLIENT_ID,
  clientSecret: process.env.INFISICAL_CLIENT_SECRET
});

const secrets = await client.secrets().listSecrets({
  environment: "prod",
  projectId: process.env.INFISICAL_PROJECT_ID,
  secretPath: "/",
  expandSecretReferences: true
});
```

**Python:**

```python
from infisical_sdk import InfisicalSDKClient

client = InfisicalSDKClient(host="https://app.infisical.com")
client.auth.universal_auth.login(
    client_id=os.environ["INFISICAL_CLIENT_ID"],
    client_secret=os.environ["INFISICAL_CLIENT_SECRET"]
)

secrets = client.secrets.list_secrets(
    project_id=os.environ["INFISICAL_PROJECT_ID"],
    environment_slug="prod",
    secret_path="/"
)
```

### Secret Reference Syntax

```
infisical://<environment>/<folder>/<key>
```

Examples:

```
infisical://dev-baile/litellm/OPENAI_API_KEY
infisical://dev-baile/dagster/DATABASE_URL
infisical://dev-baile/firecrawl/FIRECRAWL_API_KEY
```

## Locket — The Sidecar

### Overview

Locket is a secret injection sidecar that resolves Infisical URI references at container runtime. It mounts a **tmpfs** volume with hydrated secrets — never touches disk.

### Key Features

- **Infisical provider**: `--provider=infisical` with machine identity credentials
- **Watch mode**: `--mode=watch` auto-reloads secrets when vault changes
- **Tmpfs secrets**: `/run/secrets/locket` is memory-only
- **Service dependency**: `depends_on: locket: condition: service_healthy`
- **Multiple providers**: Infisical, 1Password, 1Password Connect, Bitwarden

### Location

```
infrastructure/stacks/*/*/sidecar.yaml  # Production sidecar configs
```

### Locket Commands

```bash
# Start sidecar agent
locket run --provider=infisical \
    --infisical-client-id=${INFISICAL_CLIENT_ID} \
    --infisical-client-secret=${INFISICAL_CLIENT_SECRET} \
    --infisical-default-environment=dev-baile \
    --mode=watch \
    --map /templates:/run/secrets/locket

# Inject secrets from references
locket inject --provider infisical \
    --infisical-client-secret=file:/path/to/secret \
    --out /run/secrets/locket \
    --secret=/path/to/secrets.yaml

# Execute command with secrets injected
locket exec --provider=infisical \
    --infisical-client-id=${CLIENT_ID} \
    --infisical-client-secret=${CLIENT_SECRET} \
    -- ./my-app

# Health check
locket healthcheck
```

### Docker Compose Integration (Standard Sidecar Pattern)

```yaml
# sidecar.yaml — used in EVERY production stack
services:
  locket:
    image: ghcr.io/bpbradley/locket:latest
    restart: unless-stopped
    command:
      - "--provider=infisical"
      - "--mode=watch"
      - "--map=/templates:/run/secrets/locket"
    environment:
      - INFISICAL_CLIENT_ID=${INFISICAL_CLIENT_ID}
      - INFISICAL_CLIENT_SECRET=${INFISICAL_CLIENT_SECRET}
      - INFISICAL_DEFAULT_ENVIRONMENT=dev-baile
    volumes:
      - ./secrets.env:/templates/secrets.env:ro
      - type: tmpfs
        target: /run/secrets/locket
        tmpfs:
          size: 1M
    healthcheck:
      test: ["CMD", "locket", "healthcheck"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

  app:
    depends_on:
      locket:
        condition: service_healthy
    volumes:
      - type: tmpfs
        target: /run/secrets/locket
        tmpfs:
          size: 1M
    env_file:
      - /run/secrets/locket/secrets.env
```

### Watch Mode & Auto-Reload

| Mode | Description | Use Case |
|------|-------------|----------|
| `one-shot` | Materialize once and exit | CI/CD, init containers |
| `watch` | Watch for changes and reinject | Production sidecars (default) |
| `park` | Inject once, keep process alive | Health-check dependent services |

```bash
locket run --mode=watch --debounce=500ms
```

### Failure Policies

| Policy | Behavior |
|--------|----------|
| `error` | Abort process on failure |
| `passthrough` | Copy unmodified template to destination (default) |
| `ignore` | Skip failed secret, log warning |

## Template Files & Hydration

### `.infisical.env` Template (Committed to Git)

```bash
# .infisical.env — committed, only contains URI references
OPENAI_API_KEY=infisical://dev-baile/litellm/OPENAI_API_KEY
DATABASE_URL=infisical://dev-baile/dagster/DATABASE_URL
FIRECRAWL_API_KEY=infisical://dev-baile/firecrawl/FIRECRAWL_API_KEY
ANTHROPIC_API_KEY=infisical://dev-baile/litellm/ANTHROPIC_API_KEY
KOMODO_PASSKEY=infisical://dev-baile/komodo/KOMODO_PASSKEY
PANGOLIN_DOMAIN=infisical://dev-baile/pangolin/PANGOLIN_DOMAIN
```

### Vault Initialization

```bash
# Sync template → vault (creates/updates each secret)
bun run secrets:init
# or
mise run secrets:init
```

### Local Hydration (mise hook)

```toml
# mise.toml
[hooks]
enter = "infisical export --env=dev-baile --format=dotenv > .env"
```

On `cd` into the project directory, `.env` is automatically hydrated from Infisical.

### Manual Refresh

```bash
infisical export --env=dev-baile > .env
```

## Provider Configuration

### Infisical (Primary)

| Option | Env | Default |
|--------|-----|---------|
| `--infisical-client-secret` | `INFISICAL_CLIENT_SECRET` | — |
| `--infisical-client-id` | `INFISICAL_CLIENT_ID` | — |
| `--infisical-default-environment` | `INFISICAL_DEFAULT_ENVIRONMENT` | — |
| `--infisical-url` | `INFISICAL_URL` | `https://us.infisical.com` |
| `--infisical-default-path` | `INFISICAL_DEFAULT_PATH` | `/` |
| `--infisical-max-concurrent` | `INFISICAL_MAX_CONCURRENT` | `20` |

### 1Password (op)

| Option | Env | Description |
|--------|-----|-------------|
| `--op-token` | `OP_SERVICE_ACCOUNT_TOKEN` | Service Account Token |
| `--op-config-dir` | `OP_CONFIG_DIR` | Config directory path |

### 1Password Connect

| Option | Env | Description |
|--------|-----|-------------|
| `--connect-host` | `OP_CONNECT_HOST` | Connect Host URL |
| `--connect-token` | `OP_CONNECT_TOKEN` | Connect Token |

### Bitwarden Secrets Manager

| Option | Env | Description |
|--------|-----|-------------|
| `--bws-token` | `BWS_MACHINE_TOKEN` | Machine Token |
| `--bws-api-url` | `BWS_API_URL` | API URL |

## Security Model

### Principles

1. **Secrets never in Git** — Only URI references in `.infisical.env`
2. **Tmpfs only** — `/run/secrets/locket` is memory-only, never touches disk
3. **Least privilege** — Machine identities scoped to specific environments/folders
4. **File permissions** — `0600` for files, `0700` for directories
5. **No root** — Locket runs as non-root user

### File Permissions

```bash
--file-mode=0600  # Secret files (default)
--dir-mode=0700   # Secret directories (default)
--max-file-size=10M  # Reject templates larger than 10MB
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Secrets not materializing | Check `locket healthcheck` exit code |
| Permission denied | Verify `--file-owner` matches app user |
| Infisical auth failure | Verify `INFISICAL_CLIENT_ID` and `CLIENT_SECRET` |
| Template not found | Check `--map` source paths |
| Watch mode not reloading | Verify `--mode=watch` and `--debounce` settings |
| Container starts before secrets ready | Use `depends_on: locket: condition: service_healthy` |

### Debug Logging

```bash
--log-level=debug --log-format=text    # Debug
--log-level=info --log-format=json     # Production
--log-format=compose                   # Docker Compose provider
```

## Quick Reference

```bash
# Local development
bun run secrets:init                    # Sync template → vault
infisical export --env=dev-baile > .env # Manual hydration

# Production sidecar
locket run --provider=infisical --mode=watch \
    --map /templates:/run/secrets/locket

# One-shot injection
locket exec --provider=infisical -- ./my-app

# Health check
locket healthcheck

# Secret reference format
infisical://<environment>/<folder>/<key>
```

## Infisical Kubernetes Operator

For Kubernetes-native deployments:

```yaml
apiVersion: secrets.infisical.com/v1alpha1
kind: InfisicalSecret
metadata:
  name: app-secrets
spec:
  hostAPI: https://app.infisical.com/api
  resyncInterval: 60
  authentication:
    universalAuth:
      secretsScope:
        projectSlug: my-project
        envSlug: prod
        secretsPath: /
      credentialsRef:
        secretName: infisical-credentials
        secretNamespace: default
  managedSecretReference:
    secretName: app-secrets
    secretNamespace: default
```

```yaml
# Use in Deployment
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    metadata:
      annotations:
        secrets.infisical.com/auto-reload: "true"
    spec:
      containers:
        - envFrom:
            - secretRef:
                name: app-secrets
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Authenticate with Infisical
  run: |
    export INFISICAL_TOKEN=$(infisical login \
      --method=universal-auth \
      --client-id=${{ secrets.INFISICAL_CLIENT_ID }} \
      --client-secret=${{ secrets.INFISICAL_CLIENT_SECRET }} \
      --silent --plain)
    echo "INFISICAL_TOKEN=$INFISICAL_TOKEN" >> $GITHUB_ENV

- name: Deploy
  run: infisical run --env=prod -- npm run deploy
```

### Docker Compose (without Locket)

```yaml
services:
  web:
    environment:
      - INFISICAL_TOKEN=${INFISICAL_TOKEN}
    entrypoint: ["infisical", "run", "--env=prod", "--", "npm", "start"]
```
