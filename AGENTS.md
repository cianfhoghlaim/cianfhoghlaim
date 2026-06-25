# Infrastructure - AI Agent Instructions

## Priority quick reference

The 4 priority compose stacks, the 4 priority skills, and the
3 priority commands at a glance. **Read this first**; the rest
of the file is the full 94-stack inventory.

### Priority compose stacks (4 of 94)

| Stack | Port | Domain | Purpose |
|:--|--:|:--|:--|
| `oideachais` | 3080, 3335, 7777, 7778, 8000 | `oideachais.cianfhoghlaim.ie` | Celtic Education Lakehouse (Dagster + FastAPI + TanStack Start + Agno AgentOS + Google ADK) |
| `litellm` | 4000 | `litellm.cianfhoghlaim.ie` | LLM gateway (OpenAI-compatible proxy for 70+ models) |
| `langfuse` | 3000 | `langfuse.cianfhoghlaim.ie` | LLM observability (traces, prompts, A/B tests) |
| `lakehouse` | 3900-3904, 5433, 8181-8182 | internal | Garage S3 + Postgres + Lakekeeper (data plane) |

### Priority skills (4 of 108)

| Skill | When to load |
|:--|:--|
| [`stack-ops`](.agents/skills/stack-ops/SKILL.md) | Add / fix / audit a Docker Compose stack (the 6-file GOLD_STANDARD pattern) |
| [`infrastructure-stacks`](.agents/skills/infrastructure-stacks/SKILL.md) | The router for the 94 stacks + the 3-tier host convergence + the 5-stage deploy |
| [`secrets-management`](.agents/skills/secrets-management/SKILL.md) | Infisical + Locket + mise 3-way contract (no manual `.env`) |
| [`pangolin`](.agents/skills/pangolin/SKILL.md) | VPN + Traefik + Pocket ID SSO (Pangolin Convergence Architecture) |

### Priority commands

```bash
bun run validate-stacks           # stack-doctor: lint all 94 compose.yaml files
bun run stack-doctor               # alias for the above
mise run lint:skills               # validate .agents/skills/ metadata (108/108 pass)
```

### Add a new stack (3 commands)

```bash
mkdir -p infrastructure/stacks/<name>
# Create the 6 GOLD_STANDARD files (compose.yaml + sidecar.yaml
# + pangolin.yaml + secrets.env + blueprint.yaml + .env.example)
bun run validate-stacks           # MUST pass before commit
```

Full recipe: [`openspec/AGENTS.md`](../openspec/AGENTS.md) §"Adding
a New Docker Compose Stack".

## Overview

Infrastructure contains deployment configurations, infrastructure-as-code, and service orchestration for the Cianfhoghlaim platform implementing Pangolin Convergence Architecture (two-tier: OCI ARM1 control plane + MacBook M4 workload host).

## Directory Structure

| Directory | Purpose | Technology |
|-----------|---------|------------|
| `stacks/` | **94 Docker Compose stacks, flat layout** (one directory per stack) | Docker Compose |
| `komodo/` | Komodo configuration and profiles | Komodo |
| `pangolin/` | Pangolin setup documentation | Markdown |
| `infisical/` | Local Infisical dev server | Docker Compose |
| `pulumi/` | Cloud infrastructure | Pulumi IaC |
| `ansible/` | Server configuration | Ansible |
| `scripts/` | Utility scripts | Shell/TypeScript |

### Flattening note (2026-06-23)

The five legacy category subdirectories (`storage/`, `infrastructure/`, `engineering/`, `machine_learning/`, `tools/`) have been **removed**. Every stack now lives at `infrastructure/stacks/<name>/` directly. Stacks that previously were grouped by category are still discoverable by purpose via the inventory table below and the per-stack README files. There is no top-level category folder any more — the category of a stack is informational, not structural. `openspec/specs/infrastructure-stacks/spec.md` has been updated to drop the "Six Docker-Compose Categories" requirement.

The `stacks/stedding/` subdirectory predates the flattening (it is a mount point for large data volumes, not a stack) and is kept.

## Stack Inventory (alphabetical)

