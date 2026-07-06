## MODIFIED Requirements

### Requirement: Documentation must reflect current v4 structure

The system SHALL keep `.agents/skills/`, `openspec/`, and
`cianfhoghlaim/notebooks/` documentation aligned with the v4-consolidated
`cianfhoghlaim/` package layout (post-2026-06-28 consolidation). All
references to pre-v4 paths (`sruth/<quadrant>/...`,
`sruth/<quadrant>/AGENTS.md`, `sruth/<quadrant>/README.md`,
`sruth/<quadrant>/dlt_sources/...`, `sruth/<quadrant>/baml_src/...`,
`sruth/<quadrant>/dagster_defs/...`, `sruth/<quadrant>/web/...`,
`sruth/<quadrant>/agents/...`, `infrastructure/stacks/...` after v4 moved
to `bonneagar/stacks/`, `infisical://dev-baile/sruth/...` after v4 dropped
the `sruth/` segment, `1Password op://` after the 2026-06 Infisical
migration, `oideachais.data_platform.*` after v4) SHALL be rewritten to the
post-v4 equivalents.

#### Scenario: Skills reflect v4 paths

- **WHEN** an agent reads `.agents/skills/dlt/SKILL.md`
- **THEN** the body references `cianfhoghlaim/dlt/` (NOT
  `sruth/oideachais/dlt_sources/`)
- **AND** the `frontmatter.description:` does not contain `sruth/oideachais`

#### Scenario: OpenSpec specs reflect v4 paths

- **WHEN** an agent reads `openspec/specs/oideachais-pipeline/spec.md`
- **THEN** the body references `cianfhoghlaim/orchestration/`,
  `cianfhoghlaim/dlt/`, `cianfhoghlaim/baml/`, `cianfhoghlaim/cocoindex/`
  (NOT `sruth/oideachais/dagster_defs/`, `sruth/oideachais/dlt_sources/`,
  `sruth/oideachais/baml_src/`, `sruth/oideachais/cocoindex_flows/`)

#### Scenario: OpenSpec `infrastructure-stacks` reflects `bonneagar/stacks/`

- **WHEN** an agent reads `openspec/specs/infrastructure-stacks/spec.md`
- **THEN** every reference to `infrastructure/stacks/<x>` has been rewritten
  to `bonneagar/stacks/<x>`

#### Scenario: Notebooks use post-v4 stack

- **WHEN** an agent reads a notebook under `cianfhoghlaim/notebooks/`
- **THEN** the notebook either has PEP 723 inline deps OR uses `marimo.App`
  with `@app.cell` reactive cells
- **AND** the notebook reads from `md:oideachais.*` via
  `mo.sql(engine=md:oideachais)` (NOT raw CSV paths or hardcoded
  `/Users/cianmacandeisigh/...` paths)
- **AND** the notebook does NOT contain hardcoded Garage access keys or
  PostgreSQL `devpassword` defaults

#### Scenario: Secrets management uses Infisical

- **WHEN** an agent reads `.agents/skills/secrets-management/SKILL.md`
- **THEN** all Infisical URI references use `infisical://dev-baile/oideachais/...`
  (NOT `infisical://dev-baile/sruth/oideachais/...`)

### Requirement: Notebooks follow the canonical marimo + DuckDB + Ibis + CocoIndex + DuckLake + LanceDB pattern

The system SHALL ensure that every notebook under `cianfhoghlaim/notebooks/`
follows the canonical pattern. Each notebook MUST be a marimo reactive
Python file (`.py` with `app = marimo.App(...)`), MUST have PEP 723 inline
deps at the top, MUST read lakehouse tables via `mo.sql(engine=md:oideachais)`
for federated DuckDB + LanceDB queries, MUST use DuckDB + Ibis (NOT
pandas-only analytics for non-trivial work), MUST read filesystem paths
from environment variables, MUST NOT hardcode secrets, and MUST wire to
live lakehouse tables where the source data exists.

#### Scenario: Notebooks follow the canonical pattern

- **WHEN** the agent runs `marimo parse <notebook>` on every file in
  `cianfhoghlaim/notebooks/`
- **THEN** the parse succeeds for all marimo notebooks
- **AND** the parse succeeds for the empty `leaving_certificate.ipynb`
  (or it is deleted)

### Requirement: Skills reflect the British-Isles Education pipeline goals

The system SHALL ensure that the skills most directly tied to the
British-Isles Education pipeline (`dlt`, `baml`, `cocoindex`, `dagster`,
`marimo`, `motherduck`, `duckdb`, `ducklake`, `ibis`, `lancedb`,
`agent-fleet-orchestration`, `agent-memory-systems`, `agent-observability`)
call out the British-Isles Education pipeline goals (6 LC subjects +
gov.ie circulars + Garage S3 PDF storage + LanceDB embeddings + DuckLake
extraction + DuckDB analytics + MotherDuck Dives) in their canonical
"When to use" sections. The skills MUST mention at least 3 of the 6 LC
subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer
Science) in their canonical example blocks.

#### Scenario: Skills reference the 6 LC subjects

- **WHEN** an agent reads `.agents/skills/dlt/SKILL.md`
- **THEN** the "When to use" or "Examples" section references at least 3 of
  the 6 LC subjects (Mathematics, Chemistry, Geography, Gaeilge, English,
  Computer Science) as a primary use case

### Requirement: Drift-cleanup removes redundant skills, openspec changes, and notebooks

The system SHALL keep `.agents/skills/`, `openspec/changes/`, and
`cianfhoghlaim/notebooks/` pruned of redundant entries. Archived openspec
changes MUST be moved to `openspec/changes/archive/` (via
`openspec archive <id> --yes`). Phantom-spec rows in `openspec/AGENTS.md`
and `openspec/project.md` MUST be removed.

#### Scenario: Stale openspec changes are archived

- **WHEN** `openspec list` is run after the drift-cleanup change
- **THEN** the 30 changes listed as "ready to ARCHIVE" in the
  `2026-07-06-drift-cleanup-and-v4-alignment` proposal have been moved
  to `openspec/changes/archive/`

#### Scenario: Phantom-spec rows are removed from AGENTS.md + project.md

- **WHEN** the user searches for `celtic-data-engineering-pipeline` or
  `gradio-ensemble-pattern` in `openspec/AGENTS.md` or `openspec/project.md`
- **THEN** no rows reference these phantom specs (they either have a
  real `openspec/specs/<name>/spec.md` or are removed entirely)