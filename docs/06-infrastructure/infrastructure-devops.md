---
truth: partial
merged_from:
  - docs/06-infrastructure/DECISION_MATRICES.md
merged_from:
  - docs/06-infrastructure/ARCHITECTURE.md
---

# Infrastructure & DevOps

Comprehensive guide to container-first architecture using Dagger CI/CD, Komodo deployment orchestration, Pangolin zero-trust networking, and 1Password secrets management.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Core Stack Components](#2-core-stack-components)
3. [CI/CD with Dagger](#3-cicd-with-dagger)
4. [Deployment with Komodo](#4-deployment-with-komodo)
5. [Zero-Trust Networking with Pangolin](#5-zero-trust-networking-with-pangolin)
6. [Secrets Management](#6-secrets-management)
7. [Infrastructure as Code](#7-infrastructure-as-code)
8. [LLM Gateway](#8-llm-gateway)
9. [Decision Matrices](#9-decision-matrices)
10. [Implementation Guide](#10-implementation-guide)

---

## 1. Architecture Overview

### 1.1 Key Principles

1. **Container-First**: All services run in containers for consistency and portability
2. **Secrets Never in Git**: All sensitive data managed through 1Password vaults
3. **Zero-Trust Networking**: Services accessible only through authenticated tunnels
4. **Infrastructure as Code**: All infrastructure defined in code and version controlled
5. **Modular Pipelines**: Build, test, and deploy steps organized as reusable Dagger modules

### 1.2 Technology Stack

| Category | Tool | Purpose |
|----------|------|---------|
| **Git Hosting** | Forgejo | Self-hosted Git with Actions |
| **CI/CD** | Dagger | Programmable pipelines in code |
| **Deployment** | Komodo | Docker Compose orchestration |
| **Networking** | Pangolin | Zero-trust tunnel access |
| **Secrets** | 1Password | Vault-based secrets management |
| **IaC** | Pulumi | Cloud resource provisioning |
| **Config** | Ansible | Server configuration |
| **Serverless** | Cloudflare | Workers, D1, R2 |

### 1.3 End-to-End Flow

```
Developer Push → Forgejo Actions → Dagger Pipeline → Build Images
                                  ↓
                         Inject 1Password Secrets
                                  ↓
                         Test with Docker Compose
                                  ↓
                    Publish to Forgejo Registry
                                  ↓
              Deploy via Komodo TypeScript SDK
                                  ↓
        Pangolin Newt Auto-registers Services
                                  ↓
              Production Deployment
```

---

## 2. Core Stack Components

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Developer Workstation                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Local Development                                               │   │
│  │  - dagger call build                                            │   │
│  │  - docker compose up                                            │   │
│  │  - op run -- command (1Password CLI)                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ git push
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Forgejo + Actions                             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────────┐ │
│  │  Git Server  │→→│ Actions      │→→│ Dagger Pipeline               │ │
│  │              │  │ Runner       │  │ - Build images                │ │
│  │  Registry    │←←│              │←←│ - Run tests                   │ │
│  └──────────────┘  └──────────────┘  │ - Push to registry            │ │
│                                       └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Komodo SDK deploy
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Production Server                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Komodo Periphery Agent                                          │  │
│  │  - Receives deployment commands                                  │  │
│  │  - Manages Docker Compose stacks                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Pangolin Newt                                                   │  │
│  │  - WireGuard tunnel to Gerbil                                    │  │
│  │  - Auto-registers services                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Application Containers                                          │  │
│  │  - Web apps, APIs, databases                                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. CI/CD with Dagger

### 3.1 Why Dagger Over YAML

| Limitation of YAML | Dagger Solution |
|--------------------|-----------------|
| Different locally vs CI | Same code everywhere |
| No real programming | TypeScript/Python/Go |
| Hard to test | Unit tests on pipelines |
| Copy-paste reuse | Module imports |

### 3.2 Module Structure

```
.dagger/
├── src/
│   ├── index.ts              # Main entry point
│   ├── build.ts              # Build functions
│   ├── test.ts               # Test functions
│   ├── deploy.ts             # Deploy functions
│   └── secrets.ts            # 1Password integration
├── dagger.json               # Module configuration
└── package.json
```

### 3.3 Pipeline Implementation

```typescript
// .dagger/src/index.ts
import { dag, Container, Directory, Secret } from "@dagger.io/dagger"

export async function build(src: Directory): Promise<Container> {
  return dag
    .container()
    .from("node:20-alpine")
    .withDirectory("/app", src)
    .withWorkdir("/app")
    .withExec(["npm", "install"])
    .withExec(["npm", "run", "build"])
}

export async function test(src: Directory): Promise<string> {
  const container = await build(src)
  return container
    .withExec(["npm", "test"])
    .stdout()
}

export async function publish(container: Container, registry: string): Promise<string> {
  return container.publish(`${registry}/my-app:latest`)
}

export async function deploy(imageRef: string): Promise<void> {
  // Call Komodo SDK
  const komodo = dag.komodo()
  await komodo.deployStack({
    name: "my-app",
    image: imageRef,
    server: "production-01"
  })
}
```

### 3.4 Secrets Integration

```typescript
// .dagger/src/secrets.ts
import { dag, Secret } from "@dagger.io/dagger"
import { execSync } from "child_process"

export function getOnePasswordSecret(ref: string): Secret {
  const value = execSync(`op read ${ref}`).toString().trim()
  return dag.setSecret(ref, value)
}

export async function withSecrets(container: Container): Promise<Container> {
  const dbUrl = getOnePasswordSecret("op://vault/database/url")
  const apiKey = getOnePasswordSecret("op://vault/api/key")

  return container
    .withSecretVariable("DATABASE_URL", dbUrl)
    .withSecretVariable("API_KEY", apiKey)
}
```

### 3.5 Forgejo Actions Workflow

```yaml
# .forgejo/workflows/ci.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Dagger
        run: |
          curl -fsSL https://dl.dagger.io/dagger/install.sh | sh
          sudo mv bin/dagger /usr/local/bin/

      - name: Run Pipeline
        run: |
          dagger call build --src=.
          dagger call test --src=.
          dagger call publish
          dagger call deploy
        env:
          OP_SERVICE_ACCOUNT_TOKEN: ${{ secrets.OP_TOKEN }}
          KOMODO_API_KEY: ${{ secrets.KOMODO_KEY }}
```

---

## 4. Deployment with Komodo

### 4.1 Architecture

```
┌─────────────────────────────────────────────────┐
│              Komodo Core                        │
│  ┌──────────────────────────────────────────┐   │
│  │  API Server                              │   │
│  │  - REST API for deployments              │   │
│  │  - WebSocket for real-time updates       │   │
│  │  - Stack configuration storage           │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
          │                      │
          ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐
│ Periphery Agent     │  │ Periphery Agent     │
│ (Server 1)          │  │ (Server 2)          │
│ - Docker daemon     │  │ - Docker daemon     │
│ - Compose runtime   │  │ - Compose runtime   │
└─────────────────────┘  └─────────────────────┘
```

### 4.2 TypeScript SDK Usage

```typescript
import { KomodoClient } from "@komodo/client"

const client = new KomodoClient({
  url: "https://komodo.example.com",
  apiKey: process.env.KOMODO_API_KEY
})

// Deploy a stack
await client.stacks.deploy({
  name: "my-app",
  server: "production-01",
  composePath: "./docker-compose.yml",
  environment: {
    TAG: "v1.2.3"
  }
})

// Check deployment status
const status = await client.stacks.status("my-app")
console.log(status.health)
```

### 4.3 Stack Configuration

```yaml
# docker-compose.yml for Komodo deployment
version: "3.8"

services:
  app:
    image: registry.example.com/my-app:${TAG:-latest}
    environment:
      - DATABASE_URL=op://vault/database/url
    labels:
      - "pangolin.enable=true"
      - "pangolin.domain=app.example.com"
    restart: always

  database:
    image: postgres:16
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=op://vault/database/password
    labels:
      - "pangolin.enable=false"  # Private only

volumes:
  db_data:
```

---

## 5. Zero-Trust Networking with Pangolin

### 5.1 Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Gerbil** | Cloud/Central | WireGuard tunnel server |
| **Newt** | Each server | Site connector |
| **Olm** | Client devices | VPN client |

### 5.2 Access Patterns

**Public Access (Internet-facing):**
```yaml
# pangolin-config.yaml
resources:
  - name: web-app
    type: http
    target: http://app:3000
    access: public
    domain: app.example.com
```

**Private Access (VPN-only):**
```yaml
resources:
  - name: admin-panel
    type: http
    target: http://admin:8080
    access: private
    # Only accessible via Olm VPN
```

**Hybrid Access:**
```yaml
resources:
  - name: api
    type: http
    target: http://api:4000
    access: public
    domain: api.example.com

  - name: api-internal
    type: http
    target: http://api:4000/internal
    access: private
    # Internal endpoints VPN-only
```

### 5.3 Docker Label Auto-Registration

Newt detects services based on Docker labels:

```yaml
services:
  my-service:
    image: my-app:latest
    labels:
      - "pangolin.enable=true"
      - "pangolin.domain=myservice.example.com"
      - "pangolin.access=public"
```

### 5.4 Newt Configuration

```yaml
# /etc/pangolin/newt.yaml
endpoint: wss://gerbil.example.com
site_id: production-01
docker:
  enabled: true
  label_prefix: pangolin
wireguard:
  private_key_file: /etc/pangolin/wg-private.key
```

---

## 6. Secrets Management

### 6.1 1Password Integration Options

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **CLI (op)** | CI/CD, local dev | Simple, no server | Requires login |
| **Connect** | Always-on services | No interactive auth | Requires server |
| **Service Account** | CI/CD automation | Token-based | Limited to 1 vault |

### 6.2 Dagger + 1Password

```typescript
import { dag, Secret } from "@dagger.io/dagger"
import { execSync } from "child_process"

export async function withSecrets(container: Container): Promise<Container> {
  // Get secret from 1Password
  const dbUrl = dag.setSecret("db-url",
    execSync("op read op://vault/database/url").toString().trim()
  )

  return container.withSecretVariable("DATABASE_URL", dbUrl)
}
```

### 6.3 Environment Variable Pattern

```bash
# In CI/CD
export OP_SERVICE_ACCOUNT_TOKEN="${{ secrets.OP_TOKEN }}"

# In scripts
op read "op://Infrastructure/database/password"
```

### 6.4 SOPS + 1Password Hybrid

For encrypted files in git:

```yaml
# .sops.yaml
creation_rules:
  - path_regex: \.enc\.yaml$
    age: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# secrets.enc.yaml (encrypted)
database:
  host: ENC[AES256_GCM,data:...,type:str]
  password: ENC[AES256_GCM,data:...,type:str]
```

---

## 7. Infrastructure as Code

### 7.1 Pulumi (TypeScript)

```typescript
// pulumi/index.ts
import * as pulumi from "@pulumi/pulumi"
import * as cloudflare from "@pulumi/cloudflare"

// Create R2 bucket
const bucket = new cloudflare.R2Bucket("data-bucket", {
  accountId: process.env.CLOUDFLARE_ACCOUNT_ID,
  name: "my-data-bucket",
})

// Create D1 database
const database = new cloudflare.D1Database("app-db", {
  accountId: process.env.CLOUDFLARE_ACCOUNT_ID,
  name: "app-database",
})

// Export outputs
export const bucketName = bucket.name
export const databaseId = database.id
```

### 7.2 Ansible for Server Configuration

```yaml
# playbooks/setup-server.yml
- name: Setup production server
  hosts: production
  become: yes
  tasks:
    - name: Install Docker
      ansible.builtin.apt:
        name: docker.io
        state: present

    - name: Install Komodo Periphery
      community.docker.docker_container:
        name: komodo-periphery
        image: ghcr.io/mbecker20/periphery:latest
        restart_policy: always
        env:
          KOMODO_HOST: "https://komodo.example.com"
          PERIPHERY_PASSKEY: "{{ lookup('community.general.onepassword', 'periphery-key') }}"

    - name: Install Pangolin Newt
      community.docker.docker_container:
        name: pangolin-newt
        image: ghcr.io/pangolin/newt:latest
        restart_policy: always
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
        env:
          PANGOLIN_ENDPOINT: "wss://gerbil.example.com"
          PANGOLIN_ID: "{{ inventory_hostname }}"
```

---

## 8. LLM Gateway

### 8.1 LiteLLM Configuration

```yaml
# litellm_config.yaml
model_list:
  # Primary models
  - model_name: claude-sonnet
    litellm_params:
      model: claude-3-5-sonnet-latest
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: claude-opus
    litellm_params:
      model: claude-3-opus-20240229
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  # Fallback chain
  - model_name: general-purpose
    litellm_params:
      model: claude-3-5-sonnet-latest
      api_key: os.environ/ANTHROPIC_API_KEY
    fallbacks:
      - model: gpt-4o
        api_key: os.environ/OPENAI_API_KEY

  # Cost-optimized routing
  - model_name: fast
    litellm_params:
      model: claude-3-5-haiku-latest
      api_key: os.environ/ANTHROPIC_API_KEY

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/DATABASE_URL

litellm_settings:
  drop_params: true
  set_verbose: false
  max_budget: 100  # USD per month
  budget_duration: monthly
```

### 8.2 Docker Compose for LiteLLM

```yaml
services:
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    command: --config /app/config.yaml
    ports:
      - "4000:4000"
    volumes:
      - ./litellm_config.yaml:/app/config.yaml
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
      - DATABASE_URL=postgresql://litellm:password@postgres:5432/litellm
    labels:
      - "pangolin.enable=true"
      - "pangolin.domain=llm.example.com"
      - "pangolin.access=private"

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_USER=litellm
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=litellm
    volumes:
      - litellm_db:/var/lib/postgresql/data

volumes:
  litellm_db:
```

---

## 9. Decision Matrices

### 9.1 Deployment Approach

| Approach | Complexity | Scalability | Best For |
|----------|------------|-------------|----------|
| **Systemd** | Low | Single server | Edge deployments |
| **Docker Compose** | Medium | Single server | Development |
| **Komodo** | Medium-High | Multi-server | Production |
| **Kubernetes** | High | Cluster | Large-scale |

### 9.2 Secrets Management

| Factor | 1Password CLI | 1Password Connect | 1Password SA | Infisical |
|--------|---------------|-------------------|--------------|-----------|
| **CI/CD Friendly** | No | Yes | Yes | Yes |
| **Local Dev** | Yes | Overkill | Limited | Yes |
| **Complexity** | Low | Medium | Low | Low |

### 9.3 CI/CD Tools

| Factor | Dagger | GitHub Actions | GitLab CI |
|--------|--------|----------------|-----------|
| **Language** | TS/Python/Go | YAML | YAML |
| **Local Testing** | Native | Limited | Limited |
| **CI/Local Parity** | Exact | Different | Different |
| **Debugging** | Interactive | Log-based | Log-based |

### 9.4 Cloud Platforms

| Factor | Cloudflare | AWS Lambda | Vercel |
|--------|------------|------------|--------|
| **Cold Start** | None (V8) | 100ms+ | Variable |
| **Edge Locations** | 200+ | Limited | 10+ |
| **Vendor Lock-in** | Low | High | Medium |

---

## 10. Implementation Guide

### 10.1 Phase 1: Environment Setup

```bash
# Install core tools
brew install dagger
brew install 1password-cli

# Rust for SpacetimeDB (if using)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cargo install spacetime-cli

# Node.js for Dagger TypeScript
fnm install 20
fnm use 20
```

### 10.2 Phase 2: Dagger Module Setup

```bash
# Initialize Dagger module
mkdir -p .dagger/src
cd .dagger

# Create dagger.json
cat > dagger.json << 'EOF'
{
  "name": "my-project",
  "sdk": "typescript"
}
EOF

# Create package.json
cat > package.json << 'EOF'
{
  "name": "@my-project/dagger",
  "type": "module",
  "dependencies": {
    "@dagger.io/dagger": "^0.9.0"
  }
}
EOF

npm install
```

### 10.3 Phase 3: Server Provisioning

```bash
# Run Ansible playbook
ansible-playbook -i inventory.ini playbooks/setup-server.yml

# Verify Periphery connection
curl https://komodo.example.com/api/servers
```

### 10.4 Phase 4: Service Deployment

```bash
# Local test
dagger call build --src=.
dagger call test --src=.

# Deploy
dagger call deploy --env=production
```

### 10.5 Complete Docker Compose Stack

```yaml
version: "3.8"

services:
  # Deployment orchestration
  komodo:
    image: ghcr.io/mbecker20/komodo:latest
    ports:
      - "9120:9120"
    environment:
      - KOMODO_PASSKEYS=${KOMODO_PASSKEYS}
    volumes:
      - komodo_data:/data

  # Zero-trust networking
  gerbil:
    image: ghcr.io/fossorial/gerbil:latest
    ports:
      - "443:443"
      - "51820:51820/udp"
    cap_add:
      - NET_ADMIN

  # LLM Gateway
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    command: --config /app/config.yaml
    volumes:
      - ./litellm_config.yaml:/app/config.yaml
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

  # Monitoring
  dozzle:
    image: amir20/dozzle:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    labels:
      - "pangolin.enable=true"
      - "pangolin.domain=logs.example.com"
      - "pangolin.access=private"

volumes:
  komodo_data:
```

---

## References

- Dagger Documentation: https://docs.dagger.io
- Komodo Documentation: https://komo.do/docs
- Pangolin Documentation: https://pangolin.dev/docs
- 1Password CLI: https://developer.1password.com/docs/cli
- Pulumi: https://www.pulumi.com/docs
- LiteLLM: https://docs.litellm.ai
- Cloudflare Workers: https://developers.cloudflare.com/workers

---

## From: ARCHITECTURE.md (leftover)

# Infrastructure Architecture Reference

## Quick Navigation

This is the primary infrastructure architecture reference. Consolidated from root-level infrastructure research documents.

**Tool-Specific Documentation:**
- [dagger/](./dagger/) - Dagger CI/CD pipelines
- [komodo/](./komodo/) - Komodo deployment orchestration
- [pangolin/](./pangolin/) - Pangolin zero-trust networking
- [1password/](./1password/) - 1Password secrets management
- [cloudflare/](./cloudflare/) - Cloudflare services (Workers, D1, R2, Tunnel)
- [pulumi/](./pulumi/) - Infrastructure as Code

**External Research (Reference Only):**
- [external-tools/github-spec-kit/](./external-tools/github-spec-kit/) - GitHub Spec Kit research (external tool, not used in project - we use OpenSpec)

---

## Table of Contents

1. [Overview & Key Principles](#overview--key-principles)
2. [Core Stack Components](#core-stack-components)
3. [System Architecture](#system-architecture)
4. [CI/CD Pipeline Architecture](#cicd-pipeline-architecture)
5. [Deployment Orchestration](#deployment-orchestration)
6. [Zero-Trust Networking](#zero-trust-networking)
7. [Secrets Management](#secrets-management)
8. [Infrastructure as Code](#infrastructure-as-code)
9. [Integration Patterns](#integration-patterns)

---

## Overview & Key Principles

This infrastructure stack enables declarative, cross-language workflows that work consistently from local development through production deployment.

### Key Architectural Principles

1. **Container-First**: All services run in containers for consistency and portability
2. **Secrets Never in Git**: All sensitive data managed through 1Password vaults
3. **Zero-Trust Networking**: Services accessible only through authenticated Pangolin tunnels
4. **Infrastructure as Code**: All infrastructure defined in code and version controlled
5. **Modular Pipelines**: Build, test, and deploy steps organized as reusable Dagger modules

### Technology Stack

| Category | Tool | Purpose |
|----------|------|---------|
| **Git Hosting** | Forgejo | Self-hosted Git with Actions |
| **CI/CD** | Dagger | Programmable pipelines in code |
| **Deployment** | Komodo | Docker Compose orchestration |
| **Networking** | Pangolin | Zero-trust tunnel access |
| **Secrets** | 1Password | Vault-based secrets management |
| **IaC** | Pulumi | Cloud resource provisioning |
| **Config** | Ansible | Server configuration |

---

## Core Stack Components

### Dagger - CI/CD in Code

Dagger replaces YAML-based CI with real programming languages (TypeScript, Python, Go).

**Key Advantages:**
- **Unified Pipelines**: Same code runs locally and in CI
- **Monorepo Support**: Context filtering for multi-project repos
- **Cross-Language**: Modules can call each other across languages
- **Caching**: Automatic layer caching for fast builds

```typescript
// Example Dagger pipeline
import { dag, Container, Directory } from "@dagger.io/dagger"

export async function build(src: Directory): Promise<Container> {
  return dag
    .container()
    .from("node:20-alpine")
    .withDirectory("/app", src)
    .withWorkdir("/app")
    .withExec(["npm", "install"])
    .withExec(["npm", "run", "build"])
}
```

### Komodo - Deployment Orchestration

Komodo manages Docker Compose stacks across servers via agents (Periphery).

**Capabilities:**
- Deploy Docker Compose stacks to remote servers
- Manage multiple deployment targets
- TypeScript SDK for programmatic control
- Integrates with 1Password for secrets

```typescript
// Komodo TypeScript SDK
import { KomodoClient } from "@komodo/client"

const client = new KomodoClient({
  url: "https://komodo.example.com",
  apiKey: process.env.KOMODO_API_KEY
})

await client.stacks.deploy({
  name: "my-app",
  server: "production-01",
  composePath: "./docker-compose.yml"
})
```

### Pangolin - Zero-Trust Access

Pangolin provides secure access to services without exposing ports.

**Components:**
- **Newt**: Site connector (runs on server)
- **Olm**: Client agent (runs on user machines)
- **Gerbil**: WireGuard-based tunnel server

**Access Models:**
- **Public**: Internet-accessible via reverse proxy
- **Private**: VPN-only access through Olm
- **Hybrid**: Public frontend, private backend

### 1Password - Secrets Management

1Password provides vault-based secrets with CLI and Connect options.

**Integration Points:**
- Dagger: Inject secrets during builds
- Komodo: Reference secrets in compose files
- Ansible: Provision secrets to servers
- Pulumi: Cloud resource credentials

---

## System Architecture

### End-to-End Flow

```
Developer Push → Forgejo Actions → Dagger Pipeline → Build Images
                                  ↓
                         Inject 1Password Secrets
                                  ↓
                         Test with Docker Compose
                                  ↓
                    Publish to Forgejo Registry
                                  ↓
              Deploy via Komodo TypeScript SDK
                                  ↓
        Pangolin Newt Auto-registers Services
                                  ↓
              Production Deployment
```

### Component Interactions

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Developer Workstation                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Local Development                                               │   │
│  │  - dagger call build                                            │   │
│  │  - docker compose up                                            │   │
│  │  - op run -- command (1Password CLI)                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ git push
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Forgejo + Actions                             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────────┐ │
│  │  Git Server  │→→│ Actions      │→→│ Dagger Pipeline               │ │
│  │              │  │ Runner       │  │ - Build images                │ │
│  │  Registry    │←←│              │←←│ - Run tests                   │ │
│  └──────────────┘  └──────────────┘  │ - Push to registry            │ │
│                                       └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Komodo SDK deploy
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Production Server                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Komodo Periphery Agent                                          │  │
│  │  - Receives deployment commands                                  │  │
│  │  - Manages Docker Compose stacks                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Pangolin Newt                                                   │  │
│  │  - WireGuard tunnel to Gerbil                                    │  │
│  │  - Auto-registers services                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Application Containers                                          │  │
│  │  - Web apps, APIs, databases                                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## CI/CD Pipeline Architecture

### Dagger Module Structure

```
.dagger/
├── src/
│   ├── index.ts              # Main entry point
│   ├── build.ts              # Build functions
│   ├── test.ts               # Test functions
│   ├── deploy.ts             # Deploy functions
│   └── secrets.ts            # 1Password integration
├── dagger.json               # Module configuration
└── package.json
```

### Pipeline Stages

**1. Build Stage**
```typescript
export async function build(src: Directory): Promise<Container> {
  // Install dependencies
  // Compile TypeScript
  // Bundle application
  return container
}
```

**2. Test Stage**
```typescript
export async function test(src: Directory): Promise<string> {
  // Run unit tests
  // Run integration tests
  // Run linting
  return testResults
}
```

**3. Publish Stage**
```typescript
export async function publish(container: Container): Promise<string> {
  // Tag image
  // Push to registry
  return imageRef
}
```

**4. Deploy Stage**
```typescript
export async function deploy(imageRef: string): Promise<void> {
  // Call Komodo API
  // Update stack
  // Verify health
}
```

### Forgejo Actions Workflow

```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Dagger
        run: |
          curl -fsSL https://dl.dagger.io/dagger/install.sh | sh
          sudo mv bin/dagger /usr/local/bin/

      - name: Run Pipeline
        run: |
          dagger call build --src=.
          dagger call test --src=.
          dagger call publish
          dagger call deploy
        env:
          OP_SERVICE_ACCOUNT_TOKEN: ${{ secrets.OP_TOKEN }}
          KOMODO_API_KEY: ${{ secrets.KOMODO_KEY }}
```

---

## Deployment Orchestration

### Komodo Architecture

```
┌─────────────────────────────────────────────────┐
│              Komodo Core                        │
│  ┌──────────────────────────────────────────┐   │
│  │  API Server                              │   │
│  │  - REST API for deployments              │   │
│  │  - WebSocket for real-time updates       │   │
│  │  - Stack configuration storage           │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
          │                      │
          │                      │
          ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐
│ Periphery Agent     │  │ Periphery Agent     │
│ (Server 1)          │  │ (Server 2)          │
│ - Docker daemon     │  │ - Docker daemon     │
│ - Compose runtime   │  │ - Compose runtime   │
└─────────────────────┘  └─────────────────────┘
```

### Stack Configuration

```yaml
# docker-compose.yml for Komodo deployment
version: "3.8"

services:
  app:
    image: registry.example.com/my-app:${TAG:-latest}
    environment:
      - DATABASE_URL=op://vault/database/url
    labels:
      - "pangolin.enable=true"
      - "pangolin.domain=app.example.com"

  database:
    image: postgres:16
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=op://vault/database/password

volumes:
  db_data:
```

---

## Zero-Trust Networking

### Pangolin Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Gerbil** | Cloud/Central | WireGuard tunnel server |
| **Newt** | Each server | Site connector |
| **Olm** | Client devices | VPN client |

### Access Patterns

**Public Access (Internet-facing)**
```yaml
# pangolin-config.yaml
resources:
  - name: web-app
    type: http
    target: http://app:3000
    access: public
    domain: app.example.com
```

**Private Access (VPN-only)**
```yaml
resources:
  - name: admin-panel
    type: http
    target: http://admin:8080
    access: private
    # Only accessible via Olm VPN
```

**Hybrid Access**
```yaml
resources:
  - name: api
    type: http
    target: http://api:4000
    access: public
    domain: api.example.com

  - name: api-internal
    type: http
    target: http://api:4000/internal
    access: private
    # Internal endpoints VPN-only
```

### Newt Auto-Registration

Newt can automatically register services based on Docker labels:

```yaml
services:
  my-service:
    image: my-app:latest
    labels:
      - "pangolin.enable=true"
      - "pangolin.domain=myservice.example.com"
      - "pangolin.access=public"
```

---

## Secrets Management

### 1Password Integration Options

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **CLI (op)** | CI/CD, local dev | Simple, no server | Requires login |
| **Connect** | Always-on services | No interactive auth | Requires server |
| **Service Account** | CI/CD automation | Token-based | Limited to 1 vault |

### Dagger + 1Password

```typescript
import { dag, Secret } from "@dagger.io/dagger"

export async function withSecrets(container: Container): Promise<Container> {
  // Get secret from 1Password
  const dbUrl = dag.setSecret("db-url",
    await execCmd("op read op://vault/database/url")
  )

  return container.withSecretVariable("DATABASE_URL", dbUrl)
}
```

### SOPS + 1Password Hybrid

For files that need to be in git (encrypted):

```yaml
# .sops.yaml
creation_rules:
  - path_regex: \.enc\.yaml$
    age: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# secrets.enc.yaml (encrypted)
database:
  host: ENC[AES256_GCM,data:...,type:str]
  password: ENC[AES256_GCM,data:...,type:str]
```

---

## Infrastructure as Code

### Pulumi for Cloud Resources

```typescript
// pulumi/index.ts
import * as pulumi from "@pulumi/pulumi"
import * as cloudflare from "@pulumi/cloudflare"

// Create R2 bucket
const bucket = new cloudflare.R2Bucket("data-bucket", {
  accountId: process.env.CLOUDFLARE_ACCOUNT_ID,
  name: "my-data-bucket",
})

// Create D1 database
const database = new cloudflare.D1Database("app-db", {
  accountId: process.env.CLOUDFLARE_ACCOUNT_ID,
  name: "app-database",
})

// Export outputs
export const bucketName = bucket.name
export const databaseId = database.id
```

### Ansible for Server Config

```yaml
# playbooks/setup-server.yml
- name: Setup production server
  hosts: production
  become: yes
  tasks:
    - name: Install Docker
      ansible.builtin.apt:
        name: docker.io
        state: present

    - name: Install Komodo Periphery
      community.docker.docker_container:
        name: komodo-periphery
        image: ghcr.io/mbecker20/periphery:latest
        restart_policy: always
        env:
          KOMODO_HOST: "https://komodo.example.com"
          PERIPHERY_PASSKEY: "{{ lookup('community.general.onepassword', 'periphery-key') }}"

    - name: Install Pangolin Newt
      community.docker.docker_container:
        name: pangolin-newt
        image: ghcr.io/pangolin/newt:latest
        restart_policy: always
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
        env:
          PANGOLIN_ENDPOINT: "wss://gerbil.example.com"
          PANGOLIN_ID: "{{ inventory_hostname }}"
```

---

## Integration Patterns

### Complete Deployment Flow

```
1. Developer pushes to main branch
   └─→ Forgejo triggers Actions workflow

2. Dagger pipeline executes
   ├─→ Build: Compile code, create container
   ├─→ Test: Run unit/integration tests
   ├─→ Secrets: Inject 1Password credentials
   └─→ Publish: Push to Forgejo registry

3. Komodo deployment
   ├─→ SDK calls Komodo API
   ├─→ Periphery pulls new image
   └─→ Stack redeployed with zero downtime

4. Pangolin registration
   ├─→ Newt detects new service
   ├─→ Registers with Gerbil
   └─→ DNS/TLS configured automatically

5. Traffic flows
   └─→ Users access via Pangolin domain
```

### Multi-Environment Strategy

```
Development:
├─→ Local Docker Compose
├─→ 1Password CLI for secrets
└─→ No Pangolin (localhost)

Staging:
├─→ Komodo deployment to staging server
├─→ 1Password Connect for secrets
└─→ Pangolin private access (VPN-only)

Production:
├─→ Komodo deployment to production cluster
├─→ 1Password Connect for secrets
└─→ Pangolin public + private access
```

---

## References

**Source Documents:**
- ci-cd-stack-integration-guide.md
- infrastructure-consolidation-guide.md
- ci-cd-platform-architecture.md
- deciding-between-systemd-agents-docker-compose-komodo-pangolin.md

**Tool Documentation:**
- [Dagger Documentation](https://docs.dagger.io)
- [Komodo Documentation](https://komo.do/docs)
- [Pangolin Documentation](https://pangolin.dev/docs)
- [1Password CLI](https://developer.1password.com/docs/cli)

**Last Updated:** November 29, 2024

---

## From: DECISION_MATRICES.md (leftover)

# Infrastructure Decision Matrices

> Technology comparison and selection guidance for the infrastructure stack

**Last Updated**: December 2025
**Status**: Generated from existing documentation

---

## Overview

This document provides decision matrices for selecting appropriate technologies across the infrastructure stack. Each matrix includes comparison criteria, trade-offs, and recommendations.

---

## 1. Deployment Approach Comparison

### When to Use What

| Approach | Complexity | Scalability | Best For |
|----------|------------|-------------|----------|
| **Systemd** | Low | Single server | Simple services, edge deployments |
| **Docker Compose** | Medium | Single server | Development, small production |
| **Komodo** | Medium-High | Multi-server | Production deployments, GitOps |
| **Kubernetes** | High | Cluster | Large-scale, complex orchestration |

### Detailed Comparison

| Factor | Systemd | Docker Compose | Komodo | Kubernetes |
|--------|---------|----------------|--------|------------|
| Setup Time | Minutes | Minutes | Hours | Days |
| Learning Curve | Low | Low | Medium | High |
| Resource Overhead | Minimal | Low | Low | High |
| Failure Recovery | Manual | Manual | Automatic | Automatic |
| Rolling Updates | No | Limited | Yes | Yes |
| Multi-Server | No | No | Yes | Yes |
| Secrets Integration | Manual | Manual | 1Password native | Secrets CRD |
| Monitoring | External | External | Built-in | External |

### Recommendation

**This project uses: Komodo + Docker Compose**

Rationale:
- Multi-server support for distributed services
- Native 1Password integration for secrets
- Simpler than Kubernetes for our scale
- GitOps workflow via Periphery agents

---

## 2. Secrets Management Options

### Comparison Matrix

| Factor | 1Password CLI | 1Password Connect | 1Password SA | Infisical | Vault |
|--------|---------------|-------------------|--------------|-----------|-------|
| **Cost** | Included | Included | Included | Free tier | Free/Paid |
| **Self-Hosted** | No | Yes | No | Yes | Yes |
| **CI/CD Friendly** | No (interactive) | Yes | Yes | Yes | Yes |
| **Local Dev** | Yes | Overkill | Limited | Yes | Complex |
| **Rotation** | Manual | Manual | Manual | Auto | Auto |
| **Audit Logs** | Yes | Yes | Yes | Yes | Yes |
| **Complexity** | Low | Medium | Low | Low | High |

### Selection Flowchart

```
Start
  │
  ├─ Single developer?
  │   └─ Yes → 1Password CLI
  │
  ├─ CI/CD automation needed?
  │   ├─ Yes + existing 1Password → Service Account
  │   └─ Yes + open source preferred → Infisical
  │
  ├─ Always-on services need secrets?
  │   └─ Yes → 1Password Connect Server
  │
  └─ Enterprise compliance required?
      └─ Yes → HashiCorp Vault
```

### Recommendation

**This project uses: 1Password (CLI + Service Account)**

Rationale:
- Already using 1Password for team credentials
- Service Account for CI/CD automation
- CLI for local development
- No additional infrastructure required

---

## 3. Networking & Access Control

### Access Pattern Comparison

| Pattern | Security | User Experience | Complexity | Use Case |
|---------|----------|-----------------|------------|----------|
| **Public** (reverse proxy) | Medium | Best | Low | Public APIs, web apps |
| **Private** (VPN-only) | High | Requires client | Medium | Admin panels, internal tools |
| **Hybrid** | High | Mixed | High | Public frontend + private backend |
| **Direct IP** | Low | Direct | None | Development only |

### Pangolin Component Selection

| Component | Purpose | Install Where |
|-----------|---------|---------------|
| **Gerbil** | WireGuard tunnel server | Central/cloud |
| **Newt** | Site connector | Each server |
| **Olm** | VPN client | Developer machines |

### When to Use Each Access Pattern

| Service Type | Access Pattern | Example |
|--------------|----------------|---------|
| Public API | Public | api.example.com |
| Marketing site | Public | www.example.com |
| Admin dashboard | Private | admin.example.com |
| Database | Private | Never expose |
| Monitoring | Private | metrics.example.com |
| Internal API | Hybrid | Public endpoint, private health |

### Recommendation

**This project uses: Pangolin with Hybrid access**

Rationale:
- Zero-trust by default
- Public APIs via reverse proxy
- Private services via VPN
- Auto-registration via Docker labels

---

## 4. CI/CD Tool Comparison

### Feature Matrix

| Factor | Dagger | GitHub Actions | GitLab CI | Jenkins |
|--------|--------|----------------|-----------|---------|
| **Language** | TS/Python/Go | YAML | YAML | Groovy |
| **Local Testing** | Native | Limited (act) | Limited | Yes |
| **CI/Local Parity** | Exact | Different | Different | Different |
| **Caching** | Automatic | Manual config | Manual config | Plugins |
| **Debugging** | Interactive | Log-based | Log-based | Log-based |
| **Self-Hosted** | Any | Any | Any | Required |
| **Learning Curve** | Medium | Low | Low | High |
| **Reusability** | Modules | Composite actions | Includes | Shared libs |

### When to Choose Dagger

Prefer Dagger when:
- You want local testing to match CI exactly
- Pipeline logic is complex (conditionals, loops)
- Multi-language support needed
- Container-based workflows
- Debugging pipelines is important

Prefer YAML-based CI (Actions/GitLab) when:
- Simple linear workflows
- Team prefers declarative config
- Existing YAML expertise
- Tight integration with specific platform

### Recommendation

**This project uses: Dagger + Forgejo Actions**

Rationale:
- TypeScript for complex pipeline logic
- Local testing matches CI exactly
- Module-based code reuse
- Forgejo Actions for triggers

---

## 5. Infrastructure as Code

### IaC Tool Comparison

| Factor | Pulumi | Terraform | Ansible | CloudFormation |
|--------|--------|-----------|---------|----------------|
| **Language** | TS/Python/Go/YAML | HCL | YAML | JSON/YAML |
| **State Management** | Backend required | Backend required | Stateless | AWS native |
| **Learning Curve** | Medium | Medium | Low | Medium |
| **Testing** | Native | Limited | Limited | Limited |
| **Provider Coverage** | Good | Excellent | N/A (config) | AWS only |
| **Type Safety** | Strong (TS) | Limited | None | None |
| **Secret Handling** | Good | External | External | SSM |

### Selection Guide

| Use Case | Recommended Tool |
|----------|------------------|
| Cloud resource provisioning | Pulumi (TypeScript) |
| Server configuration | Ansible |
| AWS-only infrastructure | CloudFormation |
| Multi-cloud, team prefers HCL | Terraform |
| Kubernetes resources | Pulumi or Helm |

### Recommendation

**This project uses: Pulumi (TypeScript) + Ansible**

Rationale:
- TypeScript for type-safe infrastructure
- Consistency with application code
- Ansible for server configuration
- 1Password integration for secrets

---

## 6. Installation Methods

### Tool Installation Comparison

| Factor | Host OS (systemd) | Docker Container | Komodo Periphery |
|--------|-------------------|------------------|------------------|
| **Dependencies** | Must manage | Isolated | Isolated |
| **Updates** | Package manager | Image pull | Image pull |
| **Privileges** | Root required | Container only | Container only |
| **Resource Usage** | Lower | Higher | Higher |
| **Debugging** | Direct access | Container access | Container access |
| **Portability** | OS-specific | Any Docker host | Any Docker host |

### Recommendation by Tool

| Tool | Recommended Installation |
|------|-------------------------|
| 1Password CLI | Host OS (for interactive use) |
| Komodo Periphery | Docker container |
| Pangolin Newt | Docker container |
| Database | Docker container |
| Application | Docker container |

---

## 7. Cloud Platform Comparison

### Serverless Platform Matrix

| Factor | Cloudflare | AWS Lambda | Azure Functions | Vercel |
|--------|------------|------------|-----------------|--------|
| **Cold Start** | None (V8) | 100ms+ | 100ms+ | Variable |
| **Pricing** | Generous free | Pay per invoke | Pay per invoke | Generous free |
| **Database** | D1 (SQLite) | RDS/DynamoDB | CosmosDB | Postgres |
| **Storage** | R2 (S3 compat) | S3 | Blob Storage | Blob |
| **Edge Locations** | 200+ | Limited | Limited | 10+ |
| **Vendor Lock-in** | Low | High | High | Medium |

### When to Choose Each

| Requirement | Platform |
|-------------|----------|
| Global low latency | Cloudflare Workers |
| Complex AWS integration | AWS Lambda |
| Microsoft ecosystem | Azure Functions |
| Next.js deployment | Vercel |
| Self-hosted required | None (use containers) |

### Recommendation

**This project uses: Cloudflare (Workers, D1, R2)**

Rationale:
- Zero cold starts (V8 isolates)
- Global edge network (200+ locations)
- S3-compatible storage (R2)
- SQLite-compatible database (D1)
- Cost-effective for our scale

---

## 8. Decision Summary

### Current Stack

| Category | Choice | Alternatives Considered |
|----------|--------|------------------------|
| **Deployment** | Komodo | Docker Compose, Kubernetes |
| **Secrets** | 1Password | Infisical, Vault |
| **Networking** | Pangolin | Cloudflare Tunnel, Tailscale |
| **CI/CD** | Dagger | GitHub Actions, GitLab CI |
| **IaC** | Pulumi | Terraform, CloudFormation |
| **Serverless** | Cloudflare | AWS Lambda, Vercel |
| **Config Mgmt** | Ansible | Chef, Puppet |

### Decision Criteria Used

1. **Team expertise**: Prefer familiar technologies
2. **Complexity budget**: Avoid over-engineering
3. **Cost**: Open source when possible
4. **Integration**: 1Password across all tools
5. **Vendor lock-in**: Minimize where possible
6. **Type safety**: TypeScript/Pydantic preferred

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Infrastructure architecture overview
- [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) - Step-by-step setup guide
- [/infrastructure/dagger/](./dagger/) - Dagger pipeline documentation
- [/infrastructure/komodo/](./komodo/) - Komodo deployment documentation
- [/infrastructure/pangolin/](./pangolin/) - Pangolin networking documentation
- [/infrastructure/pulumi/](./pulumi/) - Pulumi IaC documentation

