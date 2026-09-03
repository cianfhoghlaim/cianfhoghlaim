# Capability: dev-tooling-surfaces

## Purpose

Define the canonical 3-tool developer surface (opencode + mise + openspec)
for the cianfhoghlaim monorepo. Each tool has a single home, a single
skill reference, and a single agent surface — preventing the sprawl that
accumulated across 2026-04 through 2026-08-19.

The three surfaces are:

1. **`mise.toml`** — the 8 task namespaces + ~60 file tasks in `mise-tasks/`
2. **`opencode.json` + `.opencode/agents/*.md`** — 4 primary + 9 domain agents
3. **`openspec/` + `.agents/skills/openspec/SKILL.md`** — 78 pending + 96
   archived changes, the 1.4 subcommands, and the spec-delta format

## ADDED Requirements

### Requirement: mise-task-canonical-shape

The `mise.toml` task catalogue SHALL contain no more than 100 TOML tasks
across exactly 9 namespaces (core, ts, schema, py, lint, opencode, baml,
openspec, cic), plus a `[task_templates]` block for repeating patterns
and a `mise-tasks/` directory for file-based tasks.

#### Scenario: namespace count check

- **WHEN** `grep -E '^\[tasks\."' mise.toml | wc -l` runs
- **THEN** the result MUST be ≤ 100
- **AND** the unique namespace prefix distribution MUST be ≤ 12

#### Scenario: alias-pair deduplication

- **WHEN** any pair of task names (`name` and `name:colon`) shares the
  same `run` body
- **THEN** the colon form MUST be the canonical task
- **AND** the bare form MUST be preserved for 1 release cycle via
  `alias = "name:colon"` on the canonical task
- **AND** no two `[tasks.*]` blocks SHALL differ only by the colon vs
  bare-name form

#### Scenario: task_templates coverage

- **WHEN** a repeating task pattern exists (e.g. one wrapper per OCR
  model, per document converter, per agent extractor, per BIEP milestone)
- **THEN** the pattern MUST be expressed as a `[task_templates."<prefix>"]`
  block in `mise.toml`
- **AND** the per-instance script MUST live in `mise-tasks/<namespace>/<name>.sh`
  with `#MISE` frontmatter

#### Scenario: depends DAG construction

- **WHEN** any quality-gate task (lint, ci, sync, test) depends on
  prerequisite tasks
- **THEN** the dependency MUST be declared via `depends = [...]` on the
  gating task (not by manual sequencing in `run`)
- **AND** `mise tasks --depends` MUST show the DAG

### Requirement: opencode-agent-markdown-split

The `opencode.json` agent catalogue SHALL define ≤5 agents inline; all
domain-specific subagents MUST live as `.md` files under
`.opencode/agents/<name>.md` with YAML frontmatter and a `prompt` field
that references canonical files via direct path (`./AGENTS.md`,
`./openspec/AGENTS.md`, etc.).

#### Scenario: agent count by location

- **WHEN** `find .opencode/agents -name "*.md" | wc -l` runs
- **THEN** the result MUST be ≥ 9
- **AND** `grep -cE '^\s+"[a-z-]+":\s+\{' opencode.json | grep -v provider` MUST be ≤ 5

#### Scenario: prompt truncation prevention

- **WHEN** any agent's `prompt` string would exceed 2000 chars
- **THEN** that string MUST live in a `.opencode/agents/<name>.md` file
- **AND** `opencode.json` MUST reference it via
  `prompt = "{file:./.opencode/agents/<name>.md}"`

#### Scenario: guides.yml alignment

- **WHEN** an agent's prompt references a domain surface
- **THEN** the prompt MUST cite at least one entry from
  `.cocoindex_code/guides.yml` via `#<entry-title>` anchor
- **AND** the cited guide MUST resolve in the CCC index after
  `bun run ccc:index`

### Requirement: opencode-permission-api-migration

Every opencode agent SHALL use the `permission` field (not the deprecated
`tools` field) for access control. `permission.task` SHALL be set on
every primary agent to control which subagents it may invoke.

#### Scenario: deprecated API absence

- **WHEN** `grep -E '"tools":\s*\{' opencode.json` runs
- **THEN** the result MUST be empty (no agent uses the deprecated API)

