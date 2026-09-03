# Requirements

> **MODIFIED** by `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/`.

The pre-v7 "4 canonical ops dirs" line was
`(bonneagar/, cianfhoghlaim/assets/, cianfhoghlaim/docs/stacks/, bonneagar/komodo/)`.
Post-v7, the `cianfhoghlaim/` prefix is dropped (the package is the
repo root), so this collapses to
`(bonneagar/, assets/, docs/stacks/, bonneagar/komodo/)`.

## ADDED Requirements

### Requirement: 4 canonical ops dirs at repo root

The system SHALL maintain the 4 canonical ops dirs at the repo root:
- `bonneagar/` — the IaC (88 stacks + Komodo resource-syncs +
  Pangolin config + the unified TypeScript IaC at
  `bonneagar/iac/`)
- `assets/` — the Dagster asset generation (formerly
  `cianfhoghlaim/assets/`)
- `docs/stacks/` — the per-stack operational docs
- `bonneagar/komodo/` — the Komodo resource-syncs + procedures
  + stacks

#### Scenario: The 4 canonical ops dirs are at the repo root

- **WHEN** a developer lists the repo root via `ls -1`
- **THEN** the 4 dirs SHALL be present
- **AND** the IaC content SHALL live under `bonneagar/`
- **AND** the Dagster assets SHALL live under `assets/`
- **AND** `docs/stacks/` SHALL hold the per-stack READMEs
- **AND** the Komodo resource-syncs SHALL live under
  `bonneagar/komodo/resource-syncs/`

### Requirement: Per-area READMEs are at the repo root

The per-area READMEs (`README.md`, `AGENTS.md`) SHALL be at the
repo root for the top-level project, plus one per major
sub-package (`agents/`, `baml/`, `dlt/`, `orchestration/`,
`web/`, `bonneagar/`).

#### Scenario: Per-area READMEs are findable

- **WHEN** a developer looks for the README of a sub-package
- **THEN** it SHALL be at `<sub-package>/README.md`
- **AND** the top-level README SHALL be at `./README.md`
- **AND** the top-level AGENTS.md SHALL be at `./AGENTS.md`

## ADDED Requirements

### Requirement: NEW — Single-repo + bonneagar/ subdir reality

The data-engineering pipeline documentation SHALL reflect the v7
single-repo + bonneagar-subdir reality:
- The repo root IS the Python package (post-v7 flatten)
- The IaC is at `bonneagar/` (NOT a separate repo)
- `leabharlann` is the only remaining separately-managed repo
  (NOT part of this repo)

#### Scenario: Docs reflect v7 reality

- **WHEN** a developer reads `README.md` or `AGENTS.md`
- **THEN** the "Repository constellation" section SHALL list
  exactly 2 repos: cianfhoghlaim + leabharlann
- **AND** it SHALL mention that the IaC lives at `bonneagar/` in
  this repo
- **AND** it SHALL NOT claim bonneagar is a separate GitHub repo
