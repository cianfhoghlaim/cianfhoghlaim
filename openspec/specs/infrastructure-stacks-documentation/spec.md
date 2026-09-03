# Infrastructure Stacks Documentation Capability

## Purpose

`infrastructure-stacks-documentation` is a capability of the
Cianfhoghlaim platform. It defines the contract for the per-stack
documentation that lives in `cianfhoghlaim/` (the code repo) but
documents the ops at `bonneagar/` (the infra repo).

The corresponding source code lives at:

- `cianfhoghlaim/docs/stacks/README.md` (the index)
- `cianfhoghlaim/docs/stacks/<name>.md` (the per-stack docs, one per stack in `bonneagar/stacks/`)
- `scripts/stack-doctor.sh` (the CI gate that fails if a stack is missing its doc)
- `.agents/skills/infrastructure-stacks-documentation/SKILL.md` (the agent entry point)

## Background

The Cianfhoghlaim monorepo has a clean separation:

- **`cianfhoghlaim/`** = the code (Python package, agents, web apps, jupytext notebooks)
- **`bonneagar/`** = the infra (94 Docker Compose stacks + Komodo + Pangolin + Infisical IaC)

Without a contract that every stack has a per-stack doc in
`cianfhoghlaim/docs/stacks/`, the agent fleet has no entry point for
"how do I run `<x>` in production". The `stack-doctor.sh` CI gate
enforces the contract.
## Requirements
### Requirement: Per-stack docs contract

The system SHALL provide a per-stack doc file at
`cianfhoghlaim/docs/stacks/<name>.md` for every stack in
`bonneagar/stacks/<name>/`. Each per-stack doc SHALL have 4 sections:

1. **Purpose** — one paragraph: what the stack does, who owns it, what
   it depends on.
2. **Why-GitOps** — one paragraph: why we self-host this stack on
   `arm1-oci` / `bunchloch` instead of using a SaaS.
3. **Cross-references** — links to the originating spec (e.g.
   `cianfhoghlaim-pipeline/spec.md`), the AGENTS.md entry, and the
   upstream docs URL.
4. **Tags** — a `tags: [<space>, <stack-name>, <protocol>]` YAML
   frontmatter for search.

#### Scenario: New stack added

- **WHEN** a developer adds a new stack at `bonneagar/stacks/<new>/`
- **THEN** they SHALL also add `cianfhoghlaim/docs/stacks/<new>.md`
- **AND** the 4 sections (Purpose, Why-GitOps, Cross-references, Tags) SHALL be present
- **AND** the doc SHALL pass the `scripts/stack-doctor.sh --check-stacks-doc` CI gate

#### Scenario: Stack doc missing

- **WHEN** a stack exists at `bonneagar/stacks/<new>/` but no doc exists at `cianfhoghlaim/docs/stacks/<new>.md`
- **THEN** `scripts/stack-doctor.sh` SHALL exit non-zero on CI
- **AND** the PR SHALL fail the gate

### Requirement: stack-doctor.sh CI gate

The system SHALL provide `scripts/stack-doctor.sh` as a CI gate that
checks:

1. Every `bonneagar/stacks/<name>/` has a `cianfhoghlaim/docs/stacks/<name>.md`
2. Every doc has the 4 required sections
3. Every doc's Tags frontmatter is parseable YAML
4. Every doc's Cross-references link to a live spec at `openspec/specs/`
5. Every doc's Purpose doesn't reference `sruth/` or pre-v4 paths

#### Scenario: CI gate failure

- **WHEN** a developer pushes a commit that adds a stack without its doc
- **THEN** the CI pipeline SHALL run `bun run validate-stacks` (which calls `stack-doctor.sh`)
- **AND** exit non-zero with the missing-stack error
- **AND** block the merge

#### Scenario: Pre-v4 path detected

- **WHEN** a doc's Purpose section contains `sruth/` or `bonneagar/stacks/` (the pre-v4 path)
- **THEN** `stack-doctor.sh` SHALL exit non-zero with the `pre-v4-path-detected` error
- **AND** print the offending file + line + the pre-v4 → post-v4 replacement hint

### Requirement: Repo boundary documented in root AGENTS.md

The root `AGENTS.md` SHALL contain a `## Repo Boundary` section
that explicitly lists which directories / files belong to
which of the 3 repos (cianfhoghlaim + bonneagar + leabharlann).

#### Scenario: A new agent reads root AGENTS.md

- **WHEN** an agent reads `AGENTS.md` to understand where to
  add a new component
- **THEN** the agent SHALL be able to identify the canonical
  repo for any of the 3 ownership domains from the
  `## Repo Boundary` section
- **AND** SHALL NOT need to read any other file to make the
  routing decision

#### Scenario: The repo boundary is queried

- **WHEN** an agent searches for `sruth/`, `stacks/`,
  `infrastructure/`, or `leabharlann/` in `AGENTS.md`
- **THEN** the result SHALL reference the correct repo for
  each path (post-v4 consolidation: `sruth/` is gone;
  `stacks/` lives in bonneagar; `leabharlann/` is a worktree)

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) — the 94 stacks at `bonneagar/stacks/`
- [.agents/skills/infrastructure-stacks-documentation](../../.agents/skills/infrastructure-stacks-documentation/SKILL.md) — the agent entry point
- [`data-engineering-pipeline-documentation`](../data-engineering-pipeline-documentation/spec.md) — the docs taxonomy this fits into

## Migrated from: *(none)*
