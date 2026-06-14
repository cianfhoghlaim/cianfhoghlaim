# Infrastructure Capability

## Purpose

`infrastructure` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.


## Background
Production infrastructure and deployment architecture implementing Pangolin Convergence Architecture (two-tier: OCI ARM1 control plane + MacBook M4 workload host), zero-egress lakehouse, and GitOps deployment via Komodo.

| Feature | Description |
|---------|-------------|
| Pangolin Convergence | Two-tier routing (control plane + workload) with Traefik reverse proxy |
| Komodo GitOps | Container orchestration with multi-server deployment |
| Infisical Secrets | Automated secret hydration via mise hooks and Locket sidecar |
| Pocket ID OIDC | Identity provider for SSO across all services |
| Docker Stacks | 65+ compose stacks across 5 categories |

## Requirements

### Requirement: Pangolin Convergence Architecture

The system SHALL route traffic via a two-tier Pangolin architecture.

#### Scenario: Control Plane Routing
- **GIVEN** OCI ARM1 instance running Pangolin control plane
- **WHEN** external request arrives at `*.cianfhoghlaim.ie`
- **THEN** Traefik routes to the correct backend service via WireGuard tunnel

#### Scenario: Workload Host Isolation
- **GIVEN** MacBook M4 workload host (bunchloch)
- **WHEN** memory-intensive workloads run locally
- **THEN** traffic stays on localhost with zero egress costs

#### Scenario: TinyAuth Protection
- **GIVEN** a service exposed via Pangolin
- **WHEN** unauthenticated request arrives
- **THEN** request is redirected to Pocket ID for OIDC authentication

### Requirement: Secret Management

The system SHALL hydrate secrets automatically via Infisical and mise hooks.

#### Scenario: Directory Entry Injection
- **GIVEN** a directory with `.infisical.env` template and `mise.toml` hooks
- **WHEN** user enters the directory
- **THEN** `mise` triggers `infisical export` resolving all secrets into `.env`

#### Scenario: Container Secrets
- **GIVEN** a Docker stack with `sidecar.yaml` and `secrets.env`
- **WHEN** stack starts via Komodo
- **THEN** Locket sidecar injects Infisical secrets into the container environment

#### Scenario: No Manual .env Files
- **GIVEN** a new service requiring secrets
- **WHEN** developer needs credentials
- **THEN** secrets SHALL be added to Infisical vault `dev-baile` and `.infisical.env` template, NOT hardcoded in `.env`

### Requirement: Komodo GitOps Deployment

The system SHALL manage container stacks via Komodo's GitOps workflow.

#### Scenario: Stack Deployment
- **GIVEN** a stack directory with `compose.yaml`, `pangolin.yaml`, `sidecar.yaml`, and `secrets.env`
- **WHEN** Komodo syncs from Forgejo repository
- **THEN** stack is deployed with Pangolin routing and secrets injected

#### Scenario: Stack Health Monitoring
- **GIVEN** deployed stacks in Komodo
- **WHEN** a container becomes unhealthy
- **THEN** Komodo alerts and attempts restart per defined restart policy

### Requirement: Zero-Egress Design

The system SHALL minimize cloud egress costs by keeping data processing local.

#### Scenario: Local Lakehouse
- **GIVEN** data stored in Garage S3 on local Docker network
- **WHEN** DuckDB queries Parquet files
- **THEN** all data transfer stays within the local Docker network

#### Scenario: Local LLM Inference
- **GIVEN** llama-swap running on workload host
- **WHEN** agent routes to local model
- **THEN** inference runs locally with no API egress costs

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| Pangolin | `infrastructure/stacks/infrastructure/pangolin/` | VPN + Traefik + Pocket ID + CrowdSec |
| Komodo | `infrastructure/stacks/infrastructure/komodo/` | Container orchestration |
| Pocket ID | `infrastructure/stacks/infrastructure/pocket-id/` | OIDC identity provider |
| Infisical | `infrastructure/infisical/` | Local Infisical dev server |
| Locket | `infrastructure/stacks/*/sidecar.yaml` | Per-stack secret injection sidecar |
| Pulumi | `infrastructure/pulumi/` | Cloud infrastructure as code |
| Ansible | `infrastructure/ansible/` | Server configuration |

## Network Architecture

```
Internet → Traefik (443/80) → Pangolin Gerbil (WireGuard)
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              OCI ARM1       MacBook M4      External
              (Control)      (Workload)      Services
                    │              │
              Pocket ID      Vector DBs
              Komodo UI      Graph DBs
              Infisical      LLM Inference
                             Local Analytics
```

## Constraint: Secret Hygiene

- `.env` SHALL be gitignored (resolved secrets)
- `.infisical.env` SHALL use `infisical://dev-baile/...` references only
- `secrets.env` in stack directories SHALL reference `infisical://` URIs
- NEVER create manual `.env` files; use `infisical export` via mise hooks

## Constraint: Stack Conventions

Each stack directory under `infrastructure/stacks/<category>/<name>/` SHALL contain:
- `compose.yaml` — Docker service definitions
- `pangolin.yaml` — Traefik routing configuration (if web-facing)
- `sidecar.yaml` — Locket sidecar for Infisical injection
- `secrets.env` — Infisical URI references for the stack

## Implementation References

| Component | Path |
|-----------|------|
| Stack Categories | `infrastructure/stacks/` |
| Secrets Template | `.infisical.env` |
| Secrets Management | `infrastructure/SECRETS-MANAGEMENT.md` |
| Pangolin Setup | `infrastructure/PANGOLIN-SETUP.md` |
| Stack Standards | `infrastructure/stacks/GOLD_STANDARD.md` |

## Related Specs

- [infrastructure-stacks](../infrastructure-stacks/spec.md) — Individual stack catalog
- [dagster](../data-pipeline/spec.md) — Pipeline orchestration
