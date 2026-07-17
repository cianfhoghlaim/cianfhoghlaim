# Infrastructure Stacks Capability

## Purpose

`infrastructure-stacks` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

## Background
94 storage, utility, engineering, machine learning, and infrastructure Docker Compose stacks managed via Komodo for the Cianfhoghlaim platform. Organised in a **flat** directory layout (one directory per stack under `bonneagar/stacks/<name>/`) with standardized Pangolin routing, Locket secret injection, and Infisical secret management. The historical 5-category subdirectory split (`storage/`, `engineering/`, `infrastructure/`, `machine_learning/`, `tools/`) was removed on 2026-06-23; functional groups are now informational only and recorded in `infrastructure/AGENTS.md` and `infrastructure/QUADRANT-TO-STACK-MAP.md`.

| Feature | Description |
|---------|-------------|
| Foundational substrates | Vector, graph, relational databases, lakehouse, AI memory |
| Dev tooling + gateways + services | Dev tooling, API gateways, MCP servers |
| AI services | Training infrastructure, LLM serving |
| Control plane | Pangolin control plane, Komodo, Pocket ID |
| Productivity + media | Productivity, media, development utilities |
## Requirements
### Requirement: Stack Standardization

The system SHALL enforce a **6-file GOLD_STANDARD** for every
`bonneagar/stacks/<name>/` directory. The 6 files are:

1. `compose.yaml` — the Docker Compose stack definition
2. `sidecar.yaml` — the Locket secret-injection sidecar (uses
   `user: 65532:65532` + `no-new-privileges:true` + `cap_drop: [ALL]` +
   `read_only: true` + `tmpfs: [/run/secrets/locket:size=1m,mode=0700]`)
3. `secrets.env` — the list of `infisical://dev-baile/<svc>/<key>` URIs
4. `pangolin.yaml` — the 6-label private resource declaration
5. `blueprint.yaml` — the rendered Pangolin state
6. `.env.example` — the documentation of every env var (every
   stack that declares a custom env var MUST have `.env.example`)

The `bun run stack-doctor` CI gate SHALL fail the build if any
of the 6 files is missing.

The `sidecar.yaml` SHALL declare one of 3 `LOCKET_MODE` values:
`watch` (long-running services, the default), `exec` (batch jobs),
or `oneshot` (CI/CD pipelines).

The `pangolin.yaml` SHALL follow the 6-label shape (`name`,
`mode`, `full-domain`, `destination-port`, `protocol`, `roles[0]`)
documented in `.agents/skills/kcg-pangolin-stack/SKILL.md`.

#### Scenario: A new stack is added to `bonneagar/stacks/<name>/`

- **GIVEN** the stack dir has been created with 1 or 2 of the 6
  GOLD_STANDARD files
- **WHEN** `bun run stack-doctor` runs on the PR
- **THEN** the gate SHALL fail with exit code 1 (missing file)
- **AND** the developer MUST add the remaining files before the
  PR merges

#### Scenario: A Locket sidecar uses the canonical security baseline

- **GIVEN** `bonneagar/stacks/cianfhoghlaim-dagster/sidecar.yaml`
- **WHEN** the stack is deployed
- **THEN** the Locket container SHALL have `user: 65532:65532` +
  `no-new-privileges: true` + `cap_drop: [ALL]` + `read_only: true`
  + `tmpfs: [/run/secrets/locket:size=1m,mode=0700]`
- **AND** the `cianchoghlaim_locket_secrets` external tmpfs volume
  SHALL be mounted

### Requirement: Storage Stacks

The system SHALL deploy database and data infrastructure for the lakehouse architecture. The dev lakehouse stack MUST extend the canonical Garage + Postgres + Lakekeeper + Lance Namespace sidecar foundation with an Iceberg catalog UI, a CDC ingestion engine, and a LanceDB table viewer. Every active srutha MUST be wired into the lakehouse via the canonical cross-sruth contract documented in the `Cross-Sruth Lakehouse Wiring Contract` requirement below.

#### Scenario: Lakehouse Stack

- **GIVEN** lakehouse stack with Garage S3, Postgres, Lakekeeper, and Lance Namespace sidecar
- **WHEN** stack deploys via Komodo
- **THEN** S3 API (3900), Postgres (5433), Iceberg REST catalog (8181), and Lance sidecar (8182) are accessible

#### Scenario: Lakehouse Iceberg Catalog UI

- **GIVEN** the Nimtable service appended to `bonneagar/stacks/lakehouse/compose.yaml`
- **WHEN** the lakehouse stack deploys
- **THEN** Nimtable is accessible at `http://localhost:3018` and `https://nimtable.cianfhoghlaim.ie` (via Pangolin)
- **AND** Nimtable connects to the shared Postgres at `jdbc:postgresql://postgres:5432/nimtable` and surfaces all Iceberg tables registered in Lakekeeper
- **AND** the `nimtable` service resource usage is capped at `cpus: '1'`, `memory: 512M` per service

#### Scenario: Lakehouse CDC Engine (Olake)

- **GIVEN** the Olake service appended to `bonneagar/stacks/lakehouse/compose.yaml`
- **WHEN** the lakehouse stack deploys
- **THEN** Olake is reachable via `https://olake.cianfhoghlaim.ie` (admin via `docker exec`) for CDC jobs
- **AND** Olake reads its source/catalog/writer config from `bonneagar/stacks/lakehouse/olake/{config,catalog,writer}.json`
- **AND** Olake persists checkpoint + offset state to the named volume `olake_state` and the Postgres DB `olake_state`
- **AND** the `olake` service resource usage is capped at `cpus: '1'`, `memory: 512M` per service

#### Scenario: Lakehouse LanceDB Viewer

- **GIVEN** the lancedb-viewer service appended to `bonneagar/stacks/lakehouse/compose.yaml`
- **WHEN** the lakehouse stack deploys
- **THEN** the LanceDB viewer is accessible at `http://localhost:8081` and `https://lance-viewer.cianfhoghlaim.ie` (via Pangolin)
- **AND** the viewer connects to the Lance namespace at `rest://lakehouse-lance-namespace:8182`
- **AND** the `lancedb-viewer` service resource usage is capped at `cpus: '0.5'`, `memory: 256M` per service

#### Scenario: AI Memory Stacks

- **GIVEN** Cognee and Graphiti stacks
- **WHEN** stacks deploy
- **THEN** knowledge graph and temporal memory services are available

#### Scenario: Vector Database Stacks

- **GIVEN** LanceDB, Qdrant, and FalkorDB stacks
- **WHEN** stacks deploy
- **THEN** vector search infrastructure is accessible

### Requirement: Engineering Stacks

The system SHALL deploy developer tooling and API infrastructure.

#### Scenario: LiteLLM Gateway
- **GIVEN** LiteLLM stack with Postgres and Prometheus
- **WHEN** stack deploys
- **THEN** LLM proxy is accessible on port 4000

#### Scenario: Crawl4AI
- **GIVEN** Crawl4AI stack
- **WHEN** stack deploys
- **THEN** web crawling API is accessible for curriculum ingestion

### Requirement: Infrastructure Stacks

The system SHALL deploy the Pangolin Convergence control plane.

#### Scenario: Pangolin Stack
- **GIVEN** pangolin stack with Traefik, Gerbil, Pocket ID, TinyAuth, and CrowdSec
- **WHEN** stack deploys
- **THEN** WireGuard VPN (51820/udp), HTTPS (443), HTTP (80), and TinyAuth (8443) are available

#### Scenario: Komodo Stack
- **GIVEN** Komodo stack with MongoDB
- **WHEN** stack deploys
- **THEN** Komodo UI is accessible at port 9120

### Requirement: Stack Audit Scripts

The monorepo SHALL provide shell scripts under
`infrastructure/audit/scripts/` that capture the live state of
the 2-host topology (bunchloch + arm1-oci) and surface
divergences from the filesystem `compose.yaml` files.

The scripts SHALL be runnable from the operator's MacBook
(`bunchloch`) and SHALL write JSON snapshots to
`infrastructure/audit/inventory/<host>-<UTC-timestamp>.json`.

#### Scenario: Snapshot bunchloch containers

- **GIVEN** the operator has Docker installed on bunchloch
- **WHEN** the operator runs `bash infrastructure/audit/scripts/inventory-bunchloch.sh`
- **THEN** a JSON file appears at `infrastructure/audit/inventory/bunchloch-<timestamp>.json`
- **AND** the JSON contains: `containers[]` (with name, image, state, ports, mounts, networks), `networks[]`, `volumes[]`, and a top-level `host_info` block

#### Scenario: Snapshot arm1-oci containers

- **GIVEN** the operator's `~/.ssh/config` has an `arm1-oci` host entry
- **AND** the operator has passwordless SSH to arm1-oci
- **WHEN** the operator runs `bash infrastructure/audit/scripts/inventory-arm1-oci.sh`
- **THEN** a JSON file appears at `infrastructure/audit/inventory/arm1-oci-<timestamp>.json`
- **AND** the JSON shape matches the bunchloch snapshot

#### Scenario: Diff against filesystem composes

