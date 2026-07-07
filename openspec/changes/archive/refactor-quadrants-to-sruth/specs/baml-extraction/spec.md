## ADDED Requirements

### Requirement: Per-sruth baml_src/ directory

The system SHALL keep BAML extraction schemas inside each sruth's own
`baml_src/` directory.

#### Scenario: 5 per-sruth baml_src/ directories exist

- **GIVEN** the post-refactor filesystem
- **WHEN** running `ls -d sruth/*/baml_src/`
- **THEN** the output contains `sruth/oideachais/baml_src/`,
  `sruth/meaisinfhoghlaim/baml_src/`, `sruth/tuatha/baml_src/`,
  `sruth/croilar/baml_src/`, `sruth/crypteolas/baml_src/`
- **AND** `sruth/codeolas/baml_src/` does NOT exist (codeolas is
  pure Python; no BAML)

#### Scenario: No root baml_src/

- **GIVEN** the refactor is complete
- **WHEN** running `ls baml_src/`
- **THEN** the command fails with "No such file or directory"
- **AND** the root `baml_src/` directory is gone

### Requirement: 3 BAML merge rules

The system SHALL merge any `.baml` file that exists at both `baml_src/<name>.baml` and `sruth/oideachais/baml_src/<name>.baml` (with optional `_0.baml` variant) into a single `sruth/oideachais/baml_src/<name>.baml`, preserving all `client` blocks and class definitions. The merged file MUST contain every `client <Name> { ... }` block from all source files (no client blocks lost; duplicate client names deduplicated with a `_v2` suffix on the duplicate).

#### Scenario: clients.baml merge

- **GIVEN** the 3 source files `baml_src/clients.baml` +
  `sruth/oideachais/baml_src/clients.baml` +
  `sruth/oideachais/baml_src/clients_0.baml`
- **WHEN** merging
- **THEN** the resulting `sruth/oideachais/baml_src/clients.baml`
  contains all `client <Name> { ... }` blocks from all 3 sources
- **AND** duplicate client names are deduplicated with `_v2` suffix
- **AND** the merge is verified by `python -c "import baml_py; baml_py.parse('sruth/oideachais/baml_src/clients.baml')"`

#### Scenario: curriculum_extraction.baml merge

- **GIVEN** the 3 source files `baml_src/curriculum_extraction.baml` +
  `sruth/oideachais/baml_src/curriculum_extraction.baml` +
  `sruth/oideachais/baml_src/curriculum_extraction_0.baml`
- **WHEN** merging
- **THEN** the resulting `sruth/oideachais/baml_src/curriculum_extraction.baml`
  contains all `class <Name> { ... }` definitions from all 3 sources
- **AND** the BAML client regen succeeds (`uv run python -m baml_py generate`)

#### Scenario: official_media.baml merge

- **GIVEN** the 2 source files `baml_src/official_media.baml` +
  `sruth/oideachais/baml_src/official_media.baml`
- **WHEN** merging
- **THEN** the resulting `sruth/oideachais/baml_src/official_media.baml`
  contains all extraction classes from both sources

### Requirement: gaois/ BAML files in sruth/meaisinfhoghlaim

The system SHALL move the 4 gaois BAML files (`duchas.baml`,
`folklore_extraction.baml`, `logainm.baml`, `tearma.baml`) from
`sruth/oideachais/baml_src/gaois/` to
`sruth/meaisinfhoghlaim/baml_src/gaois/` because they are AI/ML
extraction schemas (gaois = gaois.ie, the Irish terminology
resource).

#### Scenario: gaois/ migrated to meaisinfhoghlaim

- **GIVEN** the 4 gaois BAML files
- **WHEN** checking their filesystem location
- **THEN** they live at `sruth/meaisinfhoghlaim/baml_src/gaois/{duchas,folklore_extraction,logainm,tearma}.baml`
- **AND** no copy of these files exists at
  `sruth/oideachais/baml_src/gaois/` or `sruth/oideachais/baml_src/`

### Requirement: LitellmClient per sruth

Each sruth that uses BAML SHALL declare its own `LitellmClient`
routing block that points to the gateway at
`http://litellm.cianfhoghlaim.ie`.

#### Scenario: sruth/oideachais/clients.baml LitellmClient

- **GIVEN** `sruth/oideachais/baml_src/clients.baml`
- **WHEN** reading the `client` blocks
- **THEN** at least one `client` block declares
  `base_url = "http://litellm.cianfhoghlaim.ie"`
- **AND** the `api_key` references the `LITELLM_API_KEY` env var
- **AND** the `model` is one of the 5 KCG model identifiers
  (`kimi-k2.6`, `glm-5.1`, `minimax-m2.5`, `mimo-v2.5`, `deepseek-v4-flash`)

#### Scenario: sruth/meaisinfhoghlaim/clients.baml LitellmClient

- **GIVEN** `sruth/meaisinfhoghlaim/baml_src/clients.baml` (NEW — created
  in Phase D of the refactor by merging the relevant LitellmClient blocks
  from the moved BAML files)
- **WHEN** reading the `client` blocks
- **THEN** the same LitellmClient contract as the oideachais one applies