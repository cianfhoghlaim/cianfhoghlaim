# Locket Integration Modes Comparison

## Overview

Locket supports three integration patterns, each with different trade-offs for modularity, complexity, and flexibility.

---

## Mode Comparison

| Aspect | Sidecar (`locket run`) | Exec (`locket exec`) | Provider (`locket compose`) |
|--------|------------------------|----------------------|----------------------------|
| **Compose file changes** | Heavy (add service, volumes, depends_on) | None | Minimal (provider block) |
| **Works without Locket** | No | Yes | No |
| **Hot-reload secrets** | Yes (watch mode) | Yes (--watch flag) | No |
| **Healthcheck support** | Yes | No (process-level) | No |
| **Container isolation** | Secrets in tmpfs volume | Secrets in env vars | Secrets in env vars |
| **Komodo integration** | Native (stack deploys sidecar) | Requires wrapper script | Plugin installation |
| **Development flexibility** | Low | High | Medium |
| **Production security** | High (tmpfs, isolated) | Medium (env inheritance) | Medium |

---

## Mode 1: Sidecar (`locket run`) - Current Implementation

**How it works:**
- Locket runs as a container in the compose stack
- Injects secrets into a shared tmpfs volume
- Services mount the volume and read secrets from files

```yaml
services:
  locket:
    image: ghcr.io/bpbradley/locket:connect
    command: ["--map=/templates:/run/secrets/locket", "--mode=park"]
    volumes:
      - ./templates/langfuse:/templates:ro
      - langfuse-secrets:/run/secrets/locket
    healthcheck:
      test: ["CMD", "/locket", "healthcheck"]

  postgres:
    depends_on:
      locket:
        condition: service_healthy
    env_file:
      - /run/secrets/locket/secrets.env
    volumes:
      - langfuse-secrets:/run/secrets/locket:ro
```

**Pros:**
- Secrets never in environment variables (more secure)
- Native healthcheck ensures secrets ready before services start
- Works with Komodo stack deployment

**Cons:**
- Compose file heavily modified
- Can't run stack without Locket/Infisical
- Every service needs volume mounts and depends_on

---

## Mode 2: Exec (`locket exec`) - Recommended for Modularity

**How it works:**
- Locket wraps the `docker compose` command
- Resolves secrets and injects them as environment variables
- Compose file stays standard, using `${VAR}` syntax

```bash
# With Locket (production)
locket exec --provider infisical \
  --connect.host http://132.145.27.89:8080 \
  --connect.token-file ./infisical_secret \
  --env-file ./templates/langfuse/secrets.env \
  -- docker compose -f langfuse.compose.yaml up -d

# Without Locket (development)
source .env.local  # Plain text dev secrets
docker compose -f langfuse.compose.yaml up -d
```

**Compose file stays standard:**
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
```

**Pros:**
- Compose files work with or without Locket
- Easy local development with `.env.local`
- No compose file modifications needed
- Can switch between dev/prod secrets easily

**Cons:**
- Secrets exposed in container environment variables
- No native Docker healthcheck for secrets
- Requires wrapper script for deployment

---

## Mode 3: Provider (`locket compose`) - Docker Plugin

**How it works:**
- Locket installs as a Docker Compose plugin
- Compose file declares a provider service block
- Plugin intercepts `docker compose up` and injects secrets

```yaml
services:
  locket:
    provider:
      type: locket
      options:
        provider: infisical
        connect.host: ${INFISICAL_HOST}
        connect.token-file: /etc/locket/token
        env_file: ./templates/langfuse/secrets.env

  postgres:
    depends_on:
      - locket
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

**Pros:**
- Cleaner than sidecar (no extra container running)
- Compose file remains mostly standard

**Cons:**
- Requires plugin installation on host
- Less flexible than exec mode
- Still modifies compose file

---

## Recommended Approach: Dual-Mode Templates

Create compose files that work in both modes:

### 1. Standard Compose File (no Locket dependencies)

