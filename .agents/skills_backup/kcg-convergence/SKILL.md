---
name: kcg-convergence
description: KCG's flat docker-compose layout (94 stacks under infrastructure/stacks/, no category subdirectory) + port allocation map (3000-3499 user apps, 3500-3999 APIs, 4000-4499 Dagster, 5000-5499 data, 6000-6999 AI/ML, 7000-7999 dev, 8000-8999 MMO, 9000-9999 infra). Use when adding a new stack, picking a port, or asking "where in the stacks/ tree does X live?".
---

# KCG Convergence

## When to use this skill

Use when you need to:

- "Add a new stack — where does the directory go?"
- "Pick a port for a new service"
- "Understand the flat layout"
- "Onboard a new dev to the KCG monorepo's infra shape"
- "Map a stack to the right host tier (control / storage /
  workload)"

## The flat docker-compose layout

The 94 KCG Docker Compose stacks live in
`infrastructure/stacks/` as a **flat** directory — one
directory per stack, no category subdirectory. Functional
purpose is recorded as information only in
`infrastructure/AGENTS.md` § "Stack Inventory" and the
cross-quadrant routing table at
`infrastructure/QUADRANT-TO-STACK-MAP.md`.

| Functional group | Examples | Notes |
|:--|:--|:--|
| **Control plane** | pangolin, komodo, pocket-id, dozzle, DnsServer, planetscale, motherduck, r2, pulumi, forgejo, forgejo-runner, monitoring, headscale, headplane, vaultwarden, backrest, glance | Pangea/identity/GitOps/observability. Lives in `infrastructure/stacks/<name>/` (flat). |
| **Foundational substrates** | garage, lakehouse, lakehouse-oci, lakekeeper, lakefs, forgejo-runner, beszel, croilar-postgres | S3 / Iceberg / git / monitoring hub. Flat. |
| **Dev tooling + gateways + services** | litellm, mlx-omni, invokeai, dagster, marimo, convex, coder, windmill, n8n, MCPJungle, DevDocs, dragonfly, crawl4ai, mathesar, agent-os, oideachais, gluetun, pipecat, pydantic-gateway, networking-toolbox, bytebase, frontend, **croilar-{web,portal,dagster,marimo,hono-api,convex}** | Where humans + agents spend their day. Flat. |
| **AI services** | cognee, graphiti, langfuse, mlflow, qdrant, memgraph, falkordb, lancedb, risingwave, docling-serve, dots-ocr, olake, olmocr, paddleocr, unstract, logfire, nimtable, lmnr | Vector / graph / observability / streaming / training. Flat. |
| **Productivity + media** | vikunja, cal-diy, n8n, paperless-ngx, searxng, stirling-pdf, karakeep, linkwarden, romm, audiobookshelf, Perplexica, skyvern, actual, blinko, Kapowarr, pinchflat, pastemax, presenton, Termix, it-tools, mailcow-dockerized, LetterFeed, rybbit, enclosed, changedetection | Self-contained utilities. Flat. |
| **Browser automation** | crawl4ai, skyvern (and any new `stagehand` / `playwright` / `agent-browser` stacks) | No dedicated category folder. Flat. |

### Per-category inventory

#### 1. Control plane (10 stacks)

| Stack | Image(s) | Key ports |
|:--|:--|:--|
| pangolin | `fosrl/pangolin:postgresql-latest`, `postgres:17`, `traefik:v3.4.0`, `pocket-id:latest`, `tinyauth:v4`, `crowdsec:latest` | 51820/udp, 443, 80, 8443 |
| komodo | `ghcr.io/moghtech/komodo-core:2`, `mongo:latest` | 9120 |
| pocket-id | `ghcr.io/pocket-id/pocket-id` | 1411 |
| dozzle | Container log viewer | Internal |
| DnsServer | Local DNS resolution | Internal |
| planetscale | MySQL-compatible cloud DB | Cloud |
| motherduck | MotherDuck cloud analytics | Cloud |
| r2 | Cloudflare R2 bridge | Internal |
| pulumi | Multi-cloud IaC | Internal |
| forgejo | Git forge (Postgres) | 3000, 2222 |
| forgejo-runner | CI/CD runner | — |

