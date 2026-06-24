# Oideachais Stack

The Celtic Education Lakehouse Engine — the production deployment
of the `oideachais/` uv workspace member. This stack wires the
3 application services (Dagster, FastAPI, TanStack Start) to the
shared LLM gateway (LiteLLM), the lakehouse (Garage S3 +
Postgres + Lakekeeper + Lance Namespace), and the LLM observability
sink (Langfuse).

## Architecture

```
bunchloch (MacBook M4 Max)
├── dagster      :3335 → :3000   Dagster webserver + daemon
├── api          :8000            FastAPI AG-UI streaming backend
├── frontend     :3080 → :3000   TanStack Start dev server
└── locket       (sidecar)       Infisical → secrets.env injector
```

| Service | Container | Host port | Internal port | Healthcheck |
|---|--:|--:|--:|---|
| `dagster` | `cianchoghlaim-oideachais-dagster` | 3335 | 3000 | `/server_info` |
| `api` | `cianchoghlaim-oideachais-api` | 8000 | 8000 | `/health` |
| `frontend` | `cianchoghlaim-oideachais-frontend` | **3080** | 3000 | `/` |
| `locket` | `cianchoghlaim-oideachais-locket` | (no host port) | (no container port) | `/run/secrets/locket/secrets.env` |

## Networks

| Network | Type | Used for |
|---|---|---|
| `cianchoghlaim` | external | Primary dev/control plane (shared with 94 other stacks) |
| `lakehouse_lakehouse` | external | Data plane (Garage S3, Postgres, Lakekeeper, Lance NS, LiteLLM) |

## Dependencies (sibling stacks)

The 3 app services consume:

- **`infrastructure/stacks/lakehouse/`** — Garage S3
  (`http://lakehouse-garage:3900`), Postgres
  (`lakehouse-postgres:5432`), Lakekeeper Iceberg catalog
  (`http://lakehouse-lakekeeper:8181`), Lance Namespace
  (`http://lakehouse-lance-namespace:8182`).
  See `blueprint.yaml` `depends_on: [lakehouse]`.
- **`infrastructure/stacks/litellm/`** — LLM proxy gateway at
  `http://litellm:4000/v1` (all `LLM_*` env vars point here).
  See `blueprint.yaml` `depends_on: [litellm]`.
- **`infrastructure/stacks/langfuse/`** — LLM observability at
  `http://langfuse:3000` (Langfuse SDK config in `api` env).
  See `blueprint.yaml` `depends_on: [langfuse]` (optional).
- **`infrastructure/stacks/lancedb/`** — Optional LanceDB
  viewer (the data is on the lakehouse stack).

## Files

| File | Purpose |
|---|---|
| `compose.yaml` | Canonical 3 app services + 1 locket sidecar + named volumes + external networks |
| `compose.dev.yaml` | Dev override: no-op `alpine:3.20 locket` shim, `env_file: ../../../../.env` |
| `sidecar.yaml` | Production override: real `locket:1.2.3` sidecar with `infisical://dev-baile/...` secrets |
| `pangolin.yaml` | Traefik routing for 3 web-facing services (`*.oideachais.cianfhoghlaim.ie`) |
| `secrets.env` | Infisical URI references (zero plaintext; mounted at `/etc/locket/secrets.env`) |
| `.env.example` | Dev-only placeholder env vars (committed for onboarding) |
| `blueprint.yaml` | Komodo stack metadata (name, ports, depends_on) |
| `README.md` | This file |

## Commands

### Local development

```bash
# 1. Hydrate the local .env via mise
cd /Users/cianmacandeisigh/dev/kings_college_galway
mise trust  # accept mise.toml

# 2. Start the stack
cd infrastructure/stacks/oideachais
docker compose -f compose.yaml -f compose.dev.yaml up -d

# 3. Open Dagster at http://localhost:3335
# 4. Open the FastAPI at http://localhost:8000/health
# 5. Open the TanStack Start at http://localhost:3080
```

### Production (via Komodo)

```bash
# The 5-stage deploy procedure is at:
#   infrastructure/komodo/procedures/deploy-oideachais-bunchloch.toml
# It deploys lakehouse + litellm + langfuse + lancedb (stage 1),
# then oideachais (stage 2), then pangolin routes (stage 3),
# then health checks (stage 4).
#
# Trigger via Komodo UI or API:
curl -X POST https://komodo.cianfhoghlaim.ie/api/procedure/run \
  -H "Authorization: Bearer $KOMODO_API_KEY" \
  -d '{"name": "deploy-oideachais-bunchloch"}'
```

## Port Allocation (per `kcg-convergence` skill)

| Port | Range category | Reserved? |
|---|---:|:--:|
| 3000 | User apps | **YES** (Forgejo + langfuse) |
| 3080 | User apps | NO — used by `frontend` |
| 3335 | Dagster | NO — used by `dagster` |
| 8000 | MMO | NO — used by `api` (drift; should be 3500 per kcg-convergence, but kept for backward compat) |

## Image Tags

| Image | Tag | Reason |
|---|---|---|
| `oideachais-dev-dagster:latest` | `latest` | Local build artifact, `pull_policy: never` |
| `oideachais-dev-api:latest` | `latest` | Local build artifact, `pull_policy: never` |
| `oideachais-dev-frontend:latest` | `latest` | Local build artifact, `pull_policy: never` |
| `ghcr.io/cianfhoghlaim/locket:1.2.3` | **pinned** | Upstream image, MUST be pinned (no `:latest`) |

## Health Checks

```bash
# Dagster webserver
curl -s http://localhost:3335/server_info | jq

# FastAPI
curl -s http://localhost:8000/health | jq

# Frontend (TanStack Start)
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3080

# Locket secrets file (inside the locket container)
docker exec cianfhoghlaim-oideachais-locket \
  test -f /run/secrets/locket/secrets.env && echo OK
```

## Cross-References

- [`../../AGENTS.md`](../../AGENTS.md) — root agent instructions
- [`../../../openspec/changes/oideachais-stack-polish/`](../../../openspec/changes/oideachais-stack-polish/) — this stack's polish change
- [`../komodo/procedures/deploy-oideachais-bunchloch.toml`](../../komodo/procedures/deploy-oideachais-bunchloch.toml) — 5-stage deploy procedure
- [`../pangolin.yaml`](../../pangolin.yaml) — Pangolin (Traefik) routing
- [`.agents/skills/kcg-convergence/SKILL.md`](../../../.agents/skills/kcg-convergence/SKILL.md) — stack inventory + port allocation
- [`../../../oideachais/STATUS.md`](../../../oideachais/STATUS.md) — pipeline state
