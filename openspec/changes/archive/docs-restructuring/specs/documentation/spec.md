# Spec Deltas: docs-restructuring

This change introduces a new `documentation` capability spec that captures
the structure, frontmatter schema, and routing conventions for the
consolidated `docs/` tree. It does not modify any existing capability
spec — this is a docs/ restructure, not a behaviour change.

## ADDED Requirements

### Requirement: Canonical Directory Layout

The `docs/` tree SHALL be organised into numbered domain directories
(`01-platform-architecture/` through `07-standards/`), each focused on
one capability area. The `00_index.md` file at the root SHALL be the
single master routing table.

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
with a YAML frontmatter block containing all of the required fields
defined in the `documentation` capability spec.

#### Scenario: Canonical document is created

- **GIVEN** a contributor is creating a new canonical document
- **WHEN** the file is written
- **THEN** the file starts with a `---`-delimited YAML block
- **AND** the block contains `title:`, `domain:`, `status:`,
  `description:`, and `last_reviewed:` (all required)
- **AND** if the file is the result of a merge, the block contains a
  `supersedes:` list of the source paths

### Requirement: Per-Domain Cognee Cognify

The `infrastructure/scripts/cognee-ingest-docs.py` script SHALL be able
to ingest canonical documents into a Cognee knowledge graph for
semantic search across the documentation.

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

### Requirement: Non-Destructive Consolidation

The system MUST preserve all original content without loss when canonical
documents are produced through heavy merge of overlapping source files.

#### Scenario: Source files are merged into a canonical

- **GIVEN** source files `a.md`, `b.md`, `c.md` are being merged into
  `docs/<domain>/canonical.md`
- **WHEN** the merge is complete
- **THEN** the canonical MUST contain the union of all unique content
- **AND** the original three files MUST be preserved in
  `docs/archive/YYYY-MM-DD-<subtree>/` with their content unchanged
- **AND** the canonical's `supersedes:` field MUST list the three
  original paths
