---
name: stack-ops
description: "This skill should be used when adding, fixing, or auditing a Docker Compose stack under infrastructure/stacks/. Trigger phrases: 'add a new stack', 'fix stack', 'audit stacks', 'add Locket sidecar', 'add Infisical secret', 'check stack health', 'stack-doctor', 'why is stack X broken'."
---

# stack-ops — Adding, fixing, and auditing Docker Compose stacks

The cianfhoghlaim monorepo manages 70+ Docker Compose stacks under `infrastructure/stacks/{engineering,tools,storage,machine_learning,infrastructure}/<name>/`. Every stack must follow the **6-file GOLD_STANDARD** pattern. This skill teaches you how to add new stacks, fix incomplete ones, and audit them in bulk.

## The 6-file GOLD_STANDARD

Every deployable stack has these files:

| File | Required? | Purpose |
|:--|:--|:--|
| `compose.yaml` | **Yes** | Service definitions. NO `env_file: .env` (Locket injects instead). NO Locket references. |
| `sidecar.yaml` | **Yes** if compose exists | Defines the Locket sidecar + service overrides that mount `/run/secrets/locket/secrets.env` |
| `secrets.env` | **Yes** | Locket template. Every value is `{{ infisical:///<key> }}`. The `--provider=infisical` flag on Locket short form. |
| `pangolin.yaml` | **Yes** if web-facing | 6-label pattern: `pangolin.private-resources.<name>.{name,mode,full-domain,destination-port,protocol,roles[0]}` |
| `blueprint.yaml` | **Yes** | Pangolin routing blueprint — mirror of `pangolin.yaml` |
| `.env.example` | **Yes** | Non-secret defaults for local dev. Copy to `.env.local`. Never commit `.env.local`. |

For non-web stacks (e.g. databases, message brokers) `pangolin.yaml` + `blueprint.yaml` may use `mode: tcp` instead of `mode: http`.

## Adding a new stack

```bash
mkdir -p infrastructure/stacks/<category>/<name>

# 1. Start from an existing stack in the same category
cp -r infrastructure/stacks/tools/linkwarden/* infrastructure/stacks/<category>/<name>/

# 2. Edit compose.yaml
#    - Remove `env_file: .env` lines
#    - Add healthcheck: blocks for every service
#    - Add deploy.resources.limits
#    - Pin image versions (no :latest)
#    - Use the shared `cianfhoghlaim` Docker network

# 3. Edit sidecar.yaml — usually no change unless you have new services

# 4. Edit secrets.env — replace any direct values with {{ infisical:///<key> }}

# 5. Add a .env.example with dev defaults

# 6. Add a Komodo procedure at infrastructure/komodo/procedures/<name>-*.toml
#    (copy from team-stack-up.toml as a template)
```

## Wiring the Pangolin private resource

The 6-label pattern is exact. Use it without exception:

```yaml
# pangolin.yaml
services:
  <service>:
    labels:
      - "pangolin.private-resources.<repo>.name=<Human Name>"
      - "pangolin.private-resources.<repo>.mode=http"   # or "tcp" for non-HTTP
      - "pangolin.private-resources.<repo>.full-domain=<repo>.cianfhoghlaim.ie"
      - "pangolin.private-resources.<repo>.destination-port=<internal_port>"
      - "pangolin.private-resources.<repo>.protocol=http"  # or "tcp"
      - "pangolin.private-resources.<repo>.roles[0]=Member"
```

```yaml
# blueprint.yaml
private-resources:
  <repo>:
    name: "<Human Name>"
    mode: http
    full-domain: "<repo>.cianfhoghlaim.ie"
    destination-port: <internal_port>
    protocol: http
    sites: [arm1-oci]      # only site is arm1-oci
    roles: [Member]
```

## Locket + Infisical pattern

Locket reads `secrets.env` and resolves `{{ infisical:///<key> }}` at container boot. The runtime secret never hits disk.

**Before editing a secrets.env**: confirm the secret exists in Infisical under `dev-baile/<category>/<key>`. If it doesn't, seed it first:

```bash
PROJECT_ID="d18560c0-75d5-436f-a411-0bb758567196"
JWT=$(curl -fsS -X POST "http://localhost:8081/api/v1/auth/universal-auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"clientId\":\"$INFISICAL_CLIENT_ID\",\"clientSecret\":\"$INFISICAL_CLIENT_SECRET\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])")

curl -fsS -X POST "http://localhost:8081/api/v3/secrets/raw/<key>" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d "{\"workspaceId\":\"$PROJECT_ID\",\"environment\":\"dev-baile\",\"secretPath\":\"/<category>\",\"secretValue\":\"<value>\"}"
```

## Auditing existing stacks

The root `scripts/stack-doctor.sh` script audits every stack in the repo. Run it before and after any stack change.