#### 2. Storage (4 stacks)

| Stack | Purpose | Key ports |
|:--|:--|:--|
| garage | CRDT S3-compatible object storage | 3900-3904 |
| lakehouse | Lakekeeper Iceberg catalog + Lance Namespace + Garage + Postgres | 3900-3904, 5433, 8181-8182 |
| lakehouse-oci | OCI variant of lakehouse | 5433, 8181-8182 |
| lakefs | Data versioning (git-for-data) | Internal |
| beszel | System + Docker monitoring | Internal |

#### 3. Engineering (10 stacks)

| Stack | Purpose | Key ports |
|:--|:--|:--|
| litellm | LLM proxy gateway (Postgres + Prometheus) | 4000, 5432, 9090 |
| dagster | Pipeline orchestration (custom image) | 3335 |
| oideachais | The app stack: Dagster + FastAPI + TanStack Start | 3335, 3000, 8000 |
| convex | Real-time backend | Cloud |
| windmill | Workflow automation | Internal |
| n8n | Visual workflows | Internal |
| coder | Cloud dev environment | Internal |
| DevDocs | API documentation aggregator | Internal |
| MCPJungle | MCP server collection | Internal |
| crawl4ai | Web crawling API | 11235 |
| stagehand | Cloudflare-Workers browser automation | Cloud |

#### 4. Machine learning (12 stacks)

| Stack | Purpose |
|:--|:--|
| cognee | AI memory (knowledge graph) |
| graphiti | Temporal knowledge graph |
| langfuse | LLM observability (Postgres + ClickHouse + Redis + MinIO) |
| mlflow | ML experiment tracking (Postgres + MinIO) |
| qdrant | Vector database |
| memgraph | Graph database (MAGE + Lab UI) |
| falkordb | Vector + graph hybrid |
| lancedb | LanceDB data viewer |
| olake | CDC replication (Postgres/MySQL → Iceberg) |
| lmnr | Language model observability |
| logfire | Pydantic observability |
| nimtable | Analytics table viewer |

#### 5. Tools (17 stacks)

- **Productivity** (5): actual, blinko, linkwarden,
  presenton, stirling-pdf
- **Media** (4): audiobookshelf, kapowarr, pinchflat, rybbit
- **Development** (8): changedetection, enclosed, pastemax,
  perplexica, skyvern, LetterFeed, romm, mailcow-dockerized

#### 6. Browser (1 stack)

| Stack | Purpose | Key ports |
|:--|:--|:--|
| browser | Browser automation (Skyvern + Postgres + Garage) | 3001, 3100, 8001, 11235 |

## The 5 integration points

The leabharlann pipeline (a representative end-to-end flow)
touches all 6 categories through 5 integration points:

1. **Komodo + Infisical + Locket** — secret injection at
   runtime (control plane), no plaintext on disk, GitOps
   workflow.
2. **dlt + DuckLake** — append-only ingestion with
   hash-based incremental; primary key `file_hash`; partition
   columns `account` + `domain` (engineering → storage).
3. **BAML + Cognee** — typed extraction with schema
   validation; `cognee.add()` + `cognify()` builds the
   knowledge graph; cross-archive edges via 8 canonical
   relationship types (engineering → machine learning).
4. **CocoIndex v1 + LanceDB** — incremental embedding with
   `@coco.fn(memo=True)`; IVF_HNSW + FTS indexes (engineering
   → machine learning → storage).
5. **FalkorDB + Graphiti** — bi-temporal graph (machine
   learning); FalkorDB for cache/queries (machine learning
   → storage).

## The port allocation map

The KCG port ranges are reserved by category. **Never**
pick a port outside these ranges (it will collide with
something else):

