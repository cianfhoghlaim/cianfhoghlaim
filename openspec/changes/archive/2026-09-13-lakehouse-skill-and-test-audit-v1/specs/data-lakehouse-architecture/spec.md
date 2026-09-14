## ADDED Requirements

### Requirement: Lakehouse Skill Currency

The system SHALL keep the Lakehouse skills (ducklake, lancedb, motherduck) aligned with the actual destination code location (dlt_sources/common/) and the 99 bonneagar production stacks.

#### Scenario: Bonneagar has ≥ 50 production stacks

- **WHEN** any developer runs `uv run pytest tests/lakehouse/`
- **THEN** `bonneagar/stacks/` contains ≥ 50 directories
- **AND** the canonical `lakehouse/` stack exists with `compose.yaml`

#### Scenario: Destination code is at dlt_sources/common/

- **WHEN** any developer runs `uv run pytest tests/lakehouse/`
- **THEN** `dlt_sources/common/destinations_cianfhoghlaim.py` exists
- **AND** `dlt_sources/common/named_destinations.py` exists
- **AND** `dlt_sources/common/motherduck_options.py` exists

#### Scenario: All 3 lakehouse skills exist

- **WHEN** any developer runs `uv run pytest tests/lakehouse/`
- **THEN** `.agents/skills/{ducklake,lancedb,motherduck}/SKILL.md` all exist

#### Scenario: dlt has motherduck extra installed

- **WHEN** `uv pip show dlt` is run
- **THEN** it succeeds and shows the dlt installation
- **AND** duckdb is listed as a dependency (bundled with motherduck extra)

#### Scenario: MOTHERDUCK_TOKEN env var is documented

- **WHEN** the docs are checked
- **THEN** `docs/INTEGRATIONS_INDEX.md` (or equivalent) references `MOTHERDUCK_TOKEN` as a required env var
