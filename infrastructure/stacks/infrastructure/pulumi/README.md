# Pulumi — Infrastructure as Code (Self-Hosted State Backend)

## Overview

Pulumi is an open-source Infrastructure as Code platform that lets you define cloud resources using general-purpose programming languages (TypeScript, Python, Go, C#). This stack runs a self-hosted Pulumi state backend, storing infrastructure state locally rather than in Pulumi Cloud — essential for air-gapped or privacy-sensitive deployments.

## Why This Matters for Kings' College Galway

The Cianfhoghlaim infrastructure spans three cloud providers (OCI, Hetzner, Cloudflare) and three physical hosts. Pulumi manages the cloud resources — OCI compute instances, Hetzner VPS, Cloudflare DNS and R2 buckets — as code in the `infrastructure/pulumi/` directory. Running a self-hosted state backend means the infrastructure state (which describes every cloud resource) never leaves the private network. This is critical for a project that handles educational data under GDPR and Irish data protection law — the state file contains resource IDs that could be used to enumerate the infrastructure.

## Key Features

- **Multi-cloud IaC** — Define OCI, Hetzner, and Cloudflare resources in a single TypeScript program
- **Self-hosted state** — No dependency on Pulumi Cloud; state stored locally in Docker volume
- **TypeScript-native** — Same language as the TanStack frontend and Bun toolchain
- **Resource graph** — Pulumi understands dependencies; parallelises independent resource creation

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/infrastructure/pulumi
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. The state backend runs as a persistent service; Pulumi CLI commands (`pulumi up`, `pulumi preview`) connect to it via the `PULUMI_BACKEND_URL`.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `PULUMI_BACKEND_URL` | Yes | Pulumi state backend URL | — |
| `PULUMI_CONFIG_PASSPHRASE` | Yes | Encryption passphrase for state | — |

## Access

- **API**: `http://localhost:8080`
- **Health**: `http://localhost:8080/api/health`
- **Auth**: Pulumi access token (configured via `pulumi login`)

## Upstream

- **Repository**: <https://github.com/pulumi/pulumi>
- **Documentation**: <https://www.pulumi.com/docs>
- **Latest**: v3.x (2025) — improved ARM64 support, self-hosted backend enhancements, TypeScript 5.x compatibility

## Screenshot

Pulumi is a CLI tool with no built-in web UI. The self-hosted backend serves a REST API at port 8080 for state management. The Pulumi Cloud console (if using the hosted version) shows resource graphs, stack history, and drift detection dashboards.
