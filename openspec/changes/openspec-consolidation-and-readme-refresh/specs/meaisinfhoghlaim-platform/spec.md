## ADDED Requirements

The `meaisinfhoghlaim-platform` capability is the first openspec spec
for the meaisinfhoghlaim quadrant. The full Requirements + Scenarios
are in the canonical spec at
`openspec/specs/meaisinfhoghlaim-platform/spec.md`.

### Requirement: 10 sub-packages

The system SHALL declare 10 sub-packages in
`meaisinfhoghlaim/pyproject.toml [tool.hatch.build.targets.wheel].packages`:
`agents`, `ocr`, `language`, `pipelines`, `alignment`, `evaluation`,
`quality`, `catalog`, `scripts`, `services`.

#### Scenario: Sub-packages import

- **WHEN** a user runs `uv run python -c "from meaisinfhoghlaim.agents import curriculum_agent"`
- **THEN** the import succeeds

### Requirement: 4 heartbeat assets

The system SHALL register 4 heartbeat assets in the
`meaisin_heartbeat` Dagster group.

#### Scenario: Heartbeat assets pass

- **WHEN** the 4 heartbeat assets materialise
- **THEN** all 4 succeed (smoke test that the 4 sub-package imports work)

### Requirement: Dagster code-location registration

The system SHALL register meaisinfhoghlaim as a Dagster code-location
in the root `dg.toml`.

#### Scenario: Code-location loads

- **WHEN** `dg dev` starts the Dagster UI
- **THEN** the meaisinfhoghlaim code-location appears in the UI

### Requirement: Cross-quadrant ingestion from oideachais DuckLake

The system SHALL ingest from the oideachais DuckLake catalog.

#### Scenario: Lakehouse to meaisinfhoghlaim ingest

- **WHEN** a meaisinfhoghlaim agent (e.g. `corpus_agent`) is invoked
- **THEN** the agent reads the leabharlann rows from DuckLake

### Requirement: Celtic-language model catalog

The system SHALL maintain a Celtic-language model catalog at
`meaisinfhoghlaim/catalog/models.yaml`.

#### Scenario: Model catalog is valid YAML

- **WHEN** the `meaisinfhoghlaim/catalog/models.yaml` file is loaded
- **THEN** the file parses without errors
