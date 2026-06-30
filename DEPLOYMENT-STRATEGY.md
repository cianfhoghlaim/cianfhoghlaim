# bonneagar/DEPLOYMENT-STRATEGY.md

The canonical playbook for taking a new Docker Compose stack
from "code on disk" to "served at `*.cianfhoghlaim.ie`" on the
Pangolin-routable public mesh.

This document was created as part of
`openspec/changes/audit-infrastructure-2026-06-15/` and
satisfies the `infrastructure-stacks` spec requirement
**Deployment Runbook** for the 9 user-named targets
(`infisical`, `komodo`, `pangolin`, `ansible`, `cal-diy`,
`vikunja`, `n8n`, `changedetection`, `bytebase`).

The per-stack deployment runbooks themselves live in
`bonneagar/deploy-runbooks/<name>.md`.

## 1. The 2-host topology

| Host | Role | Spec | What runs there |
|:--|:--|:--|:--|
| `bunchloch` | Primary Workloads | MacBook M4 Max, ~14 cores, 48 GB RAM, NVMe | 35 containers: lakehouse (Garage + Postgres + Lakekeeper + Lance NS), Langfuse, LiteLLM, llama-swap, Convex, browser stack, oideachais frontend + API + Dagster, komodo-core + komodo-periphery, Cognee, LanceDB, newt (Pangolin client) |
| `arm1-oci` | Control Plane | Oracle Cloud London, 4 ARM OCPUs, 24 GB RAM, 200 GB | ~10 containers: Pangolin + Gerbil + Traefik + Pocket ID + TinyAuth + Middleware Manager + CrowdSec, Komodo Core, Infisical, Garage, Beszel, Dozzle, Qdrant, cal-diy (3 containers) |

