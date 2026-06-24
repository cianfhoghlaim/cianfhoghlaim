# Infrastructure (The Foundation)

> The compute, secrets, mesh, and orchestration layer that everything
> else in `kings_college_galway` runs on. Sovereign. Zero-trust.
> GitOps-first. Multi-cloud.

This quadrant provisions and operates the underlying infrastructure for
the entire `cianfhoghlaim` stack — spanning two physical hosts
(`arm1-oci` Ampere A1 in Oracle Cloud, `bunchloch` MacBook M4) and
94 pre-configured Docker Compose stacks under `infrastructure/stacks/` (the actual file count is 93 as of 2026-06-24; the 94th is the `oideachais/` quadrant stack which is also tracked under `infrastructure/stacks/oideachais/`).

It is the **only** part of the monorepo that:

- **Provisions compute** (Pulumi → OCI Ampere A1)
- **Bootstraps servers** (Ansible → Pangolin + Komodo on each host)
- **Orchestrates the fleet** (Komodo GitOps, no Kubernetes)
- **Secures the mesh** (Pangolin + WireGuard + Traefik + Pocket ID SSO)
- **Stores every secret** (Infisical `dev-baile` → mise hook → Locket sidecar)
- **Builds and ships the platform images** (Dagger module with 4
  pipelines + 8 callable functions)

Everything else — the data lakehouse, the AI agents, the personas, the
notebooks, the team workflow — *runs* on this. When you SSH into a
server, you touch this quadrant first.

---

## 1. Quick start — first bring-up

If you're setting up a fresh installation, follow this exact order. Each
step depends on the one above it.

| Step | Stack | What you get | Validation |
|:--|:--|:--|:--|
| 1 | **Pulumi + OCI** | `arm1-oci` Ampere A1 instance, public IP, Infisical handoff | `ping arm1-oci` |
| 2 | **Ansible** | Pangolin Core + Komodo Core installed on `arm1-oci` and `bunchloch` | `komodo version` on each host |
| 3 | **Pangolin** | VPN mesh + Traefik + Pocket ID SSO + TinyAuth gate | `https://pangolin.cianfhoghlaim.ie` |
| 4 | **Infisical** | Secret vault with `dev-baile` environment hydrated | `infisical run -- printenv MOTHERDUCK_TOKEN` |
| 5 | **Garage** | S3-compatible object storage (DuckLake + LanceDB + asset bucket) | `mc ls garage/croilar-assets/` |
| 6 | **Lakehouse** | Iceberg catalog + LanceDB + DuckLake endpoints | `mc ls garage/lakekeeper/` |
| 7 | **Komodo** | Fleet orchestrator with all 93 stack blueprints | `https://komodo.cianfhoghlaim.ie` |
| 8 | **LiteLLM** | Unified LLM gateway (all agents + Dagster routes through this) | `https://litellm.cianfhoghlaim.ie` |
| 9 | **Langfuse** | LLM observability (traces every call) | `https://langfuse.cianfhoghlaim.ie` |
| 10 | **Croilár** | The personal portfolio platform (Dagster + Hono API + Convex + Web + Portal) | `https://croilar.cianfhoghlaim.ie` |

**One-liner health check** after each step:

```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "Up|healthy"
```

---

## 2. Architecture map

The control-plane pipeline that keeps the platform running:

```
       ┌──────────────────────────────────────────────────────────────┐
       │                      CLOUD                                  │
       │                                                              │
       │  Pulumi ──► OCI ──► Ansible ──► Pangolin Core + Komodo Core  │
       │     │                                                          │
       │     └─► Infisical vault handoff (public IP, DNS, OAuth)      │
       └──────────────────────────────────────────────────────────────┘
                                       │
                                       │ WireGuard mesh
                                       │
       ┌──────────────────────────────────────────────────────────────┐
       │                  ON-PREMISE / EDGE                            │
       │                                                              │
       │  Komodo ◄──WSS── Periphery agents (outbound only)            │
       │    │                                                          │
     │    ├── 93 Docker Compose stacks (infrastructure/stacks/)     │
    │    │   └─ each: compose.yaml + sidecar.yaml + pangolin.yaml    │
       │    │      + secrets.env + blueprint.yaml + .env.example       │
       │    │                                                          │
       │    ├── Pocket ID (OIDC) ◄── Traefik forwardAuth ─── clients   │
       │    │                                                          │
       │    ├── LLM traffic:  app ──► LiteLLM gateway ──► Anthropic    │
       │    │                                            OpenAI        │
       │    │                                            Gemini        │
       │    │                                            llama-swap     │
       │    │                                                          │
       │    └── Observability: Langfuse + MLflow + Logfire + Grafana    │
       │                                                              │
       └──────────────────────────────────────────────────────────────┘
```