| Range | Category | Examples |
|:--|:--|:--|
| **3000-3499** | User apps | TanStack Start (sruth/cianfhoghlaim/web) :3000, Forgejo :3000, Browse :3001 |
| **3500-3999** | APIs | FastAPI :3500-3599, AG-UI :3600, oRPC :3700 |
| **4000-4499** | Dagster | Dagster webserver :3335, LiteLLM :4000 |
| **5000-5499** | Data | Lakehouse Postgres :5433, MLflow :5000 |
| **6000-6999** | AI/ML | LanceDB viewer :8081, Cognee :8000, FalkorDB :6379, llama-swap :8080, mlx-omni-server :10240, invokeai :9090 |
| **7000-7999** | Dev | Coder, DevDocs, MCPJungle (internal) |
| **8000-8999** | MMO | Tuatha game ports (Babylon.js client) |
| **9000-9999** | Infra | Komodo :9120, Pocket ID :1411, Gerbil :51820/udp, Traefik :80/:443, TinyAuth :8443, Dozzle :8080 |

Reserved system ports (do not use):

- 22 (SSH)
- 80, 443 (Traefik HTTP/S)
- 1411 (Pocket ID)
- 3000 (Forgejo + TanStack + others — check first)
- 51820/udp (Gerbil WireGuard)
- 8443 (TinyAuth forward auth)
- 9120 (Komodo Core)

## Decision tree for "where does X go?"

```
New stack?
│
└── Always: infrastructure/stacks/<name>/
    (flat — no category subdirectory, no subcategory)
    Then:
      1. Add a row to the Stack Inventory in
         infrastructure/AGENTS.md (purpose + ports)
      2. Add a row to infrastructure/QUADRANT-TO-STACK-MAP.md
         if a workspace quadrant consumes it
      3. Run bun run validate-stacks
```

## Image pinning policy (no `:latest`)

Every image pushed to `ghcr.io/cianfhoghlaim/` MUST be pinned to a
semver tag. **Never use `:latest` in production stacks.**

All in-repo images SHALL be tagged as `<major>.<minor>.<patch>` and
built for multi-arch (`linux/amd64,linux/arm64`).

- **Registry:** `ghcr.io/cianfhoghlaim/`
- **Auth:** GitHub Actions OIDC → `GITHUB_TOKEN` with `write:packages`
- **Visibility:** Public
- **Production stacks** SHALL reference the sidecar / upstream images
  with a pinned tag (e.g. `ghcr.io/cianfhoghlaim/locket:1.2.3`), never
  `:latest`. Local-build images (with `pull_policy: never`) may use
  `latest` because the image is built and tagged locally, but the
  compose file MUST include a comment explaining the deviation.

## Cross-references

- `.agents/skills/kcg-bunchloch/SKILL.md` — the 3-tier
  host convergence (where the stacks run)
- `.agents/skills/stack-ops/SKILL.md` — the 6-file
  GOLD_STANDARD pattern (how each stack is structured)
- `.agents/skills/cianfhoghlaim-storage/SKILL.md` — the
  storage layer detail
- `.agents/skills/kcg-leabharlann-pipeline/SKILL.md` — the
  5-stage pipeline that touches many functional groups
- `infrastructure/AGENTS.md` — the canonical stack inventory
- `infrastructure/QUADRANT-TO-STACK-MAP.md` — quadrant → stack
  routing

## Team-workflow stack

The 8 live private resources behind the Cianfhoghlaim
two-tier zero-trust network (Pangolin + WireGuard mesh,
PocketID passkey SSO, TinyAuth forward auth):

| Resource | Domain | Port | Status |
|:--|:--|:--|:--|
| **Pangolin Admin** | `pangolin.cianfhoghlaim.ie` | 443 | Online |
| **PocketID** (OIDC) | `auth.cianfhoghlaim.ie` | 443 | Online |
| **TinyAuth** (forward auth) | `tinyauth.cianfhoghlaim.ie` | 443 | Online |
| **Infisical Vault** | `infisical.cianfhoghlaim.ie` | 8080→443 | Online |
| **n8n Workflow Automation** | `n8n.cianfhoghlaim.ie` | 5678 | Online |
| **Vikunja Team Workspace** | `vikunja.cianfhoghlaim.ie` | 3456 | Online |
| **ChangeDetection.io** | `changedetection.cianfhoghlaim.ie` | 5000 | Online |
| **Glance Dashboard** | `glance.cianfhoghlaim.ie` | 8080 | Online |