`arm1-oci` is the orchestrator (the operator runs the Komodo
web UI at `komodo.cianfhoghlaim.ie` from the MacBook; the
Oracle box's periphery agents connect outbound to the Core).
`bunchloch` is the workload host (data plane + the dev /
analytics container that the operator interacts with
locally).

## 2. The 4 deploy surfaces

A new stack is composed of 4 deploy surfaces:

| Surface | Where it lives | What it does |
|:--|:--|:--|
| **Komodo Core** | `bunchloch` (operator's MacBook) | Orchestrates the fleet via web UI + REST API at `komodo.cianfhoghlaim.ie:9120` (per `bonneagar/komodo/stacks/komodo.toml`) |
| **Komodo Periphery** | `arm1-oci` + `bunchloch` (2 agents) | Each runs as a `komodo-periphery-{oci,macbook}` container; connects outbound to Core (per `bonneagar/komodo/stacks/komodo.toml`) |
| **Infisical Vault** | `arm1-oci` (`infisical.cianfhoghlaim.ie`) | Self-hosted; the `dev-baile` environment is the source of truth (per `bonneagar/infisical/` + `bonneagar/SECRETS-MANAGEMENT.md`) |
| **Pangolin** | `arm1-oci` (Traefik + Gerbil + Pocket ID) | Reverse-proxy + identity + TinyAuth SSO; routes `*.cianfhoghlaim.ie` to internal containers (per `bonneagar/PANGOLIN-SETUP.md`) |

## 3. The 6-step golden path

For every new stack, follow these 6 steps in order. Each
step has a dedicated runbook in
`bonneagar/deploy-runbooks/<name>.md`.

### Step 1: Write the 6 GOLD_STANDARD files

In `bonneagar/stacks/<name>/`, create the 6
required files (per `bonneagar/GOLD_STANDARD.md`):

| File | Purpose |
|:--|:--|
| `compose.yaml` | Docker service definitions (health checks, restart policies, volumes, network) |
| `sidecar.yaml` | Locket container for Infisical secret injection at runtime |
| `secrets.env` | Infisical URI references (`infisical://dev-baile/...`) — NO plaintext |
| `blueprint.yaml` | Pangolin private-resource definition (YAML form) |
| `.env.example` | Local-dev placeholder env vars (committed, no real secrets) |
| `README.md` | Human-facing docs (recommended) |

### Step 2: Validate with the stack-doctor

```bash
bun run validate-stacks
# (the stack-doctor turbo task — see infrastructure/GOLD_STANDARD.md
#  "CI gate" section for the green/red rules)
```

### Step 3: Add secrets to the Infisical vault

```bash
bun run secrets:init
# (alias for bun run scripts/init-vault.ts; reads .env + .infisical.env
#  and creates / updates each vault secret. The mise directory hook
#  auto-hydrates .env on cd.)
```

The 9 user-named targets have these Infisical paths already
provisioned (per `HEALTH_REPORT.md` Session 3 + 4 blockers):

- `infisical` → `/komodo`, `/pangolin`, `/pocketid-team-workflow`
- `cal-diy` → `/calcom`, `/planetscale`, `/pocketid-team-workflow`
- `vikunja`, `n8n`, `changedetection`, `bytebase` → `/<name>` per-stack

### Step 4: Add a `[[stack]]` entry to a Komodo stack file

In `bonneagar/komodo/stacks/<host>.toml`, append a new
`[[stack]]` block. The block declares:

- `name` — the human-friendly name (e.g. `vikunja`)
- `server_id` — `arm1-oci` or `bunchloch`
- `tags` — `["host:<host>", "tier:<tier>", "type:<service-type>"]`
- `run_directory` — where the compose lives on the target host (e.g. `/etc/komodo/storage/vikunja`)
- `file_paths` — which of the 6 GOLD_STANDARD files to load
- `environment` — a `"""\nK=V\n"""` block of env vars

### Step 5: Sync to Komodo

Either via the Komodo Core UI at `komodo.cianfhoghlaim.ie` (click
"Pull" on the stack), or programmatically:

```bash
# via komodo_client (TypeScript, already in node_modules/)
node -e "
  import('komodo_client').then(async ({ KomodoClient }) => {
    const c = new KomodoClient({
      url: 'https://komodo.cianfhoghlaim.ie',
      key: process.env.KOMODO_API_KEY,
      secret: process.env.KOMODO_API_SECRET,
    });
    await c.deployStack({ stack: 'vikunja', server: 'bunchloch' });
  });
"
```

### Step 6: Verify

```bash
# 1. The container is up
docker ps | grep vikunja

# 2. The HTTP endpoint is healthy
curl -I http://localhost:<port>/health

# 3. The Pangolin private resource is registered
bash bonneagar/audit/scripts/probe-public-urls.sh | grep vikunja
```

## 4. The 4 known blockers (from `HEALTH_REPORT.md` Session 3)

A deploy at the moment will hit these 4 known issues. Fix
them once, then the 6-step golden path is clean.

| # | Blocker | Fix |
|--:|:--|:--|
| 1 | Newt 1.12.5 + Pangolin server 1.18.4 are incompatible (`CLIENTS WILL NOT WORK ON THIS VERSION OF NEWT WITH THIS PANGOLIN SERVER`) | Update Pangolin server to ≥1.13.0 OR downgrade newt to 1.11.x |
| 2 | 3 manually-created private resources (`komodo`, `cal-diy`, `infisical`) override the blueprints. New blueprint: `Blueprint application failed: Site resource already exists with domain: <X>` | Open the Pangolin UI → Sites → each resource → delete the manual entry. Blueprint reapplies on the next newt cycle. |
| 3 | Both `PANGOLIN_API_KEY` and `PANGOLIN_API_KEY_0` in `.env` return 401 | Use the Pangolin UI to mint a fresh machine-identity token. Save to `.env` as `PANGOLIN_API_KEY`. |
| 4 | `komodo-locket` sidecar fails: `error: invalid value '${INFISICAL_CLIENT_ID}'` — the `$${INFISICAL_CLIENT_ID}` YAML escape was being passed as a literal | Switch to single-dollar Compose substitution; add `--infisical-default-environment` + `--infisical-default-project-id` flags; provision an Infisical machine identity with `/komodo` access |

## 5. The 5-stamp Pangolin private-resource blueprint

Per `bonneagar/pangolin/a2a-resources.blueprint.yaml` and
the schema in `bonneagar/GOLD_STANDARD.md`, every
`*.cianfhoghlaim.ie` private resource has the same shape:

```yaml
# bonneagar/stacks/<name>/blueprint.yaml
private-resources:
  <name>:
    name: "<Display Name>"
    mode: "http"
    destination-port: <container-port>
    full-domain: "<name>.cianfhoghlaim.ie"
    protocol: "http"
    roles:
      - "Member"
    destination: "<container_name>"   # NOT the resource-name, the real container_name
```

The Session 3 fix (commit `9f07d3fb7`) corrected a
schema-violating `destination: <host>:<port>` collapse back
into two separate fields per the official Pangolin 1.18.4
docs.

## 6. Where the runbooks live

The 9 user-named deploy targets each have a runbook at
`bonneagar/deploy-runbooks/<name>.md`. Each runbook
follows the 4-section structure mandated by the
**Deployment Runbook** spec requirement:

- `## Pre-flight` — required Infisical secrets, compose profiles, Komodo server_id
- `## First-time deploy` — step-by-step
- `## Verify` — `curl` / healthcheck / Dagster materialisation checks
- `## Rollback` — `komodo_client` API call to revert

The runbooks are written for a *future AI agent* that
executes the deploy. They contain no prose rationale, only
shell snippets copy-pastable verbatim.
