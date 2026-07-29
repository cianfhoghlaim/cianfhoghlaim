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
- **AND** the `cianfhoghlaim_locket_secrets` external tmpfs volume
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
- `volumes: [cianfhoghlaim_locket_secrets:/run/secrets/locket:ro]`
- `environment.LOCKET_MODE`: one of `watch` / `exec` / `oneshot`
- `environment.LOCKET_SECRETS_FILE: /run/secrets/locket/secrets.env`

The `cianfhoghlaim_locket_secrets` external tmpfs volume is
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

### Requirement: BIEP v3 preflight bug fixes (P0)

The system SHALL have:

1. Valid YAML in `motherduck/flights/config.yaml` (4 BIEP v3 flights
   indented under `flights:` key).
2. `BIEPV3ExtractStrong` BAML client uses a non-VLM text model
   (`gemma-3-27b-it`) per the user's audit decision.
3. `dlt/common/motherduck_snapshots.py` makes real HTTPS POST requests
   to `api.motherduck.com` for snapshot/share/attach (NOT stub dict
   factories).
4. `seed_registry()` asserts 3,780 rows (matches actual loader output).
5. All 4 BIEP v3 jurisdiction pipelines inherit from
   `JurisdictionPipelineBase` (eliminating ~120 LOC of duplicated
   boilerplate).

#### Scenario: MotherDuck flight YAML loads correctly

- **WHEN** `python -c "import yaml; yaml.safe_load(open('motherduck/flights/config.yaml'))"` runs
- **THEN** the call succeeds without a `yaml.YAMLError`
- **AND** the `flights` key contains exactly 13 entries (9 daily-sync + 4 BIEP v3)

#### Scenario: All 4 BIEP v3 flights discoverable

- **WHEN** `dg list jobs | grep -E "(ireland|england|sct_wls_ni|crown_dependencies)_full_coverage_flight"` runs
- **THEN** exactly 4 BIEP v3 flight names are listed

#### Scenario: BIEPV3ExtractStrong uses non-VLM text model

- **WHEN** `baml_src/clients_biep_v3.py` is inspected
- **THEN** `BIEPV3ExtractStrong` SHALL equal `"gemma-3-27b-it"` (not a VLM model)

#### Scenario: snapshot_database makes a real POST

- **WHEN** `snapshot_database("snap_2026_08_10", "oideachais")` is called
- **THEN** a real HTTPS POST to `https://api.motherduck.com/v1/databases/oideachais/snapshots` is made
- **AND** the response is returned as a dict
- **AND** the call uses `MOTHERDUCK_TOKEN` from the env for auth

#### Scenario: create_share makes a real POST

- **WHEN** `create_share("share_biep_v3", "oideachais")` is called
- **THEN** a real HTTPS POST to `https://api.motherduck.com/v1/shares` is made
- **AND** the response includes a `share_url` field

#### Scenario: attach_share makes a real POST

- **WHEN** `attach_share(share_url, "biiep_v3_share")` is called
- **THEN** a real HTTPS POST to `https://api.motherduck.com/v1/shares/attach` is made
- **AND** the call succeeds with HTTP 200 or 201

#### Scenario: seed_registry asserts 3,780 rows

- **WHEN** `seed_registry()` is called
- **THEN** the function returns a counts dict with a total of 3,780 rows
- **AND** an `AssertionError` is raised if the row count drifts

#### Scenario: Per-jurisdiction breakdown

- **WHEN** `seed_registry()` is called
- **THEN** the returned counts dict MUST include:
  - ireland: 544
  - england: 276
  - scotland: 600
  - wales: 640
  - northern_ireland: 280
  - jersey: 480
  - guernsey: 480
  - isle_of_man: 480

#### Scenario: All 4 pipelines inherit from JurisdictionPipelineBase

- **WHEN** any of the 4 BIEP v3 jurisdiction pipelines is loaded
- **THEN** the pipeline class MUST be a subclass of `JurisdictionPipelineBase`
- **AND** `isinstance(pipeline_obj, JurisdictionPipelineBase)` returns `True`

#### Scenario: Boilerplate eliminated

- **WHEN** comparing pre-refactor vs post-refactor
- **THEN** the 4 pipeline files SHALL contain ~30 LOC less boilerplate each
- **AND** the shared `subject_to_row()` and `build_pipeline()` methods MUST be on the base class

### Requirement: BIEP v3 lakehouse population (P1)

The system SHALL have a populated lakehouse with:

1. The 11-service Lakehouse stack deployed + healthy on `bunchloch`
   (Mac M4).
2. 3,780 rows in `cianfhoghlaim.education._registry.subjects`.
3. All 4 BIEP v3 jurisdiction pipelines executed successfully (writes
   544 + 276 + 1,520 + 720 = 3,060 cohort rows to DuckLake).
4. 8 CocoIndex v1 BIIP parity flows wired (consume DuckLake → LanceDB).
5. 4 BIEP v3 MotherDuck Flights emitting Dagster RunRequests.
6. 0 `md:oideachais` references in `notebooks/` (post-sweep).

