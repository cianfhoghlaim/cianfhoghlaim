# Forgejo Runner — Self-Hosted CI/CD Actions Runner

## Overview

The Forgejo Runner executes CI/CD workflows defined in `.forgejo/workflows/` using the same Actions syntax as GitHub Actions. It connects to the self-hosted Forgejo instance at `git.cianfhoghlaim.ie` and provides Docker-in-Docker container job execution. Powered by the same `act_runner` engine that Gitea Actions uses.

## Why This Matters for Kings' College Galway

Every commit to this monorepo triggers automated workflows: Python linting (ruff), TypeScript typechecking (bun), Dagster asset validation, model conversion verification, and OpenSpec schema checks. The Forgejo Runner executes these on the ARM1-OCI control plane without leaving the private network — no GitHub, no external CI service, no secrets leaving the infrastructure mesh. This self-hosted CI loop is the enforcement mechanism for code quality across all 5 programming languages and 89 stacks.

## Key Features

- **GitHub Actions-compatible** — Same YAML syntax, same `uses:` directive, same `${{ }}` expressions
- **Docker-in-Docker** — Run containerised build/test jobs without external Docker registries
- **Self-hosted** — Zero dependency on GitHub, GitLab, or any external CI provider
- **ARM64-native** — Runs on the OCI Ampere A1 without emulation

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/storage/forgejo-runner
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. The runner connects to `git.cianfhoghlaim.ie` using a registration token generated from the Forgejo admin panel.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `FORGEJO_RUNNER_NAME` | No | Runner display name in Forgejo | `forgejo-runner` |
| `FORGEJO_RUNNER_LABELS` | No | Runner labels for job matching | `ubuntu-latest:docker://...` |
| `FORGEJO_URL` | No | Forgejo instance URL | `https://git.cianfhoghlaim.ie` |
| `FORGEJO_RUNNER_TOKEN` | Yes | Registration token from Forgejo admin panel | — |

## Access

- **Status**: Visible in Forgejo at `https://git.cianfhoghlaim.ie/admin/actions/runners`
- **Network**: Shared `pangolin` Docker network for Forgejo connectivity
- **Auth**: Registration token-based (one-time setup per runner)

## Upstream

- **Repository**: <https://code.forgejo.org/forgejo/runner>
- **Documentation**: <https://forgejo.org/docs/latest/user/actions/>
- **Latest**: v5.0 — updated act_runner engine, improved ARM64 support, Docker-in-Docker stability fixes

## Screenshot

Headless CI service. Runner status is visible in the Forgejo admin panel under Site Administration > Actions > Runners, showing online/offline status, labels, and last job execution time.