Every stack under `infrastructure/stacks/` is listed below. Port numbers reflect internal container ports; web-facing services are routed through Pangolin and reach the user at `<stack>.cianfhoghlaim.ie` (private) or via the public domain if flagged in `pangolin.yaml`.

| Stack | Purpose | Key Ports |
|:--|:--|:--|
| `actual/` | Self-hosted budgeting (Envelope Zero successor) | Internal |
| `agent-os/` | AgentOS (Letta) long-running agent runtime | Internal |
| `audiobookshelf/` | Self-hosted audiobook + podcast server | Internal |
| `backrest/` | Restic-based backup orchestrator with Web UI | Internal |
| `beszel/` | Server / Docker monitoring hub | 8090 |
| `blinko/` | Personal knowledge base (note-taking) | Internal |
| `bytebase/` | Database DevOps / CI for Postgres + MySQL | Internal |
| `cal-diy/` | Cal.com community build (team scheduling) | Internal |
| `changedetection/` | Website change monitor (Firecrawl-friendly) | Internal |
| `coder/` | Cloud development environment (Coder OSS) | Internal |
| `cognee/` | AI memory system (Neo4j, Memgraph, FalkorDB) | 8000 |
| `convex/` | Real-time backend for web | Internal |
| `crawl4ai/` | Web crawling API | 11235 |
| `croilar-convex/` | Convex backend + dashboard for Croilár | 3210-3211, 6791 |
| `croilar-dagster/` | Croilár-scoped Dagster code-location | per Komodo |
| `croilar-hono-api/` | Croilár Hono + BAML API on Bun | per Komodo |
| `croilar-marimo/` | Croilár-scoped Marimo notebooks | per Komodo |
| `croilar-postgres/` | Croilár Postgres (primary store) | 5432-5434 |
| `croilar-web/` | Croilár TanStack Start web + Convex auth | per Komodo |
| `dagster/` | Pipeline orchestration (engineering entry) | 3335 |
| `DevDocs/` | Developer documentation UI | Internal |
| `DnsServer/` | Local DNS resolution (split-horizon) | Internal |
| `docling-serve/` | Document AI / OCR (IBM Docling) | Internal |
| `dots-ocr/` | Dots.OCR vision-language OCR | Internal |
| `dozzle/` | Container log viewer (live tail) | Internal |
| `dragonfly/` | In-memory cache (Redis-compatible) | Internal |
| `enclosed/` | Encrypted file / paste sharing | Internal |
| `falkordb/` | Vector + graph hybrid (Redis protocol) | 6379, 3000 |
| `forgejo/` | Self-hosted Git forge (control-plane) | 3000, 2222 |
| `forgejo-runner/` | Forgejo Actions runner | Internal |
| `frontend/` | Multi-app frontend reverse proxy / shared infra | Internal |
| `garage/` | CRDT S3-compatible object storage | 3900-3904 |
| `glance/` | Personal dashboard (RSS, weather, links) | Internal |
| `gluetun/` | VPN tunnel client (WireGuard, OpenVPN) | Internal |
| `graphiti/` | Temporal knowledge graph (bi-temporal) | 8080 |
| `headplane/` | Headscale web UI | Internal |
| `headscale/` | Self-hosted Tailscale control server | Internal |
| `invokeai/` | SDXL image generation | 9090 |
| `it-tools/` | IT admin toolbox (encoders, formatters) | Internal |
| `Kapowarr/` | Comic library manager | Internal |
| `karakeep/` | Bookmark manager with AI tagging | Internal |
| `komodo/` | Container orchestration and deployment | 9120 |
| `lakefs/` | Git-for-data on S3 (versioned lake) | 8000 |
| `lakehouse/` | Lakekeeper + Lance Namespace + Postgres + Garage | 3900-3904, 5433, 8181-8182 |
| `lakehouse-oci/` | OCI-deployed lakehouse variant | per OCI |
| `lakekeeper/` | Iceberg REST catalog | 8181 |
| `lancedb/` | LanceDB data viewer | 8080 |
| `langfuse/` | LLM observability (v3) | 3000 |
| `LetterFeed/` | Newsletter aggregator | Internal |
| `linkwarden/` | Bookmark + archive manager | Internal |
| `litellm/` | LLM proxy gateway (Postgres + Prometheus) | 4000, 5432, 9090 |
| `lmnr/` | LMNR observability | Internal |
| `logfire/` | Pydantic Logfire (Python tracing) | Internal |
| `mailcow-dockerized/` | Self-hosted mail server (Postfix + Dovecot) | 25, 143, 465, 587, 993, 4190 |
| `marimo/` | Reactive Python notebooks (notebook server) | Internal |
| `mathesar/` | Postgres UI / spreadsheet | Internal |
| `MCPJungle/` | MCP server manager / proxy | Internal |
| `memgraph/` | Graph database (MAGE + Lab UI) | 7687, 7444, 3000 |
| `mlflow/` | ML experiment tracking | 5000 |
| `mlx-omni/` | Apple Silicon MLX OpenAI-compatible server | 10240 |
| `monitoring/` | Prometheus + Grafana + Loki | 9090, 3000 |
| `motherduck/` | Cloud query engine (MotherDuck adapter) | Internal |
| `n8n/` | Visual workflow automation | 5678 |
| `networking-toolbox/` | Network diagnostic tools | Internal |
| `nimtable/` | Iceberg catalog UI | Internal |
| `sruth/oideachais/` | Celtic Education Lakehouse Engine (Dagster + FastAPI + TanStack Start + Agno AgentOS + Google ADK). **Canonical** — replaces the legacy `/sruth/oideachais/compose.yaml` quartet. Build source of truth. | 3080, 3335, 7777, 7778, 8000 |
| `olake/` | ELT from MongoDB → Iceberg | 8080 |
| `olmocr/` | OlmOCR (Allen AI) document OCR | Internal |
| `paddleocr/` | PaddleOCR multilingual OCR | Internal |
| `pangolin/` | VPN + Traefik + Pocket ID + CrowdSec + TinyAuth | 51820/udp, 443, 80, 8443 |
| `paperless-ngx/` | Document scanning / archive | Internal |
| `pastemax/` | Paste sharing (local-first) | Internal |
| `Perplexica/` | Self-hosted Perplexity-style search | Internal |
| `pinchflat/` | YouTube channel archival | Internal |
| `pipecat/` | Real-time voice / multimodal pipeline | 8765 |
| `planetscale/` | Postgres-compatible cloud DB adapter | Internal |
| `pocket-id/` | OIDC identity provider | 1411 |
| `presenton/` | Slide presentations from data | Internal |
| `pulumi/` | Multi-cloud IaC runner | Internal |
| `pydantic-gateway/` | Pydantic AI gateway (LLM routing) | Internal |
| `qdrant/` | Vector search | 6333, 6334 |
| `r2/` | Cloudflare R2 adapter | Internal |
| `risingwave/` | Streaming SQL database | (Kafka) |
| `romm/` | ROM / game library manager | Internal |
| `rybbit/` | Web analytics (privacy-friendly) | Internal |
| `searxng/` | Private meta-search engine | Internal |
| `skyvern/` | Browser-agent automation (LLM-driven) | Internal |
| `stirling-pdf/` | PDF manipulation toolkit | Internal |
| `Termix/` | SSH / terminal in browser | Internal |
| `unstract/` | Unstructured data extraction | Internal |
| `vaultwarden/` | Bitwarden-compatible password manager | Internal |
| `vikunja/` | Kanban + Gantt + tasks | Internal |
| `windmill/` | Workflow automation (developer-first) | Internal |

