# Capability: documentation

## Purpose

Establish the standard structure, frontmatter schema, and routing conventions
for the Cianfhoghlaim `docs/` tree. The goal is to make every canonical
document simultaneously:

1. **Cognee-cognify-ready** — explicit entity names and relationships so
   the LLM can extract a clean knowledge graph.
2. **ccc-indexable** — frontmatter fields that improve semantic search
   relevance for the exact queries users type.
3. **Agent-skill-consumable** — frontmatter fields that the
   `.agents/skills/agent-docs/` skill can route against.
## Requirements
### Requirement: Canonical Directory Layout

The `docs/` tree SHALL be organised into numbered domain directories,
each focused on one capability area. The `00_index.md` file at the
root SHALL be the single master routing table.

In addition, every README in the Cianfhoghlaim monorepo SHALL
follow the canonical 6-section structure:

1. **What lives here** — the quadrant/area overview (1-2 paragraphs)
2. **Quick start** — the dev quick-start (5-10 commands)
3. **Key commands** — the canonical commands (build / dev / test /
   lint / deploy)
4. **Common workflows** — the add-a-new-X workflows (3-5 patterns)
5. **How to deploy** — the deploy playbook (the per-area steps)
6. **How to debug** — the troubleshooting guide (5-10 common
   failure modes + fixes)

The 7 READMEs in the monorepo are:

- `README.md` (root) — the monorepo overview + the 8-phase
  end-to-end deploy playbook
- `infrastructure/README.md` — the 94-stack inventory
- `cianfhoghlaim/README.md` — the lakehouse quadrant
- `cianfhoghlaim/README.md` — the AI/ML quadrant
- `cianfhoghlaim/README.md` — the MMO + crypto quadrant
- `cianfhoghlaim/README.md` — the portfolio quadrant
- `spaces/README.md` — the HuggingFace Spaces

A standalone `DEPLOY.md` at the repo root SHALL contain the
end-to-end deploy playbook (the 8 phases + the 9th phase rollback).

#### Scenario: New canonical document is added to a domain

- **GIVEN** a contributor wants to add a new canonical document covering
  a topic in the `data_platform` domain
- **WHEN** the document is created
- **THEN** it is placed in `docs/02-data-platform/` with a kebab-case
  filename that matches the topic
- **AND** the document carries the standard frontmatter schema
- **AND** the `00_index.md` routing table is updated to include the new
  document in the "I want to..." table and the per-domain document list

#### Scenario: A README follows the 6-section structure

- **GIVEN** a new quadrant is added to the monorepo
- **WHEN** the quadrant's `README.md` is created
- **THEN** it SHALL have the 6 canonical sections
  (What lives here / Quick start / Key commands / Common workflows /
  How to deploy / How to debug)
- **AND** the section ordering SHALL be consistent with the other
  7 READMEs

### Requirement: Standard Frontmatter Schema

Every canonical document at the root of a domain directory SHALL start
with a YAML frontmatter block containing all of the following fields:

#### Scenario: Canonical document is created

- **GIVEN** a contributor is creating a new canonical document
- **WHEN** the file is written
- **THEN** the file starts with a `---`-delimited YAML block
- **AND** the block contains a `title:` (string, required)
- **AND** the block contains a `domain:` (enum, required) from
  `architecture`, `data_platform`, `agents`, `ai_ml`, `web`, `product`,
  `standards`
- **AND** the block contains a `status:` (enum, required) from
  `stable`, `draft`, `superseded`, `archived`
- **AND** the block contains a `description:` (string, required) — a
  one-sentence summary
- **AND** the block contains a `supersedes:` (list of paths, required
  when the file is the result of a merge) listing the source files that
  were folded into this canonical
- **AND** the block contains an `entities:` (list of strings, optional)
  naming the named concepts (tools, protocols, services) the document
  discusses
- **AND** the block contains a `related_skills:` (list of paths,
  optional) listing the agent skills that should load this document
- **AND** the block contains a `ccc_query_hints:` (list of strings,
  optional) — the natural-language queries a user would type that
  should return this document
