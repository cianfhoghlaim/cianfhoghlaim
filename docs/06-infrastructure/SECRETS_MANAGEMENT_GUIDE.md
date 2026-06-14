---
truth: partial
---

# Secrets Management — Locket + Infisical Complete Guide

> **Merged From:** `docs/bonneagar/locket/` (23 files) + `docs/bonneagar/infisical/` (7 files)
> Consolidated: locket.md, KCG_SUMMARY.md, CONFIGURATION.md, README.md, compose.md, run.md, exec.md, healthcheck.md, locket/docs/inject.md, locket/docs/volume.md, locket/docs/compose.md, locket/docs/CONFIGURATION.md, locket/docs/exec.md, locket/docs/healthcheck.md, locket/docs/providers/*.md, infisical.md, KCG_SUMMARY.md, SKILL_CONTEXT.md, DESIGN.md, SECURITY.md, CLAUDE.md, README.md, CODE_OF_CONDUCT.md, and root-level infisical.md.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture: Three-Way Secret Contract](#architecture-three-way-secret-contract)
3. [Infisical — The Vault](#infisical--the-vault)
4. [Locket — The Sidecar](#locket--the-sidecar)
5. [Secret Reference Syntax](#secret-reference-syntax)
6. [Locket Commands](#locket-commands)
7. [Provider Configuration](#provider-configuration)
8. [Docker Compose Integration](#docker-compose-integration)
9. [Template Files & Hydration](#template-files--hydration)
10. [Watch Mode & Auto-Reload](#watch-mode--auto-reload)
11. [Health Checks](#health-checks)
12. [Exec Mode (Process Injection)](#exec-mode-process-injection)
13. [mise Directory Hooks](#mise-directory-hooks)
14. [Security Model](#security-model)
15. [Troubleshooting](#troubleshooting)

---

## Overview

Secrets management in the Cianfhoghlaim stack follows a strict three-way contract:

1. **Infisical** — Source of truth vault (self-hosted on arm1-oci)
2. **`.infisical.env`** — Template file with URI references (committed to Git)
3. **`.env`** — Hydrated runtime file (gitignored, written by mise/Locket)

**Never hand-edit `.env`.** All secret changes go through Infisical → template → hydration.

---

## Architecture: Three-Way Secret Contract

```
┌──────────────────────┐
│  Infisical Vault      │  ← Source of truth (dev-baile environment)
│  (arm1-oci)           │
└──────────┬───────────┘
           │ infisical://dev-baile/<folder>/<key>
           ↓
┌──────────────────────┐
│  .infisical.env       │  ← Template (committed to Git)
│  (URI references)     │
└──────────┬───────────┘
           │ mise hook / locket inject
           ↓
┌──────────────────────┐
│  .env                 │  ← Hydrated runtime (gitignored)
│  (actual values)      │
└──────────────────────┘
```

### Two Hydration Paths

| Path | When | How |
|------|------|-----|
| **Local dev** | `cd` into project | `mise` directory hook → `infisical export` |
| **Production** | Container startup | Locket sidecar → `locket inject --mode=watch` |

---

## Infisical — The Vault

### Overview

Infisical is an open-source secret management platform providing:
- Central vault for API keys, database passwords, configuration secrets
- REST API and CLI for secret retrieval
- Project-scoped environments (dev-baile, staging, production)
- Folder-based organization by service

### In the Cianfhoghlaim Stack

The `dev-baile` environment is the single source of truth for all project secrets.

### Machine Identity Authentication

```bash
# Environment variables for automated access
INFISICAL_CLIENT_ID=<machine-identity-client-id>
INFISICAL_CLIENT_SECRET=<machine-identity-client-secret>
```

### Folder Organization

Secrets organized by service:
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
└── ...
```

### CLI Usage

```bash
# Export all secrets for an environment
infisical export --env=dev-baile --format=dotenv > .env

# Get a specific secret
infisical secrets get OPENAI_API_KEY --env=dev-baile --folder=/litellm

# List all secrets
infisical secrets list --env=dev-baile
```

---

## Locket — The Sidecar

### Overview

Locket is a secret injection sidecar that resolves Infisical URI references at container runtime. It mounts a tmpfs volume with hydrated secrets, allowing containers to access credentials without hardcoded `.env` files.

### Key Features

- **Infisical provider**: `--provider=infisical` with machine identity credentials
- **Watch mode**: `--mode=watch` auto-reloads secrets when vault changes
- **Tmpfs secrets**: `/run/secrets/locket` is memory-only — never touches disk
- **Service dependency**: `depends_on: locket: condition: service_healthy`
- **Multiple providers**: 1Password, Bitwarden, 1Password Connect, Infisical

### Location

```
infrastructure/stacks/*/*/sidecar.yaml  # Production sidecar configs
```

---

## Secret Reference Syntax

### Infisical URI Format

```
infisical://<environment>/<folder>/<key>
```

**Examples:**
```
infisical://dev-baile/litellm/OPENAI_API_KEY
infisical://dev-baile/dagster/DATABASE_URL
infisical://dev-baile/firecrawl/FIRECRAWL_API_KEY
```

### Template Syntax (Jinja-like)

```
{{ infisical:///<key> }}
{{ op://vault/item/field }}           # 1Password
{{ bws://project/secret/key }}        # Bitwarden
```

---

## Locket Commands

### `locket run`

Start the secret sidecar agent. Collects and materializes all secrets.

```bash
locket run --provider=infisical \
    --infisical-client-id=${INFISICAL_CLIENT_ID} \
    --infisical-client-secret=${INFISICAL_CLIENT_SECRET} \
    --infisical-default-environment=dev-baile \
    --mode=watch \
    --map /templates:/run/secrets/locket
```

### `locket inject`

Inject secrets from references into files and directories.

```bash
locket inject --provider infisical \
    --infisical-client-secret=file:/path/to/secret \
    --out /run/secrets/locket \
    --secret=/path/to/secrets.yaml \
    --secret=auth_key=@key.pem \
    --map ./tpl:/run/secrets/locket/mapped
```

### `locket exec`

Execute a command with secrets injected into the process environment.

```bash
locket exec --provider=infisical \
    --infisical-client-id=${CLIENT_ID} \
    --infisical-client-secret=${CLIENT_SECRET} \
    -- ./my-app --config /run/secrets/locket/config.yaml
```

### `locket healthcheck`

Check health of the sidecar agent by verifying materialized secrets.

```bash
locket healthcheck
# Exit 0 = all secrets materialized
# Exit non-zero = missing or failed secrets
```

### `locket compose`

Docker Compose provider API for integration with compose stacks.

---

## Provider Configuration

### Infisical (Primary)

| Option | Env | Default | Description |
|--------|-----|---------|-------------|
| `--infisical-client-secret` | `INFISICAL_CLIENT_SECRET` | — | Universal Auth client secret |
| `--infisical-client-id` | `INFISICAL_CLIENT_ID` | — | Universal Auth client ID |
| `--infisical-default-environment` | `INFISICAL_DEFAULT_ENVIRONMENT` | — | Default environment slug |
| `--infisical-default-project-id` | `INFISICAL_DEFAULT_PROJECT_ID` | — | Default project ID |
| `--infisical-url` | `INFISICAL_URL` | `https://us.infisical.com` | Infisical instance URL |
| `--infisical-default-path` | `INFISICAL_DEFAULT_PATH` | `/` | Default secret path |
| `--infisical-max-concurrent` | `INFISICAL_MAX_CONCURRENT` | `20` | Max concurrent API requests |

### 1Password (op)

| Option | Env | Description |
|--------|-----|-------------|
| `--op-token` | `OP_SERVICE_ACCOUNT_TOKEN` | Service Account Token |
| `--op-config-dir` | `OP_CONFIG_DIR` | Config directory path |

### 1Password Connect

| Option | Env | Description |
|--------|-----|-------------|
| `--connect-host` | `OP_CONNECT_HOST` | Connect Host HTTP(S) URL |
| `--connect-token` | `OP_CONNECT_TOKEN` | Connect Token |
| `--connect-max-concurrent` | `OP_CONNECT_MAX_CONCURRENT` | Max concurrent requests (default: 20) |

### Bitwarden Secrets Manager

| Option | Env | Description |
|--------|-----|-------------|
| `--bws-token` | `BWS_MACHINE_TOKEN` | Machine Token |
| `--bws-api-url` | `BWS_API_URL` | API URL (default: `https://api.bitwarden.com`) |
| `--bws-identity-url` | `BWS_IDENTITY_URL` | Identity URL |
| `--bws-max-concurrent` | `BWS_MAX_CONCURRENT` | Max concurrent (default: 20) |

---

## Docker Compose Integration

### Standard Sidecar Pattern

Every production stack uses this pattern:

```yaml
# sidecar.yaml
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
    # Mount the same tmpfs or use env_file
    env_file:
      - /run/secrets/locket/secrets.env
```

### Shared Tmpfs Volume

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
```

---

## Template Files & Hydration

### `.infisical.env` Template (Committed)

```bash
# .infisical.env — committed to Git
OPENAI_API_KEY=infisical://dev-baile/litellm/OPENAI_API_KEY
DATABASE_URL=infisical://dev-baile/dagster/DATABASE_URL
FIRECRAWL_API_KEY=infisical://dev-baile/firecrawl/FIRECRAWL_API_KEY
```

### Vault Initialization

```bash
# Sync template to vault
bun run secrets:init
# or
mise run secrets:init
```

This reads `.infisical.env` and creates/updates each secret in the Infisical vault.

### Local Hydration (mise hook)

```bash
# Automatic on cd into project directory
# mise hook runs: infisical export --env=dev-baile > .env
```

---

## Watch Mode & Auto-Reload

### Configuration

```bash
locket run --mode=watch --debounce=500ms
```

### Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `one-shot` | Materialize once and exit | CI/CD, init containers |
| `watch` | Watch for changes and reinject | Production sidecars (Docker default) |
| `park` | Inject once, keep process alive | Health-check dependent services |

### Debounce

Events within the debounce window are coalesced to avoid overwhelming the secrets manager:

```bash
--debounce=500ms  # Default
--debounce=2s     # For noisy environments
```

---

## Health Checks

### Sidecar Health

```yaml
healthcheck:
  test: ["CMD", "locket", "healthcheck"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 10s
```

### Status File

```bash
--status-file=/dev/shm/locket/ready
```

The status file is written when all secrets are materialized. Docker default: `/dev/shm/locket/ready`.

### Failure Policies

| Policy | Behavior |
|--------|----------|
| `error` | Abort process on failure |
| `passthrough` | Copy unmodified template to destination (default) |
| `ignore` | Skip failed secret, log warning |

---

## Exec Mode (Process Injection)

Inject secrets directly into a process environment without writing files:

```bash
locket exec --provider=infisical \
    --infisical-client-id=${CLIENT_ID} \
    --infisical-client-secret=${CLIENT_SECRET} \
    --secret DB_PASS={{infisical:///database/password}} \
    -- python my_script.py
```

---

## mise Directory Hooks

### Automatic Hydration

When you `cd` into a project directory, `mise` hooks automatically hydrate `.env`:

```toml
# mise.toml
[hooks]
enter = "infisical export --env=dev-baile --format=dotenv > .env"
```

### Manual Refresh

```bash
mise run secrets:init     # Sync template → vault
infisical export --env=dev-baile > .env  # Manual hydration
```

---

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
```

### Max File Size

```bash
--max-file-size=10M  # Reject templates larger than 10MB (default)
```

---

## Troubleshooting

### Common Issues

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
--log-level=debug --log-format=text
```

### JSON Logging (Production)

```bash
--log-level=info --log-format=json
```

### Docker Compose Logging

```bash
--log-format=compose  # Special format for Docker Compose provider
```

---

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