For quadrant-aware routing (which stack serves which workspace member, which
ports, which `*.cianfhoghlaim.ie` domain, which Dagster code-location), see
[`infrastructure/QUADRANT-TO-STACK-MAP.md`](QUADRANT-TO-STACK-MAP.md). For
the live health snapshot of all 94 containers, see
[`infrastructure/stacks/HEALTH_REPORT.md`](stacks/HEALTH_REPORT.md).

## Standard Stack Structure

Each stack under `infrastructure/stacks/<name>/` SHALL follow this structure:

```
stacks/<name>/
├── compose.yaml           # Docker service definitions (image pinned to semver; no :latest)
├── compose.dev.yaml       # (optional) Dev override: no-op locket, env_file
├── pangolin.yaml          # Traefik routing + TinyAuth (if web-facing) — 6-label shape
├── sidecar.yaml           # Locket container for Infisical injection (user: 65532:65532, no-new-privileges, cap_drop: [ALL], read_only: true, tmpfs /run/secrets/locket:size=1m,mode=0700)
├── secrets.env            # Infisical URI references (infisical://dev-baile/<svc>/<key>)
├── .env.example           # Dev-only placeholder env vars
├── blueprint.yaml         # Komodo resource-sync metadata
└── config/                # Configuration files
    └── *.yaml
```