- **AND** the block contains a `last_reviewed:` (ISO date, required)
  showing the last time the document was verified accurate

### Requirement: Archive of Merged Originals

The system SHALL preserve the originals in `docs/archive/` with a
clear provenance trail when a contributor merges multiple source files
into a single canonical document.

#### Scenario: Originals are merged into a canonical

- **GIVEN** multiple source files are being merged into a canonical
- **WHEN** the merge is complete
- **THEN** the originals are moved (not copied) to
  `docs/archive/YYYY-MM-DD-<source-subtree>/`
- **AND** the canonical's `supersedes:` field lists the original paths
  so the provenance is traceable from the canonical
- **AND** the original file content is unchanged in the archive

### Requirement: Per-Domain Cognee Cognify

The platform SHALL be able to ingest the canonical documents into a
Cognee knowledge graph for semantic search across the documentation.

#### Scenario: Operator runs Cognee ingestion

- **GIVEN** the Cognee REST API is reachable and `LLM_API_KEY` is set
- **WHEN** the operator runs
  `uv run python infrastructure/scripts/cognee-ingest-docs.py --all`
- **THEN** each of the 7 domain directories is iterated
- **AND** for each canonical `.md` file in the directory, the file's
  body is added to a Cognee dataset named `docs-<domain>`
- **AND** after all files in a domain are added, `cognify()` is
  triggered for that dataset
- **AND** the script exits with a non-zero status if any add or cognify
  call fails

#### Scenario: Operator stores data without LLM key

- **GIVEN** the Cognee REST API is reachable but `LLM_API_KEY` is not
  set
- **WHEN** the operator runs
  `uv run python infrastructure/scripts/cognee-ingest-docs.py --all --no-cognify`
- **THEN** each canonical file's body is added to the appropriate
  `docs-<domain>` dataset
- **AND** no `cognify()` is attempted
- **AND** a warning is printed explaining that the knowledge graph
  has not been built

### Requirement: Skill-to-Doc Routing

The `docs/00_index.md` SHALL provide a mapping from agent skill name
to the canonical document(s) the skill should consult first.

#### Scenario: Agent skill is loaded

- **GIVEN** an agent skill is loaded by the OpenCode runtime
- **WHEN** the agent needs documentation context
- **THEN** the agent consults `docs/00_index.md` for the skill-to-doc
  mapping
- **AND** reads the primary canonical document(s) listed for the skill
- **AND** the canonical's `related_skills:` frontmatter field includes
  the agent skill path, providing a bidirectional link

### Requirement: Non-Destructive Consolidation

The system MUST preserve all original content without loss when canonical
documents are produced through heavy merge of overlapping source files.

#### Scenario: Source files are merged into a canonical

- **GIVEN** source files `a.md`, `b.md`, `c.md` are being merged into
  `docs/<domain>/canonical.md`
- **WHEN** the merge is complete
- **THEN** the canonical MUST contain the union of all unique content
  from the three source files
- **AND** the original three files MUST be preserved in
  `docs/archive/YYYY-MM-DD-<subtree>/` with their content unchanged
- **AND** the canonical's `supersedes:` field MUST list the three
  original paths

### Requirement: End-to-end deploy playbook

The root `README.md` SHALL contain an 8-phase end-to-end deploy
playbook. The 8 phases are:

1. **Phase 0: Pre-flight** — verify the toolchain (`mise install`),
   the secrets (`bun run secrets:env` + `bun run secrets:init`),
   and the 2 hosts (`arm1-oci` + `bunchloch`)
2. **Phase 1: Infrastructure** — bootstrap the Infisical vault
   (the `dev-baile` environment) + the Komodo control plane
   + the Pangolin mesh + the Locket sidecar + the 4 quadrant
   stacks (infra → oideachais → meaisinfhoghlaim → tuatha →
   croilar)
3. **Phase 2: Oideachais** — deploy the lakehouse (Dagster +
   FastAPI + TanStack Start + Agno AgentOS + Google ADK)
