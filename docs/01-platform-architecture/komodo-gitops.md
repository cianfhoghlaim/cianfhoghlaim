---
title: 'Komodo GitOps'
domain: 'platform_architecture'
status: 'stable'
description: 'Komodo GitOps deployment orchestration for the Cianfhoghlaim platform.'
read_when:
  - deploying a new stack
  - triggering a Komodo sync
  - debugging a deployment failure
updated: '2026-06-13'
truth: sole
ccc_query_hints:
  - komodo gitops deployment
---

# Komodo GitOps

> For the full project identity + quadrant map, see
> [`docs/00-core/CLAUDE.md`](../../00-core/CLAUDE.md).
> Komodo is the **deploy orchestration layer** — it lives in
> `infrastructure/komodo/` and deploys the 88 Docker Compose stacks
> under `infrastructure/stacks/`.

## Where things live (post-restructure)

| Component | Path |
|---|---|
| Komodo CLI invocation | `mise run komodo:sync` (from root `mise.toml`) |
| Komodo stack definitions | `infrastructure/komodo/stacks/*.toml` |
| Stack Compose files | `infrastructure/stacks/{category}/{stack}/compose.yaml` |
| Komodo procedures (5-stage deploy) | `infrastructure/komodo/procedures/*.toml` |
| Stack secrets | `infrastructure/stacks/{category}/{stack}/secrets.env` (Infisical URI refs) |
| Pocket ID SSO | `infrastructure/stacks/infrastructure/pocket-id/` |
| Forgejo (control-plane git) | `infrastructure/stacks/infrastructure/forgejo/` |
| Pulumi IaC | `infrastructure/pulumi/{project}/` |
| Ansible bootstrap | `infrastructure/ansible/` |

## Triggering a Komodo sync

From the repo root:

```bash
mise run komodo:sync
```

Or directly via the Komodo CLI if installed:

```bash
komodo sync
```

The sync re-reads `infrastructure/stacks/*/compose.yaml` and reapplies
the desired state.

## 5-stage deploy procedure (per stack)

For new stacks, the procedure `infrastructure/komodo/procedures/deploy-{stack}.toml` typically runs:

1. **prereqs** — verify Pangolin tunnel + Komodo core are up
2. **substrate** — bring up `infrastructure/stacks/storage/{lakehouse,garage,lakekeeper}`
3. **ai-gateways** — bring up `infrastructure/stacks/engineering/{litellm,lancedb,langfuse}`
4. **app** — bring up the target stack itself
5. **routes** — register Pangolin routes; health checks

See any `infrastructure/komodo/procedures/deploy-*.toml` for the
canonical template.

## Stacks deployed by Komodo (88 total, by category)

| Category | Count | Examples |
|---|---|---|
| `infrastructure/` | ~12 | pangolin, komodo, pocket-id, forgejo, dnsserver, dozzle, r2, motherduck, planetscale, monitoring |
| `engineering/` | ~30 | litellm, mlx-omni, invokeai, crawl4ai, coder, windmill, MCPJungle, DevDocs, n8n, dagster, convex, pydantic-gateway, mathesar, agent-os, oideachais, … |
| `machine_learning/` | ~15 | cognee, graphiti, langfuse, lmnr, olake, qdrant, memgraph, falkordb, lancedb, mlflow, logfire, nimtable, docling-serve, dots-ocr, paddleocr, olmocr, unstract, risingwave |
| `storage/` | ~8 | garage, lakehouse, lakekeeper, lakefs, forgejo-runner, beszel, croilar-postgres |
| `tools/` | ~10 | cal-diy, n8n, agentic-scraping, … |
| `browser/` | ~3 | sruth_browser, stagehand_proxy |

## Infisical + Locket

Every stack uses an Infisical URI in `secrets.env`:

```bash
# Example: infrastructure/stacks/engineering/dagster/secrets.env
DAGSTER_PORT=3335
USE_DUCKLAKE=true
AWS_ACCESS_KEY_ID=infisical://dev-baile/garage/aws_access_key_id
```

`mise` auto-hydrates `.env` on directory entry. Locket sidecars
inject secrets at container start.

See [`infrastructure/SECRETS-MANAGEMENT.md`](../../../infrastructure/SECRETS-MANAGEMENT.md).

## See also

- [`infrastructure/README.md`](../../../infrastructure/README.md) — infra quadrant overview
- [`infrastructure/AGENTS.md`](../../../infrastructure/AGENTS.md) — agent instructions for infra
- [`infrastructure/PANGOLIN-SETUP.md`](../../../infrastructure/PANGOLIN-SETUP.md) — VPN + tunnel setup
- [`docs/01-platform-architecture/pangolin-networking.md`](../../01-platform-architecture/pangolin-networking.md)
- [`docs/01-platform-architecture/secrets-management.md`](../../01-platform-architecture/secrets-management.md)
- [`docs/01-platform-architecture/infrastructure-stacks.md`](../../01-platform-architecture/infrastructure-stacks.md)
