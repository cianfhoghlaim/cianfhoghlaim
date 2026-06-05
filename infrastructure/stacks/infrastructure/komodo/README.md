# Komodo — Container Orchestration and GitOps

## Overview

Komodo is an open-source container orchestration platform by Moghtech that provides GitOps-driven deployment management with a web UI, API, and CLI. It syncs Docker Compose stacks from a Git repository (Forgejo), manages multi-server deployments, and integrates with Pangolin for service routing. Think of it as a self-hosted alternative to Portainer with native GitOps.

## Why This Matters for Kings' College Galway

Komodo is the deployment engine for all 89 stacks. Every `compose.yaml` + `sidecar.yaml` in this repository is synced from Forgejo to Komodo, which applies them to the correct server (arm1-oci, cax41-hetzner, or bunchloch MacBook). When a new OCR model is added, the `olmocr` stack is updated in Forgejo, Komodo detects the change, and redeploys — no SSH, no manual `docker compose`, no downtime from misconfiguration. This GitOps loop is what makes the infrastructure reproducible rather than artisanal.

## Key Features

- **GitOps sync** — Automatically deploys stacks when Forgejo repository changes
- **Multi-server** — Manage ARM1 (OCI), CAX41 (Hetzner), and MacBook (bunchloch) from one dashboard
- **Web UI + API** — Graphical stack management, log viewer, resource monitoring
- **MongoDB-backed** — Production-grade document database for deployment state
- **Pangolin integration** — All stacks automatically register as private Pangolin resources

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/infrastructure/komodo
docker compose up -d
```

### Production (with Locket and Pangolin)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `KOMODO_DATABASE_USERNAME` | No | MongoDB root username | `komodo` |
| `KOMODO_DATABASE_PASSWORD` | Yes | MongoDB root password | — |
| `KOMODO_IMAGE_TAG` | No | Komodo Core image tag | `2` |
| `KOMODO_PERIPHERY_IMAGE_TAG` | No | Periphery agent image tag | `2` |
| `KOMODO_ADMIN_USERNAME` | No | Initial admin username | `admin` |
| `KOMODO_ADMIN_PASSWORD` | Yes | Initial admin password | — |

## Access

- **Web UI**: `https://komodo.cianfhoghlaim.ie` (private, Admin role)
- **API**: `https://komodo.cianfhoghlaim.ie/api`
- **Auth**: Local admin account + Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/moghtech/komodo>
- **Documentation**: <https://komo.do/docs>
- **Latest**: v2 series — FerretDB v2 replacement for MongoDB, ARM64 support, improved Periphery agent communication

## Screenshot

Komodo's web UI shows: server list with resource utilisation, stack deployment status (running/stopped/error), per-stack log viewer, Git sync configuration, and deployment history. The dashboard provides quick actions: start, stop, restart, pull, and deploy for each stack across all servers.
