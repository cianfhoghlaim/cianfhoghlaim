# Notebooks Sync Loop (Layer 11)

## Purpose

The Layer 11 of the 11-layer pull-based sync architecture. Validates the 119 notebook files at `notebooks/` (20+ numeric prefixes, 108 `@app.cell` decorators) + closes the last remaining gap in the sync loop.

The 10-layer architecture (Layers 1–10) covered 13 of the 14 knowledge surfaces:

| Layer | Task | Surface |
|:--|:--|:--|
| 1 | sync:paths | file paths |
| 2 | sync:ccc | code + openspec + skills (via 21st concept guide) |
| 3 | sync:cognee | 14 clusters |
| 4 | sync:skills | 157 skills |
| 5 | sync:mcp | MCP servers |
| 6 | sync:dagster | Dagster assets |
| 7 | sync:baml | 320 .baml files |
| 8 | sync:stacks | 87 IaC stacks |
| 9 | sync:dlt | 1903 DLT sources |
| 10 | sync:agents | 188 agent files |

**Not yet covered** (1 surface):

- **Notebook files** (119 files at `notebooks/`, 20+ numeric prefixes, 108 `@app.cell` decorators) — the **only** surface still without automated health validation. Every BIEP per-subject notebook + every marimo dashboard + every dev-env demo + every educational stage notebook flows through this surface, so drift in `notebooks/` propagates silently into the public web app (`web/apps/cianfhoghlaim-web/`) + the 6 BIEP per-subject dashboards + the 12 speedrun notebooks.

This change extends the sync loop with **Layer 11 — `sync:notebooks`** that closes the notebooks gap.

## Requirements

### Requirement: Layer 1 — sync:notebooks-drift

The system SHALL provide a `bash scripts/sync/notebooks-drift.sh` task that detects notebook registration drift across the 119 notebook files at `notebooks/`.

#### Scenario: Notebook drift detection runs cleanly

- **WHEN** `bash scripts/sync/notebooks-drift.sh` is invoked
- **THEN** the task SHALL scan all 119 files matching `notebooks/[0-9]*_*.py`
- **AND** the task SHALL detect:
  - Notebooks not registered in `notebooks/cli.py` GROUPS
  - Broken `@app.cell` decorators (AST parse failure)
  - Missing entry points (no `@app.cell` or `app = marimo.App(...)` lines)
  - Stale schema references (e.g. `md:oideachais` after the v7 rename to `md:cianfhoghlaim`)
- **AND** the task SHALL write a per-file report to
  `stedding/sync-reports/notebooks-drift-{date}.md`

### Requirement: Layer 2 — sync:notebooks-ccc

The system SHALL provide a `bash scripts/sync/notebooks-ccc.sh` task that refreshes the CCC index + appends the **26th concept guide** `notebook-search` to `.cocoindex_code/guides.yml`.

#### Scenario: 26th concept guide surfaces the notebook fleet

- **WHEN** `bash scripts/sync/notebooks-ccc.sh` is invoked
- **THEN** the task SHALL append the `notebook-search` guide
  to `.cocoindex_code/guides.yml`
- **AND** the task SHALL run `bun run ccc:index` for incremental refresh
- **AND** a user searching CCC for "BIEP pipeline lakehouse notebook"
  SHALL get the new guide in the top 3 hits

### Requirement: Layer 3 — sync:notebooks-cognee

The system SHALL provide a `bash scripts/sync/notebooks-cognee.sh` task that ingests the 119 notebook files into the **15th Cognee cluster** `notebooks`.

#### Scenario: Cognee has 15 typed clusters after sync

- **WHEN** `cognee-mcp` is queried for the cluster list
- **THEN** the response SHALL include all 15 typed clusters
  (14 existing + `notebooks`)

#### Scenario: Notebooks Cognee cluster grows over time

- **WHEN** `bash scripts/sync/notebooks-cognee.sh` is invoked
- **THEN** the task SHALL ingest the 119 notebook files
- **AND** the cluster SHALL have a per-notebook summary

### Requirement: Layer 4 — sync:notebooks-test

The system SHALL provide a `bash scripts/sync/notebooks-test.sh` task that runs the notebook import test + reports which notebooks are properly importable.

#### Scenario: Notebook import test runs

- **WHEN** `bash scripts/sync/notebooks-test.sh` is invoked
- **THEN** the task SHALL report per-prefix notebook counts
- **AND** the task SHALL write a per-prefix report to
  `stedding/sync-reports/notebooks-test-{date}.md`
- **AND** the task SHALL document the manual `uv run python -c "import notebooks.X"` flow

### Requirement: Layer 5 — sync:notebooks-lint

The system SHALL provide a `bash scripts/sync/notebooks-lint.sh` task that reports per-prefix stats + the canonical `notebooks/_shared/` helpers + the `notebooks/cli.py` registry.

#### Scenario: Per-prefix stats

- **WHEN** `bash scripts/sync/notebooks-lint.sh` is invoked
- **THEN** the task SHALL produce a per-prefix report to
  `stedding/sync-reports/notebooks-lint-{date}.md`
- **AND** the task SHALL show the per-prefix .py file counts +
  the `@app.cell` decorator counts + the 3 canonical helpers

### Requirement: Layer 6 — sync:notebooks orchestrator

The system SHALL provide a `bash scripts/sync/notebooks.sh` task that runs all 5 layers in sequence.

#### Scenario: sync:notebooks orchestrator runs all 5 layers

- **WHEN** `bash scripts/sync/notebooks.sh` is invoked
- **THEN** the task SHALL run sync:notebooks-drift + sync:notebooks-ccc +
  sync:notebooks-cognee + sync:notebooks-test + sync:notebooks-lint
  in sequence
- **AND** the task SHALL write a unified report to
  `stedding/sync-reports/notebooks-{date}.md`

### Requirement: Notebooks evolution feedback loop

The system SHALL grow its knowledge surface over time via the
notebooks evolution feedback loop.

#### Scenario: Notebook file change triggers re-cognify

- **WHEN** a file under `notebooks/` is modified
- **THEN** the next `sync:notebooks-cognee` SHALL detect the change
  (via file mtime comparison)
- **AND** the task SHALL re-cognify the modified file into the
  `notebooks` Cognee cluster
- **AND** the task SHALL update the 26th CCC concept guide