- **GIVEN** the operator has run both inventory scripts
- **WHEN** the operator runs `bash infrastructure/audit/scripts/diff-against-composes.sh <bunchloch.json> <arm1-oci.json>`
- **THEN** the script prints a table of: orphaned containers (live, not in any compose), missing services (in a compose, not running), port conflicts (same host port, two services)

#### Scenario: Probe public Pangolin URLs

- **GIVEN** the operator has network access to the Pangolin-routable `*.cianfhoghlaim.ie` domains
- **WHEN** the operator runs `bash infrastructure/audit/scripts/probe-public-urls.sh`
- **THEN** the script reads `infrastructure/pangolin/a2a-resources.blueprint.yaml`
- **AND** for each `full-domain` entry, prints the URL, the HTTP status code, and the round-trip time
- **AND** the script returns exit code 0 if all probed URLs are 2xx, 3xx, or 4xx; exit code 1 if any URL is 5xx or unreachable

### Requirement: Deployment Runbook

Every user-named deploy target SHALL have a 1-page Markdown
runbook under `infrastructure/deploy-runbooks/<name>.md` that
documents the deploy steps as shell snippets copy-pastable
into a future AI agent's run loop.

A runbook is in scope for this requirement if it is on the
2026-06-15 user-named list:
`infisical`, `komodo`, `pangolin`, `ansible`, `cal-diy`,
`vikunja`, `n8n`, `changedetection`, `bytebase`.

#### Scenario: A runbook exists for each user-named target

- **GIVEN** the 2026-06-15 audit identified 9 user-named deploy targets
- **WHEN** a future AI agent queries `ls infrastructure/deploy-runbooks/`
- **THEN** the 9 expected `<name>.md` files are present (one per target)

#### Scenario: A runbook contains diagnostic checks

