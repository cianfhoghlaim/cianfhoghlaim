## MODIFIED Requirements

### Requirement: DLT Skill and Dependency Currency

The system SHALL use the latest dlt release available on PyPI (currently
1.29.x) and SHALL adopt each major version's recommended patterns within
two weeks of release.

#### Scenario: dlt dependency pins `hub` extra

- **WHEN** any developer runs `uv pip install -e .`
- **THEN** `dlt` is installed with extras `duckdb,motherduck,filesystem,hub`
- **AND** `dlthub` CLI is available at `.venv/bin/dlthub`
- **AND** `dlt` CLI is available at `.venv/bin/dlt`

#### Scenario: dlt skill reflects current version

- **WHEN** a future agent loads `.agents/skills/dlt/SKILL.md`
- **THEN** the version field in the frontmatter matches `dlt.__version__`
- **AND** the live-features list includes everything from the latest 2
  releases

#### Scenario: write_disposition='replace' is deprecated

- **WHEN** any source file under `dlt_sources/` contains
  `write_disposition='replace'`
- **THEN** `tests/dlt/test_curated_sources.py::test_write_disposition_replace_audit`
  fails with the list of offending files
- **AND** the test output links to the per-source migration guide in
  the skill

#### Scenario: Curated source catalog matches CLI

- **WHEN** `uv run python -m dlt_sources.cli list-sources` runs
- **THEN** the output matches `CURATED_SOURCE_PATHS` in
  `tests/dlt/test_curated_sources.py`
- **AND** each source's file path resolves under `dlt_sources/`
