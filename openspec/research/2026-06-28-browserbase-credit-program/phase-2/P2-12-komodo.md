# P2-12 — komodo (Phase 2, Infrastructure)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** infrastructure

## TL;DR

Komodo is the **Docker Compose orchestrator** that deploys and manages the 90 Cianfhoghlaim stacks across the 3 hosts (arm1-oci + bunchloch + cax41-hetzner). It reads TOML procedures from `infrastructure/komodo/stacks/*.toml` and `infrastructure/komodo/procedures/*.toml` and runs the GitOps loop.

The canonical Cianfhoghlaim pattern: every stack has a Komodo procedure TOML that references the stack's `compose.yaml` + `sidecar.yaml` (Locket) + `pangolin.yaml` (6-label).

## Code

| Path | Purpose |
|:--|:--|
| `infrastructure/komodo/servers/servers.toml` | 3 hosts (arm1-oci + bunchloch + cax41-hetzner) |
| `infrastructure/komodo/stacks/*.toml` | Stack deployment configs (90 files) |
| `infrastructure/komodo/procedures/*.toml` | Reusable procedures (e.g., storage-lakehouse.toml, deploy-cognee-bunchloch.toml) |
| `infrastructure/komodo/builder/builder.toml` | Image builder config (if any custom builds) |
| `infrastructure/komodo/variables.toml` | Shared variables (registry URLs, image tags) |

**Canonical stack TOML** (from `infrastructure/komodo/stacks/storage-lakehouse.toml`):

```toml
[[stack]]
name = "lakehouse"
description = "Unified lakehouse with Garage + Lakekeeper + Lance Namespace"
tags = ["host:bunchloch", "tier:lakehouse", "type:data-platform"]

[stack.config]
server_id = "bunchloch"
run_directory = "/etc/komodo/storage/lakehouse"
file_paths = ["compose.yaml", "pangolin.yaml", "sidecar.yaml"]
environment = """
LAKEKEEPER_PORT=8181
LAKEKEEPER_METRICS_PORT=9000
LANCE_NAMESPACE_PORT=8182
"""

[stack.schedule]
enabled = true
cron = "0 4 * * 0"  # weekly Sunday 4am restart for log rotation
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `KOMODO_BASE_URL` | `https://komodo.cianfhoghlaim.ie` | Locket |
| `KOMODO_API_KEY` | `infisical://dev-baile/komodo/api_key` | Locket |
| `KOMODO_API_SECRET` | `infisical://dev-baile/komodo/api_secret` | Locket |
| `SSH_KEY_PATH` | `~/.ssh/komodo_ed25519` | per-host |

## CCC anchors

`infrastructure/komodo/` (4 sub-dirs: servers, stacks, procedures, builder) · `infrastructure/komodo/stacks/*.toml` (90 files) · `infrastructure/komodo/procedures/*.toml` (50+ files) · `infrastructure/komodo/servers/servers.toml` (3 hosts)

Search terms: `"[[stack]]"`, `"server_id"`, `"file_paths"`, `"run_directory"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-09 | Initial Komodo deploy (single host) |
| 2025-12 | Added bunchloch as second host (workloads) |
| 2026-02 | Migrated from Komodo v1 to v2 (TOML-based config) |
| 2026-03 | Added procedures/ subdir (reusable deploy patterns) |
| 2026-04 | Onboarded cax41-hetzner as 3rd host (storage backups) |
| 2026-06 | Added `infrastructure-audit` cron (weekly health check) |

## Anti-patterns

1. Don't put secrets in TOML — use `infisical://...` placeholders
2. Don't run Komodo in a container — it needs host-level Docker access
3. Don't use `latest` tag in image references — pin versions
4. Don't skip `server_id` — it's how Komodo knows which host runs the stack
5. Don't use `run_directory` outside `/etc/komodo/` — that's the Komodo convention
6. Don't put LLM keys in Komodo procedures — use Locket sidecar env injection
7. Don't disable the weekly audit — it catches stuck stacks

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Komodo version | v2 (current) | TOML config, better GitOps support |
| Hosts | arm1-oci + bunchloch + cax41-hetzner | 3-tier (control / workload / backup) |
| Auth | API key + secret (HMAC) | No OIDC overhead for server-to-server |
| Stack config | TOML in git | Diffable, reviewable |
| Procedure reuse | TOML includes with variables | Avoid duplication |
| Image pinning | Always version-pinned | Reproducibility |
| Secrets | Infisical placeholders | No plaintext in git |
| Audit | Weekly cron (`infrastructure-audit`) | Catch stuck stacks |

## Files to read next

`infrastructure/komodo/servers/servers.toml` · `infrastructure/komodo/stacks/storage-lakehouse.toml` · `infrastructure/komodo/procedures/storage-lakehouse.toml` · `.agents/skills/komodo/SKILL.md` · `.agents/skills/kcg-deploy-runbooks/SKILL.md`