```bash
bun run turbo doctor           # via turbo (fast)
bash scripts/stack-doctor.sh   # direct
bash scripts/stack-doctor.sh --json | jq  # CI / structured output
```

Severity:
- **CRITICAL** — stack cannot deploy (no compose.yaml, no blueprint.yaml, or compose fails to parse)
- **WARNING** — stack deploys but doesn't follow the 5-file pattern
- **INFO** — best-practices polish (`:latest` tags, missing healthchecks, no resource limits)

## Common fixes

### Adding a sidecar to a stack that's missing it

```bash
# 1. Copy the Locket sidecar template
cp infrastructure/stacks/tools/linkwarden/sidecar.yaml infrastructure/stacks/<category>/<name>/sidecar.yaml

# 2. Edit the `services:` block at the bottom to override your main service
# 3. Add the secrets.env with infisical:// references
# 4. Append new infisical env vars to root .infisical.env
```

### Fixing `latest` image tags

Look up the latest stable version on Docker Hub / GitHub Container Registry. Replace `image: foo:latest` with `image: foo:1.2.3`. Document the policy in the stack README.

### Adding healthchecks

For every service with a health endpoint:
```yaml
healthcheck:
  test: ["CMD", "wget", "-q", "-O-", "http://localhost:<port>/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

For services that depend on it, add `depends_on:` with `condition: service_healthy`.

## Cross-references

- `infrastructure/stacks/GOLD_STANDARD.md` — full 5-file pattern with examples
- `infrastructure/SECRETS-MANAGEMENT.md` — Locket + Infisical + mise bootstrap
- `infrastructure/PANGOLIN-SETUP.md` — Pangolin private resource topology
- `infrastructure/stacks/engineering/n8n/sidecar.yaml` — canonical sidecar reference
- `scripts/stack-doctor.sh` — the auditor this skill complements
- `.agents/skills/dagster/SKILL.md` — for the data platform orchestration layer
- `.agents/skills/dlt/SKILL.md` — for the data ingestion layer
- `.agents/skills/docker-compose/SKILL.md` — for compose syntax reference

## KCG context (Section 0)

### Quadrant model

The Cianfhoghlaim platform is organised in **4 quadrants**,
each a top-level uv workspace:

| Quadrant | Path | Wheel name | Use case |
|:--|:--|:--|:--|
| **Oideachais** | `oideachais/` | `oideachais` | Celtic education data platform |
| **Meaisínfhoghlaim** | `meaisínfhoghlaim/` | `meaisinfhoghlaim` | AI/ML services |
| **Tuatha** | `tuatha/` | `tuath` | Celtic MMO + crypto platform |
| **Croílár** | `croilar/` | (TS) | Public persona site |

### Technology stack table

| Layer | Technology | Where |
|:--|:--|:--|
| Polyglot toolchain | `mise` | root `mise.toml` |
| TS package manager | `bun` | `package.json` workspaces |
| Python package manager | `uv` | root `pyproject.toml` |
| Task pipeline | `turbo` | `turbo.json` |
| CI/CD | `dagger` | `dagger/src/main.py` |
| IaC | `pulumi` | `infrastructure/pulumi/` |
| Container orchestration | `komodo` | `infrastructure/komodo/` |
| Networking | `pangolin` | `infrastructure/pangolin/` |
| Secrets | `infisical` | `.infisical.env` |
| Object storage | `garage` (S3-compatible) | `infrastructure/stacks/storage/garage/` |
| Lakehouse | `ducklake` (DuckDB + S3) | `oideachais/storage/ducklake_client.py` |
| Vector DB | `lancedb` | `oideachais/storage/lancedb.py` |
| Knowledge graph | `falkordb` | `oideachais/graph/falkordb.py` |
| Orchestration | `dagster` | `oideachais/dagster_defs/` |
| Front-end | `tanstack-start` | `oideachais/web/`, `tuatha/ui/`, `croilar/apps/portal/` |
| API | `hono` | `oideachais/web/src/server/`, `tuatha/ui/src/server/` |

### Multi-network isolation

KCG services are isolated in 4 networks:

| Network | Purpose | Services |
|:--|:--|:--|
| `edge` | Public-facing (Pangolin) | Traefik, Pangolin, Pocket ID |
| `data` | Data plane (private) | Postgres, FalkorDB, LanceDB, Cognee |
| `control` | Control plane | Komodo, Komodo DB, Locket |
| `cross` | Cross-network (edge ↔ data) | FastAPI, Dagster |

### Port allocation map

| Range | Use case |
|:--|:--|
| 3000-3499 | User-facing apps (oideachais/web, tuatha/ui, croilar) |
| 3500-3999 | APIs (FastAPI, Hono) |
| 4000-4499 | Dagster (webserver, daemon, gRPC) |
| 5000-5499 | Data stores (Postgres, FalkorDB, LanceDB) |
| 6000-6999 | AI/ML (Cognee, MLflow, Langfuse) |
| 7000-7999 | Dev tooling (Jupyter, VS Code server) |
| 8000-8999 | MMO (Babylon.js dev server, SpacetimeDB) |
| 9000-9999 | Infrastructure (Pangolin, Komodo, Pocket ID) |

### Service dependency graph

| Tier | Services | Depends on |
|:--|:--|:--|
| Edge | Traefik, Pangolin, Pocket ID | (none) |
| Control | Komodo, Komodo DB, Locket | Edge (for routing) |
| Auth | BetterAuth, Pocket ID, Infisical | Edge, Control |
| Data | Postgres, FalkorDB, LanceDB, Cognee, DuckLake | (none — direct disk) |
| API | FastAPI, Hono, TanStack Start, Dagster | Data, Auth |
| MMO | Babylon.js, SpacetimeDB, Rust | Data, Auth, API |
| AI/ML | BAML, RAGAS, Unsloth, MLflow, Langfuse | Data, API |

### Health check patterns

```yaml
# .env
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 30s
```

Always include `start_period` to allow long-startup services
(Cognee, LanceDB, Dagster) to become healthy.

### Storage architecture

| Storage class | Use case | Provisioner |
|:--|:--|:--|
| `local` | Dev (single-host) | Docker local volume |
| `tmpfs` | Secrets (Locket) | tmpfs (mode 0700) |
| `nfs` | Shared files (Leabharlann) | NFS server (Hetzner) |
| `s3` | Object storage (Datasets, model weights) | Garage (S3-compatible) |
| `rook-ceph` | K8s scale-out | Rook-Ceph |

### Deployment order (5 phases)

1. **Foundation**: mise, bun, uv, dagger
2. **Secrets**: Infisical org + project + Locket sidecar
3. **Networking**: Pangolin + Pocket ID + CrowdSec
4. **Data**: Postgres, FalkorDB, LanceDB, DuckLake (S3)
5. **Apps**: FastAPI, Dagster, Hono, MMO

Each phase has a `mise run ci:phase-<n>` task that runs the
Dagger call for that phase.

### scripts/stack.sh wrapper

```bash
#!/usr/bin/env bash
# scripts/stack.sh — the canonical stack helper
# Usage: mise run stack:up <category>/<name>
#        mise run stack:down <category>/<name>
#        mise run stack:rebuild <category>/<name>
#        mise run stack:logs <category>/<name> [service]

