# Agent 16 — Pangolin EE (Reverse Proxy + VPN Gateway)

**Agent:** 16 of 25 (parallel wave, BrowserBase Program 2)
**Date:** 2026-06-28T22:10Z
**Package:** Pangolin Enterprise Edition + Gerbil + Newt + Pocket ID
**Wall clock:** ~7 min
**BrowserBase credits:** ~6 (1 navigation + 4 Firecrawl scrapes + 1 end)
**Spec anchor:** [`P2-11-pangolin.md`](../../../2026-06-28-browserbase-credit-program/phase-2/P2-11-pangolin.md)

## TL;DR

Pangolin is the **identity-aware tunneled reverse proxy** built by Fossorial. EE (`fosrl/pangolin:ee-latest`, pinned `ee-postgresql-1.19.4`) is what we run on `arm1-oci` because we need the PostgreSQL catalog backend (`flags.disable_enterprise_features` can hide EE-only UI on community but we keep EE active). The **blueprint / `pangolin.yaml` model** lets every Docker Compose stack declare a private resource via a **6-label pattern** (`pangolin.private-resources.<key>.name|mode|full-domain|destination-port|protocol|roles[0]`) — we have **17 stacks** doing this across both `infrastructure/stacks/` (legacy, 15 files) and `cianfhoghlaim/stacks/` (v4, 9 files). `Newt 1.13.0` is the WireGuard tunnel agent (`fosrl/newt:1.13.0`); sites are either **continuous-apply** (`--blueprint-file` / container labels) or **one-shot bootstrap** (`--provisioning-blueprint-file`). **OIDC via Pocket ID** is just a generic OAuth2/OIDC IdP in Pangolin (client-id/secret + 4 URLs + JMESPath claim mapping); TinyAuth sits in front of services that lack native SSO. The KCG posture is: `vpn-only` middleware on every internal resource, `tinyauth@file` for everything else, **never** `--no-auth` / `--disable-enterprise-features`, and **always** declare `sites:` in private blueprints (so multi-site failover routing works). Big EE-vs-OSS delta: **public-resource `maintenance` page** is EE-only; **resource policies** (`public-policies`) are reusable across resources; **private HTTP** needs EE + PG; **wildcard resources / wildcard TLS** are EE-only. Refactor opportunities cluster around (a) killing the **`protocol` vs `mode`** drift in our 17 `pangolin.yaml` files (one uses `protocol:` only — that's the legacy form, should normalize to `mode:`), (b) adding `sites:` + `tcp-ports:` to the 9 stacks that omit them, (c) capturing `maintenance:` EE-blocks for our public resources, and (d) consuming the **Integration API** (`pangolin apply blueprint --api-key`) instead of the bespoke `komodo` procedure.

## Code

### What we actually have locally

| Path | What it is |
|:--|:--|
| `infrastructure/stacks/pangolin/compose.yaml` | Pangolin EE + PostgreSQL 17 + Gerbil + Traefik 3.6 + Pocket ID + TinyAuth + Locket sidecar (arm1-oci control plane) |
| `infrastructure/stacks/pangolin/newt.yaml` | `fosrl/newt:1.13.0` tunnel agent for bunchloch |
| `infrastructure/stacks/pangolin/newt.sidecar.yaml` | Locket + Infisical override for Newt env vars |
| `infrastructure/stacks/pangolin/README.md` | 65-line stack overview (now slightly stale; cites 89 stacks, today is 90+) |
| `infrastructure/komodo/stacks/pangolin-core-arm1.toml` | Komodo `[[stack]]` block for the control plane |
| `infrastructure/komodo/stacks/pangolin-tunnels.toml` | Komodo `[[stack]]` + `[[procedure]] deploy-tunnels` for Newt + OLM agents |
| `infrastructure/stacks/GOLD_STANDARD.md:136-153` | Canonical 6-label pattern (public + private) |
| `infrastructure/stacks/oideachais/pangolin.yaml` | **Legacy Traefik `http:` routers** form (NOT blueprint) — replaced by `cianfhoghlaim/stacks/*/pangolin.yaml` for v4 |
| `infrastructure/stacks/lakehouse/pangolin.yaml` | 6-label blueprint form (`private-resources.lakehouse`) |

**17 stacks currently emit a `pangolin.yaml`** (15 in legacy `infrastructure/stacks/`, 9 in v4 `cianfhoghlaim/stacks/`, with overlap):

> Legacy (15): `mlflow`, `oideachais`, `tuatha`, `dozzle`, `lakehouse`, `langfuse`, `cognee`, `forgejo`, `frontend`, `croilar/croilar-convex`, `openchamber`, `croilar/croilar-hono-api`, `falkordb`, `graphiti`, `openclaw`
> v4 (9): `graphiti`, `openchamber`, `cognee`, `tuatha`, `mlflow`, `lakehouse`, `langfuse`, `falkordb`, `openclaw`

### Canonical 6-label blueprint (private HTTP resource)

This is the shape every one of our 9 v4 `cianfhoghlaim/stacks/*/pangolin.yaml` files uses (verbatim from `cianfhoghlaim/stacks/lakehouse/pangolin.yaml:1-12`):

```yaml
# Lakehouse — Pangolin private-resource route
# Routes lakehouse.cianfhoghlaim.ie → lakekeeper (Iceberg REST Catalog) at port 8181.
# TinyAuth protects the route; Lakekeeper has no built-in UI auth.
pangolin:
  private-resources:
    lakehouse:
      name: lakehouse
      mode: http
      full-domain: lakehouse.cianfhoghlaim.ie
      destination-port: 8181
      protocol: http
      roles[0]: tinyauth@file
```

The 6 labels under `pangolin.private-resources.<key>` are **`name`, `mode`, `full-domain`, `destination-port`, `protocol`, `roles[0]`** — confirmed in `infrastructure/stacks/GOLD_STANDARD.md:136-153` and the `openspec/specs/infrastructure-stacks/spec.md:644-651` scenario ("A pangolin.yaml is malformed … rename `destination_port` to `destination-port` (hyphen)").

### Container-label equivalent (for stack-internal sites)

Per `docs.pangolin.net/manage/blueprints` "Container Labels Format", the same schema flattened as Docker labels:

```yaml
labels:
  - "pangolin.private-resources.lakehouse.name=lakehouse"
  - "pangolin.private-resources.lakehouse.mode=http"
  - "pangolin.private-resources.lakehouse.full-domain=lakehouse.cianfhoghlaim.ie"
  - "pangolin.private-resources.lakehouse.destination-port=8181"
  - "pangolin.private-resources.lakehouse.protocol=http"
  - "pangolin.private-resources.lakehouse.roles[0]=tinyauth@file"
```

### Blueprint resource schema (full, from upstream docs)

**`private-resources.<key>` fields** (everything we touch + the things we *should* add):

| Field | Type | Required | Notes / EE? |
|:--|:--|:--|:--|
| `name` | string | yes | Human-readable |
| `mode` | string | yes | `host`, `cidr`, `http`, `ssh` (preferred over `protocol`) |
| `protocol` | string | (legacy) | normalized to `mode` |
| `sites` | array | optional* | Multi-site failover; optional when deploying from a Newt |
| `site` | string | deprecated | use `sites` |
| `destination` | string | mode-cond. | host / IP / CIDR / domain (domain needs `alias`) |
| `destination-port` | integer | for http | **HYPHEN not underscore — `stack-doctor` fails exit 8** |
| `full-domain` | string | for http | FQDN exposed via Olm client |
| `ssl` | bool | no | edge TLS termination at the site |
| `scheme` | string | no | `http` or `https` upstream |
| `tcp-ports` | string | for host/cidr | comma-sep, ranges OK, `*` = all |
| `udp-ports` | string | for host/cidr | same shape |
| `disable-icmp` | bool | no | default false |
| `alias` | string | for domain dest | FQDN with optional wildcards |
| `roles` | array | yes | `Admin` is reserved; cannot be listed |
| `users` | array | no | direct user identifiers |
| `machines` | array | no | machine identities (client creds) |
| `auth-daemon` | object | no | `{ pam, mode: site|remote|native, port }` |

**`public-resources.<key>` extras** we don't currently use but should consider:

- `auth.pincode` / `auth.password` / `auth.sso-enabled` / `auth.sso-roles` / `auth.sso-users` / `auth.whitelist-users` / `auth.basic-auth` / `auth.auto-login-idp`
- `rules[]` with `action: allow|deny|pass`, `match: cidr|path|ip|country|asn|region`, `priority`
- `headers[]` static header injection
- **`maintenance: { enabled, type: forced|automatic, title, message, estimated-time }`** — **(EE)**
- `auth-daemon` (same as private)
- `host-header`, `tls-server-name` upstream overrides
- `targets[]` with `site`, `hostname`, `port`, `method: http|https|h2c`, `path`, `path-match`, `rewrite-path`, `priority`, `healthcheck{}`

**`public-policies.<key>`** — reusable across many resources. This is the path that maps to our `tinyauth@file` pattern at scale: define one policy, point many resources at it.

**`sites.<key>`** — site-level settings: `name`, `docker-socket-enabled` (default `true`, which is what makes our container-label discovery work).

### Newt CLI flags we actually use / should use

`fosrl/newt:1.13.0`, pinned in `infrastructure/stacks/pangolin/newt.yaml:20`:

- `PANGOLIN_ENDPOINT` — required, our env: `https://pangolin.cianfhoghlaim.ie`
- `NEWT_ID` / `NEWT_SECRET` — required, from Infisical via Locket (`infisical://dev-baile/newt/{id,secret}`)
- `DOCKER_SOCKET=/var/run/docker.sock` — enables container-label discovery
- `LOG_LEVEL=INFO`
- `--blueprint-file` (declarative, **continuous** apply) **or** `--provisioning-blueprint-file` (one-shot bootstrap)
- `--metrics` (Prometheus), `--otlp` (OTEL), `--pprof` — we don't enable these yet
- `--tls-client-cert-file` / `--tls-client-key` / `--tls-client-ca` — split PEM mTLS
- `--disable-clients` / `--disable-ssh` — if we ever want a pure server-side relay

### Composition — the "control plane + workload host" pattern

```yaml
# arm1-oci (control plane) — /infrastructure/stacks/pangolin/compose.yaml
services:
  postgres:    { image: postgres:17 }             # Pangolin catalog DB
  pangolin:    { image: fosrl/pangolin:ee-latest }  # identity + UI + API
  gerbil:      { image: fosrl/gerbil:latest }      # WireGuard tunnel controller
  traefik:     { image: traefik:v3.6.0, network_mode: service:gerbil }
  pocket-id:   { image: ghcr.io/pocket-id/pocket-id:latest }  # OIDC IdP
  tinyauth:    { image: ghcr.io/steveiliop56/tinyauth:v4 }    # forward auth
  locket:      { image: ghcr.io/bpbradley/locket:infisical }  # secret injection

# bunchloch (workload host) — /infrastructure/stacks/pangolin/newt.yaml
services:
  newt:        { image: fosrl/newt:1.13.0, DOCKER_SOCKET, NET_ADMIN, NET_RAW, SYS_MODULE }
```

## Env

| Env var | Source | Set in | Purpose |
|:--|:--|:--|:--|
| `PANGOLIN_ENDPOINT` | `https://pangolin.cianfhoghlaim.ie` | `newt.yaml:24`, `pangolin-core-arm1.toml:18` | Newt control-plane URL |
| `NEWT_ID` | `infisical://dev-baile/newt/id` | Locket | Newt site ID |
| `NEWT_SECRET` | `infisical://dev-baile/newt/secret` | Locket | Newt site secret |
| `PANGOLIN_API_URL` | `https://pangolin.cianfhoghlaim.ie/api/v1` | Locket | Integration API base |
| `PANGOLIN_API_KEY` | `infisical://dev-baile/pangolin/api_key` | Locket | Integration API key (Komodo provisioning) |
| `PANGOLIN_SCRIPTING_INTEGRATION_KEY` | Infisical | Komodo | Per `P2-11-pangolin.md` drift log |
| `POSTGRES_PASSWORD` | Infisical | Locket | Pangolin catalog DB |
| `POCKETID_CLIENT_ID` / `POCKETID_CLIENT_SECRET` | Infisical | Locket | TinyAuth → Pocket ID OIDC |
| `POCKETID_ENCRYPTION_KEY` | Infisical | `compose.yaml:109` | Pocket ID session encryption |
| `INFISICAL_CLIENT_ID` / `INFISICAL_SECRET_FILE` | Infisical | `compose.yaml:173-206` | Locket-side secret resolution |
| `LOCKET_MODE` | `watch` | `pangolin-core-arm1.toml:19` | Hot-reload secrets |
| `SERVER_SECRET` | Infisical | env (optional override) | Encrypts sensitive Pangolin data; min 8 chars |
| `POSTGRES_CONNECTION_STRING` | Infisical | env (EE with external PG) | Overrides local Postgres if set |

## CCC anchors

Search terms to find prior art and patterns:

- `private-resources` → `infrastructure/stacks/<name>/blueprint.yaml` (70+ files — every stack)
- `pangolin.yaml` → `infrastructure/stacks/GOLD_STANDARD.md`, `infrastructure/stacks/pinchflat/blueprint.yaml`, `openspec/changes/add-openclaw-stack-and-channel-fanout/proposal.md`
- `destination-port` → `openspec/specs/agent-memory-systems/spec.md:91-109`, `infrastructure/stacks/oideachais/pangolin.yaml`
- `tinyauth@file` → only in `cianfhoghlaim/stacks/*/pangolin.yaml` (v4 shape)
- `pangolin.private-resources.<key>` → CCC HITS confirm the canonical 6-label shape

**Local files to read next:**

- `infrastructure/stacks/GOLD_STANDARD.md` (the canonical 6-label definition)
- `infrastructure/stacks/pangolin/{compose,newt.yaml,newt.sidecar.yaml,secrets.env}.yaml`
- `infrastructure/komodo/stacks/pangolin-{core-arm1,tunnels}.toml`
- `infrastructure/stacks/oideachais/pangolin.yaml` (legacy Traefik form, for migration)
- All 9 `cianfhoghlaim/stacks/*/pangolin.yaml` (v4 form)
- `openspec/specs/infrastructure-stacks/spec.md` (formal Requirement scenarios for malformed-blueprint detection)
- `.agents/skills/pangolin/SKILL.md` (router skill)

## Drift log

| Date | Event |
|:--|:--|
| 2025-11 | Initial Pangolin OSS deploy (arm1-oci) |
| 2026-01 | Newt tunnels added (bunchloch ↔ arm1-oci) |
| 2026-03 | Pocket ID SSO integration (OIDC) |
| 2026-04 | Migrated OSS → EE for PostgreSQL catalog |
| 2026-06 | `PANGOLIN_SCRIPTING_INTEGRATION_KEY` added (Komodo provisioning) |
| 2026-06-28 | v4 consolidation: stacks moved to `cianfhoghlaim/stacks/*/pangolin.yaml` (sibling to legacy) |
| 2026-06-28 | Today: confirmed blueprint schema (mode/protocol dual-field, public-policies, maintenance EE), EE licensing terms (free < $100K USD gross revenue), Integration API endpoint `PUT /org/{orgId}/blueprint` |

## Anti-patterns

1. **Don't use `protocol:` alone.** Use `mode:`. `protocol` is accepted for backward compat but normalized — and the codebase mixes them (`protocol: http` in our v4 stacks is **legacy** form, not current upstream).
2. **Don't use `_` instead of `-`.** `destination_port` (underscore) → `stack-doctor` exit 8. Always `destination-port`.
3. **Don't bypass Pocket ID SSO.** `roles[0]: tinyauth@file` is fine; `--no-auth` / public-resource with `auth` block omitted is **NOT** for anything in production.
4. **Don't use the public internet for control-plane traffic.** Newt ↔ Pangolin over WireGuard (`PANGOLIN_ENDPOINT` is reachable, but data-plane goes through Gerbil).
5. **Don't hardcode `PANGOLIN_API_KEY` / `NEWT_*`.** Always Locket + Infisical.
6. **Don't use Pangolin's built-in SQLite for production.** Use Postgres 17 (the bundled container in `compose.yaml`) or external `POSTGRES_CONNECTION_STRING`.
7. **Don't update Pangolin EE without re-running `infrastructure-audit`** — Gerbil/Traefik/pangolin image tags move together.
8. **Don't put `Admin` in `roles[]` or `sso-roles[]`.** It's reserved and rejected by the blueprint validator.
9. **Don't use `proxy-port` for HTTP resources.** It's only valid for `tcp` / `udp`. HTTP resources use `full-domain` + LetsEncrypt.
10. **Don't duplicate resource definitions across `pangolin.yaml` + `blueprint.yaml` + Komodo `toml`.** Pick one source of truth per resource; for per-stack private resources, the v4 `pangolin.yaml` is canonical.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Edition | Pangolin EE | PostgreSQL catalog, resource policies, maintenance page, wildcard resources |
| Image pin | `fosrl/pangolin:ee-latest` | Track stable (drift-log says `ee-postgresql-1.19.4` was latest as of 2026-06) |
| Tunnel agent | Newt 1.13.0 (`fosrl/newt:1.13.0`) | Native, supports `--blueprint-file`, mTLS, OTEL/Prom |
| SSO | Pocket ID OIDC + TinyAuth forward auth | Self-hosted, passkey-based, generic OAuth2/OIDC IdP in Pangolin |
| Catalog DB | Postgres 17 (bundled container) | HA + EE-only feature; external `POSTGRES_CONNECTION_STRING` allowed for migration |
| Source of truth | `pangolin.yaml` per stack (6-label) | GitOps; Komodo deploys; spec-validated |
| Blueprint apply mode | `--blueprint-file` (continuous) | Compose-driven sites auto-update on stack change |
| Resource auth pattern | `roles[0]: tinyauth@file` (private) | Re-usable forward-auth; admin uses Pocket ID directly |
| License | Free (< $100K USD gross revenue — we qualify) | No payment needed; upgradeable to Starter/Scale later |
| Backup | Daily dump of `pangolin` Postgres DB | Quick restore on disaster |

## §8 Refactor opportunities

Concretely actionable based on what the upstream docs allow vs. what we actually ship today.

### R1. Normalize `protocol:` → `mode:` across all 9 v4 stacks

`cianfhoghlaim/stacks/{graphiti,openchamber,cognee,tuatha,mlflow,lakehouse,langfuse,falkordb,openclaw}/pangolin.yaml` all use `protocol: http` — that's the **legacy field**. Upstream docs say `mode` is preferred. Refactor: one-shot sed/script to rename `protocol:` → `mode:` (no semantic change, just forward-compat). Stack-doctor should pass either way.

### R2. Add `sites:` to private resources that omit it

Currently our v4 `pangolin.yaml` files omit `sites:` and rely on Newt's "assign to my site" default. That's brittle when we have **multiple Newt sites** (e.g., `newt-oci` + future `newt-bunchloch` for HA — `pangolin-tunnels.toml` already has the `newt-oci` skeleton). Refactor: add `sites: - arm1-oci` (or whatever the site ID is) to every private-resource block so multi-site failover actually works.

### R3. Migrate to **public-policies** for the TinyAuth pattern

Today: `roles[0]: tinyauth@file` is **repeated** in every v4 `pangolin.yaml`. Upstream lets us define one `public-policies.tinyauth-members` (or `private-policies`, when added) and reference it via `policy: tinyauth-members`. Refactor: define once, replace 9 inline `roles[0]` lines with `policy: tinyauth-members`. Cuts ~18 lines + 9 places to update on TinyAuth change.

### R4. Capture EE `maintenance:` block for public-facing stacks

`lakehouse.cianfhoghlaim.ie`, `langfuse.cianfhoghlaim.ie`, `cognee.cianfhoghlaim.ie`, `falkordb.cianfhoghlaim.ie`, `mlflow.cianfhoghlaim.ie`, `graphiti.cianfhoghlaim.ie` are all `mode: http` private resources behind TinyAuth — **none are public**. But `oideachais.cianfhoghlaim.ie`, `api.oideachais.cianfhoghlaim.ie`, `pangolin.cianfhoghlaim.ie`, `openchamber.cianfhoghlaim.ie`, `auth.cianfhoghlaim.ie` ARE public (Traefik `entryPoints: [https]`, `Host(\`oideachais.cianfhoghlaim.ie\`)`). For each of those public routes, add `maintenance: { enabled: true, type: automatic, title, message, estimated-time }` so a 30-min outage during, say, a Dagster restart doesn't 502 users. **(EE)** — confirms our EE license is paying off.

### R5. Wire Newt metrics to the Langfuse/Lakehouse observability stack

Newt supports `--metrics` (Prometheus on `:2112`) and `--otlp` (OTLP traces/metrics). We have a full Langfuse + MLflow + Logfire stack — feeding Newt bandwidth + connection counts there gives us alerting when WireGuard peers drop. Today: zero Newt telemetry exported. Refactor: set `NEWT_METRICS_PROMETHEUS_ENABLED=true` + scrape from `langfuse-prometheus` (or whichever) + Grafana panel.

### R6. Replace `infrastructure/stacks/oideachais/pangolin.yaml` with the blueprint form

This file is the **legacy Traefik `http: routers:` form**, NOT a blueprint. It coexists with `infrastructure/komodo/stacks/pangolin-*` TOML that already drives deployment. Refactor: convert the 5 routers (`oideachais-web`, `-api`, `-dagster`, `-agent-os`, `-adk-agents`) into a single blueprint with 5 `public-resources` (each with the appropriate `auth.sso-enabled` + `targets[]`). Removes the bespoke Traefik config entirely; lets us use `--blueprint-file` + Komodo's existing run-directory.

### R7. Consume the Integration API from Komodo (no more bespoke TOML)

Today: `pangolin-core-arm1.toml` and `pangolin-tunnels.toml` are Komodo procedures that deploy via `[[stack]]` (Docker Compose). Upstream offers `pangolin apply blueprint --api-key <id.secret> --endpoint ... --org <org_id> --file /path/to/blueprint.yaml`. Refactor: replace the Komodo TOML with a single `apply-blueprint` procedure that calls the Pangolin CLI (or the REST `PUT /org/{orgId}/blueprint` API). Single source of truth, no Compose indirection for the resource layer.

### R8. Pin Pangolin EE image with SemVer, not `:ee-latest`

`infrastructure/stacks/pangolin/compose.yaml:39` uses `fosrl/pangolin:ee-latest`. We learned the hard way in other stacks that `:latest` makes rollback impossible. Refactor: pin `fosrl/pangolin:ee-postgresql-1.19.4` (current stable per `P2-11-pangolin.md:97`), bump deliberately.

### R9. Add `disable_email_verification: false` and `disable_signup_without_invite: true` explicitly

Upstream `config.yml` defaults to `require_email_verification: false` and `disable_signup_without_invite: false`. Our posture (admin-only onboarding) wants the latter `true` and the former stays false (we don't email-verify Pocket ID passkey users — Pocket ID does). Refactor: explicit flags in `config.yml`, document the rationale.

### R10. Skill update — `.agents/skills/pangolin/SKILL.md` should cross-link this report

The skill is referenced as the router for VPN+Traefik+PocketID. It should link to `agent-16-pangolin.md` + the 6-label pattern definition in `infrastructure/stacks/GOLD_STANDARD.md`. Also: pull the **canonical blueprint schema** (the table in §Code above) into the skill so adding a new stack doesn't require re-deriving field names.

---

**Cross-agent dependencies:**

- **Agent 11 (Graphiti)**: shares `cianfhoghlaim/stacks/graphiti/pangolin.yaml` and `graphiti.cianfhoghlaim.ie` route — same `roles[0]: tinyauth@file` pattern. R3 above (public-policies) cuts both stacks' definitions.
- **Agent 12 (Cognee)**: same shared pattern (`cognee.cianfhoghlaim.ie`, `cognee` blueprint).
- **Agent 7 (FalkorDB)**: same (`falkordb.cianfhoghlaim.ie`).
- **Agent 4 (langfuse) / Agent 5 (mlflow)**: same.

The 9 v4 stacks all share **R1, R2, R3, R4** — refactor as a single change under `openspec/changes/2026-06-28-pangolin-blueprint-v4-cleanup/`.