#### Scenario: Lakehouse smoke-test passes

- **WHEN** `mise run biep:v3:lakehouse:smoke-test` runs
- **THEN** Nimtable :3018 MUST return HTTP 200 at `/`
- **AND** Olake :3901 MUST return HTTP 200 at `/health`
- **AND** LanceDB Viewer :8081 MUST return HTTP 200 at `/v1/databases`

#### Scenario: Lakekeeper deep health check

- **WHEN** `curl http://localhost:8181/health/deep` runs
- **THEN** the response MUST return HTTP 200
- **AND** the response MUST include `{"postgres": "healthy", "s3": "healthy"}`

#### Scenario: Registry seeds 3,780 rows

- **WHEN** `mise run biep:v3:registry:seed` runs
- **THEN** the registry table MUST contain 3,780 rows
- **AND** Lakekeeper MUST list 8 namespaces under `cianfhoghlaim.education`

#### Scenario: Ireland pipeline writes 544 cohorts

- **WHEN** `dg launch --job ireland_jurisdiction_pipeline` runs
- **THEN** the DuckLake table MUST contain 544 cohort rows

#### Scenario: England pipeline writes 276 cohorts

- **WHEN** `dg launch --job england_jurisdiction_pipeline` runs
- **THEN** the DuckLake table MUST contain 276 cohort rows

#### Scenario: SCT+WLS+NI pipeline writes 1,520 cohorts

- **WHEN** the SCT+WLS+NI pipeline is run with
  `jurisdiction=scotland,wales,northern_ireland`
- **THEN** the combined DuckLake tables MUST contain 600 + 640 + 280 = 1,520 rows

#### Scenario: Crown Dependencies pipeline writes 720 cohorts

- **WHEN** the Crown Dependencies pipeline is run with
  `jurisdiction=jersey,guernsey,isle_of_man`
- **THEN** the combined DuckLake tables MUST contain 240 + 240 + 240 = 720 rows

#### Scenario: All 4 BIEP v3 MotherDuck Flights listed

- **WHEN** `dg list jobs | grep -E "(ireland|england|sct_wls_ni|crown_dependencies)_full_coverage"` runs
- **THEN** exactly 4 BIEP v3 flight job names are listed

#### Scenario: Each flight emits a Dagster RunRequest

- **WHEN** `dg launch --job ireland_full_coverage_flight` runs
- **THEN** the Dagster event log MUST include at least 1 `RunRequest` event
  with `tags.jurisdiction = "ireland"`

(Same for england, sct_wls_ni, crown_dependencies.)

#### Scenario: Zero md:oideachais references in notebooks

- **WHEN** `grep -rn "md:oideachais" notebooks/ | wc -l` runs
- **THEN** the output MUST be `0`
- **AND** all notebooks MUST connect via `notebooks/_shared/db.py:connect_md()`

#### Scenario: LAKEHOUSE_URI_DEFAULT is canonical

- **WHEN** `notebooks/_shared/db.py` is inspected
- **THEN** `LAKEHOUSE_URI_DEFAULT` MUST equal `"md:cianfhoghlaim"`

#### Scenario: 8-jurisdiction overview dashboard runs

- **WHEN** `notebooks/23_8_jurisdiction_overview.py` is launched
- **THEN** the dashboard MUST query `cianfhoghlaim.education._registry.subjects`
- **AND** show all 8 jurisdictions with their subject counts

### Requirement: Locket sidecar pattern for Infisical v0.161+ requires locket >= v0.18 or a request transformer

The system SHALL ensure that the locket sidecar (`ghcr.io/bpbradley/locket:infisical`)
used by every agent surface (openclaw, hermes, litellm, langfuse) is
compatible with the Infisical server version it authenticates against.

#### Scenario: Locket v0.17.3 with Infisical v0.161+ server

- **GIVEN** a stack with locket sidecar image
  `ghcr.io/bpbradley/locket:infisical` (tag ≤ `v0.17.3`)
- **AND** an Infisical server image `infisical/infisical` (tag ≥ `v0.161.0`)
- **WHEN** the locket sidecar starts in `watch` or `one-shot` mode
- **THEN** the locket sends `GET /api/v4/secrets/<KEY>?project_id=...&secret_path=...&secret_type=...`
  with **snake_case** query parameter names
- **AND** the Infisical server returns HTTP 422 `ValidationFailure`
  because v0.161+ requires **camelCase** query parameter names
  (`projectId`, `secretPath`, `secretType`)
- **AND** the locket catches the 422 and falls back to "policy=passthrough"
  — writing the raw `{{ infisical://... }}` template to the destination
  instead of the resolved secrets
- **AND** the consumer container (openclaw, hermes) tries to `source
  /run/secrets/locket/secrets.env` in `/bin/sh`, which interprets each
  `{{ infisical:///... }}` line as a command and fails with
  `not found`, causing the container to crash

**Acceptable workarounds (any one):**

1. **Upgrade locket** to a version that uses camelCase field names
   (e.g. `ghcr.io/bpbradley/locket:infisical-v0.18` or a `bons-locket:infisical`
   fork) — the canonical fix.