CATEGORY=${1%/*}
NAME=${1#*/}

case "$0" in
    *up)      docker compose -f infrastructure/stacks/$CATEGORY/$NAME/compose.yaml up -d ;;
    *down)    docker compose -f infrastructure/stacks/$CATEGORY/$NAME/compose.yaml down ;;
    *rebuild) docker compose -f infrastructure/stacks/$CATEGORY/$NAME/compose.yaml build --no-cache ;;
    *logs)    docker compose -f infrastructure/stacks/$CATEGORY/$NAME/compose.yaml logs -f "${@:2}" ;;
esac
```

## KCG: The 6 docker-compose categories (canonical map)

The 70+ KCG Docker Compose stacks live in
`infrastructure/stacks/` and are organised into 6
categories by **purpose**, not by host. (Full per-category
inventory in `.agents/skills/kcg-convergence/SKILL.md`.)

| # | Category | Path |
|:--|:--|:--|
| 1 | **Control plane** | `infrastructure/` |
| 2 | **Storage** | `infrastructure/stacks/storage/` |
| 3 | **Engineering** | `infrastructure/stacks/engineering/` |
| 4 | **Machine learning** | `infrastructure/stacks/machine_learning/` |
| 5 | **Tools** | `infrastructure/stacks/tools/` |
| 6 | **Browser** | `infrastructure/stacks/browser/` |

### The 5 integration points (the leabharlann canonical flow)

The leabharlann pipeline (`.agents/skills/kcg-leabharlann-pipeline/SKILL.md`)
touches all 6 categories through 5 integration points:

1. **Komodo + Infisical + Locket** (control plane) — secret
   injection at runtime, no plaintext on disk
2. **dlt + DuckLake** (engineering → storage) — append-only
   ingestion with hash-based incremental
3. **BAML + Cognee** (engineering → machine learning) —
   typed extraction + knowledge graph
4. **CocoIndex v1 + LanceDB** (engineering → machine
   learning → storage) — incremental embedding
5. **FalkorDB + Graphiti** (machine learning → storage) —
   bi-temporal graph

### Related skills

- `.agents/skills/komodo/SKILL.md` — deploys the stacks
- `.agents/skills/pangolin/SKILL.md` — wires the private
  resources
- `.agents/skills/secrets-management/SKILL.md` — the
  3-way secret contract
- `.agents/skills/monorepo/SKILL.md` — mise + dagger +
  turbo
- `.agents/skills/kubernetes/SKILL.md` — the scale-out
  trigger
