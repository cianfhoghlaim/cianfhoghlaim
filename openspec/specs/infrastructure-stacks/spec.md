# Infrastructure Stacks Capability

## Purpose

`infrastructure-stacks` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

## Background
94 storage, utility, engineering, machine learning, and infrastructure Docker Compose stacks managed via Komodo for the Cianfhoghlaim platform. Organised in a **flat** directory layout (one directory per stack under `infrastructure/stacks/<name>/`) with standardized Pangolin routing, Locket secret injection, and Infisical secret management. The historical 5-category subdirectory split (`storage/`, `engineering/`, `infrastructure/`, `machine_learning/`, `tools/`) was removed on 2026-06-23; functional groups are now informational only and recorded in `infrastructure/AGENTS.md` and `infrastructure/QUADRANT-TO-STACK-MAP.md`.

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
`infrastructure/stacks/<name>/` directory. The 6 files are:

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

#### Scenario: A new stack is added to `infrastructure/stacks/<name>/`

- **GIVEN** the stack dir has been created with 1 or 2 of the 6
  GOLD_STANDARD files
- **WHEN** `bun run stack-doctor` runs on the PR
- **THEN** the gate SHALL fail with exit code 1 (missing file)
- **AND** the developer MUST add the remaining files before the
  PR merges

#### Scenario: A Locket sidecar uses the canonical security baseline

- **GIVEN** `infrastructure/stacks/oideachais-dagster/sidecar.yaml`
- **WHEN** the stack is deployed
- **THEN** the Locket container SHALL have `user: 65532:65532` +
  `no-new-privileges: true` + `cap_drop: [ALL]` + `read_only: true`
  + `tmpfs: [/run/secrets/locket:size=1m,mode=0700]`
- **AND** the `cianchoghlaim_locket_secrets` external tmpfs volume
  SHALL be mounted

### Requirement: Storage Stacks

The system SHALL deploy database and data infrastructure for the lakehouse architecture.

#### Scenario: Lakehouse Stack
- **GIVEN** lakehouse stack with Garage S3, Postgres, Lakekeeper, and Lance Namespace sidecar
- **WHEN** stack deploys via Komodo
- **THEN** S3 API (3900), Postgres (5433), Iceberg REST catalog (8181), and Lance sidecar (8182) are accessible

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
`infrastructure/stacks/` in a **flat** layout — every stack
is a direct child of `infrastructure/stacks/`, with no
category subdirectory. Functional purpose (control plane,
storage, engineering, ML, tools, browser) is recorded as
**information only** in `infrastructure/AGENTS.md` § "Stack
Inventory" and the cross-quadrant routing table at
`infrastructure/QUADRANT-TO-STACK-MAP.md`, and is not
encoded in the directory hierarchy.

A new stack's directory is therefore `infrastructure/stacks/<name>/`
and not `infrastructure/stacks/<category>/<name>/`.

#### Scenario: A new stack is added

- **GIVEN** a developer wants to add a new "Pocket ID
  bridge" stack
- **WHEN** they create `infrastructure/stacks/pocket-id-bridge/`
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
- **THEN** the Locket sidecar (infrastructure/stacks/<name>)
  injects Infisical secrets
- **AND** the Garage S3 (infrastructure/stacks/garage) holds
  the Parquet
- **AND** the Dagster + LiteLLM + BAML
  (infrastructure/stacks/dagster, litellm, oideachais)
  orchestrate + extract
- **AND** the Cognee + FalkorDB + LanceDB
  (infrastructure/stacks/cognee, falkordb, lancedb) serve
  the graph + vector
- **AND** the DevDocs (infrastructure/stacks/DevDocs) hosts
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

KCG skills MUST follow: (5) the canonical name prefixes (motherduck* / browser-tools / ccc / kcg-* / oideachais-* / tuatha-* / croilar-* / meaisinfhoghlaim-*), (6) no vendoring of upstream Anthropic / vendor skills, (7) no skills that duplicate the root `AGENTS.md` "Critical Agent Protocols" content, (8) no embedded git sub-repositories.

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

- **WHEN** a new DLT source is added under `oideachais/dlt_sources/`
- **THEN** the `.agents/skills/dlt/SKILL.md` "KCG examples" appendix gets a 1-line addition naming the new source