2. **Downgrade Infisical** to a version that accepts snake_case
   field names (e.g. `infisical/infisical:v0.160.0`).
3. **Add a request transformer** in the locket sidecar
   (e.g. a `mitmproxy` sidecar that rewrites `project_id` → `projectId`
   in outgoing requests).
4. **Patch the locket source** in `stedding/locket/src/provider/infisical.rs`
   (change the `SecretQueryParams` struct's `serde(rename_all = "snake_case")`
   to `"camelCase"`) and rebuild the image.

**Verification:** `curl http://<infisical>/api/v4/secrets/<KEY>?projectId=...&secretPath=...`
returns HTTP 200 with the resolved secret value (NOT 422).

### Requirement: Hermes s6-overlay requires running as root with cap_add [SETUID, SETGID]

The system SHALL ensure that any NousResearch/hermes-agent container
(image tag ≥ `v2026.7.1`) is configured to satisfy s6-overlay's init
constraints when deployed via docker compose.

#### Scenario: Hermes s6-overlay init phase

- **GIVEN** a hermes container with `image: nousresearch/hermes-agent:v2026.7.1`
- **AND** the image's s6-overlay init phase requires:
  - `/run` writable by the container user (s6-overlay checks
    `fatal: /run belongs to uid X instead of Y`)
  - `/opt/data` accessible by the internal `hermes` user (uid 10000)
    which the `main-wrapper.sh: cd /opt/data` step needs
  - `SETUID` + `SETGID` capabilities for s6-overlay's `suexec` to
    transition between root and the `hermes` user
- **WHEN** the container is configured with:
  - `user: 10000:10000` (the internal hermes user) + `read_only: true`
    + `no-new-privileges: true` + `cap_drop: [ALL]`
- **THEN** s6-overlay fails with `fatal: /run belongs to uid 0 instead of
  10000, ... lacking the privileges to fix it`
- **AND** the `tmpfs: /run:mode:1777` workaround is REJECTED by the
  Docker daemon with `invalid tmpfs option ["mode:1777"]` when
  `no-new-privileges: true` is set

**Acceptable configurations (any one):**

1. **Canonical upstream pattern** (recommended): `user: "0:0"` (root),
   no `read_only`, no `no-new-privileges`, `cap_drop: [ALL]`. The s6-overlay
   entrypoint runs as root (allowed to chown /run + /opt/data), then
   transitions to user 10000 via the s6 service definitions. This is the
   upstream pattern documented in the hermes-agent image.

2. **Sidecar pattern** (if root is unacceptable): add a chmod
   `init` container that runs as root before the main hermes container,
   performs the necessary chowns on /run + /opt/data, then EXITS
   (the main container is started only after the init exits).
   The main container then starts with `user: 10000:10000` and the
   pre-chowned /run + /opt/data.

3. **Custom base image** (most invasive): fork hermes-agent to
   remove s6-overlay (replace with a pure dumb-init or tini). Allows
   running as non-root from the start.

### Requirement: ChangeDetection.io for England awarding bodies

The system SHALL provide 3 ChangeDetection.io monitors in
`bonneagar/stacks/changedetection/monitors/`:

- `aqa_monitor.yaml` — AQA spec pages
  (`https://www.aqa.org.uk/subjects/<subject>/specifications`)
- `ocr_monitor.yaml` — OCR spec pages
  (`https://www.ocr.org.uk/qualifications/<subject>/`)
- `edexcel_monitor.yaml` — Edexcel spec pages
  (`https://qualifications.pearson.com/en/qualifications/edexcel-<subject>.html`)

Each monitor MUST:

- Use `web_scraping` mode + CSS selector for the spec version + PDF link
- Trigger a webhook to
  `http://dagster-webhook:8080/webhooks/england_change_detection`
- Be uploaded to the dev ChangeDetection.io vault via the ChangeDetection.io
  REST API

The system SHALL also provide 1 DuckLake audit table
`cianfhoghlaim.education.british_isles.england.changes` with the 11 columns
declared in the proposal.

#### Scenario: AQA maths GCSE spec change detected

- **GIVEN** AQA publishes a new version of the GCSE Mathematics specification
- **WHEN** the ChangeDetection.io `aqa_monitor.yaml` detects the change
- **THEN** the monitor posts a webhook payload to
  `http://dagster-webhook:8080/webhooks/england_change_detection`
- **AND** the Dagster sensor `england_change_detection_sensor` fires
- **AND** the sensor triggers the `england_england_re_extraction_job`
  for `(board=aqa, subject=mathematics, qualification_level=gcse)`
- **AND** a new row lands in
  `cianfhoghlaim.education.british_isles.england.changes` with
  `board='aqa'`, `subject='mathematics'`, `qualification_level='gcse'`
- **AND** a Slack alert posts to `#kcg-biep-v2`
- **AND** an email alert posts to `kcg-curriculum@cianfhoghlaim.ie`
- **AND** the re-extraction runs the full Change 3 ensemble (BAML +
  Unstract + qwen3-vl-8b + gemma-4-26B-A4B + RAGAS vote)