Three trust boundaries:

1. **Outbound-only WebSocket** from each Periphery to Komodo Core — no
   inbound firewall ports needed.
2. **WireGuard mesh** via Pangolin — services talk over the private
   tunnel, not the public internet.
3. **Pocket ID SSO + TinyAuth** — every web app is gated through
   Traefik `forwardAuth`, which validates the JWT with Pocket ID before
   proxying.

---

## 3. Directory map

| Directory | Purpose | Key technology |
|:--|:--|:--|
| **`ansible/`** | Server bootstrapping for Pangolin + Komodo roles | Ansible + Locket |
| **`pulumi/`** | Cloud provisioning (OCI + Cloudflare IaC) | Pulumi (Python) |
| **`komodo/`** | Fleet orchestrator — 56 procedures, 17 stack TOMLs, 2 server configs | Komodo v2.2 |
| **`pangolin/`** | Zero-trust mesh — WireGuard + Traefik + PocketID + TinyAuth | Pangolin (Enterprise) |
| **`infisical/`** | Self-hosted secret vault (`dev-baile` environment) | Infisical |
| **`dagger/`** | CI/CD module — 8 callable functions across 3 pipelines | Dagger v0.20 |
| **`browser/`** | Browser automation client (`sruth-browser` Python project) | Stagehand, Playwright, BAML |
| **`observability/`** | Unified tracing library (Langfuse + MLflow + Logfire) | Python |
| **`scripts/`** | Utility scripts (Olm client creation, blueprint sync, stack helpers) | Bash |
| **`templates/`** | Forgejo workflow templates (PR forwarding, etc.) | YAML |
| **`docs/`** | Generic user guide | Markdown |
| **`stacks/`** | **93 Docker Compose stacks**, flat layout (one directory per stack) | Docker Compose |
| **`.forgejo/workflows/`** | CI workflows (Renovate, etc.) | YAML |

For the full stack-by-stack catalogue, see [`stacks/README.md`](stacks/README.md).

---

## 4. The 93-stack flat view

The 93 stacks under `infrastructure/stacks/` are organised in a **flat**
layout — every stack is a direct child of `stacks/` (e.g. `stacks/garage/`,
`stacks/litellm/`, `stacks/pangolin/`). The legacy 5-category
subdirectory structure (`stacks/storage/`, `stacks/infrastructure/`,
`stacks/engineering/`, `stacks/machine_learning/`, `stacks/tools/`) was
removed on 2026-06-23; every category subdirectory was lifted one level.

| Functional group | Count | Key stacks | Critical-path dependency |
|:--|:-:|:--|:--|
| **Foundational substrates** | 8 | Garage, Lakehouse, Lakekeeper, lakefs, beszel, forgejo-runner, **croilar-postgres**, lakehouse-oci | After Infisical (step 4) |
| **Control plane** | 15 | Pangolin, Komodo, Pocket ID, forgejo, Dozzle, headscale, headplane, monitoring, MotherDuck, PlanetScale, R2, Pulumi, vaultwarden, DnsServer, backrest, glance | After Pulumi + Ansible (steps 1-2) |
| **Dev tooling + gateways + services** | 22 | LiteLLM, dagster, marimo, convex, **croilar-web/portal/dagster/marimo/hono-api/convex**, coder, windmill, MCPJungle, agent-os, mathesar, DevDocs, dragonfly, n8n, mlx-omni, invokeai, pipecat, pydantic-gateway, networking-toolbox, crawl4ai, bytebase, gpt-researcher, pydantic-gateway, frontend | After storage (Garage + Lakehouse) |
| **AI services** | 17 | Cognee, Graphiti, Langfuse, MLflow, Memgraph, FalkorDB, LanceDB, Qdrant, RisingWave, docling-serve, dots-ocr, olake, olmocr, paddleocr, unstract, logfire, nimtable, lmnr | After LiteLLM (step 8) |
| **Productivity + media** | 24 | Vikunja, cal-diy, n8n, Paperless-NGX, SearXNG, Stirling-PDF, Karakeep, Linkwarden, Romm, Audiobookshelf, Perplexica, Skyvern, Actual, Blinko, Kapowarr, Pinchflat, Pastemax, Presenton, Termix, it-tools, mailcow-dockerized, LetterFeed, RomM, rybbit, enclosed, audiobookshelf, changedetection | Self-contained |