- **GIVEN** a runbook exists at `infrastructure/deploy-runbooks/<name>.md`
- **WHEN** a future AI agent greps the runbook for the section headings `## Pre-flight`, `## First-time deploy`, `## Verify`, `## Rollback`
- **THEN** all 4 sections are present
- **AND** each section has at least one shell snippet prefixed with ```` ```bash ```` and a `curl`-based diagnostic

#### Scenario: A runbook does not execute the deploy itself

- **GIVEN** a runbook exists
- **WHEN** the runbook is opened in a text editor
- **THEN** it is documentation only — no shell script that starts the deploy runs as a result of opening the file
- **AND** every `docker compose up` / `komodo sync` / `infisical` call is guarded by an explicit shell comment noting that the agent must paste the snippet, not auto-execute it

### Requirement: Embedding pipeline as a first-class infrastructure concern

The system SHALL treat the embedding pipeline (BGE-M3
inference + batching + HNSW lifecycle) as a first-class
infrastructure concern, with canonical patterns documented in
`.agents/skills/embedding-pipeline/SKILL.md`.

#### Scenario: Embedding pipeline bootstraps a new corpus

- **GIVEN** a new corpus at `stedding/ingest_queue/<corpus>/`
  (e.g. a fresh NCCA PDF dump)
- **WHEN** the `embedding_pipeline_bootstrap` Dagster asset
  runs
- **THEN** the `BatchedEmbeddingService` is invoked with
  `MIN_EMBEDDING_BATCH_SIZE = 100` (the KCG production rule
  for 100× performance)
- **AND** the embeddings are persisted to LanceDB via
  `lancedb.mount_table_target`
- **AND** the HNSW index is dropped and recreated above 50k
  rows

### Requirement: Monorepo infrastructure (bun + uv + turbo)

The system SHALL use a polyglot monorepo (bun + uv + turbo)
managed via the Inner/Outer loop pattern (mise = inner
loop, Dagger = outer loop), documented in
`.agents/skills/monorepo/SKILL.md`.

#### Scenario: New workspace member added

- **GIVEN** a new quadrant (e.g. `meaisínfhoghlaim/`) needs
  to be added to the monorepo
- **WHEN** the developer runs `mise run monorepo:add-member
  meaisínfhoghlaim`
- **THEN** the workspace is updated in `package.json`
  (TypeScript) and `pyproject.toml` (Python)
- **AND** the turbo pipeline is updated in `turbo.json`
- **AND** the mise polyglot toolchain is updated in `mise.toml`
- **AND** `dagger call test` runs the new member's test suite
  hermetically

### Requirement: Flat Stack Layout

The system SHALL organise the 94 Docker Compose stacks under
`bonneagar/stacks/` in a **flat** layout — every stack
is a direct child of `bonneagar/stacks/`, with no
category subdirectory. Functional purpose (control plane,
storage, engineering, ML, tools, browser) is recorded as
**information only** in `infrastructure/AGENTS.md` § "Stack
Inventory" and the cross-quadrant routing table at
`infrastructure/QUADRANT-TO-STACK-MAP.md`, and is not
encoded in the directory hierarchy.

A new stack's directory is therefore `bonneagar/stacks/<name>/`
and not `bonneagar/stacks/<category>/<name>/`.

#### Scenario: A new stack is added

- **GIVEN** a developer wants to add a new "Pocket ID
  bridge" stack
- **WHEN** they create `bonneagar/stacks/pocket-id-bridge/`
  with the 6 GOLD_STANDARD files
- **THEN** `bun run stack-doctor.sh` validates it under the
  flat layout
- **AND** the developer adds a row to the **Stack Inventory**
  table in `infrastructure/AGENTS.md` (alphabetical, with
  purpose and ports)
- **AND** the row's purpose field ("control plane" for a
  Pocket ID bridge) is informational only — it does not
  imply a subdirectory

#### Scenario: A leabharlann PDF flows through the data plane

- **GIVEN** a leabharlann PDF lands at
  `leabharlann/gaeilge/<file>.pdf`
- **WHEN** the Dagster asset materialises
- **THEN** the Locket sidecar (bonneagar/stacks/<name>)
  injects Infisical secrets
- **AND** the Garage S3 (bonneagar/stacks/garage) holds
  the Parquet
- **AND** the Dagster + LiteLLM + BAML
  (bonneagar/stacks/dagster, litellm, oideachais)
  orchestrate + extract
- **AND** the Cognee + FalkorDB + LanceDB
  (bonneagar/stacks/cognee, falkordb, lancedb) serve
  the graph + vector
- **AND** the DevDocs (bonneagar/stacks/DevDocs) hosts
  the analyst dashboard

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

### Requirement: Skill consolidation ratio

KCG-authored umbrella skill trees (e.g. MotherDuck, browser, code search) MUST be reorganised so that no more than 5 task-specific sub-skills exist per tree, with a single routing skill that dispatches to the right one.

#### Scenario: MotherDuck skill tree is consolidated

- **WHEN** an agent triggers a phrase that should load a MotherDuck skill
- **THEN** the loader matches one of: `motherduck` (router), `motherduck-architecture`, `motherduck-data-modeling`, `motherduck-analytics`, `motherduck-connections` (4 task-specific)
- **AND** the 18 prior `motherduck-*` sub-skills are removed

#### Scenario: Router points to the 4 consolidated skills

- **WHEN** `motherduck/SKILL.md` is read
- **THEN** it contains a router table that points to exactly `motherduck-architecture`, `motherduck-data-modeling`, `motherduck-analytics`, `motherduck-connections` (no orphan references to deleted skills)

### Requirement: Browser tools consolidation

KCG browser / scraping / agent-on-the-web skills MUST be consolidated to exactly 3 entry points: 1 routing skill (`browser-tools`) + the 2 Firecrawl variants (MCP + Bash CLI). All upstream-specific skills (browserbase-cli, stagehand, cookie-sync, safe-browser, firecrawl-crawl, firecrawl-scrape, etc.) MUST be deleted, with their content absorbed into the router or the 2 kept Firecrawl skills.

#### Scenario: Agent picks the right browser tool

- **WHEN** an agent needs to scrape a URL, click a button, or run an autonomous agent-on-the-web task
- **THEN** the loader matches one of: `browser-tools` (router), `firecrawl` (MCP), `firecrawl-cli` (Bash)
- **AND** the 17 prior browser / firecrawl sub-skills are removed

#### Scenario: Router points to all 3 entry points

- **WHEN** `browser-tools/SKILL.md` is read
- **THEN** it contains a 6-tool table (Stagehand, Firecrawl MCP, Firecrawl CLI, crawl4ai, browser, safe-browser) + a decision tree + KCG safety rules

### Requirement: Single canonical code search skill

The code search capability SHALL be provided by exactly one skill: `ccc`. The canonical implementation uses CocoIndex v1 + BGE-M3 embeddings + LanceDB HNSW + Dagster asset group. Alternative engines (e.g. ChunkHound) MAY be documented as a subsection of `ccc/SKILL.md` but MUST NOT ship as a separate top-level skill.

#### Scenario: Agent uses ccc for code search

- **WHEN** an agent needs to search the codebase, find a function definition, or summarise a directory
- **THEN** the loader matches exactly one skill: `ccc`
- **AND** `chunkhound` is no longer a top-level skill (its content lives in `ccc/SKILL.md` Appendix A)

#### Scenario: ccc documents the ChunkHound alternative

- **WHEN** an agent reads `ccc/SKILL.md`
- **THEN** an "Appendix A: Alternative engines" section exists
- **AND** that section documents when to use ChunkHound over ccc (the multi-hop exploration pattern, the air-gapped / no-cloud use case)

### Requirement: Infrastructure stacks router skill

The infrastructure stacks capability MUST be discoverable via a single router skill at `.agents/skills/infrastructure-stacks/SKILL.md`. The router SHALL document the 6-file GOLD_STANDARD pattern, the 3-tier host convergence (arm1-oci / bunchloch / cax41-hetzner), the 5-stage deploy procedure, the 11 inventory categories, the 5 integration points (Pangolin / Locket / Komodo / LiteLLM / Langfuse), and the port allocation map.

#### Scenario: Agent finds the infrastructure router

- **WHEN** an agent searches for "add a stack", "fix stack", "stack-doctor", "GOLD_STANDARD", "compose.yaml", or "94 stacks"
- **THEN** the loader matches `.agents/skills/infrastructure-stacks/SKILL.md`
- **AND** the skill points at the underlying operational skills (kcg-convergence, stack-ops, kcg-bunchloch, pangolin, komodo, secrets-management)

### Requirement: Skills are refreshed to the current package state

Every KCG-authoritative skill that documents a third-party package (CocoIndex, Dagster, Cognee, MotherDuck, Langfuse, etc.) MUST have a "2026-06 update" or equivalent date-stamped section that captures the latest package features. The section SHALL be appended at the end of the skill (after the "Pair this skill with" cross-references) and SHALL include a date stamp so agents can see the freshness of the content.

#### Scenario: Agent sees the 2026-06 feature set

- **WHEN** an agent reads a skill that documents a package with a major release after the skill was last updated
- **THEN** the skill contains a "## 2026-06 update" (or equivalent) section
- **AND** that section covers the major features released since the original skill was written

#### Scenario: Refresh is a single openspec change

- **WHEN** a batch of skills needs a 2026-06 update
- **THEN** the batch is captured in one openspec change (the `refresh-skills-to-2026-06` change)
- **AND** the change is archived after the commit

### Requirement: Skill metadata hygiene

Every skill under `.agents/skills/` MUST have: (1) a YAML frontmatter block with `name:` and `description:`, (2) a `name:` field that equals the parent directory name, (3) a `description:` field of at least 40 characters, and (4) a `SKILL.md` body under 2,000 lines.

#### Scenario: lint:skills passes

- **WHEN** `mise run lint:skills` runs against the current `.agents/skills/` tree (post-consolidation: 110 skills)
- **THEN** all 110 skills pass the 4 metadata checks (frontmatter, name match, description length, line count)
- **AND** the script exits 0

#### Scenario: New skill violates a rule

- **WHEN** a new skill is added without frontmatter, or with a name that does not match its directory, or with a < 40-char description, or with a > 2000-line body
- **THEN** `mise run lint:skills` reports the violation and exits 1

### Requirement: Skill consolidation conventions

KCG skills MUST follow: (5) the canonical name prefixes (motherduck* / browser-tools / ccc / kcg-* / cianfhoghlaim-* / tuatha-* / croilar-* / meaisinfhoghlaim-*), (6) no vendoring of upstream Anthropic / vendor skills, (7) no skills that duplicate the root `AGENTS.md` "Critical Agent Protocols" content, (8) no embedded git sub-repositories.

#### Scenario: New skill follows the prefixes

- **WHEN** a new skill is added for, e.g., the Convex backend
- **THEN** the directory is `convex/` (not `convex-crm/` or `vendor-convex/`)
- **AND** the frontmatter `name: convex` matches the directory

#### Scenario: Upstream skill is referenced, not vendored

- **WHEN** a third-party tool's docs are needed (e.g. Anthropic's design patterns)
- **THEN** the content lives in a KCG-authored skill (e.g. `frontend-design`) with cross-links to the upstream source
- **AND** the upstream skill directory is NOT vendored into `.agents/skills/`

### Requirement: Skill + openspec alignment

Every openspec capability spec MUST have either a matching `.agents/skills/<spec>/SKILL.md` or an explicit "absorbed into <other-skill>" annotation in `openspec/AGENTS.md`. When an openspec change is archived, the canonical skill SHOULD get a "Post-archive update" note (or be the change's "implementation in skill.md" reference).

#### Scenario: Every spec has a skill pointer

- **WHEN** `openspec list --specs` is run
- **THEN** every spec has either a matching `.agents/skills/<spec>/SKILL.md` OR an entry in `openspec/AGENTS.md` "Capability Specs" table that names a parent skill

#### Scenario: Archived change has a post-archive note

- **WHEN** an openspec change is archived (`openspec archive`)
- **THEN** the canonical skill (if any) gains a "Post-archive update" or "Last archived: <date>" note
- **AND** agents reading the skill know the change is no longer pending

### Requirement: Project to openspec to skill feedback loop

The Cianfhoghlaim platform MUST maintain a formal feedback loop between projects, openspec changes, and skills. (1) When an openspec change is archived, the canonical skill (if any) gets a "Post-archive update" note in its cross-reference table. (2) When a project changes a BAML extraction / DLT source / Dagster asset, the corresponding skill (`baml`, `dlt`, `dagster`) gets a 1-line addition to its "When to use this skill" section. (3) When a project's `STATUS.md` / `REFACTORING.md` / README.md changes, the `data-engineering-pipeline-documentation` skill gets a link to the new content.

#### Scenario: New openspec change updates the canonical skill

- **WHEN** an openspec change is archived
- **THEN** the canonical skill (e.g. `motherduck-architecture` for a MotherDuck change) gets a "Post-archive update: 2026-06-24-..." note in its cross-reference section

#### Scenario: New DLT source updates the dlt skill

- **WHEN** a new DLT source is added under `cianfhoghlaim/dlt_sources/`
- **THEN** the `.agents/skills/dlt/SKILL.md` "KCG examples" appendix gets a 1-line addition naming the new source

### Requirement: Quadrant-specific Related skills

Each quadrant's `AGENTS.md` "Related skills" section MUST list only the skills used by that quadrant (no shared "default" list across quadrants). The 4 quadrants are `oideachais`, `meaisinfhoghlaim`, `tuatha`, `croilar`, plus the cross-cutting `infrastructure` layer.

#### Scenario: cianfhoghlaim/AGENTS.md lists 12 cianfhoghlaim-specific skills

- **WHEN** `cianfhoghlaim/AGENTS.md` is read
- **THEN** the "Related skills" section lists 12+ skills (dagster, dlt, baml, cocoindex, cognee, lancedb, falkordb, duckdb, motherduck, dignified-python, marimo, ccc, cianfhoghlaim-storage, cianfhoghlaim-pipeline, cianfhoghlaim-leabharlann, cianfhoghlaim-baml-schemas, cianfhoghlaim-cognify-knowledge-graph)
- **AND** does NOT list skills specific to other quadrants (e.g. babylonjs for tuatha, hono for croilar)

#### Scenario: Each archived change points at the canonical skill

- **WHEN** an openspec change is archived
- **THEN** the archived `proposal.md` "What changes" section includes a line "Canonical skill: `.agents/skills/<skill>/SKILL.md`" naming the skill that should receive the post-archive note

### Requirement: Priority quick reference section in every AGENTS.md

Every AGENTS.md file under the Cianfhoghlaim monorepo (`/AGENTS.md`, the 4 quadrant `AGENTS.md` files, `/infrastructure/AGENTS.md`, `/openspec/AGENTS.md`) MUST start with a "Priority quick reference" section (immediately after the title heading) that prominently surfaces the canonical skills, the ccc code-search command, the openspec commands, and the priority tools for that file's audience. The section MUST be at most 50 lines and MUST be a structured table (not prose).

#### Scenario: Root AGENTS.md leads with priority quick reference

- **WHEN** an agent reads `/AGENTS.md` from the repo root
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it contains 4 tables: Priority skills (5 entries), ccc + openspec commands, Priority mise tasks (4 entries), Priority compose stacks (4 entries)

#### Scenario: Quadrant AGENTS.md leads with priority quick reference

- **WHEN** an agent reads `/cianfhoghlaim/AGENTS.md` (or any of the 4 quadrant `AGENTS.md` files)
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it lists the 5-8 skills most relevant to that quadrant + the ccc command + the 4 openspec commands

#### Scenario: infrastructure/AGENTS.md leads with priority quick reference

- **WHEN** an agent reads `/infrastructure/AGENTS.md`
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it contains the stack-doctor command + the stack-ops skill + the 4 priority compose stacks (oideachais, litellm, langfuse, lakehouse)

#### Scenario: openspec/AGENTS.md leads with priority quick reference

- **WHEN** an agent reads `/openspec/AGENTS.md`
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it contains the 4 priority specs (cianfhoghlaim-pipeline, infrastructure-stacks, agent-memory-systems, dagger-pipelines) + the ccc command + the lint:skills task

### Requirement: Stack-Doctor CI Gate

The system SHALL run `bun run stack-doctor` on every PR via a
GitHub Action. The 4 gates are:

1. **File gate** (exit code 1) — every
   `bonneagar/stacks/<name>/compose.yaml` has the other 5
   GOLD_STANDARD files
2. **Container gate** (exit code 2) — every `container_name:` is
   in the live inventory OR explicitly documented as
   `stacked-only: true` in a `kcg-meta.yaml` file
3. **Secret gate** (exit code 4) — every `secrets.env` URI
   resolves in the Infisical vault (via `bun run scripts/init-vault.ts`)
4. **Pangolin gate** (exit code 8) — every `pangolin.yaml`
   parses against the official 6-label schema

The script's exit code SHALL be the bitwise-OR of the 4 gate
failures. The CI workflow SHALL report which gates failed in
the GitHub Actions summary.

The system SHALL also enforce the 3 host tags
(`host:bunchloch`, `host:arm1-oci`, `host:cax41-hetzner`) on every
Komodo stack definition; reference stacks MAY have no tag.

#### Scenario: A PR adds a new compose file but is missing the other 5 files

- **GIVEN** a developer adds `bonneagar/stacks/<new>/compose.yaml`
  with a new service
- **WHEN** the PR's GitHub Action runs `bun run stack-doctor`
- **THEN** the File gate (exit code 1) SHALL fail
- **AND** the Action SHALL post a comment on the PR listing the
  5 missing files
- **AND** the PR SHALL be blocked from merging

#### Scenario: A secret URI in `secrets.env` doesn't resolve in the vault

- **GIVEN** a developer adds
  `INFI_FOO=infisical://dev-baile/cianfhoghlaim/foo` to
  `bonneagar/stacks/<stack>/secrets.env`