### Requirement: Pocket ID + Pangolin + Komodo OIDC wiring MUST be automatable via the bons IaC + the wire-pocketid-pangolin-komodo.sh script

The system SHALL provide a single one-shot automation that wires Pocket ID
as the OIDC identity provider for both Komodo (orchestrator) and
Pangolin (proxy) so non-technical operators do not need to manually
configure 4+ steps (Pocket ID OIDC client creation, Komodo OIDC config,
Pangolin IDP creation, Pangolin Resource IdP binding).

#### Scenario: Operator first deploys the cianfhoghlaim stack

- GIVEN the operator has populated the repo's .env with the
  required credentials (POCKETID_API_KEY, PANGOLIN_API_KEY, and
  optionally KOMODO_PASSWORD)
- WHEN the operator runs ./scripts/wire-pocketid-pangolin-komodo.sh
- THEN the script:
  - Creates (or finds) the komodo OIDC client in Pocket ID via
    POST /api/oidc/clients + POST /api/oidc/clients/{id}/secret
  - Updates Komodos OIDC config via POST /api/v1/set-core-config
  - Creates (or finds) the Pocket ID Identity Provider in Pangolin
    via POST /api/v1/idp
  - Writes the credentials to .env + (optionally) to the local
    Infisical vault at /komodo
  - Writes an audit record to /tmp/wire-pocketid-pangolin-komodo-{ts}.json
- AND the operator can verify the wiring by visiting
  https://komodo.cianfhoghlaim.ie and https://pangolin.cianfhoghlaim.ie

#### Scenario: Operator re-runs the script (idempotency)

- GIVEN the wiring is already in place
- WHEN the operator runs the script again
- THEN each step checks for existing state first and skips

#### Scenario: Operator wants to rotate the OIDC client secret

- WHEN the operator runs the script with --force
- THEN the script deletes the existing komodo OIDC client and creates a new one

### Requirement: Pocket ID OIDC clients are reconciled idempotently by the bash script + Pocket ID admin API (re-running is a no-op)

The system SHALL ensure that the wire-pocketid-pangolin-komodo.sh script
never creates duplicate OIDC clients in Pocket ID, never overwrites valid
Pangolin IdP configs, and never downgrades a working Komodo OIDC setup.

#### Scenario: Partial deployment (Komodo not yet up)

- WHEN the operator runs the script with --skip-komodo
- THEN the script skips Step 2 (Komodo OIDC config update) with a warning log
- AND still completes Steps 1, 3, 4, 5, 6 (Pocket ID + Pangolin + .env + audit)

#### Scenario: Partial deployment (Pangolin not yet up)

- WHEN the operator runs the script with --skip-pangolin
- THEN the script skips Step 3 (Pangolin IDP creation) with a warning log
- AND still completes Steps 1, 2, 4, 5, 6

#### Scenario: Script runs against a non-existent Komodo/Pangolin (DNS failure)

- WHEN the operator runs the script but Pocket ID / Pangolin / Komodo DNS resolution fails
- THEN the script logs the DNS failure and exits with a clear error code

#### Scenario: Pocket ID rejects the client_secret fetch (auth or permission issue)

- WHEN the Pocket ID admin API returns 401 or 403
- THEN the script logs the error and exits with code 1

### Requirement: PocketID IdP MUST be bound to every Pangolin Resource (4th manual step) — wired by wire-pocketid-resource-idp.sh

The system SHALL ensure that the PocketID Identity Provider (created in
step 3 by wire-pocketid-pangolin-komodo.sh) is bound to every Pangolin
Resource (site) so that users in Pocket ID can access the Resource.

#### Scenario: Operator runs wire-pocketid-resource-idp.sh --all

- **WHEN** the operator runs `wire-pocketid-resource-idp.sh --all`
- **THEN** the script:
  - Lists all Resources in the org via `GET /api/v1/site-resources`
  - For each Resource, calls `POST /v1/org/{orgId}/site-resource/{id}/idp`
    with the PocketID IdP id
  - Logs success/failure per Resource
  - Writes an audit record

#### Scenario: Operator runs wire-pocketid-resource-idp.sh --resource=mlflow.cianfhoghlaim.ie

- **WHEN** the operator specifies a single Resource
- **THEN** the script binds the PocketID IdP only to that Resource

#### Scenario: A Resource already has the PocketID IdP bound

- **WHEN** the operator runs the script multiple times
- **THEN** the script detects the existing binding (via the Pangolin
  Resource IdPs list) and skips the duplicate
- **OR** the script logs a warning that the IdP is already bound

### Requirement: Komodo + Periphery MUST be self-configured from the get-go (5th manual step) — wired by bootstrap-komodo-periphery.sh

The system SHALL ensure that when a new Komodo + Periphery deployment is
started, the auto-derive workflow runs and Periphery self-registers with
Pangolin + auto-derives its API key from Pocket ID.

#### Scenario: Operator runs bootstrap-komodo-periphery.sh after Komodo + Periphery are deployed

