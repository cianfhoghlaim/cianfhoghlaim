---
name: kcg-convergence
description: KCG's 6 docker-compose categories (control plane / storage / engineering / machine_learning / tools / browser) + port allocation map (3000-3499 user apps, 3500-3999 APIs, 4000-4499 Dagster, 5000-5499 data, 6000-6999 AI/ML, 7000-7999 dev, 8000-8999 MMO, 9000-9999 infra). Use when adding a new stack, picking a port, understanding which category a new service belongs to, or asking "where in the 6 categories does X live?".
---

# KCG Convergence

## When to use this skill

Use when you need to:

- "Add a new stack — which category does it go in?"
- "Pick a port for a new service"
- "Understand the 6 categories"
- "Onboard a new dev to the KCG monorepo's infra shape"
- "Map a stack to the right host tier (control / storage /
  workload)"

## The 6 docker-compose categories

The 70+ KCG Docker Compose stacks live in
`infrastructure/stacks/` and are organised into 6
categories by **purpose**, not by host:

| # | Category | Path | Purpose |
|:--|:--|:--|:--|
| 1 | **Control plane** | `infrastructure/` | Pangolin (zero-trust), Komodo (GitOps), Pocket ID (OIDC), CrowdSec (WAF), PlanetScale (Postgres), MotherDuck, R2 bridge, Pulumi, Forgejo, Dozzle |
| 2 | **Storage** | `infrastructure/stacks/storage/` | Garage (S3), Lakehouse (Lakekeeper + Lance Namespace + Postgres), LakeFS, Beszel |
| 3 | **Engineering** | `infrastructure/stacks/engineering/` | LiteLLM, Dagster, oideachais, Convex, Windmill, n8n, Coder, DevDocs, MCPJungle, crawl4ai |
| 4 | **Machine learning** | `infrastructure/stacks/machine_learning/` | Cognee, Graphiti, Langfuse, MLflow, Qdrant, Memgraph, FalkorDB, LanceDB, olake, lmnr, logfire, nimtable |
| 5 | **Tools** | `infrastructure/stacks/tools/` | 17 productivity / media / dev utilities |
| 6 | **Browser** | `infrastructure/stacks/browser/` | Browser automation (Skyvern, crawl4ai) |

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
| **3000-3499** | User apps | TanStack Start (oideachais/web) :3000, Forgejo :3000, Browse :3001 |
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
├── Is it the control plane (Pangolin/Komodo/Pocket ID/etc.)?
│   └── infrastructure/ (no category subdir)
│
├── Is it data storage (S3 / Postgres / Iceberg)?
│   └── infrastructure/stacks/storage/
│
├── Is it dev tooling / API gateway / orchestration?
│   └── infrastructure/stacks/engineering/
│
├── Is it ML / AI / graph / vector?
│   └── infrastructure/stacks/machine_learning/
│
├── Is it productivity / media / dev utility?
│   └── infrastructure/stacks/tools/<subcategory>/
│
└── Is it a browser automation?
    └── infrastructure/stacks/browser/
```

## Cross-references

- `.agents/skills/kcg-bunchloch/SKILL.md` — the 3-tier
  host convergence (where the categories run)
- `.agents/skills/stack-ops/SKILL.md` — the 6-file
  GOLD_STANDARD pattern (how each stack is structured)
- `.agents/skills/oideachais-storage/SKILL.md` — the
  storage layer detail
- `.agents/skills/kcg-leabharlann-pipeline/SKILL.md` — the
  5-stage pipeline that touches all 6 categories
- `infrastructure/AGENTS.md` — the canonical 6-category
  reference
- `infrastructure/stacks/GOLD_STANDARD.md` — the 6-file
  pattern per stack