### Requirement: Quadrant-specific Related skills

Each quadrant's `AGENTS.md` "Related skills" section MUST list only the skills used by that quadrant (no shared "default" list across quadrants). The 4 quadrants are `oideachais`, `meaisinfhoghlaim`, `tuatha`, `croilar`, plus the cross-cutting `infrastructure` layer.

#### Scenario: oideachais/AGENTS.md lists 12 oideachais-specific skills

- **WHEN** `oideachais/AGENTS.md` is read
- **THEN** the "Related skills" section lists 12+ skills (dagster, dlt, baml, cocoindex, cognee, lancedb, falkordb, duckdb, motherduck, dignified-python, marimo, ccc, oideachais-storage, oideachais-pipeline, oideachais-leabharlann, oideachais-baml-schemas, oideachais-cognify-knowledge-graph)
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

- **WHEN** an agent reads `/oideachais/AGENTS.md` (or any of the 4 quadrant `AGENTS.md` files)
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it lists the 5-8 skills most relevant to that quadrant + the ccc command + the 4 openspec commands

#### Scenario: infrastructure/AGENTS.md leads with priority quick reference

- **WHEN** an agent reads `/infrastructure/AGENTS.md`
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it contains the stack-doctor command + the stack-ops skill + the 4 priority compose stacks (oideachais, litellm, langfuse, lakehouse)

#### Scenario: openspec/AGENTS.md leads with priority quick reference

- **WHEN** an agent reads `/openspec/AGENTS.md`
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it contains the 4 priority specs (oideachais-pipeline, infrastructure-stacks, agent-memory-systems, dagger-pipelines) + the ccc command + the lint:skills task

### Requirement: Stack-Doctor CI Gate

The system SHALL run `bun run stack-doctor` on every PR via a
GitHub Action. The 4 gates are:

1. **File gate** (exit code 1) — every
   `infrastructure/stacks/<name>/compose.yaml` has the other 5
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

- **GIVEN** a developer adds `infrastructure/stacks/<new>/compose.yaml`
  with a new service
- **WHEN** the PR's GitHub Action runs `bun run stack-doctor`
- **THEN** the File gate (exit code 1) SHALL fail
- **AND** the Action SHALL post a comment on the PR listing the
  5 missing files
- **AND** the PR SHALL be blocked from merging

#### Scenario: A secret URI in `secrets.env` doesn't resolve in the vault

- **GIVEN** a developer adds
  `INFI_FOO=infisical://dev-baile/oideachais/foo` to
  `infrastructure/stacks/<stack>/secrets.env`
- **AND** the `dev-baile` Infisical environment does NOT have a
  secret at path `oideachais/foo`
- **WHEN** the Secret gate runs
- **THEN** the gate SHALL fail with exit code 4
- **AND** the developer MUST either create the secret in
  Infisical OR remove the URI from `secrets.env`

### Requirement: Image Pinning Policy

The system SHALL pin every `image:` line in every
`infrastructure/stacks/<name>/compose.yaml` to a specific
`<major>.<minor>.<patch>` semver tag. The tag `:latest` is
**forbidden** for upstream images. Local-build images with
`pull_policy: never` are exempt and MUST include an inline YAML
comment explaining the deviation.

The `stack-doctor` SHALL report any unpinned image as
**WARNING** (exit code 1, soft failure) so that pre-existing
stacks can be migrated incrementally.

#### Scenario: A PR introduces an unpinned image

- **GIVEN** a developer adds
  `image: ghcr.io/cianfhoghlaim/oideachais-dagster:latest` to
  a compose file
- **WHEN** the Image Pinning Policy gate runs
- **THEN** the gate SHALL report a WARNING
- **AND** the developer SHOULD pin to a semver tag like
  `ghcr.io/cianfhoghlaim/oideachais-dagster:1.2.3`

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
| All Stacks | `infrastructure/stacks/` |
| Gold Standard | `infrastructure/stacks/GOLD_STANDARD.md` |
| Stack README | `infrastructure/stacks/README.md` |

## Related Specs

- [infrastructure](../infrastructure/spec.md) — Pangolin convergence, secrets, Komodo GitOps
- [data-pipeline](../data-pipeline/spec.md) — Pipeline orchestration