- **WHEN** the operator runs `bootstrap-komodo-periphery.sh`
- **THEN** the script:
  1. Mints a fresh Pangolin API key (via Pocket ID OIDC client_credentials)
  2. Self-registers Periphery with Pangolin (Newt protocol: POST /api/v1/newt)
  3. Wipes stale credentials from .env
  4. Verifies reachability of Komodo + Pangolin
  5. Writes an audit record to /tmp/bootstrap-komodo-periphery-{ts}.json

#### Scenario: PocketID secret rotation via cron

- **WHEN** the cron job `rotate-pocketid-secrets.sh` runs (default: 3am on the 1st of every 3rd month)
- **THEN** the script:
  1. Fetches a fresh secret via Pocket ID admin API (X-API-Key auth)
  2. Mints a fresh Pangolin API key (7-day TTL)
  3. Updates .env atomically
  4. Writes an audit record to /tmp/pocketid-rotation-{ts}.json
  5. Exits 0 on success or 1 on failure (with the failure logged)

### Requirement: Bunchloch OpenChamber external-development stack

The Bunchloch OpenChamber development stack MUST pin OpenChamber to version
`1.16.3` and SHALL run in explicit external OpenCode mode. The stack SHALL
configure `OPENCODE_HOST` for the host OpenCode server at port `4096`, set
`OPENCODE_PORT=4096`, and set `OPENCODE_SKIP_START=true`; it MUST NOT start a
second bundled OpenCode server in the container.

#### Scenario: External mode is selected explicitly

- **WHEN** the Bunchloch OpenChamber development container starts
- **THEN** its resolved environment contains the external OpenCode host,
  port `4096`, and `OPENCODE_SKIP_START=true`
- **AND** the container does not launch a bundled OpenCode daemon

#### Scenario: The image is reproducible and git-capable

- **WHEN** the OpenChamber image is inspected and executed
- **THEN** its OpenChamber version is exactly `1.16.3`
- **AND** `git --version` succeeds inside the container

### Requirement: Identical absolute repository mount

The Bunchloch OpenChamber development stack SHALL mount the host repository
`/Users/cianmacandeisigh/dev/kings_college_galway` at that identical absolute
path inside the container. The stack MUST preserve the path identity used by
the host OpenCode server so session directory filters, worktrees, and git
operations resolve to the same project.

#### Scenario: Session project paths resolve identically

- **WHEN** a user opens the canonical repository from OpenChamber
- **THEN** the external OpenCode server receives
  `/Users/cianmacandeisigh/dev/kings_college_galway` as the project path
- **AND** git status and file discovery operate on the host checkout rather
  than a container-only path

### Requirement: Persistent OpenChamber configuration without application shadowing

The Bunchloch development stack SHALL persist OpenChamber configuration and
UI-owned state in a dedicated config volume under
`/home/bun/.config/openchamber` (or an equivalent XDG config path). It MUST NOT
mount that volume over `/home/bun/.openchamber` or any other application work
directory containing the installed OpenChamber files.

#### Scenario: Config survives recreation

- **WHEN** the OpenChamber container is recreated
- **THEN** UI configuration and preferences remain available from the
  dedicated persistent config volume
- **AND** the installed application files and runtime entrypoint remain visible
  and executable

#### Scenario: Application files are not shadowed

- **WHEN** the running container is inspected
- **THEN** `/home/bun/.openchamber` contains the installed OpenChamber runtime
- **AND** no persistent config mount covers that application directory

### Requirement: Infisical/Locket-only secret delivery

The Bunchloch OpenChamber stack SHALL obtain runtime secrets through the
canonical Infisical/Locket sidecar contract. It MUST NOT commit, bake, print,
or pass plaintext secret values through stack files, image layers, example
files, verification artifacts, or ordinary container environment declarations.

#### Scenario: Secret injection succeeds

- **WHEN** Locket becomes healthy and OpenChamber starts
- **THEN** the required runtime secrets are available from the mounted
  Locket-managed secret file
- **AND** the OpenChamber service starts without a plaintext secret value in
  the repository or image

#### Scenario: Secret leakage is rejected

- **WHEN** the implementation is inspected for secret delivery
- **THEN** all secret entries resolve to Infisical references or runtime mounts
- **AND** no secret value appears in `compose.yaml`, `.env.example`, the
  Dockerfile, committed logs, or a deployment receipt

### Requirement: Loopback-only Bunchloch exposure and correct health endpoints

The Bunchloch OpenChamber development UI SHALL bind its host port to
`127.0.0.1` only. Its health check MUST target OpenChamber's `/health` path,
and the external host OpenCode health check MUST target `/global/health` on
port `4096`; implementations MUST NOT substitute the legacy `/api/health`
path for the OpenChamber dev check.

#### Scenario: Local UI health is green

- **WHEN** the Bunchloch stack is running
- **THEN** `curl -fsS http://127.0.0.1:<dev-port>/health` returns HTTP 200
- **AND** the published port is not bound to `0.0.0.0` or a public interface

#### Scenario: External OpenCode health is green

