## ADDED Requirements

### Requirement: 6 code-locations

The system SHALL load exactly 6 Dagster code-locations in the workspace,
one per sruth that ships Dagster assets (the `crypteolas_demo` app is a
separate code-location from the `crypteolas` library).

#### Scenario: dg list reports 6 code-locations

- **GIVEN** the post-refactor root `dg.toml`
- **WHEN** running `dg list` from the repo root
- **THEN** the output contains exactly: `oideachais`, `meaisinfhoghlaim`,
  `tuatha`, `crypteolas`, `crypteolas_demo`, `croilar`
- **AND** no code-location references the legacy `tuatha/apps/crypteolas_demo`
  path (it is now `sruth/crypteolas/apps/crypteolas_demo`)
- **AND** no code-location references `meaisin_heartbeat` (the correct
  name is `meaisinfhoghlaim`)

#### Scenario: codeolas has no code-location

- **GIVEN** `sruth/codeolas/` is a pure Python library (no Dagster assets)
- **WHEN** checking for a `dg.toml`
- **THEN** `sruth/codeolas/dg.toml` does NOT exist
- **AND** `sruth/codeolas/` is NOT in the root `dg.toml`'s
  `[[workspace.locations]]` list
- **AND** `dg list` does not include `codeolas` as a code-location

### Requirement: Modernized [[workspace.locations]] syntax

The system SHALL use the current Dagster `[[workspace.locations]]` syntax
in the root `dg.toml`, NOT the deprecated `[[workspace.projects]]` syntax.

#### Scenario: Root dg.toml syntax is current

- **GIVEN** the root `dg.toml`
- **WHEN** reading the workspace declaration
- **THEN** the file contains `[[workspace.locations]]` sections
- **AND** no `[[workspace.projects]]` section exists
- **AND** each location entry has the fields: `path`, `code_location_name`
  (or `location_name`), `code_location_module` (or `module_name`) per
  current Dagster docs

### Requirement: Per-sruth dg.toml required

Every sruth that ships Dagster assets SHALL have a `dg.toml` file at
`sruth/<flow>/dg.toml`.

#### Scenario: sruth/oideachais/dg.toml exists

- **GIVEN** the oideachais sruth ships Dagster assets
- **WHEN** reading the file
- **THEN** `sruth/oideachais/dg.toml` exists (CREATED in Phase C of
  `refactor-quadrants-to-sruth/tasks.md`)
- **AND** it declares `module_name = "oideachais.data_platform.dagster_defs.definitions"`
- **AND** it declares `location_name = "oideachais"`
- **AND** it is in the root `dg.toml`'s `[[workspace.locations]]` list
  with `path = "sruth/oideachais"`

#### Scenario: 4 other per-sruth dg.toml files exist with updated paths

- **GIVEN** the meaisinfhoghlaim, tuatha, crypteolas, croilar sruthanna
- **WHEN** reading their `dg.toml` files
- **THEN** `sruth/meaisinfhoghlaim/dg.toml` exists with
  `name = "meaisinfhoghlaim"`, `location_name = "meaisinfhoghlaim"`
- **AND** `sruth/tuatha/dg.toml` exists with `name = "tuath"`
  (5-char), `location_name = "tuath"`
- **AND** `sruth/crypteolas/dg.toml` exists with
  `location_name = "crypteolas"`
- **AND** `sruth/croilar/dg.toml` exists with
  `location_name = "croilar"`

### Requirement: location_name canonical naming

The system SHALL use the canonical Irish-language name for each sruth's
Dagster code-location, NOT abbreviations or heartbeats.

#### Scenario: meaisinfhoghlaim is the canonical location_name

- **GIVEN** the meaisinfhoghlaim sruth's Dagster assets
- **WHEN** reading the `location_name` field
- **THEN** it is `"meaisinfhoghlaim"` (the canonical Irish word for
  "machine learning")
- **AND** it is NOT `"meaisin_heartbeat"` (the latter was an incorrect
  name in one skill file that this refactor corrects)

#### Scenario: tuatha uses 5-char "tuath"

- **GIVEN** the tuatha sruth's Dagster assets
- **WHEN** reading the `name` field in `sruth/tuatha/dg.toml`
- **THEN** it is `"tuath"` (5-char form, NOT `tuatha`)
- **AND** `location_name` is `"tuath"`