- **AND** the `dev-baile` Infisical environment does NOT have a
  secret at path `cianfhoghlaim/foo`
- **WHEN** the Secret gate runs
- **THEN** the gate SHALL fail with exit code 4
- **AND** the developer MUST either create the secret in
  Infisical OR remove the URI from `secrets.env`

### Requirement: Image Pinning Policy

The system SHALL pin every `image:` line in every
`bonneagar/stacks/<name>/compose.yaml` to a specific
`<major>.<minor>.<patch>` semver tag. The tag `:latest` is
**forbidden** for upstream images. Local-build images with
`pull_policy: never` are exempt and MUST include an inline YAML
comment explaining the deviation.

The `stack-doctor` SHALL report any unpinned image as
**WARNING** (exit code 1, soft failure) so that pre-existing
stacks can be migrated incrementally.

#### Scenario: A PR introduces an unpinned image

- **GIVEN** a developer adds
  `image: ghcr.io/cianfhoghlaim/cianfhoghlaim-dagster:latest` to
  a compose file
- **WHEN** the Image Pinning Policy gate runs
- **THEN** the gate SHALL report a WARNING
- **AND** the developer SHOULD pin to a semver tag like
  `ghcr.io/cianfhoghlaim/cianfhoghlaim-dagster:1.2.3`

### Requirement: Locket Sidecar Contract

The system SHALL enforce the canonical Locket sidecar template
across all 86+ stacks. The contract is:

- `image: ghcr.io/cianfhoghlaim/locket:<sha-pinned-tag>`
- `user: "65532:65532"` (nobody:nogroup)
- `security_opt: ["no-new-privileges:true"]`
- `cap_drop: ["ALL"]`
- `read_only: true`
- `tmpfs: [/run/secrets/locket:size=1m,mode=0700,uid=65532,gid=65532]`
- `volumes: [cianchoghlaim_locket_secrets:/run/secrets/locket:ro]`
- `environment.LOCKET_MODE`: one of `watch` / `exec` / `oneshot`
- `environment.LOCKET_SECRETS_FILE: /run/secrets/locket/secrets.env`

The `cianchoghlaim_locket_secrets` external tmpfs volume is
defined in `infrastructure/locket/compose.yaml` and is
**shared** across all 86+ stacks.

#### Scenario: A Locket sidecar uses the wrong user

- **GIVEN** a developer's `sidecar.yaml` declares `user: root`
- **WHEN** the Locket Sidecar Contract gate runs
- **THEN** the gate SHALL fail with exit code 8
- **AND** the developer MUST change to `user: "65532:65532"`

### Requirement: Host Tag Mandatory

The system SHALL require every
`infrastructure/komodo/stacks/<name>.toml` to declare exactly
one `host:*` tag from the 3-tag taxonomy
(`host:bunchloch`, `host:arm1-oci`, `host:cax41-hetzner`).
Reference stacks (which document a pattern but are not deployed)
MAY have no tag.

The `stack-doctor` SHALL report a stack without a `host:*` tag
as **CRITICAL** (exit code 16).

#### Scenario: A new Komodo stack has no host tag

- **GIVEN** a developer adds
  `infrastructure/komodo/stacks/<new>.toml` with no `tags = [...]`
  field
- **WHEN** the Host Tag gate runs
- **THEN** the gate SHALL fail with exit code 16
- **AND** the developer MUST add `tags = ["host:<one-of-3>"]`

### Requirement: Pangolin 6-Label Pattern

The system SHALL enforce the 6-label pattern in every
`pangolin.yaml` (per `.agents/skills/kcg-pangolin-stack/SKILL.md`):

1. `pangolin.private-resources.<name>.name` — unique slug
2. `pangolin.private-resources.<name>.mode` — `http` / `tcp` / `udp`
3. `pangolin.private-resources.<name>.full-domain` — the FQDN
4. `pangolin.private-resources.<name>.destination-port` — the container port
5. `pangolin.private-resources.<name>.protocol` — `http` / `https`
6. `pangolin.private-resources.<name>.roles[0]` — the Traefik role

The 4 common Traefik middlewares are `tinyauth@file`,
`secure-headers@file`, `rate-limit-api@file`, `rate-limit-auth@file`.

#### Scenario: A pangolin.yaml is malformed

- **GIVEN** a developer adds a `pangolin.yaml` with the wrong
  field name (`destination_port` with an underscore)
- **WHEN** the Pangolin gate runs
- **THEN** the gate SHALL fail with exit code 8
- **AND** the developer MUST rename to `destination-port`
  (with a hyphen)

### Requirement: Spaces route through the canonical LiteLLM gateway

The Cianfhoghlaim HuggingFace Spaces (`an_scrudu`, `meaisin_cliste`, `cianfhoghlaim`, `anam_tuatha`, `data-engineering`) MUST route every LLM call through the canonical LiteLLM gateway (`http://litellm:4000/v1`) as the primary tier, with the hand-rolled HF Inference 3-tier chain kept as the offline fallback. The gateway is configured in `cianfhoghlaim/baml_src/clients.baml` (the `LitellmClient`) and `cianfhoghlaim/foinse/litellm_config.yaml` (the 5-key rotation).

#### Scenario: Space calls LLM via the gateway

- **WHEN** a Space (e.g. `an_scrudu/extraction.py`) calls `chat_complete_json(messages=...)`
- **THEN** the underlying `chat_complete()` first tries the LiteLLM gateway with the canonical model (`minimax` by default)
- **AND** if the gateway is unreachable (offline / dev / HF free tier), it falls back to the HF Inference 3-tier chain (Qwen 7B → Llama 8B → Gemma 9b)

#### Scenario: Langfuse auto-traces every Space LLM call

- **WHEN** the LiteLLM gateway is the tier that responds
- **THEN** Langfuse records the call with cost + latency + model (because the gateway is the same proxy that every KCG agent uses)
- **AND** the HF Inference fallback is invisible to Langfuse (acceptable: it only fires when the gateway is down)

### Requirement: Anti-phish Space moved to private archive

The `spaces/anti-phish/` directory MUST NOT be a public Cianfhoghlaim HuggingFace Space. The 6 Colab notebooks + the original README MUST live in `archive/anti-phish-2022-academic/` (private archive, not pushed to HF) until a new openspec change (`modernize-anti-phish-space`) rebuilds the directory with the KCG canonical stack.

#### Scenario: User finds the old anti-phish Space

- **WHEN** an agent or user navigates to `spaces/anti-phish/`
- **THEN** the directory does not exist (it was moved to `archive/anti-phish-2022-academic/`)
- **AND** the `spaces/AGENTS.md` (added by the `spaces-priority-quick-reference` change) explains the move

#### Scenario: Re-publishing requires a new openspec change

- **WHEN** the user wants to re-publish the anti-phish work as a public HF Space
- **THEN** they MUST create a new `modernize-anti-phish-space` openspec change that uses the KCG canonical stack (LiteLLM gateway + BAML + ccc + Cognee) and does NOT include the personal reflection

### Requirement: Priority quick reference section in every Spaces AGENTS.md

Every AGENTS.md file under the `spaces/` tree (`spaces/AGENTS.md`, `spaces/_common/AGENTS.md`, `spaces/{an_scrudu,meaisin_cliste,cianfhoghlaim,anam_tuatha,data-engineering}/AGENTS.md`) MUST start with a "Priority quick reference" section that prominently surfaces the canonical skills, the ccc code-search command, the openspec commands, and the openspec specs most relevant to that Space. The section MUST be at most 60 lines and MUST be a structured table (not prose).

