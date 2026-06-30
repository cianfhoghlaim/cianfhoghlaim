---
name: infrastructure-stacks
description: The KCG 70+ Docker Compose stacks + the 6-file GOLD_STANDARD pattern (compose.yaml + sidecar.yaml + secrets.env + pangolin.yaml + blueprint.yaml + .env.example) + the stack-doctor 4-gate check + the Pangolin private-resources 6-label shape + the Infisical + Locket + mise 3-way secrets contract + the Komodo deploy procedure template. Use when adding a new stack, validating the existing inventory, wiring a Pangolin private resource, or wiring a Locket-injected secret.
---

# Infrastructure Stacks

## Overview

The Cianfhoghlaim platform deploys **70+ Docker Compose stacks** across
2 hosts:

- **Control plane** (`arm1-oci` — 4-core ARM, 16 GB RAM): identity
  (Pocket ID), routing (Pangolin), orchestration (Komodo), secrets
  (Infisical), observability (Langfuse, MLflow, RAGAS), the openclaw
  chat gateway, the oideachais ADK agents.
- **Workload host** (`bunchloch` — MacBook M4 Max, 128 GB RAM):
  memory-intensive workloads (LanceDB, Graphiti, FalkorDB, Cognee,
  the leabharlann Dagster container, the oideachais lakehouse).

Each stack follows the **6-file GOLD_STANDARD pattern**:

1. `compose.yaml` — the Docker Compose service definitions
2. `sidecar.yaml` — the Locket sidecar (secret injection at runtime)
3. `secrets.env` — the Infisical `infisical://dev-baile/...` references
4. `pangolin.yaml` — the Pangolin private-resources 6-label shape
5. `blueprint.yaml` — the Komodo stack metadata (name, tags, deps)
6. `.env.example` — the non-secret defaults (hostname, TZ, etc.)

`bun run validate-stacks` (the `stack-doctor` turbo task) runs the
4-gate check on every stack in the inventory.

## The 4-gate stack-doctor check

1. **Compose parses** — `docker compose -f compose.yaml config` exits 0.
2. **Sidecar wires** — `docker compose -f compose.yaml -f sidecar.yaml config`
   shows `locket` as a `service_healthy` dependency.
3. **Pangolin 6-label** — every `pangolin.yaml` has
   `name`, `mode`, `full-domain`, `destination-port`, `protocol`,
   `roles`.
4. **Infisical synced** — every `secrets.env` line resolves via
   `bun run scripts/init-vault.ts` + `mise run secrets:init`.

## The 6-label Pangolin private-resources shape

```yaml
# cianfhoghlaim/stacks/<name>/pangolin.yaml
resources:
  <name>:
    name: <name>
    mode: private           # private | public
    full-domain: <name>.cianfhoghlaim.ie
    destination-port: <port>
    protocol: https         # https | http | tcp
    roles:                  # member | admin | etc.
      - member
```

## The Komodo deploy procedure template (5-stage)

```toml
# infrastructure/komodo/procedures/deploy-<stack>-<host>.toml
[procedure]
name = "deploy-<stack>-<host>"

[[step]]
name = "prereqs"
run = "mise run secrets:init"

[[step]]
name = "locket-volume"
run = "docker volume create <stack>_locket"

[[step]]
name = "compose-up"
run = "docker compose -f compose.yaml -f sidecar.yaml up -d"

[[step]]
name = "pangolin-routes"
run = "pangolin apply pangolin.yaml"

[[step]]
name = "health-check"
run = "curl --fail https://<name>.cianfhoghlaim.ie/health"
```

## Cross-references

- `.agents/skills/secrets-management/SKILL.md` — the Infisical +
  Locket + mise 3-way contract
- `.agents/skills/komodo/SKILL.md` — the Komodo orchestration
  patterns
- `.agents/skills/pangolin/SKILL.md` — the Pangolin routing patterns
- `.agents/skills/kcg-pangolin-stack/SKILL.md` — the Pangolin
  convergence architecture
- `.agents/skills/kcg-infrastructure-audit/SKILL.md` — the
  `infrastructure/audit/` scripts
- `infrastructure/AGENTS.md` — the full stack inventory + the 4
  priority compose stacks (oideachais, litellm, langfuse, lakehouse)
- `infrastructure/komodo/procedures/` — the deploy procedures
- `infrastructure/komodo/stacks/` — the stack TOMLs
- `infrastructure/pangolin.yaml` — the Pangolin resources
- `openspec/specs/infrastructure-stacks/spec.md` — the canonical spec

## Email-triage stack row (2026-06-29)

The new `mailcow-dockerized/` stack (the export spine for the
email-inbox pipeline) is provisioned on `bunchloch` (the M4 Max
workload host) and uses the standard 6-file GOLD_STANDARD pattern.
The 3 Pangolin private resources are:

- `mail.cianfhoghlaim.ie` (webmail/IMAPS, port 443, public)
- `imap.cianfhoghlaim.ie` (port 993, internal — bound to
  `127.0.0.1` only)
- `smtp.cianfhoghlaim.ie` (port 587, internal — bound to
  `127.0.0.1` only, receive-only in v1)

The 4 per-account IMAP credentials are stored as
`infisical://dev-baile/mailcow/imap_credentials/<account>` and
injected via the Locket sidecar. The full mailcow wiring (5 Komodo
stages + 8 Dagster inbox assets + 12 vault refs) is documented in
[`.agents/skills/oideachais-email-triage/SKILL.md`](../oideachais-email-triage/SKILL.md).

> **Note:** the mailcow-dockerized stack row itself is the
> infrastructure sub-agent's scope. This entry is a cross-reference
> only.

---

## Agent-platform cluster omnibus procedure (added 2026-06-30)

The `deploy-agent-platform-cluster-bunchloch` Komodo procedure brings up the 8-stack agent-platform cluster in dependency order, with `--skip=<foundation|observability|memory|surfaces>` flags for partial re-deploys:

- **Stage 0** — pre-reqs (Pangolin + Pocket ID + Infisical + Bunchloch resource ceiling check)
- **Stage 1** — `foundation` (lakehouse: Garage S3 + Postgres + Lakekeeper)
- **Stage 2** — `observability` (litellm + langfuse + mlflow + logfire)
- **Stage 3** — `memory` (cognee + graphiti + lancedb)
- **Stage 4** — `surfaces` (openclaw + openchamber + hermes)
- **Stage 5** — health checks (8 stacks + paperless-ngx + 4 OCR stacks)
- **Stage 6** — validate (`bun run validate-stacks`)

The `hermes` stack itself is the 89th stack (88 + hermes) at `bonneagar/stacks/hermes/`. Its 7-file GOLD_STANDARD shape matches `openclaw/` and `openchamber/`.
