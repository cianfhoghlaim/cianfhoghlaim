# Forgejo — Self-Hosted Git Forge with Package Registry

## Overview

Forgejo is a self-hosted Git service and software forge — a lightweight, community-maintained fork of Gitea. It provides Git repository hosting, issue tracking, pull requests, CI/CD (Forgejo Actions), and built-in package registries for PyPI, npm, Cargo, and Docker containers.

## Why This Matters for Kings' College Galway

Forgejo is the canonical source of truth for the entire monorepo. Every `compose.yaml`, every BAML schema, every Dagster asset, every marimo notebook lives in Forgejo at `git.cianfhoghlaim.ie`. The built-in PyPI registry hosts internal Python packages (códeolas, sruth-browser, oideachais) that the Dagster pipeline imports — no dependency on PyPI.org for proprietary code. Forgejo Actions (via the Forgejo Runner stack) provide CI/CD for all 5 programming languages in the monorepo. This complete self-hosting of the software supply chain eliminates a critical attack vector — no code, no packages, and no CI secrets ever leave the infrastructure mesh.

## Key Features

- **Git hosting** — Full Git server with web UI, pull requests, code review
- **Package registries** — PyPI, npm, Cargo, Container, and Composer registries built-in
- **Forgejo Actions** — GitHub Actions-compatible CI/CD engine
- **Lightweight** — Single Go binary; runs on ARM64 with <500 MB memory
- **Open-source** — Community-maintained fork of Gitea with active development

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/forgejo
docker compose up -d
```

### Production (with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)

Deployed via Komodo on arm1-oci as a PUBLIC resource (git access must work without VPN). First user to register becomes the site administrator.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `FORGEJO_DB_USER` | No | PostgreSQL user | `forgejo` |
| `FORGEJO_DB_PASSWORD` | Yes | PostgreSQL password | — |
| `FORGEJO_DB_NAME` | No | Database name | `forgejo` |
| `FORGEJO__server__ROOT_URL` | No | Public URL | `https://git.cianfhoghlaim.ie` |
| `FORGEJO__server__DOMAIN` | No | Server domain | `git.cianfhoghlaim.ie` |
| `FORGEJO__server__SSH_DOMAIN` | No | SSH domain | `git.cianfhoghlaim.ie` |
| `FORGEJO__server__SSH_PORT` | No | SSH port | `2222` |

## Access

- **Web UI**: `https://git.cianfhoghlaim.ie` (public)
- **SSH**: `ssh://git@git.cianfhoghlaim.ie:2222` (public)
- **PyPI Registry**: `https://git.cianfhoghlaim.ie/api/packages/{owner}/pypi`
- **Auth**: Email/password (local accounts) + Pocket ID OIDC

## Upstream

- **Repository**: <https://codeberg.org/forgejo/forgejo>
- **Documentation**: <https://forgejo.org/docs>
- **Latest**: v10.x (2025) — improved Actions runner compatibility, PyPI registry v2, OIDC provider support, ARM64 optimisations

## Screenshot

Forgejo's web UI resembles GitHub: repository browser with file tree and README rendering, issue tracker with labels and milestones, pull request review with inline comments, Actions tab showing CI/CD workflow runs, and Packages tab listing published PyPI/npm/container artifacts.