4. **Phase 3: Meaisínfhoghlaim** — deploy the AI/ML services
   (llama-swap + mlx-omni + invokeai + the 12 agents)
5. **Phase 4: Tuatha** — deploy the MMO + the crypteolas
   achievement ledger
6. **Phase 5: Croílár** — deploy the 3-persona portfolio
   + the DevTools Hub
7. **Phase 6: Spaces** — deploy the 4 active HuggingFace
   Spaces (sync via the reusable workflow)
8. **Phase 7: Verify** — run the 4 audit scripts (the
   `infrastructure/audit/scripts/` quartet) + the `stack-doctor`
   CI gate
9. **Phase 8: Rollback** — the canonical rollback procedure
   (the Locket sidecar auto-rollback + the Infisical version
   restore + the Komodo stack disable)

The playbook SHALL also be duplicated as a standalone `DEPLOY.md`
at the repo root (for users who want the playbook without the
monorepo overview).

#### Scenario: A developer follows the 8-phase playbook

- **GIVEN** a developer wants to deploy the entire Cianfhoghlaim
  monorepo to a fresh `bunchloch` + `arm1-oci` cluster
- **WHEN** they follow the 8-phase playbook in `README.md`
  (or the standalone `DEPLOY.md`)
- **THEN** the 5 quadrants (infrastructure + oideachais +
  meaisinfhoghlaim + tuatha + croilar) + the 4 Spaces deploy
  in dependency order
- **AND** the 4 audit scripts return 0 (clean)
- **AND** the `stack-doctor` CI gate passes
- **AND** the developer can roll back via Phase 8 if any phase
  fails

### Requirement: Per-stack docs cross-reference every active stack

The system SHALL maintain one Markdown cross-reference document for every active stack in the stack inventory. Each active stack listed in `docs/stacks/README.md` SHALL have a corresponding `docs/stacks/<name>.md` document, using the documented stack-doc template.

The docs contract SHALL remain separate from the `bonneagar/` source-of-truth stack files: this repo documents and validates cross-references, while the separate `bonneagar` repo owns the live `bonneagar/stacks/<name>/` stack definitions.

#### Scenario: Stack docs inventory is complete

- **GIVEN** the stack inventory lists an active stack name `<name>`
- **WHEN** a contributor runs the stack-doc completeness check
- **THEN** `docs/stacks/<name>.md` SHALL exist
- **AND** the document SHALL include purpose, GitOps rationale, cross-references, and tags sections

#### Scenario: Missing generator is treated as deferred implementation work

- **GIVEN** this final drift cleanup change is implemented
- **AND** the optional T1 generator `scripts/generate-stack-docs.ts` is not present in the Cianfhoghlaim worktree
- **WHEN** the optional T1 follow-up is evaluated
- **THEN** stack-doc generation MAY be deferred
- **AND** the OpenSpec proposal MUST record the deferred status rather than modifying the separate `bonneagar/` repo

#### Scenario: Stack docs do not hand-edit secrets

- **GIVEN** a stack doc references a stack's secret contract
- **WHEN** the doc describes how runtime secrets are hydrated
- **THEN** it SHALL point to Infisical + Locket + mise
- **AND** it SHALL NOT instruct contributors to manually create `.env` files

### Requirement: PlanetScale Postgres Centralisation (documentation)

The system SHALL cross-reference the PlanetScale Postgres Data Strategy umbrella in the canonical `docs/` frontmatter schema so that any future spec + ADR + operator doc that mentions a Postgres connection can resolve the substrate decision quickly.

#### Scenario: An agent searches docs for a Postgres connection

- **GIVEN** an agent searches `docs/` for "PlanetScale postgres"
- **WHEN** they read the relevant doc
- **THEN** the doc SHALL cross-reference `openspec/specs/planetscale-postgres-data-strategy/spec.md`
- **AND** the doc SHALL cross-reference `openspec/architecture-decisions/0005-planetscale-postgres-centralisation.md`
- **AND** the operator SHALL be able to pick the substrate from R7 in 1 hop

