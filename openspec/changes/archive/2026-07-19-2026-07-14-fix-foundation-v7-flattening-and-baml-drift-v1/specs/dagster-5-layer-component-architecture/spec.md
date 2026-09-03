# Spec delta — `dagster-5-layer-component-architecture` — ADDED Requirement: canonical v7 flattened package layout

> This file is the spec delta for the change
> `2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1`. Apply by
> merging the ADDED Requirements block below into
> `openspec/specs/dagster-5-layer-component-architecture/spec.md`.

## ADDED Requirements

### Requirement: Canonical v7 flattened package layout

The system SHALL treat the repository root as the canonical location of the
`cianfhoghlaim` Python package. Every `from cianfhoghlaim.X import Y` import
SHALL resolve against the flat repo-root layout — there SHALL NOT be a
separate `cianfhoghlaim/` subdirectory containing the package source.

The package marker files (`__init__.py`, `__main__.py`, `__deployment__.py`,
`cli.py` for the cianfhoghlaim CLI) SHALL live at the repository root and
SHALL use the `__double_underscore__` naming convention so they sort first in
directory listings.

The top-level sub-directories SHALL serve as `cianfhoghlaim` sub-modules
either by (a) carrying an `__init__.py` (regular package) or (b) relying on
Python 3.12+ implicit namespace package semantics. The following
directories SHALL be importable as `cianfhoghlaim.<name>`:

- `agents/` → `cianfhoghlaim.agents`
- `baml_src/` → `cianfhoghlaim.baml_src`
- `bonneagar/` → `cianfhoghlaim.bonneagar`
- `cocoindex/` → `cianfhoghlaim.cocoindex`
- `dlt/` → `cianfhoghlaim.dlt`
- `meaisinfhoghlaim/` → `cianfhoghlaim.meaisinfhoghlaim`
- `notebooks/` → `cianfhoghlaim.notebooks`
- `orchestration/` → `cianfhoghlaim.orchestration`

The web and spaces directories SHALL NOT be part of the Python package
(the web/ sub-tree is bun-managed; spaces/ is a separate project with its own
`pyproject.toml`).

The Dagster code-location entry point SHALL be
`orchestration.definitions` (the file `orchestration/definitions.py` at the
repository root). The historical path `cianfhoghlaim.dagster.definitions`
SHALL NOT be the entry point. Any `from cianfhoghlaim.dagster.X import Y`
import in test code or documentation SHALL be rewritten to
`from orchestration.X import Y`.

#### Scenario: uv sync succeeds

- **WHEN** the user runs `uv sync` from the repository root
- **THEN** uv SHALL resolve all dependencies (including dagster >= 1.13, duckdb >= 1.4, cocoindex >= 1.0,<2.0,!=1.0.8, lancedb >= 0.15)
- **AND THEN** exit 0

#### Scenario: Python imports resolve

- **WHEN** the user runs `python -c "from cianfhoghlaim.dlt.common.cli import main"`
- **THEN** the import SHALL succeed
- **AND THEN** the resolution path SHALL be `orchestration/...` or `dlt/...` at the repo root (NOT from a non-existent `cianfhoghlaim/` subdirectory)

#### Scenario: Dagster code-location loads

- **WHEN** the user runs `mise run cic:dagster:dev`
- **THEN** Dagster SHALL load the 5-layer component architecture from the
  `orchestration/defs/` directory tree
- **AND THEN** the code location SHALL report 199 assets + 31 jobs + 6 schedules + 16 sensors + 22 asset checks

#### Scenario: Dagster module-name canonical

- **WHEN** the user reads `dg.toml`
- **THEN** the `module_name` field SHALL equal `orchestration.definitions`
- **AND THEN** the `mise.toml:138` `cic:dagster:dev` task body SHALL run
      `uv run dagster dev -m orchestration.definitions`
