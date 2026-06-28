# P2-11 — pangolin (Phase 2, Infrastructure)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** infrastructure

## TL;DR

Pangolin is the **reverse proxy + VPN gateway** that fronts every Cianfhoghlaim service with HTTPS + Pocket ID SSO. It runs on arm1-oci (Oracle Cloud London ARM64) as the **control plane** and on bunchloch as the **workload host**, with Newt tunnels connecting them.

The canonical pattern: every stack has a `pangolin.yaml` with 6-label pattern (`private-resources.<name>.<protocol>.<port>.<subdomain>.<host>`).

## Code

| Path | Purpose |
|:--|:--|
| `stacks/pangolin/` | Docker Compose stack (Pangolin + Gerbil + Traefik) |
| `stacks/pangolin/pangolin.yaml` | Stack's pangolin.yaml (6-label pattern) |
| `infrastructure/komodo/stacks/pangolin-core-arm1.toml` | Komodo procedure for control plane |
| `infrastructure/komodo/stacks/pangolin-tunnels.toml` | Komodo procedure for Newt tunnels |
| `infrastructure/pangolin/newt/` | Newt tunnel client configs (bunchloch) |
| `infrastructure/pangolin-config/config.yml` | Main Pangolin config (sites, targets, resources) |

**Canonical `pangolin.yaml` snippet** (from `stacks/lakehouse/pangolin.yaml`):

```yaml
private-resources:
  lakehouse-garage:
    name: "Lakehouse Garage S3 (bunchloch)"
    mode: "http"
    destination: "lakehouse-garage"
    destination-port: 3900
    full-domain: "lakehouse-garage.lakehouse.cianfhoghlaim.ie"
    protocol: "http"
    roles:
      - "Member"
  lakehouse-postgres:
    name: "Lakehouse Postgres (bunchloch)"
    mode: "http"
    destination: "lakehouse-postgres"
    destination-port: 5432
    full-domain: "lakehouse-postgres.lakehouse.cianfhoghlaim.ie"
    protocol: "http"
    roles:
      - "Member"
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `PANGOLIN_API_URL` | `https://pangolin.cianfhoghlaim.ie/api/v1` | Locket |
| `PANGOLIN_API_KEY` | `infisical://dev-baile/pangolin/api_key` | Locket (Integration API) |
| `NEWT_ID` | `infisical://dev-baile/newt/id` | Locket |
| `NEWT_SECRET` | `infisical://dev-baile/newt/secret` | Locket |
| `POCKET_ID_URL` | `https://pocket-id.cianfhoghlaim.ie` | Locket |

## CCC anchors

`stacks/pangolin/` · `infrastructure/pangolin-config/config.yml` · `infrastructure/komodo/stacks/pangolin-*.toml` · `infrastructure/pangolin/newt/`

Search terms: `"private-resources"`, `"pangolin.yaml"`, `"newt"`, `"destination-port"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-11 | Initial Pangolin deploy (arm1-oci) |
| 2026-01 | Newt tunnels added (bunchloch ↔ arm1-oci) |
| 2026-03 | Pocket ID SSO integration (OIDC) |
| 2026-04 | Migrated from Pangolin OSS to EE for PostgreSQL catalog |
| 2026-06 | PANGOLIN_SCRIPTING_INTEGRATION_KEY added (for Komodo provisioning) |
| 2026-06-28 | v4 consolidation: stacks moved to `cianfhoghlaim/stacks/pangolin/` (sibling to legacy `infrastructure/stacks/pangolin/`) |

## Anti-patterns

1. Don't bypass Pocket ID SSO — every resource MUST require auth
2. Don't use the public internet for control-plane traffic — always via Newt tunnels
3. Don't hardcode the `PANGOLIN_API_KEY` — use Locket + Infisical
4. Don't use `--no-auth` mode for any production resource
5. Don't skip the 6-label naming pattern — Komodo procedures rely on it
6. Don't use Pangolin's built-in DB for production — use PlanetScale Postgres (Pangolin EE)
7. Don't update Pangolin to a new major version without re-running `infrastructure-audit`

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Reverse proxy | Pangolin EE | OSS has no Postgres catalog; we need it |
| Tunnel client | Newt (WireGuard) | Native to Pangolin, faster than WireGuard directly |
| SSO | Pocket ID (OIDC) | Self-hosted, no external IdP dependency |
| Catalog DB | PlanetScale Postgres | HA + managed |
| Config storage | `config.yml` in git (encrypted secrets via sops) | GitOps-first |
| Stack config | `pangolin.yaml` per stack (6-label pattern) | Komodo-driven provisioning |
| Backup strategy | Daily dump of `pangolin` DB | Quick restore on disaster |
| Version pin | `fosrl/pangolin:ee-postgresql-1.19.4` | Latest stable as of 2026-06 |

## Files to read next

`stacks/pangolin/compose.yaml` · `infrastructure/pangolin-config/config.yml` · `infrastructure/komodo/stacks/pangolin-core-arm1.toml` · `.agents/skills/pangolin/SKILL.md` · `.agents/skills/kcg-pangolin-stack/SKILL.md`