**3 onboarding steps for team members**: (1) install
**Olm** (Pangolin client for macOS) from the admin →
"Install Site Connector" — gives your Mac a routable IP
in the Pangolin WireGuard mesh (e.g., `100.64.0.X`),
(2) set up a **PocketID passkey** (Touch ID, YubiKey, etc.)
at `https://auth.cianfhoghlaim.ie` — passkey-only, no
passwords, (3) access private resources via
`https://<service>.cianfhoghlaim.ie` directly — Pangolin's
PocketID SSO layer handles auth.

**5 architectural planes**:
- **Identity** — PocketID OIDC provider, passkey-only;
  TinyAuth forward auth proxy; Pangolin auth-aware reverse
  proxy + WireGuard mesh coordinator
- **Secrets** — Infisical vault of record; Locket sidecar
  pattern; `.infisical.env` (committed template) + `.env`
  (gitignored runtime)
- **Routing** — Traefik v3.6 (TLS termination, host-based
  routing); Gerbil (WireGuard peers + tunnels); Newt
  (per-site tunnel agent, Docker blueprint enabled)
- **Sites** — `arm1-oci` (Oracle Cloud ARM, 24GB RAM, 4 CPU,
  194GB disk, primary control plane); `bunchloch` (MacBook
  M4, workload host)
- **Workflow automation** — n8n + Vikunja + cal-diy +
  ChangeDetection.io + Glance

**Resource declaration pattern** — every Docker service
gets a `pangolin.yaml` overlay with 7 labels
(`pangolin.private-resources.<svc>.{name,mode,destination,
full-domain,destination-port,protocol,roles}`). Deploy
with `docker compose -f compose.yaml -f pangolin.yaml up
-d`; Newt's Docker socket picks up the labels and
registers the resource with Pangolin within ~10s.

**Secret hydration pipeline**: `.infisical.env` (committed
template) → `bun run secrets:init` (pushes values to
Infisical `dev-baile` vault) → Locket sidecar (resolves
`infisical://...` refs at container boot) → container env
at runtime.

**5 architectural principles**: zero-trust by default (no
public exposure), passkey-only auth (no passwords to phish),
GitOps-friendly (`compose.yaml` + `pangolin.yaml` +
`secrets.env` overlay per stack), self-hosted (no SaaS
dependencies), open source (Pangolin + PocketID + TinyAuth
+ Infisical + n8n + Vikunja + Glance + ChangeDetection +
Locket — all FOSS).

**3 common troubleshooting issues**: (1) "Cannot access
service" → check Olm, check Pangolin resource
registration, check Newt Docker network; (2) "Service in
restart loop" → usually missing Locket env var, check
`docker logs` for "env file not found" or auth errors,
verify secret in Infisical; (3) "Locket can't connect to
Infisical" → Locket needs Docker gateway URL
(`http://172.18.0.1:8081`), set `INFISICAL_URL` in stack's
`.env`, confirm `infisical-machine-identity` exists.

**4 "what's next" items** (status as of 2026-06-06): n8n
+ Vikunja OIDC login (clients in PocketID pending), n8n
workflows connected to Infisical for credential
provisioning, cal-diy + paperless-ngx stacks deployed
(compose files ready, need `compose up`), Beszel monitoring
agent on arm1-oci (currently restarting).

The **migration report** at
`references/team-workflow-migration-2026-06-06.md` (268
lines) covers the Infisical v0.160.10 migration, the
Locket URL fix, and the 22-folder audit. It is the
canonical handoff for any new team member onboarding to
the workflow stack.

See `references/TEAM_HANDOFF.md` for the full 168-line
team handoff: the network diagram, the 8 live private
resources table, the 3-step onboarding flow, the 5
architectural planes, the resource declaration pattern,
the secret hydration pipeline, the 3 common
troubleshooting issues, the 5 architectural principles,
and the screenshot references.
- `infrastructure/GOLD_STANDARD.md` — the 6-file pattern per stack