#### Scenario: Spaces AGENTS.md leads with priority quick reference

- **WHEN** an agent reads any `spaces/*/AGENTS.md` file
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it lists the 3-5 skills most relevant to that Space + the ccc command + the 4 openspec commands

#### Scenario: Parent spaces AGENTS.md links to all 4 active Spaces

- **WHEN** an agent reads `spaces/AGENTS.md`
- **THEN** it lists the 4 active Spaces + the 1 archived Space + the 5 priority skills + the 4 priority openspec specs
- **AND** it links to each per-Space AGENTS.md for the developer-quick-reference routing table

### Requirement: data-engineering Space must use the KCG canonical stack

The data-engineering Space MUST consume the KCG canonical stack: `stedding/ingest_queue/pypi/` as the source (not BigQuery), MotherDuck as the destination (not local DuckDB), dbt-duckdb as the adapter (not raw dbt), and Cognee + Graphiti for the knowledge graph.

#### Scenario: Modernized data-engineering Space

- **WHEN** the data-engineering Space runs
- **THEN** it reads from `stedding/ingest_queue/pypi/`
- **AND** it writes to MotherDuck
- **AND** it uses dbt-duckdb
- **AND** it has a Cognee + Graphiti cognify pass

### Requirement: crypteolas DeFi Monitor Space

The crypteolas data platform MUST provide a DeFi Monitor HuggingFace Space at `spaces/crypteolas_defi_monitor/` that exposes the 4 streams (GitHub + DeFi + Knowledge Graph + Marimo) as a single Gradio app. The Space MUST be wired to the canonical Cognee + Graphiti knowledge graph and the Agno multi-agent team.

#### Scenario: User opens the DeFi Monitor

- **WHEN** a user navigates to the crypteolas_defi_monitor Space
- **THEN** they see 4 tabs (GitHub + DeFi + Knowledge Graph + Marimo)
- **AND** each tab shows the corresponding stream's data
- **AND** the Knowledge Graph tab is wired to Cognee + Graphiti
- **AND** the Marimo tab launches the 4 crypteolas notebooks

### Requirement: Tuatha MMO Demo Space

The tuatha quadrant MUST provide an MMO Demo HuggingFace Space at `spaces/tuatha_mmo_demo/` that demonstrates the Tuatha Celtic Educational MMO with 1 Babylon.js 7 + WebGPU quest + the 4 tuatha agents + the crypteolas achievement-ledger.

#### Scenario: User opens the MMO Demo

- **WHEN** a user navigates to the tuatha_mmo_demo Space
- **THEN** they see 4 tabs (Map + Quest + Achievement Ledger + Knowledge Graph)
- **AND** the Map tab shows a Babylon.js 7 + WebGPU British Isles scene
- **AND** the Quest tab shows 1 quest with the 4-feedback-channel pattern
- **AND** the Achievement Ledger tab shows the 5-feat progression

### Requirement: Croílár Portfolio Demo Space

The croilar quadrant MUST provide a Portfolio Demo HuggingFace Space at `spaces/croilar_portfolio_demo/` that demonstrates the Croílár multi-persona portfolio platform with the 3 personas (aleyum / cianfhoghlaim / carlcashman) + the bilingual EN/GA routing + the 12 DLT pipelines + the marimo notebooks.

#### Scenario: User opens the Portfolio Demo

- **WHEN** a user navigates to the croilar_portfolio_demo Space
- **THEN** they see 4 tabs (Aleyum + Cianfhoghlaim + Carlcashman + Bilingual EN/GA)
- **AND** each persona tab shows the 4 DLT pipelines + the 5 marimo notebooks
- **AND** the Bilingual EN/GA tab provides the canonical Celtic language toggle

### Requirement: Cross-Sruth Lakehouse Wiring Contract

Every active srutha in the Cianfhoghlaim monorepo MUST wire into the canonical dev lakehouse via two contracts: (1) `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` for LanceDB vector RAG (set via `.env` or compose.yaml default), and (2) a dedicated `ducklake_{namespace}` PostgreSQL database created in `bonneagar/stacks/lakehouse/init-db.sql` for DuckLake write-ahead-log storage. The canonical factory for both contracts is `cianfhoghlaim/dlt_utils/destinations.py:with_namespace()` (the `with_namespace()` method at line 289 of the file). The 6 active srutha DBs are: `ducklake_oideachais`, `ducklake_crypteolas`, `ducklake_croilar`, `ducklake_tuath`, `ducklake_meaisinfhoghlaim`, `ducklake_aleyum` (legacy — superseded by croilar).

#### Scenario: An active srutha needs LanceDB vector RAG

- **GIVEN** an active srutha stack (e.g. `croilar-dagster`, `croilar-marimo`, `oideachais`)
- **WHEN** the stack boots
- **THEN** its `LANCEDB_URI` env var MUST default to `rest://lakehouse-lance-namespace:8182`
- **AND** the default MUST be overridable via `.env` for legacy file-path deployments
- **AND** the stack MUST be on the `lakehouse` external network so it can reach the Lance sidecar at `:8182`

#### Scenario: An active srutha needs DuckLake storage

- **GIVEN** an active srutha (e.g. `oideachais`, `croilar`, `crypteolas`, `tuath`, `meaisinfhoghlaim`)
- **WHEN** its Dagster code-location runs `with_namespace()` to materialise a DuckLake destination
- **THEN** the factory MUST produce a connection string referencing `ducklake_{namespace}` on the shared `lakehouse-postgres`
- **AND** the database MUST exist in `bonneagar/stacks/lakehouse/init-db.sql` with `OWNER lakehouse`
- **AND** if the database is missing, the `with_namespace()` factory MUST raise an actionable error pointing at the lakehouse `init-db.sql` file

#### Scenario: meaisinfhoghlaim is wired into the lakehouse

- **GIVEN** the `meaisinfhoghlaim` srutha has a Dagster code-location but historically had no `ducklake_*` database
- **WHEN** the lakehouse `init-db.sql` runs on a fresh `docker compose up`
- **THEN** the `ducklake_meaisinfhoghlaim` database MUST be created with `OWNER lakehouse` and `GRANT ALL PRIVILEGES`
- **AND** the `meaisinfhoghlaim` Dagster assets MUST be able to materialise to `with_namespace("meaisinfhoghlaim")` on the shared Postgres without manual DB creation

#### Scenario: The standalone olake/ and nimtable/ stacks are deprecated

- **GIVEN** the standalone `bonneagar/stacks/olake/` and `bonneagar/stacks/nimtable/` Compose stacks predate this change
- **WHEN** a contributor searches for the canonical Olake or Nimtable location
- **THEN** each stack directory MUST contain a `DEPRECATED.md` file pointing at the canonical location (`bonneagar/stacks/lakehouse/olake/` and the `nimtable` service inside `bonneagar/stacks/lakehouse/compose.yaml`)
- **AND** the `compose.yaml` files MUST remain on disk (not deleted) to avoid breaking any automated tests that import from them; deletion is left to a follow-up change after one release cycle

### Requirement: 33 User-Selected Selfhosted Stacks (v4)

The system SHALL expose the 33 user-selected selfhosted stacks at `cianfhoghlaim/stacks/{backrest,browser,cognee,dagster,docling-serve,dots-ocr,dragonfly,falkordb,garage,graphiti,infisical,invokeai,komodo,lakehouse,lancedb,langfuse,litellm,logfire,marimo,memgraph,mlflow,mlx-omni,motherduck,nimtable,olake,olmocr,openchamber,openclaw,paddleocr,pangolin,planetscale,r2,risingwave}/`. The remaining 57 stacks remain at `bonneagar/stacks/` for archival.

#### Scenario: Stack discoverability