The `sidecar.yaml` SHALL declare one of 3 LOCKET_MODE values:
`watch` (long-running services, the default), `exec` (batch jobs),
or `oneshot` (CI/CD pipelines). The `pangolin.yaml` SHALL
follow the 6-label shape (`name`, `mode`, `full-domain`,
`destination-port`, `protocol`, `roles[0]`) documented in
`.agents/skills/kcg-pangolin-stack/SKILL.md`. The Locket sidecar
contract is documented in `.agents/skills/kcg-locket-sidecar/SKILL.md`.
The 4 audit scripts (inventory-bunchloch.sh, inventory-arm1-oci.sh,
diff-against-composes.sh, probe-public-urls.sh) are documented in
`.agents/skills/kcg-infrastructure-audit/SKILL.md`.

**Image pinning policy:** every `image:` line in `compose.yaml` SHALL
be pinned to `<major>.<minor>.<patch>` (no `:latest`); local-build
images with `pull_policy: never` are exempt and MUST include an
inline YAML comment. The `bun run stack-doctor` CI gate (4 gates
documented in `infrastructure/GOLD_STANDARD.md`) reports any
unpinned image as a WARNING.

## Canonical Oideachais Stack

**The oideachais platform is the only stack whose compose file lives outside
`infrastructure/stacks/`.** It is a *consumer* of the engineering patterns
(Locket, Pocket ID, Pangolin) rather than a single-purpose service.

| Path | Role |
|:--|:--|
| `sruth/oideachais/` (root) | Application source. Contains `Dockerfile.dagster`, `Dockerfile`, `web/Dockerfile`, `dagster.yaml`, `workspace.yaml`, `pyproject.toml`. **No docker-compose, sidecar, pangolin, or blueprint files at this level** — they live in the `sruth/oideachais/` stack under `infrastructure/stacks/`. |
| `infrastructure/stacks/sruth/oideachais/` | Canonical deployment. Has `compose.yaml` (uses `build:` from the root sources), `compose.dev.yaml`, `sidecar.yaml`, `pangolin.yaml`, `secrets.env`, `.env.example`, `blueprint.yaml`. |
| `infrastructure/komodo/stacks/oideachais-bunchloch.toml` | Komodo stack definition referencing the `sruth/oideachais/` stack files. |
| `infrastructure/komodo/procedures/deploy-oideachais-bunchloch.toml` | 5-stage deploy procedure (prereqs → lakehouse/litellm/lancedb/langfuse → oideachais → pangolin routes → health checks). |

**Do not reintroduce `sruth/oideachais/compose.yaml`, `sruth/oideachais/sidecar.yaml`,
`sruth/oideachais/pangolin.yaml`, or `sruth/oideachais/blueprint.yaml`** — the
`infrastructure/stacks/sruth/oideachais/` stack is the single source of truth.

## Critical Constraints

### Docker Compose Best Practices

```yaml
# CORRECT: Health checks, restart policies, named volumes
services:
  database:
    image: postgres:16
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### Secret Management

**NEVER commit secrets to git.** The `.env` file is gitignored. Secrets flow:

1. **Infisical vault** (`dev-baile`): Source of truth for all secrets
2. **`.infisical.env` template** (committed): Contains `infisical://dev-baile/...` references
3. **`mise` hooks**: Automatically run `infisical export` on directory entry, hydrating `.env`
4. **Locket sidecar**: Per-stack container that injects secrets at runtime

```bash
# Template format (.infisical.env - committed, no plaintext)
MOTHERDUCK_TOKEN=infisical://dev-baile/motherduck/token
FIRECRAWL_API_KEY=infisical://dev-baile/firecrawl/api_key

# Stack format (secrets.env - committed, no plaintext)
MOTHERDUCK_TOKEN=infisical://dev-baile/motherduck/token
```

