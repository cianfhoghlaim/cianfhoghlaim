# Komodo Infrastructure

GitOps-managed infrastructure using Komodo for container orchestration.

## Directory Structure

```
komodo/
├── actions/              # TypeScript automation scripts
│   ├── sync-dns-records.ts
│   ├── setup-pangolin-site.ts
│   ├── generate-ansible-inventory.ts
│   ├── validate-deployments.ts
│   └── sync-storage-configs.ts
├── procedures/           # Multi-stage orchestration
│   ├── init-site.toml
│   ├── sync-infrastructure.toml
│   ├── deploy-storage-stack.toml
│   ├── deploy-devtools.toml
│   ├── deploy-hetzner.toml
│   └── deploy-macbook.toml
├── stacks/               # Stack definitions
│   ├── oci-control-plane.toml
│   ├── hetzner-databases.toml
│   ├── macbook-analytics.toml
│   ├── oci-devtools.toml
│   ├── hetzner-devtools.toml
│   ├── macbook-media.toml
│   └── forgejo.toml
├── sites/                # Site configurations
│   ├── oci/
│   ├── hetzner/
│   └── macbook/
├── servers/              # Server definitions
│   └── servers.toml
└── resource-syncs/       # GitOps sync configs
```

## Quick Commands

### Actions

```bash
# Sync DNS records to Cloudflare
km run action sync-dns-records --dryRun=true
km run action sync-dns-records

# Setup new Pangolin site
km run action setup-pangolin-site --server=arm1-oci

# Generate Ansible inventory
km run action generate-ansible-inventory

# Validate all deployments
km run action validate-deployments
km run action validate-deployments --server=arm1-oci
km run action validate-deployments --stack=forgejo

# Sync storage configs to servers
km run action sync-storage-configs --dryRun=true
```

### Procedures

```bash
# Initialize new site (Periphery + Newt)
km run procedure init-site

# Pre-deploy infrastructure sync
km run procedure sync-infrastructure

# Deploy storage stack
km run procedure deploy-storage-stack

# Deploy dev tools
km run procedure deploy-devtools
```

### Stacks

```bash
# Deploy individual stack
km deploy-stack forgejo
km deploy-stack garage
km deploy-stack perplexica

# List stacks
km ps
km ps --down
```

## Sites

| Site | Server | Purpose |
|------|--------|---------|
| arm1-oci | Oracle Cloud | Control plane, lightweight tools |
| cax41-hetzner | Hetzner CAX41 | Databases, resource-intensive apps |
| bunchloch | MacBook | Analytics, media, development |

## Stack Categories

### OCI Control Plane
- garage - S3-compatible object storage
- beszel - Server monitoring
- dozzle - Docker log viewer
- qdrant - Vector database
- forgejo - Git server

### Hetzner Databases
- memgraph - Graph database
- falkordb - GraphRAG database
- lancedb - Vector database
- graphiti - Knowledge graph
- mlflow - ML experiment tracking
- langfuse - LLM observability

### MacBook Analytics
- lakefs - Data versioning
- lakekeeper - Lakehouse management
- convex - Reactive backend
- cognee - AI memory

### Dev Tools
- glance - Dashboard
- backrest - Backup management
- chartdb - Database visualization
- searxng - Privacy search
- perplexica - AI search
- restate - Durable execution

### Media
- audiobookshelf - Audiobook server
- calibre - E-book management
- kavita - Comic reader
- karakeep - Knowledge base

## Requirements

- Komodo Core 2.0.0-dev-102+
- Periphery on each server
- Pangolin for tunneling
- 1Password Connect for secrets