- **WHEN** a developer asks "where is the dagster stack?"
- **THEN** `ls cianfhoghlaim/stacks/dagster/` returns the 6-file GOLD_STANDARD pattern (`compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `README.md`)
- **AND** the stack file path is documented in `cianfhoghlaim/stacks/STACKS_INDEX.md` (NEW)

### Requirement: No Workspace Stack Re-addition (v4)

The system SHALL NOT re-add any of the previously deleted stacks (`blinko`, `croilar-convex`, `croilar-dagster`, `croilar-hono-api`, `croilar-marimo`, `croilar-postgres`, `croilar-web`, `DevDocs`, `DnsServer`, `mathesar`, `MCPJungle`, `monitoring`, `networking-toolbox`, `Perplexica`, `presenton`, `Termix`) to `cianfhoghlaim/stacks/` unless explicitly approved via a new openspec change.

#### Scenario: Validation

- **WHEN** `bun run validate-stacks` runs
- **THEN** the 33 user-selected stacks validate
- **AND** the 57 archived stacks at `bonneagar/stacks/` are skipped (marked `archived: true` in `STACKS_INDEX.md`)

### Requirement: Bonneagar worktree for infrastructure history

The `infrastructure/` directory history SHALL live in the sibling `bonneagar` worktree (at `./bonneagar/`) per the worktree approach adopted 2026-06-29. The cianfhoghlaim monorepo SHALL NOT re-import the bonneagar history as a subtree because the 6.9 MB subtree size made every `git push` upload the full content. The cianfhoghlaim monorepo SHALL retain a thin `infrastructure/` reference (a README pointer) for navigation; the canonical `infrastructure/` lives in https://github.com/cianfhoghlaim/bonneagar.

#### Scenario: a developer looks for the canonical infrastructure history

- **GIVEN** the developer wants to find the canonical 70+ Docker Compose stack history
- **WHEN** the developer runs `cd ./bonneagar && git log --oneline`
- **THEN** the developer sees the canonical history
- **AND** the monorepo's `git log -- infrastructure/` shows only the 2026-06-29 reset marker

### Requirement: Consumer Stack Locket Pointing at Local Vault

The system SHALL route every consumer stack's Locket sidecar
(`stack-shared locket container`) at `http://infisical-backend:8080` on the
shared `bunchloch-infra` external network. The Locket sidecar SHALL read
machine identity `INFISICAL_CLIENT_ID`, `INFISICAL_CLIENT_SECRET`,
`INFISICAL_PROJECT_ID` from a file-mounted secret at
`/run/secrets/infisical_secret` (matching the production secret mount path).

#### Scenario: A consumer stack's Locket sidecar successfully syncs

- **GIVEN** the local Infisical vault from Change 1 is up at
  `http://infisical-backend:8080`
- **AND** the `dev-baile/dev/<stack>/<key>` paths are seeded via the bootstrap script
- **AND** the consumer stack is brought up via
  `docker compose -f compose.yaml -f sidecar.yaml up -d`
- **WHEN** `docker logs <stack>-locket` is observed
- **THEN** the output SHALL contain `secrets synced` within 10 seconds of boot
- **AND** `${VAR}` interpolation in the consumer's `compose.yaml` SHALL
  resolve to the Infisical-stored value (NOT the developer's local `.env`)

### Requirement: Lakehouse Stack Versions 2026-07

The system SHALL pin every container in `bonneagar/stacks/lakehouse/` to
the versions verified via Firecrawl on 2026-07-06.

#### Scenario: All lakehouse containers are semver-pinned

- **WHEN** `bun run validate-stacks` runs against the lakehouse stack
- **THEN** every `image:` line SHALL be a `<major>.<minor>.<patch>` semver
  tag (NOT `:latest`)
- **AND** the canonical versions SHALL be:
  - `quay.io/lakekeeper/catalog:v0.13.1`
  - `dxflrs/garage:v2.3.0`
  - `clickhouse/clickhouse-server:25.8.28.1-lts`
  - `nimtable/nimtable:v0.1.0`
  - `ghcr.io/olake-io/olake:v0.8.0`

### Requirement: LiteLLM Production Memory Formula

The `bonneagar/stacks/litellm/compose.yaml` SHALL declare
`memory: 16G` for the litellm service when `--num_workers=4` is used,
per the upstream `4Gi × num_workers` formula documented at
<https://docs.litellm.ai/docs/proxy/prod>.

#### Scenario: Stack honours the memory formula

- **WHEN** `bun run validate-stacks` runs against litellm
- **THEN** the `litellm` service declaration SHALL contain
  `deploy.resources.limits.memory: 16G` when `command` includes
  `--num_workers=4`
- **AND** the runbook SHALL document the `1×=4G / 2×=8G / 4×=16G` matrix

### Requirement: MLflow v3 Security Middleware

The `bonneagar/stacks/mlflow/` stack SHALL declare the v3-mandatory
`--allowed-hosts="localhost,mlflow.cianfhoghlaim.ie"` and
`--cors-allowed-origins="https://cianfhoghlaim.cianfhoghlaim.ie"` flags on
the `mlflow server` command, per the upstream v3.5.0+ security
middleware requirement documented at
<https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/>.

#### Scenario: Stack uses the v3 semver + middleware flags

- **WHEN** `compose.yaml` is read
- **THEN** the image SHALL be `ghcr.io/mlflow/mlflow:v3.12.0` (NOT
  `v2.22.4` and NOT `:latest`)
- **AND** the `command:` list SHALL include
  `--allowed-hosts="localhost,mlflow.cianfhoghlaim.ie"`

### Requirement: Unstract OSS Self-Host at v0.177.7

The `bonneagar/stacks/unstract/` stack SHALL match the upstream
`Zipstack/unstract:v0.177.7` (released 2026-07-06) 15-service
docker-compose layout. The stack SHALL NOT pin to `unstract/unstract:latest`
(which does not exist as a single image).

#### Scenario: Unstract compose is a true 15-service fleet

- **WHEN** `compose.yaml` is read
- **THEN** it SHALL declare ALL 8 upstream images pinned to `:v0.177.7`:
  `unstract/{backend,frontend,platform-service,x2text-service,runner,
  worker-unified,tool-sidecar,llm-whisperer}:v0.177.7`
- **AND** it SHALL declare the 6 Celery worker services
  (`worker-metrics`, `worker-ide-callback`, `worker-api-deployment`,
  `worker-callback`, `worker-file-processing`,
  `worker-general`)
- **AND** the `db` image SHALL be `pgvector/pgvector:pg15` (NOT
  `postgres:16` — per upstream dev essentials)
- **AND** the `backend` healthcheck SHALL target port `:8000/health` (NOT
  `:8002`)
- **AND** the stack SHALL NOT declare `UNSTRACT_API_KEY` (OSS does not
  require it)
- **AND** every container SHALL be named with the bare KCG pattern
  (`unstract-backend`, `unstract-celery-worker-general`, etc.) — NOT the
  upstream's `*-1` numeric suffixes

### Requirement: Unstract OSS Self-Host at v0.177.7 (15-service fleet)

The `bonneagar/stacks/unstract/` stack MUST match the upstream
`Zipstack/unstract:v0.177.7` (released 2026-07-06) 15-service
docker-compose layout, vendored as 731 lines + 6 unstract images +
7 infrastructure images, with the KCG bare container-name
convention applied.

#### Scenario: Unstract compose is a true 15-service fleet

- **WHEN** `compose.yaml` is read
- **THEN** it SHALL declare ALL 6 upstream unstract images pinned to
  `:v0.177.7`:
  - `unstract/backend:v0.177.7`
  - `unstract/frontend:v0.177.7`
  - `unstract/platform-service:v0.177.7`
  - `unstract/x2text-service:v0.177.7`
  - `unstract/runner:v0.177.7`
  - `unstract/worker-unified:v0.177.7`
- **AND** it SHALL declare the 6 worker-unified worker services
  (api-deployment, callback, file-processing, general, notification,
  log-consumer, scheduler, executor, log-history-scheduler)
- **AND** it SHALL declare the 7 infrastructure services
  (pgvector, redis, minio, qdrant, rabbitmq, flipt, traefik) with
  pinned semver tags
- **AND** every container SHALL be named with the bare KCG pattern
  (`unstract-backend`, `unstract-worker-api-deployment`, etc.) — NOT
  the upstream's `*-1` numeric suffixes
- **AND** the `db` image SHALL be `pgvector/pgvector:pg15` (matching
  the upstream dev-essentials default)
- **AND** the `secrets.env` SHALL declare at least 20 canonical
  `infisical://dev-baile/unstract/<key>` entries (no Jinja `{{...}}`
  wrappers)
- **AND** the `sidecar.yaml` SHALL declare the canonical Locket
  sidecar (user 65532:65532, no-new-privileges, cap_drop ALL, tmpfs 700)
- **AND** the `compose.dev.yaml` SHALL override the locket service
  with a no-op alpine container that passes healthcheck

### Requirement: Unstract secrets in Infisical vault

The bunchloch-local Infisical vault MUST contain at least 20 secrets
under the path `dev-baile/dev/unstract/*`, covering postgres, minio,
qdrant, rabbitmq, django, celery, oauth, and LLM-provider keys.

#### Scenario: Universal Auth can read all 21 unstract secrets

- **WHEN** the bunchloch-locket-machine UA identity logs in to the
  local Infisical and queries `GET /api/v3/secrets/raw/<key>?workspaceId=...&environment=dev&secretPath=/unstract`
- **THEN** the response SHALL contain the secret value for at least
  20 distinct keys (postgres_user, postgres_password, postgres_db,
  postgres_schema, minio_root_user, minio_root_password,
  minio_access_key, minio_secret_key, qdrant_user, qdrant_pass,
  qdrant_db, rabbitmq_user, rabbitmq_pass, django_secret_key,
  celery_broker_url, celery_result_backend, openai_api_key, etc.)

### Requirement: Agent skills use v4 namespace paths

The system SHALL keep every `.agents/skills/` Markdown file aligned with the post-v4 `cianfhoghlaim/` namespace and directory layout. Skill documentation MUST NOT introduce pre-v4 `sruth/<quadrant>/...` path references except in archived point-in-time artifacts outside `.agents/skills/`.

For application code examples, skill documentation SHALL use import paths rooted at `cianfhoghlaim`, `meaisinfhoghlaim`, `tuatha`, or `croilar` as appropriate for the v4 package surface. For filesystem path examples, skill documentation SHALL use the actual v4 homes such as `cianfhoghlaim/dlt/`, `cianfhoghlaim/baml_src/`, `cianfhoghlaim/cocoindex/`, `cianfhoghlaim/orchestration/`, `cianfhoghlaim/agents/`, and `cianfhoghlaim/web/apps/*/`.

#### Scenario: Skill drift check stays clean

- **GIVEN** a contributor edits any file under `.agents/skills/`
- **WHEN** `grep -rln "sruth/" .agents/skills/` runs
- **THEN** the command returns 0 files
- **AND** `mise run lint:skills` reports all registered skills pass

#### Scenario: Skill examples use v4 application paths

- **GIVEN** a skill documents an oideachais DLT source
- **WHEN** it references the source's filesystem location
- **THEN** it uses `cianfhoghlaim/dlt/...` rather than `sruth/cianfhoghlaim/dlt_sources/...`
- **AND** if it shows a Python import example, the example uses `from cianfhoghlaim...` for actual code imports

#### Scenario: Bonneagar infra drift remains out of repo scope

- **GIVEN** a drift reference exists inside the separate `bonneagar/` repo/worktree
- **WHEN** this Cianfhoghlaim OpenSpec change is implemented
- **THEN** the `bonneagar/` file is not modified from this repo
- **AND** any follow-up is tracked as a separate repo-boundary task

### Requirement: All procedures have `server_id` by 2026-07-13

The system SHALL require every Komodo procedure TOML under `komodo/procedures/` to declare a top-level `server_id` field with one of the values:
- `"bunchloch"` — for procedures that deploy + verify resources on the `bunchloch` host
- `"arm1-oci"` — for procedures that deploy + verify resources on the `arm1-oci` host

Procedures added or modified after **2026-07-13** MUST include `server_id = "bunchloch"` or `server_id = "arm1-oci"`. The legacy back-compat path (procedures without `server_id` showing in both hosts' UIs) is **deprecated and SHALL be removed by 2026-08-15**: at that date, any procedure without `server_id` SHALL emit a hard error from `openspec validate` (not just a warning) and SHALL be removed from both UIs.

The convention is documented in `komodo/procedures/server_id_legend.md` (the legend doc added by the `2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow` change).

#### Scenario: New procedure has `server_id`

- **WHEN** a new procedure is added to `komodo/procedures/` after 2026-07-13
- **THEN** the procedure SHALL include `server_id = "bunchloch"` or `server_id = "arm1-oci"` at the top of the `[[procedure.config]]` (or `[[procedure]]`) block
- **AND** `openspec validate <change-id> --strict` SHALL emit an error if the field is missing
- **AND** the procedure SHALL appear in only the matching host's `km` UI

#### Scenario: Backfill of legacy procedures

- **WHEN** a procedure is added to `komodo/procedures/` without a `server_id` field between **2026-07-13** and **2026-08-15**
- **THEN** the procedure SHALL appear in BOTH hosts' UIs (back-compat path)
- **AND** Komodo Core SHALL log a deprecation warning: `WARN: procedure '<name>' has no server_id field; defaulting to both hosts. Add server_id = 'bunchloch' or 'arm1-oci'.`

#### Scenario: 2026-08-15 hard cutover

- **WHEN** the 2026-08-15 cutover date passes
- **THEN** any procedure without a `server_id` field SHALL be hard-rejected by `openspec validate` (not just a warning)
- **AND** the back-compat path SHALL be removed from Komodo Core (procedures without `server_id` are invisible in both UIs)
- **AND** the only valid procedure files are ones with `server_id = "bunchloch"` or `server_id = "arm1-oci"`

### Requirement: preflight:arm-oci hard-gates arm1-oci cluster deployment

The system SHALL require the `preflight:arm-oci` safety gate to exit 0
before any ClusterDeployment procedure on `arm1-oci` proceeds past
Stage 0. The preflight report (`--emit-md` output) SHALL be captured
to `/tmp/preflight-reports/arm-oci/<utc-timestamp>.md` for every
deploy attempt (success or failure).

The omnibus `deploy-agent-platform-cluster-arm1-oci` MUST set
`require_success = true` on its Stage 0 `preflight` RunShellCommand so
that a non-zero preflight exit code aborts the omnibus before Stage 1
(control-plane foundation).

The `--skip=preflight` flag SHALL be rejected (exit code 2) on any
arm1-oci cluster procedure; preflight is a mandatory first step.

#### Scenario: preflight exits 0 — omnibus proceeds

- **WHEN** `bun run preflight:arm-oci --strict --emit-md` exits 0
- **THEN** the omnibus proceeds to Stage 1 (control-plane foundation)
- **AND** the captured report exists at `/tmp/preflight-reports/arm-oci/<utc-ts>.md`
- **AND** the report ends with `PASS` or `ALL CHECKS PASSED`

#### Scenario: preflight exits non-zero — omnibus aborts at Stage 0

- **WHEN** `bun run preflight:arm-oci --strict --emit-md` exits non-zero
- **THEN** the omnibus aborts at Stage 0
- **AND** no Stage 1+ execution is attempted
- **AND** the captured report retains the failure cause (e.g.
  `Pangolin unreachable`, `Komodo unreachable`, `Infisical unreachable`,
  `process-namespace conflict`)
- **AND** the operator sees the report path in the Komodo log

#### Scenario: --skip=preflight is rejected

- **WHEN** `km run procedure deploy-agent-platform-cluster-arm1-oci -- --skip=preflight` runs
- **THEN** the procedure exits with code 2
- **AND** the operator sees the message "preflight is a mandatory first step; --skip=preflight is rejected"
- **AND** no Stage 0+ execution is attempted

### Requirement: Drift-remediation pass

The IaC at `bonneagar/iac/` SHALL expose a `iac:bootstrap`
command at the repo root via the cianfhoghlaim `package.json`
script `iac:bootstrap` (delegating to
`bun run --cwd bonneagar iac:bootstrap`).

#### Scenario: Root-level iac:bootstrap is callable

- **WHEN** a developer runs `bun run iac:bootstrap` from the
  cianfhoghlaim repo root
- **THEN** the IaC SHALL execute the 8-phase Pulumi →
  Infisical → Pangolin → Komodo → Newt → all syncs sequence
- **AND** the exit code SHALL be 0 on success

#### Scenario: iac:bootstrap supports --dry-run

- **WHEN** a developer runs `bun run iac:bootstrap --dry-run`
- **THEN** the IaC SHALL print the diff between the declared
  state and the actual state
- **AND** SHALL NOT mutate any remote system

### Requirement: preflight:arm-oci safety script

The repo SHALL provide a `bun run preflight:arm-oci` script
at `scripts/preflight-arm-oci.ts` that runs 4 checks before any
arm-oci stack deploy:

1. **Pangolin health** — `GET ${PANGOLIN_URL}/api/v1/` returns 200
2. **Komodo health** — `GET ${KOMODO_URL}/ping` returns 200
3. **Infisical health** — `GET ${INFISICAL_URL}/api/status` returns 200
4. **Process namespace isolation** — the opencode session PID
   MUST NOT share a PID namespace with any running container
   named `openchamber`, `openclaw`, `hermes`, `komodo`,
   `pangolin`, or `infisical`

#### Scenario: All 4 checks pass

- **WHEN** an opencode session runs `bun run preflight:arm-oci`
- **AND** Pangolin + Komodo + Infisical all return 200
- **AND** the opencode PID is in a distinct PID namespace
- **THEN** the script SHALL exit 0 with "ALL CHECKS PASSED"

#### Scenario: Pangolin is unreachable

- **WHEN** an opencode session runs `bun run preflight:arm-oci`
- **AND** Pangolin returns 5xx or times out
- **THEN** the script SHALL exit 1 with a clear error message
  identifying which check failed and how to remediate

#### Scenario: Opencode PID shares namespace with openchamber

- **WHEN** an opencode session runs `bun run preflight:arm-oci`
- **AND** the current PID is in the same PID namespace as a
  running openchamber container
- **THEN** the script SHALL exit 1 with the message
  "REFUSING TO DEPLOY: opencode PID <X> shares namespace with
  openchamber container <Y>; restart opencode outside the
  openchamber namespace first"

### Requirement: newt image is pinned to v1.14.0 + SHA digest across all clusters

The system SHALL pin the fossorial `newt` Pangolin client image to **v1.14.0** with a **SHA256 digest** (not a mutable tag, not `:latest`) in every cluster that runs newt (bunchloch operator-laptop + arm1-oci control-plane).

The canonical image pin lives at `bonneagar/stacks/newt/IMAGE` (a single-file `NEWT_VERSION` + `NEWT_IMAGE` + `NEWT_SHA` constants). All other compose files reference these constants via the pinned image reference.

When upgrading newt:
1. Bump `NEWT_VERSION` + `NEWT_SHA` in `stacks/newt/IMAGE`
2. Update the 2 image references in `stacks/newt/docker-compose.yaml` + `stacks/pangolin/newt.yaml`
3. Open an openspec change documenting the bump (e.g. `2026-07-14-bump-newt-v1.14.0-cross-cluster-v1`)
4. Validate + commit + push + archive

#### Scenario: newt is pinned at v1.14.0

- **GIVEN** `stacks/newt/IMAGE` declares `NEWT_VERSION=1.14.0` + `NEWT_SHA=60c78391...`
- **AND** `stacks/newt/docker-compose.yaml` + `stacks/pangolin/newt.yaml` reference the same SHA
- **WHEN** `bun run stack-doctor` runs across the repo
- **THEN** no newt-related `:latest` warnings fire
- **AND** the newt image-pin check passes

#### Scenario: newt version mismatches across clusters

- **WHEN** `docker exec bunchloch-newt -- newt --version` returns `1.14.0`
- **AND** `docker exec pangolin-newt -- newt --version` returns `1.13.0`
- **THEN** the deploy-newt-bunchloch-v2 + deploy-pangolin-newt-arm1-oci procedures
  Stage 4 (health-checks) emit a MISMATCH error
- **AND** the operator is blocked from proceeding until both newt containers are on the same version

#### Scenario: IMAGE rotation is atomic

- **WHEN** the IMAGE file is updated to v1.15.0 (e.g. new SHA `abc...123`)
- **THEN** the 2 compose files SHALL reference the new SHA in the same commit
- **AND** the openspec change documents the upgrade
- **AND** the rotation is rolled out via the cross-cutting prereq order
  (pangolin-first → komodo-core → infisical-first → locket-deploy →
  deploy-pangolin-newt-arm1-oci → deploy-newt-bunchloch-v2)

### Requirement: iac:health checks 6 auth surfaces (was 4-way; now komodo + pangolin + infisical + newt + pocket-id + tinyauth)

The system SHALL provide a `bun run iac:health` command that checks
all 6 auth surfaces in the bons IaC:

1. **Komodo** — the GitOps orchestrator
2. **Pangolin** — the identity-aware reverse proxy + WireGuard server (gerbil)
3. **Infisical** — the secrets source of truth
4. **Newt** — the WireGuard client(s) on bunchloch + arm1-oci
5. **Pocket ID** — the OIDC identity provider (admin SSO for Pangolin + newt creds)
6. **Tinyauth** — the ForwardAuth middleware (Pangolin's auth gate)

Each check SHALL report a clear actionable error message. The command
SHALL exit 0 only if all 6 are healthy.

#### Scenario: all 6 surfaces healthy

- **WHEN** the bons IaC has been fully bootstrapped
- **THEN** `bun run iac:health` outputs:
  ```
  ✓ komodo: N servers, M stacks
  ✓ pangolin: healthy
  ✓ infisical: healthy
  ✓ newt (bunchloch): container Up, version 1.14.0, WireGuard tunnel LIVE
  ✓ pocket-id: v2.9.0, U users, C OIDC clients, signup=off
  ✓ tinyauth: http://tinyauth.cianfhoghlaim.ie returned 200
  ```
- **AND** exits 0

#### Scenario: Pocket ID DB is empty (the common operator-error case)

- **WHEN** `bun run iac:health` runs and Pocket ID has 0 users
- **THEN** the output is:
  ```
  ✗ pocket-id: v2.9.0 but DB is empty (run: bun run iac:bootstrap-pocketid-admin)
  ```
- **AND** the command exits 1

#### Scenario: Tinyauth container is down (the Locket sidecar missing case)

- **WHEN** `bun run iac:health` runs and Tinyauth is not Up
- **THEN** the output is:
  ```
  ✗ tinyauth: http://tinyauth.cianfhoghlaim.ie returned 502
  ```
- **AND** the command exits 1
- **AND** the operator can run `km run procedure deploy-tinyauth-bunchloch` to fix it

#### Scenario: pocketIdHealth() has a 3-second timeout on docker exec

- **WHEN** the SQLite query inside the docker container takes longer than 3s
- **THEN** the function returns with `dbUsers=0, dbOidcClients=0, signupEnabled=false` (defaults)
- **AND** the rest of the health check still completes in <5s
- **AND** the operator sees a partial-but-actionable health result

## Infrastructure (Control Plane) Stacks

| Stack | Image(s) | Key Ports |
|-------|----------|-----------|
| pangolin | `fosrl/pangolin:postgresql-latest`, `postgres:17`, `traefik:v3.4.0`, `pocket-id:latest`, `tinyauth:v4`, `crowdsec:latest` | 51820/udp, 443, 80, 8443 |
| komodo | `ghcr.io/moghtech/komodo-core:2`, `mongo:latest` | 9120 |
| pocket-id | `ghcr.io/pocket-id/pocket-id` | 1411 |
| dozzle | Container log viewer | Internal |
| DnsServer | Local DNS resolution | Internal |

## Storage Stacks

| Stack | Purpose | Key Ports |
|-------|---------|-----------|
| garage | CRDT S3-compatible object storage | 3900-3904 |
| lakehouse | Lakekeeper Iceberg catalog + Lance Namespace + Garage + Postgres | 3900-3904, 5433, 8181-8182 |
| lakehouse-oci | OCI variant of lakehouse | 5433, 8181-8182 |
| dagster | Pipeline orchestration (custom image) | 3335 |
| langfuse | LLM observability (Postgres + ClickHouse + Redis + MinIO) | 3000 |
| mlflow | ML experiment tracking (Postgres + MinIO) | 5000 |
| forgejo | Git forge (Postgres) | 3000, 2222 |
| forgejo-runner | CI/CD runner | — |
| memgraph | Graph database (MAGE + Lab UI) | 7687, 7444, 3000 |
| falkordb | Vector+graph hybrid | 6379, 3000 |
| qdrant | Vector database | 6333, 6334 |
| lancedb | LanceDB data viewer | 8080 |
| agent-os | 4 custom services: oideachais, crypteolas, browser, croilar (was aleyum) | 7771-7774 |
| browser | Browser automation (Skyvern + Postgres + Garage) | 3001, 3100, 8001, 11235 |
| confluent | Kafka UI (kafka+zookeeper commented out) | 9080 |
| graphiti | Temporal knowledge graph | Internal |
| cognee | AI memory system | Internal |
| convex | Real-time backend | Cloud |
| lakefs | Data versioning | Internal |
| lakekeeper | Iceberg catalog (standalone) | Internal |
| mathesar | Database UI | Internal |
| nimtable | Analytics table viewer | Internal |
| olake-ui | CDC replication UI | Internal |
| beszel | System monitoring | Internal |
| kafka | Standalone Kafka | Internal |
| r2 | Cloudflare R2 bridge | Internal |

### Documentation-Only Stacks (secrets configured, no local compose)

| Stack | Purpose |
|-------|---------|
| motherduck | MotherDuck cloud analytics |
| planetscale | MySQL-compatible cloud DB |
| pydantic-gateway | Pydantic AI gateway |
| logfire | Pydantic observability |

## Engineering Stacks

| Stack | Purpose | Key Ports |
|-------|---------|-----------|
| litellm | LLM proxy gateway (Postgres + Prometheus) | 4000, 5432, 9090 |
| crawl4ai | Web crawling API | 11235 |
| coder | Cloud development environment | Internal |
| windmill | Workflow automation | Internal |
| MCPJungle | MCP server collection | Internal |
| DevDocs | API documentation aggregator | Internal |
| networking-toolbox | Network diagnostic tools | Internal |

## Machine Learning Stacks

| Stack | Purpose |
|-------|---------|
| cognee | AI memory (ML variant) |
| graphiti | Temporal graphs (ML variant) |
| langfuse | LLM observability (ML variant) |
| lmnr | Language model observability |
| olake | CDC replication |

## Tools Stacks (17)

Productivity: `actual`, `blinko`, `linkwarden`, `presenton`, `stirling-pdf`
Media: `audiobookshelf`, `kapowarr`, `pinchflat`, `rybbit`
Development: `changedetection`, `enclosed`, `pastemax`, `perplexica`, `skyvern`, `LetterFeed`, `romm`, `mailcow-dockerized`

## Stack Configuration Standard

| File | Purpose | Required |
|------|---------|----------|
| `compose.yaml` | Docker service definitions | Yes |
| `pangolin.yaml` | Traefik routing + TinyAuth config | For web-facing |
| `sidecar.yaml` | Locket container for Infisical injection | Yes |
| `secrets.env` | Infisical URI references for stack | Yes |

## Implementation References

| Component | Path |
|-----------|------|
| All Stacks | `bonneagar/stacks/` |
| Gold Standard | `bonneagar/stacks/GOLD_STANDARD.md` |
| Stack README | `bonneagar/stacks/README.md` |

## Related Specs

- [infrastructure](../infrastructure/spec.md) — Pangolin convergence, secrets, Komodo GitOps
- [data-pipeline](../data-pipeline/spec.md) — Pipeline orchestration

## Migrated from (2026-07-06)

- `stack-audit` — the stack-audit capability (5 Requirements covering the stack health + drift detection) was absorbed into the `infrastructure-stacks` GitOps + audit surfaces