**DO NOT manually create `.env` files.** Allow mise hooks and Locket to hydrate the environment.

### Network Configuration

All stacks use shared Docker network for inter-service communication:

```yaml
services:
  app:
    networks:
      - cianfhoghlaim

networks:
  cianfhoghlaim:
    external: true
```

## Deployment Workflow

### Local Development

```bash
# Stacks use Komodo for management. For direct Docker Compose:
cd infrastructure/stacks/<stack>
docker compose up -d
docker compose logs -f
docker compose down
```

### Production Deployment (Komodo GitOps)

Komodo syncs from Forgejo and manages all stacks:

```bash
# Access Komodo UI
open https://komodo.cianfhoghlaim.ie

# Deploy/update a stack via Komodo UI or API
# Each stack has compose.yaml + pangolin.yaml + sidecar.yaml + secrets.env
```

### Infrastructure Changes (Pulumi)

```bash
cd infrastructure/pulumi/<project>
pulumi preview
pulumi up
```

## Key Infrastructure Services

### Garage (S3 Object Storage)
- CRDT-based S3-compatible object storage
- Ports: 3900 (S3 API), 3901 (admin), 3902 (web), 3903-3904 (rpc)
- Used by DuckLake for Parquet storage and LanceDB for vector data

### Lakehouse Stack
- Garage S3 → Lakekeeper Iceberg Catalog (8181) → Lance Namespace Sidecar (8182)
- Postgres (5433) for Lakekeeper catalog metadata
- Custom `lakehouse-lance-namespace:latest` sidecar registers LanceDB tables as Iceberg tables

### Pangolin (VPN + Routing)
- WireGuard-based tunneling (port 51820/udp)
- Traefik v3.4.0 reverse proxy
- Pocket ID OIDC + TinyAuth for SSO
- CrowdSec for intrusion detection

### Komodo (Container Orchestration)
- GitOps workflow synced from Forgejo
- Multi-server deployments (OCI + MacBook)
- Integrated with Pangolin for service routing

## Common Operations

### Starting Core Infrastructure

```bash
# Core control plane (Pangolin + Komodo + Pocket ID) managed via Komodo
# Individual stacks can be started via:
docker compose -f infrastructure/stacks/garage/compose.yaml up -d
docker compose -f infrastructure/stacks/lakehouse/compose.yaml up -d
```

### Health Checks

```bash
# Check all container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check specific service
docker inspect --format='{{.State.Health.Status}}' <container>

# View resource usage
docker stats --no-stream
```

### Adding New Stacks

1. Create directory structure:
   ```bash
   mkdir -p infrastructure/stacks/<name>
   ```
2. Create `compose.yaml` with health checks, restart policies, named volumes, and network config
3. Create `pangolin.yaml` for web-facing services (Traefik + TinyAuth routing)
4. Create `sidecar.yaml` for Locket secret injection
5. Create `secrets.env` with Infisical URI references
6. Add a row to the **Stack Inventory** table above with port and purpose
7. Commit and let Komodo sync deploy

## Resources

- **Pangolin Docs:** https://pangolin.dev
- **Komodo Docs:** https://komo.do/docs
- **Infisical Docs:** https://infisical.com/docs
- **Pulumi Docs:** https://www.pulumi.com/docs

## Feedback loop (project → openspec → skill)

Per the `skills-as-project-docs` openspec change, the
infrastructure layer participates in the formal feedback
loop:

1. **When a new stack is added** (via the `stack-ops` skill +
   the 6-file GOLD_STANDARD pattern), the
   `infrastructure-stacks/SKILL.md` gets a 1-line addition
   in the "11 inventory categories" section.
2. **When the Komodo procedure changes** (e.g. a new
   `deploy-<stack>-<host>.toml`), the
   `dagger-pipelines/SKILL.md` gets a 1-line addition
   in the "8 callable functions" section.
3. **When a stack is removed or renamed**, the
   `infrastructure-stacks/SKILL.md` "11 inventory categories"
   section is updated to reflect the new state.

The lint script `mise run lint:skills` enforces the 4 metadata
rules (frontmatter, name match, description length, line count)
on every skill in `.agents/skills/`.