The functional-group column is **informational only** — it does not
impose a directory hierarchy. The full alphabetical inventory is in
[`infrastructure/AGENTS.md`](AGENTS.md) § "Stack Inventory".

**The critical path** (must exist before any croilar/ pipeline runs):

```
Infisical → Garage → Lakehouse → LiteLLM → Langfuse
```

Everything else can come up in any order. The `croilar-*` stacks
(web, portal, dagster, marimo, hono-api, convex) form the *last* ring —
they depend on every previous step.

---

## 5. The control plane pipeline

### 5.1 Pulumi → Cloud provisioning

Pulumi (Python) in `pulumi/oci/` provisions the **arm1-oci** Ampere A1
instance. Once the VM is up, Pulumi:

1. Stores the public IP in the Infisical `dev-baile` vault under
   `infra/oci/host`.
2. Regenerates the Ansible inventory at `ansible/inventory/`.
3. Triggers the Pangolin Core + Komodo Core playbooks.

Cloudflare DNS, R2 buckets, and CDN settings live in `pulumi/cloudflare/`.

### 5.2 Ansible → Server bootstrap

Ansible in `ansible/playbooks/` runs the roles in `ansible/roles/`:

- `komodo_core/` — installs Komodo Core + Periphery + the
  `komodo-sockproxy` agent
- `pangolin_core/` — installs Pangolin (Gerbil), Traefik, Pocket ID,
  TinyAuth, the Let's Encrypt DNS-01 challenge
- `newt/` — installs the Newt client (for bringing new devices onto
  the WireGuard mesh)

**Source of truth**: every host is rebuilt by Ansible from scratch.
There are no manual `.local` configuration overrides in production. If
you need to change a host's state, you change a playbook.

### 5.3 Komodo → Fleet orchestration

Komodo is a Rust application that:

- **Pulls** Compose stacks from GitHub on schedule.
- **Dispatches** to Periphery agents via outbound WebSocket — no
  inbound firewall ports required.
- **Renders** Web UIs for monitoring, procedures, resource-syncs, and
  per-stack history.

The `komodo/` directory contains:

- `procedures/` — 56 TOML files (chain of stack operations)
- `stacks/` — 17 canonical TOML stack definitions
- `resource-syncs/` — external resource watch (Renovate-like)
- `servers/` — host registry (arm1-oci, bunchloch)
- `sites/{oci,macbook}/` — per-host bootstrap configs

The Croilár-specific procedures (`croilar-stack-up`,
`croilar-image-rebuild`, `croilar-gitops-fullstack`, etc.) live here too.

### 5.4 Pangolin → Zero-trust mesh

Pangolin (Fossorial) creates the WireGuard mesh that all internal
services run over. Components:

- **Gerbil** — central controller
- **Newt** — per-device client (MacBook, iPhone, Linux server)
- **Olm** — VPN client for end users
- **Traefik v3.4** — reverse proxy, runs the `forwardAuth` middleware
- **CrowdSec** — intrusion detection (fail2ban on steroids)
- **Pocket ID** — OIDC identity provider
- **TinyAuth** — Traefik forwardAuth gatekeeper

Adding a new internal service is a **single Traefik label**:

```yaml
labels:
  - "pangolin.resource.middlewares=tinyauth"
  - "pangolin.resource.full-domain=myapp.cianfhoghlaim.ie"
  - "pangolin.resource.sites=arm1-oci"
```

The Traefik relay pauses every request to `/myapp`, bounces the user to
Pocket ID for SSO, and only allows traffic through once a valid JWT is
issued.

### 5.5 Infisical → Secret vault

Every secret in the platform — API keys, OCI tokens, LLM keys, R2
credentials, database URLs — lives in the `dev-baile` Infisical vault.
No `.env` files are committed to git.

Two consumption patterns:

- **Developer**: `mise` hooks run `infisical export` on `cd` into a
  project directory, hydrating `.env` in <1 second. Secrets are
  auto-unset on `cd` out.