#### Scenario: plan-agent read-only enforcement

- **WHEN** the `plan` agent is invoked
- **THEN** `permission.edit` MUST equal `deny`
- **AND** `permission.bash` MUST default to `ask` for `*`
- **AND** `permission.bash` MUST `allow` the safe read-only commands
  (`git status`, `git log*`, `git diff`, `openspec *`, `mise tasks`,
  `mise run lint*`)
- **AND** `permission.task` MUST `deny` `*` except `research` and
  `deep-cuts` (which MUST be `allow`)

#### Scenario: domain-agent scope enforcement

- **WHEN** a domain-specific subagent (e.g. `data-platform`) is invoked
- **THEN** `permission.bash` MUST `allow` only the commands within its
  scope (e.g. `uv run *`, `mise run *`)
- **AND** `permission.external_directory` MUST equal `deny`
- **AND** `permission.task` MUST allow only its sibling subagents

### Requirement: openspec-skill-canonical-reference

The `.agents/skills/openspec/SKILL.md` file SHALL exist, SHALL have valid
YAML frontmatter passing `mise run lint:skills`, and SHALL document the
8 canonical subcommands (`list`, `view`, `show`, `status`, `validate`,
`archive`, `instructions`, `schemas`).

#### Scenario: skill lint pass

- **WHEN** `bash .agents/skills/lint-skills.sh` runs
- **THEN** the openspec skill MUST appear in the pass list
- **AND** the skill MUST mention all 8 subcommands
- **AND** the skill MUST document the spec-delta format (ADDED/MODIFIED/
  REMOVED Requirements + Scenario blocks)

#### Scenario: priority command registered

- **WHEN** an agent reads `openspec/AGENTS.md`
- **THEN** the file MUST reference `.agents/skills/openspec/SKILL.md`
- **AND** the file MUST list `openspec view` + `openspec status` +
  `openspec validate --all` as new priority commands
- **AND** the file MUST include a 1-section "OPSX vs legacy schema" note

### Requirement: ccc-guides-coverage

The `.cocoindex_code/guides.yml` file MUST contain at least 30 entries,
including the 3 new entries `opencode-agent-search`, `mise-task-search`,
and `openspec-change-search`.

#### Scenario: guide count check

- **WHEN** `mise run lint:guides-yml` runs
- **THEN** the guide count MUST be ≥ 30
- **AND** the 3 new guides MUST be present
- **AND** every file path referenced in each guide MUST resolve on disk

#### Scenario: guides.yml domain alignment

- **WHEN** any new concept guide is appended
- **THEN** it MUST carry a `domain: "00-tooling"` tag (or a more
  specific domain if the concept is domain-specific)
- **AND** it MUST include a `tags: [...]` array with at least 3 keywords
  for semantic search matching
- **AND** it MUST follow the canonical schema (`title`, `description`,
  `files`, `tags`, `domain`)

### Requirement: openspec-schema-stability

The repository SHALL remain on the legacy `spec-driven` schema
(proposal + tasks + spec deltas under `openspec/changes/<id>/`); the
experimental `OPSX` schema (YAML + Markdown templates, DAG dependencies)
SHALL NOT be adopted in this capability.

#### Scenario: schema non-migration

- **WHEN** `openspec schemas` runs
- **THEN** the result MUST NOT show a fork or fork-derivative of `opsx`
  as the active schema for this repo
- **AND** the legacy `spec-driven` schema MUST remain the canonical
  workflow for all 78 pending + 96 archived changes

## Cross-references

- `.agents/skills/mise/SKILL.md`
- `.agents/skills/opencode/SKILL.md`
- `.agents/skills/openspec/SKILL.md`
- `openspec/specs/knowledge-sync-loop/spec.md`
- `openspec/specs/indexing-and-cognition/spec.md`
- `openspec/specs/agent-platform-cluster/spec.md`
- `openspec/specs/centralized-registry/spec.md`
- `.cocoindex_code/guides.yml#opencode-agent-search`
- `.cocoindex_code/guides.yml#mise-task-search`
- `.cocoindex_code/guides.yml#openspec-change-search`