- **WHEN** host OpenCode 1.17.9 is running on port `4096`
- **THEN** `curl -fsS http://127.0.0.1:4096/global/health` returns HTTP 200
- **AND** the same `/global/health` endpoint is reachable from OpenChamber via
  `host.docker.internal:4096`

### Requirement: Locket sidecar env_file must be runtime-mounted, not host-validated

The system SHALL declare every `env_file:` path consumed by a Locket-using
service (openclaw, hermes, openchamber, langfuse, litellm, mlflow,
logfire, etc.) as a path inside the `stack-secrets` tmpfs volume that is
mounted into BOTH the locket sidecar AND the consuming service. The path
SHALL NOT be validated against the host filesystem at compose-parse time.
Stack-doctor MUST detect any `env_file:` entry whose source path is not
either (a) a host file inside the stack directory, or (b) a tmpfs volume
mount shared with a `locket` sidecar.

#### Scenario: Parse-time env_file failure surfaces as a stack-doctor finding

- **GIVEN** a developer commits a `sidecar.yaml` with
  `services.openclaw.env_file: /run/secrets/locket/secrets.env` AND
  no `stack-secrets` tmpfs volume shared with `locket`
- **AND** the developer's local docker compose parse fails with
  `env file /run/secrets/locket/secrets.env not found`
- **WHEN** `bun run validate-stacks` runs against that stack
- **THEN** the parse-time failure is reported as a **CRITICAL** finding
- **AND** the developer MUST either add the `stack-secrets` volume
  + mount OR replace the env_file with a host-readable bootstrap file

#### Scenario: A correct sidecar contract passes the gate

- **WHEN** the stack has `locket` + `<service>` both mounting
  `stack-secrets:/run/secrets/locket[:ro]` AND
  `env_file: /run/secrets/locket/secrets.env`
- **THEN** the stack-doctor parse-time gate returns OK
- **AND** `docker compose config` on the merged file resolves the
  env_file reference without error

### Requirement: Bunchloch fallback Infisical vault when arm1-OCI private resource is unhealthy

The system SHALL provide a fallback deployment path on the `bunchloch`
host that brings up a local Infisical vault (no Pangolin routing, port
8081 bound to `127.0.0.1` only) when the arm1-OCI Pangolin private
resource for `infisical.cianfhoghlaim.ie` is returning HTTP 5xx
(specifically 502 Bad Gateway at the WireGuard hop). The fallback MUST
seed a fresh `dev-baile` project with the 9 infisical paths consumed by
the openclaw + hermes services, and MUST write the bons-iac Universal
Auth client_id + client_secret to `/etc/komodo/secrets/infisical_secret`
so the Komodo Periphery mounts it identically to the OCI path.

The fallback MUST NOT modify the arm1-OCI Infisical vault. It MUST NOT
expose the local Infisical via Pangolin. The fallback MUST be torn down
with `docker compose -f bonneagar/stacks/infisical/compose.yaml down -v`
once the OCI path is repaired.

#### Scenario: Operator triggers the fallback when OCI is unhealthy

- **GIVEN** `mise run preflight:arm-oci --skip-namespace` reports
  `Infisical health: FAIL (502 Bad Gateway)`
- **AND** bunchloch has >= 25 GB free disk + >= 2 GB RAM headroom
- **WHEN** the operator runs
  `docker compose -f bonneagar/stacks/infisical/compose.yaml up -d`
- **THEN** the local Infisical backend (port 8081), postgres, and redis
  containers start
- **AND** `curl -fsS http://127.0.0.1:8081/api/status` returns 200
- **AND** running
  `bun run scripts/seed-bunchloch-fallback-vault.sh` populates the 9
  openclaw + hermes infisical paths under `dev-baile/dev`

#### Scenario: Locket resolves secrets from the fallback vault

- **GIVEN** the local Infisical is up and the seed script has populated
  the 9 secret paths
- **AND** `/etc/komodo/secrets/infisical_secret` contains the bons-iac
  Universal Auth client_id + client_secret
- **WHEN** the operator runs
  `cd bonneagar/stacks/openclaw && docker compose -f compose.yaml -f sidecar.yaml up -d`
- **THEN** the locket sidecar healthcheck returns OK
- **AND** `docker exec openclaw-locket -- /locket healthcheck` reports
  >= 9 resolved secrets
- **AND** the openclaw container starts with its env_file populated
  (no parse-time `env file not found` error)

#### Scenario: Fallback is torn down once the OCI path is repaired

- **WHEN** the operator runs
  `docker compose -f bonneagar/stacks/infisical/compose.yaml down -v`
- **THEN** the 3 local Infisical containers stop and the named volume
  is removed
- **AND** no orphan processes reference the local Infisical backend
- **AND** the operator can resume the canonical OCI path via
  `km run procedure deploy-openclaw-bunchloch`

### Requirement: Pangolin private-resource drift is detected and repaired via iac:sync:sites