- **Production**: every Docker stack has a `secrets.env` file with
  `{{ infisical:///path/to/key }}` references. The Locket sidecar
  resolves these at container boot, then injects them as env vars.

### 5.6 Locket → Runtime secret injection

`ghcr.io/bpbradley/locket:infisical` is the sidecar container that
resolves Infisical templates. Every production stack has a
`sidecar.yaml` that:

1. Mounts `./secrets.env` read-only as a template source.
2. Authenticates to Infisical with a service-account token.
3. Writes resolved values to a tmpfs volume at `/run/secrets/locket`.
4. Exits so healthcheck reports the secrets are ready.
5. Application containers `env_file: /run/secrets/locket/secrets.env`.

Secrets **never** persist on disk. They live in tmpfs for the lifetime
of the stack.

### 5.7 Dagger → CI/CD orchestration

`infrastructure/dagger/` is a Dagger module (Python root) that
orchestrates 8 callable functions across 3 pipelines + the Croilár
sub-pipeline:

| Pipeline | Functions |
|:--|:--|
| `InfrastructurePipeline` | `test`, `pulumi_preview`, `pulumi_up`, `deploy` |
| `WebPipeline` | `test`, `build`, `deploy`, `rollback` |
| `DataPipeline` | `test`, `build`, `deploy` |
| `CroilarPipeline` | `ci`, `build_images`, `deploy_cloudflare`, `deploy_komodo`, `deploy_pangolin`, `gitops_fullstack` |

Top-level `CianchoghlaimDagger` orchestrator composes the 4 pipelines.
All `deploy` and `rollback` functions are gated by an
`approved: bool = False` parameter for production safety.

---

## 6. Secrets flow

```
   Infisical (dev-baile)
        │
        │  ← mise hook (dev only, 1s)
        │     ───► .env
        │
        │  ← Locket sidecar (prod, at container boot)
        │     ───► /run/secrets/locket/secrets.env (tmpfs)
        │             │
        │             ▼
        │         app container env vars
        │
        ▼
   Application reads env, never touches disk
```

**NEVER:**

- Edit `.env` files manually in dev
- Hardcode secrets in compose.yaml
- Commit `.env.example` with real values (only `{{ infisical://... }}` templates)

**ALWAYS:**

- Use the `.infisical.env` template syntax in the repo
- Let Locket resolve templates at container boot
- Use the mise hook in dev for `.env` hydration

---

## 7. Key services reference

| Service | URL (prod) | Internal port | Purpose |
|:--|:--|:-:|:--|
| **Pangolin** | `pangolin.cianfhoghlaim.ie` | 443 | VPN mesh + Traefik + IDP gateway |
| **Pocket ID** | (private) | 1411 | OIDC IdP |
| **TinyAuth** | (internal) | 3001 | Traefik forwardAuth gate |
| **Komodo** | `komodo.cianfhoghlaim.ie` | 9120 | Fleet orchestrator |
| **Garage** | (internal) | 3900-3904 | S3-compatible object storage |
| **Lakehouse / Lakekeeper** | (internal) | 8181-8182, 5433 | Iceberg catalog + Lance namespace |
| **LiteLLM** | `litellm.cianfhoghlaim.ie` | 4000 | Unified LLM gateway |
| **mlx-omni** | (internal) | 10240 | Apple Silicon MLX-format OpenAI server |
| **InvokeAI** | (internal) | 9090 | SDXL image generation |
| **Langfuse v3** | `langfuse.cianfhoghlaim.ie` | 3000 | LLM observability |
| **MLflow** | (internal) | 5000 | ML experiment tracking |
| **Monitoring** | (internal) | 9090, 3000 | Prometheus + Grafana + Loki |
| **Cognee** | (internal) | 8000 | AI memory (Neo4j+Memgraph+FalkorDB) |
| **Graphiti** | (internal) | 8080 | Temporal knowledge graph |
| **Memgraph** | (internal) | 7687 | Graph database |
| **FalkorDB** | (internal) | 6379, 3000 | Vector+graph hybrid |
| **LanceDB viewer** | (internal) | 8080 | LanceDB data viewer |
| **Qdrant** | (internal) | 6333, 6334 | Vector search |
| **RisingWave** | (internal) | (Kafka) | Streaming SQL |
| **n8n** | `n8n.cianfhoghlaim.ie` | 5678 | Workflow automation |
| **Vikunja** | `vikunja.cianfhoghlaim.ie` | (internal) | Task management |
| **cal-diy** | `calcom.cianfhoghlaim.ie` | (internal) | Team scheduling |
| **Dagster** | `dagster.cianfhoghlaim.ie` | 3335 | Pipeline orchestration |
| **Convex** | `convex.croilar.cianfhoghlaim.ie` | 3210 | Real-time backend |
| **Convex dashboard** | (internal) | 6791 | Convex web UI |
| **Coder** | (internal) | (Cloud) | Cloud development environment |
| **Dozzle** | (internal) | (web) | Container log viewer |
| **beszel** | (internal) | 8090 | Server/Docker monitoring hub |

