# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Six Docker-Compose Categories

The system SHALL organize the 70+ Docker Compose stacks
under `infrastructure/stacks/` into 6 categories by purpose:

1. **Control plane** (`infrastructure/`) — Pangolin, Komodo,
   Pocket ID, CrowdSec, PlanetScale, MotherDuck, R2 bridge,
   Pulumi, Forgejo, Dozzle
2. **Storage** (`infrastructure/stacks/storage/`) — Garage
   S3, Lakehouse (Lakekeeper + Lance Namespace + Postgres),
   LakeFS, Beszel
3. **Engineering** (`infrastructure/stacks/engineering/`) —
   LiteLLM, Dagster, oideachais, Convex, Windmill, n8n,
   Coder, DevDocs, MCPJungle, crawl4ai
4. **Machine learning** (`infrastructure/stacks/machine_learning/`) —
   Cognee, Graphiti, Langfuse, MLflow, Qdrant, Memgraph,
   FalkorDB, LanceDB, olake, lmnr, logfire, nimtable
5. **Tools** (`infrastructure/stacks/tools/`) — 17 stacks
   spanning productivity (actual, blinko, linkwarden,
   presenton, stirling-pdf), media (audiobookshelf,
   kapowarr, pinchflat, rybbit), and development
   (changedetection, enclosed, pastemax, perplexica,
   skyvern, LetterFeed, romm, mailcow-dockerized)
6. **Browser** (`infrastructure/stacks/browser/`) —
   browser automation (Skyvern, crawl4ai)

#### Scenario: A new stack fits the right category

- **GIVEN** a developer wants to add a new "Pocket ID
  bridge" stack
- **WHEN** they look at `infrastructure/AGENTS.md` and the
  kcg-convergence skill's category map
- **THEN** the answer is unambiguously "control plane"
  (because Pocket ID is the OIDC SSO for Pangolin) — not
  "engineering" (which is for dev tools) or "tools"

#### Scenario: A leabharlann PDF flows through all 6 layers

- **GIVEN** a leabharlann PDF lands at
  `leabharlann/gaeilge/<file>.pdf`
- **WHEN** the Dagster asset materialises
- **THEN** the Locket sidecar (control plane) injects
  Infisical secrets
- **AND** the Garage S3 (storage) holds the Parquet
- **AND** the Dagster + LiteLLM + BAML (engineering)
  orchestrate + extract
- **AND** the Cognee + FalkorDB + LanceDB (machine learning)
  serve the graph + vector
- **AND** the DevDocs (tools) hosts the analyst dashboard
- **AND** the crawl4ai (browser) scrapes the next page in
  Phase 2

### Requirement: Three-Tier Host Convergence

The system SHALL deploy the KCG platform across a
**3-tier host convergence model** rather than a single host
or a 2-tier model:

| Tier | Host | Role | Key stacks |
|:--|:--|:--|:--|
| **Control plane** | `arm1-oci` (Oracle Cloud ARM free tier) | Komodo (GitOps) + Pangolin (zero-trust) + Pocket ID (OIDC) + CrowdSec (WAF) | Komodo :9120, Pangolin :3001, Gerbil :51820/udp, Pocket ID :1411 |
| **Storage** | `cax41-hetzner` (Hetzner Cloud ARM) | Garage (S3) + Lakekeeper (Iceberg REST) + Postgres (catalog) + LakeFS (data versioning) | Garage :3900-3904, Lakekeeper :8181, Lance Namespace :8182, Postgres :5433 |
| **Workload** | `bunchloch` (MacBook M4 Max, 48GB) | Dagster (orchestration) + LiteLLM (LLM gateway) + CocoIndex (embedding) + the 70+ model backends (GGUF/MLX/safetensors) | Dagster :3335, LiteLLM :4000, llama-swap :8080, mlx-omni-server :10240, invokeai :9090 |

The 3 tiers are wired by **Pangolin WireGuard tunnels**
(arm1-oci Gerbil :51820/udp) and **Locket sidecars** that
inject Infisical secrets into every container (no plaintext
on disk).

#### Scenario: A Dagster asset on bunchloch reads from arm1-oci Pangolin

- **GIVEN** a Dagster asset on `bunchloch` is materialising
- **WHEN** it calls a service that is only exposed on the
  `arm1-oci` Pangolin proxy
- **THEN** the WireGuard tunnel (via Newt) routes the call
  through Pangolin
- **AND** Pocket ID OIDC validates the JWT
- **AND** the response returns within the standard RTT
  budget for the cluster

#### Scenario: A new Cognee dataset lands on the storage tier

- **GIVEN** a Dagster asset on `bunchloch` runs
  `cognee.cognify()`
- **WHEN** the cognify call writes to the knowledge graph
- **THEN** the data is persisted on the `cax41-hetzner`
  storage tier (Lakekeeper Iceberg REST + Lance Namespace)
- **AND** the metadata is registered in Postgres
- **AND** the next reader (on `bunchloch` or `arm1-oci`)
  reads the Iceberg table via the Lakekeeper REST API

## REMOVED Requirements

(None.)