The system SHALL detect when any Pangolin private resource (of which
`infisical.cianfhoghlaim.ie` is one of 6) returns HTTP 5xx for
> 5 consecutive minutes, and SHALL provide the
`iac:sync:sites` command as the canonical repair path. The command
MUST be idempotent and MUST re-emit the private-resource YAML via the
Pangolin Integrations API. The system SHALL NOT silently re-emit
without operator confirmation — `iac:sync:sites` is gated behind a
Komodo procedure that pauses for human approval after the dry-run.

#### Scenario: A private resource returns 502 for > 5 minutes

- **GIVEN** `https://infisical.cianfhoghlaim.ie/api/status` returns
  502 across 6 consecutive 60-second polls
- **WHEN** the operator runs
  `km run procedure repair-pangolin-private-infisical-arm1-oci-v1`
- **THEN** stage 2 of the procedure invokes `iac:sync:sites --dry-run`
  and pauses for `--yes` confirmation
- **AND** on `--yes`, `iac:sync:sites` re-emits the private resource
- **AND** `/api/status` returns 200 within 60s of the re-emit
- **AND** a JSON audit record is written to
  `/tmp/infisical-pangolin-private-repair-${TS}.json`

#### Scenario: iac:sync:sites is a no-op when the resource is healthy

- **GIVEN** `/api/status` returns 200 on the first poll
- **WHEN** the operator runs
  `km run procedure repair-pangolin-private-infisical-arm1-oci-v1`
- **THEN** stage 2 exits early with the message
  `pangolin private resource healthy — no repair needed`
- **AND** no re-emit is performed
- **AND** stages 3-6 are skipped

### Requirement: iac:rotate-auth must run after every Pangolin EE upgrade

The system SHALL require `iac:rotate-auth` to be re-run within 24
hours of any Pangolin EE upgrade that touches the Traefik forward-auth
middleware, the Pangolin Integrations API, OR the WireGuard tunnel
mutual-TLS handshake. The upgrade is detected by a mismatch between
`pangolin.cianfhoghlaim.ie/api/v1/version` and the last recorded
version in `~/.cache/bons-iac/pangolin-version.json`. The bons-iac
CLI SHALL emit a `WARN: pangolin EE upgraded; rotate bons-iac
client_secret` message when the operator runs any `iac:*` command
after the mismatch is detected.

#### Scenario: Operator runs iac:plan after a Pangolin upgrade

- **GIVEN** `pangolin.cianfhoghlaim.ie/api/v1/version` returns
  `vX.Y.Z` (newer than the cached version)
- **WHEN** the operator runs `mise run iac:plan`
- **THEN** the command emits
  `WARN: pangolin EE upgraded from vA.B.C to vX.Y.Z; rotate bons-iac client_secret before applying changes`
- **AND** the operator MUST run `mise run iac:rotate-auth` before
  the next `iac:deploy` will succeed (the deploy gate rejects with
  exit code 17)

#### Scenario: iac:rotate-auth re-derives the infisical_secret file

- **WHEN** the operator runs
  `mise run iac:rotate-auth --target=bons-iac`
- **THEN** a fresh client_secret is minted via `openssl rand -hex 32`
- **AND** the new credential is pushed to the dev-baile project on
  Infisical as `bons-iac/client_secret`
- **AND** `/etc/komodo/secrets/infisical_secret` is rewritten with
  the new credential (mode 0600, owner root)
- **AND** `locket healthcheck` against the rotated credential returns
  OK

### Requirement: portal-cloudflare-r2 stack entry

The system SHALL add a new stack at `bonneagar/stacks/portal-cloudflare-r2/`
following the 6-file GOLD_STANDARD pattern (compose.yaml + wrangler.jsonc +
Dockerfile + README.md + docs/STACK.md + Pangolin route).

The stack SHALL host:
- 1 Cloudflare R2 bucket (`cianfhoghlaim-pdfs`)
- 1 Cloudflare Pages project (`portal`)
- 1 Pangolin resource binding (`portal.cianfhoghlaim.ie` → Cloudflare tunnel)
- 1 Locket sidecar (secret injection from Infisical `dev-baile`)
- 1 Cloudflare Tunnel sidecar

**No Cloudflare Worker is required.** Signed URLs are issued from the
existing `hono-api` service (which already has S3 credentials via the
Garage S3 backend). This keeps the project on the Cloudflare free tier
with **no Workers Paid subscription required**.

Free-tier limits SHALL be called out in the README (10 GB storage + 1M
Class A ops/mo).

#### Scenario: Operator reads the stack README

- **WHEN** the operator opens `bonneagar/stacks/portal-cloudflare-r2/README.md`
- **THEN** they see the 6-file pattern + the free-tier limits
- **AND** the document notes that signed URLs are issued from Hono (no Workers Paid required)
- **AND** the stack is `bun run iac:plan --stack portal-cloudflare-r2`-able

#### Scenario: Stack deploys end-to-end

- **GIVEN** the operator runs `bun run iac:deploy --stack portal-cloudflare-r2`
- **WHEN** the deploy completes
- **THEN** `portal.cianfhoghlaim.ie` resolves to the leaving-cert app
- **AND** PDF assets download via Hono-issued signed R2 URLs (15-min TTL)