---

## 8. Glossary

| Term | Meaning |
|:--|:--|
| **Bonneagar** | Irish for "infrastructure" (legacy naming still in some scripts) |
| **Croilár** | The core platform (Dagster + Hono API + Marimo + Convex + Web + Portal) |
| **dev-baile** | The development Infisical vault environment |
| **Gerbil** | Pangolin central controller |
| **Newt** | Pangolin per-device client (MacBook, iPhone, Linux) |
| **Olm** | Pangolin VPN client for end users |
| **Oideachais** | The data lakehouse / education quadrant |
| **Periphery** | Komodo execution agent (Rust process, outbound WebSocket to Core) |
| **stedding** | Mount point for large data volumes (HF cache, GGUF, repos) |
| **Tuatha** | The Celtic Educational MMO quadrant |
| **Meaisínfhoghlaim** | The machine learning / AI quadrant |

---

## 9. When to read what

| You want to... | Read |
|:--|:--|
| Set up a fresh install | This file → §1 |
| Add a new Docker stack | This file → §5.3, then [`stacks/GOLD_STANDARD.md`](stacks/GOLD_STANDARD.md) |
| Provision a new cloud resource | This file → §5.1, then `pulumi/<cloud>/README.md` |
| Bootstrap a new server | This file → §5.2, then [`ansible/README.md`](ansible/README.md) |
| Add a new Traefik-protected service | This file → §5.4, then [`PANGOLIN-SETUP.md`](PANGOLIN-SETUP.md) |
| Configure a new secret | This file → §5.5-5.6, then [`SECRETS-MANAGEMENT.md`](SECRETS-MANAGEMENT.md) |
| Add a new CI pipeline | This file → §5.7, then [`dagger/README.md`](dagger/README.md) |
| Operate an existing stack | This file → §7, then the per-stack README |
| Find a service URL | This file → §7 (Key services reference) |
| Find what a project-specific term means | This file → §8 (Glossary) |

---

## 10. License

MIT.

---

## How to deploy

```bash
# 1. The 4 infra-first stacks
for stack in garage lakehouse litellm lancedb langfuse; do
  cd infrastructure/stacks/$stack && docker compose up -d
done

# 2. The 4 quadrant stacks
for stack in oideachais meaisinfhoghlaim tuatha croilar; do
  cd infrastructure/stacks/$stack && docker compose up -d
done

# 3. The Pangolin mesh (Traefik + Pocket ID)
cd infrastructure/stacks/pangolin && docker compose up -d
```

The full 8-phase playbook is in [`DEPLOY.md`](../DEPLOY.md).

## How to debug

| Symptom | Cause | Fix |
|:--|:--|:--|
| `docker compose up -d` hangs | Locket sidecar waiting for a secret | `docker logs <stack>-locket-1` |
| `bun run validate-stacks` fails | A `compose.yaml` is missing a healthcheck | Add `healthcheck:` block to the offending service |
| Pangolin route 404s | The Traefik label is wrong | Check the 6-label shape in `pangolin.yaml` |
| Locket injects the wrong secret | The Infisical URI is stale | `bun run secrets:init` to refresh |

## Common workflows

1. **Add a new stack** — 6 GOLD_STANDARD files (compose.yaml + sidecar.yaml + pangolin.yaml + secrets.env + blueprint.yaml + .env.example)
2. **Audit a host** — `bash infrastructure/audit/scripts/inventory-<host>.sh`
3. **Diff compose vs running** — `bash infrastructure/audit/scripts/diff-against-composes.sh`
4. **Probe a public URL** — `bash infrastructure/audit/scripts/probe-public-urls.sh`
5. **Roll back a stack** — `docker exec <stack>-locket-1 locket rollback --service=<stack>`