```yaml
# langfuse.compose.yaml - Works standalone with .env or with locket exec

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-devpassword}
      POSTGRES_DB: ${POSTGRES_DB:-langfuse}
    # ... rest of config
```

### 2. Secret Template File

```env
# templates/langfuse/secrets.env
POSTGRES_USER={{ infisical://taisce-secrets/databases/langfuse-postgres/username }}
POSTGRES_PASSWORD={{ infisical://taisce-secrets/databases/langfuse-postgres/password }}
POSTGRES_DB={{ infisical://taisce-secrets/databases/langfuse-postgres/database }}
# ... other secrets
```

### 3. Local Development File

```env
# .env.local (git-ignored, plain text for dev)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=devpassword
POSTGRES_DB=langfuse
# ... other dev values
```

### 4. Wrapper Scripts

```bash
# scripts/stack-up.sh
#!/bin/bash
STACK=$1
shift

if [ -n "$LOCKET_ENABLED" ]; then
  locket exec --provider infisical \
    --connect.host "${INFISICAL_HOST:-http://132.145.27.89:8080}" \
    --connect.token-file "${INFISICAL_TOKEN_FILE:-./infisical_secret}" \
    --env-file "./templates/${STACK}/secrets.env" \
    -- docker compose -f "${STACK}.compose.yaml" "$@"
else
  # Use local env file for development
  docker compose --env-file .env.local -f "${STACK}.compose.yaml" "$@"
fi
```

**Usage:**
```bash
# Development (no Locket)
./scripts/stack-up.sh langfuse up -d

# Production (with Locket)
LOCKET_ENABLED=1 ./scripts/stack-up.sh langfuse up -d

# Or via taisce-deploy.ts for Komodo
bun run taisce-deploy.ts deploy langfuse
```

---

## Implementation Comparison

### Current (Sidecar) - High Coupling

```
┌─────────────────────────────────────────────┐
│ langfuse.compose.yaml                       │
│  ├── locket service (required)              │
│  ├── postgres (depends_on: locket)          │
│  ├── clickhouse (depends_on: locket)        │
│  └── ... all services modified              │
└─────────────────────────────────────────────┘
         │
         ▼ Can only run with Locket
```

### Proposed (Exec) - Low Coupling

```
┌─────────────────────────────────────────────┐
│ langfuse.compose.yaml (standard)            │
│  ├── postgres                               │
│  ├── clickhouse                             │
│  └── ... unmodified services                │
└─────────────────────────────────────────────┘
         │
         ├──▶ Direct: docker compose up (uses .env.local)
         │
         └──▶ Wrapped: locket exec ... -- docker compose up
```

---

## Recommendation

**For taisce stacks:**

1. **Revert compose files** to standard format (no sidecar)
2. **Keep secret templates** as-is (they work with exec mode)
3. **Create wrapper script** for locket exec deployment
4. **Update taisce-deploy.ts** to use exec mode via SSH

**Benefits:**
- Stacks work locally without Infisical
- Same compose files for dev and prod
- Easier testing and debugging
- Komodo can still deploy via SSH commands

---

## Migration Path

### Step 1: Create modular compose file

Remove Locket sidecar, use standard env vars with defaults:

```yaml
services:
  postgres:
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-devpassword}
```

### Step 2: Keep templates for production secrets

```env
# templates/langfuse/secrets.env (unchanged)
POSTGRES_USER={{ infisical://taisce-secrets/... }}
```

### Step 3: Create local dev env

```env
# .env.local (plain text, git-ignored)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=localdev
```

### Step 4: Deploy with locket exec

```bash
# Via SSH to arm1.oci
ssh ubuntu@132.145.27.89 << 'EOF'
cd /opt/taisce
locket exec --provider infisical \
  --connect.token-file /etc/locket/infisical_secret \
  --env-file ./templates/langfuse/secrets.env \
  -- docker compose -f langfuse.compose.yaml up -d
EOF
```