### Requirement: Pocket ID SSO as the single OIDC provider

The system SHALL use Pocket ID OIDC as the single SSO provider
across all 5 canonical surfaces + the central portal. The 5 OIDC
audiences SHALL be:

| Audience | Surface |
|---|---|
| `convex_backend` | Convex (all surfaces) |
| `croilar_web` | `croilar-web` |
| `croilar_portal` | `croilar-portal` |
| `leaving_cert_portal` | `cianfhoghlaim-leaving-cert` (5th surface) |
| `portal` | `portal.cianfhoghlaim.ie` (central portal entry) |

The Pocket ID instance SHALL live on `arm1-oci`.

#### Scenario: An operator adds a new OIDC audience

- **GIVEN** the operator wants to add a 6th audience for a future surface
- **WHEN** they edit `bonneagar/iac/pocketid/audiences.yaml`
- **THEN** the Pocket ID instance picks up the change via resource-sync
- **AND** the new audience appears in the JWKS at `/.well-known/jwks.json`

### Requirement: Sequential domain-by-domain migration as architectural principle

The system SHALL document the sequential domain-by-domain migration
principle (no big-bang cutovers) as a core IaC architectural rule.
The pattern is operationalized by the feature-flag rollout documented
in
`openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R25.

#### Scenario: A new stack is deployed

- **GIVEN** the operator wants to deploy the `portal-cloudflare-r2` stack
- **WHEN** they run `bun run iac:deploy --stack portal-cloudflare-r2`
- **THEN** the rollout is gated by the `portal_rollout` feature flag
- **AND** the rollout proceeds 10% → 50% → 100% over 7 days
- **AND** any error rate spike triggers automatic rollback

### Requirement: Canonical Infisical URI grammar

Every `bonneagar/stacks/<name>/secrets.env` file MUST use one of two
Infisical URI forms, and MUST NOT mix both forms in the same file:

1. **Bare form (canonical, post-v4)**: `KEY=infisical://dev-baile/<svc>/<key>`
2. **Jinja-wrapped form (legacy, accepted by the bons-locket-shim v0.2.0)**:
   `KEY={{ infisical:///KEY?path=/<svc> }}`

The two forms parse through different code paths:

- The bare form is parsed by `scripts/init-vault.ts` (which pushes local
  `.env` values into the Infisical vault).
- The Jinja form is parsed by `bonneagar/scripts/cianfhoghlaim-locket-shim.py`
  (which the Locket sidecar uses at container runtime).

A stack whose `secrets.env` mixes both forms is a silent integration break:
the shim sees one half, the seeder sees the other half, the operator sees
neither.

#### Scenario: stack-doctor --strict --check-grammar reports clean

```
$ mise run stack-doctor:strict
[lakehouse/secrets.env]    ✓ 7 bare + 0 Jinja (canonical)
[litellm/secrets.env]      ✓ 11 bare + 0 Jinja (canonical)
[openclaw/secrets.env]     ✓ 3 bare + 0 Jinja (canonical)
[openchamber/secrets.env]  ⚠ 5 Jinja + 0 bare (legacy, accepted but warning)
...
```

#### Scenario: a mixed-grammar secrets.env fails CI

```
$ mise run stack-doctor:strict
[tuatha/secrets.env]       ✗ MIXED: 4 bare + 2 Jinja (CI GATE FAILURE)
  bare line 12:  TUATH_OPENAI_API_KEY=infisical://dev-baile/tuatha/openai_api_key
  jinja line 18: TUATH_LANGFUSE_HOST={{ infisical:///langfuse/host }}
  → fix: pick one grammar; the canonical form is bare.
exit 1
```

#### Scenario: migration helper sweeps Jinja → bare

```
$ bun run scripts/normalize-infisical-uri.ts --apply
[lakehouse/secrets.env]    7 Jinja → 7 bare  (committed)
[litellm/secrets.env]      11 Jinja → 11 bare (committed)
[tuatha/secrets.env]       6 Jinja → 6 bare (committed)
...
synced 24 files in 4.2s
```

### Requirement: stack-doctor:strict CI gate

The `mise run stack-doctor:strict` task MUST be wired into CI and MUST
fail any merge that introduces a mixed-grammar `secrets.env` or a
`secrets.env` without any `infisical://` URI at all.

The task wraps `bun run scripts/stack-doctor.sh --strict --check-grammar`
which:

1. Lists every `bonneagar/stacks/<name>/secrets.env`
2. For each file, counts bare-form lines + Jinja-form lines + mixed
   detection
3. Exits non-zero if any stack has mixed grammar
4. Exits non-zero if any stack has zero URI lines (regression)
5. Prints a single-line summary per stack

#### Scenario: pre-commit hook blocks a mixed-grammar file

```
$ git commit -m "feat(tuatha): add TUATH_LANGFUSE_HOST env"
> mise run stack-doctor:strict
[tuatha/secrets.env]       ✗ MIXED: 4 bare + 2 Jinja (CI GATE FAILURE)
hook: pre-commit exited with code 1
```

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
