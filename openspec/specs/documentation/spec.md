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

#### Scenario: New canonical document is added to a domain

- **GIVEN** a contributor wants to add a new canonical document covering
  a topic in the `data_platform` domain
- **WHEN** the document is created
- **THEN** it is placed in `docs/02-data-platform/` with a kebab-case
  filename that matches the topic
- **AND** the document carries the standard frontmatter schema
- **AND** the `00_index.md` routing table is updated to include the new
  document in the "I want to..." table and the per-domain document list

#### Scenario: User searches for documentation

- **GIVEN** a user (human or agent) wants to find the canonical doc
  covering a specific topic
- **WHEN** they consult `docs/00_index.md`
- **THEN** they find a "I want to..." routing entry that points to the
  correct canonical file
- **OR** they consult the per-domain "Documents by Domain" section

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

When a contributor merges multiple source files into a single canonical
document, the originals SHALL be preserved in `docs/archive/` with
a clear provenance trail.

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
