## MODIFIED Requirements

### Requirement: British Isles Subject Registry is canonical (BIEP v3)

The system SHALL provide a canonical British Isles subject registry
stored in DuckDB as 3 tables under the
`cianfhoghlaim.education._registry` schema:

- `subjects` — every (jurisdiction, stage, subject_slug, board,
  qualification_level, language) tuple across all 8 British Isles
  jurisdictions
- `jurisdiction_overrides` — per-jurisdiction field overrides
- `cross_jurisdiction_bridges` — slug mappings between jurisdictions
  (e.g. Ireland `gaeilge` ↔ Northern Ireland `irish`)

Every BIEP v3 jurisdiction pipeline (Phases 2-5) MUST query the
registry to discover which subjects to materialise (no per-subject
Python files).

#### Scenario: Registry has 12 seeded cross-jurisdiction bridges

- **WHEN** the migration `2026-07-27-cianfhoghlaim-subject-registry.sql` is applied
- **THEN** `query_cross_jurisdiction_bridges()` returns 12 bridges
  (MATHEMATICS, ENGLISH, BIOLOGY, CHEMISTRY, PHYSICS, HISTORY,
  GEOGRAPHY, COMPUTER_SCIENCE, FRENCH, GERMAN, SPANISH, IRISH_LANGUAGE,
  BUSINESS_STUDIES) — the 10 core concepts + 2 jurisdiction-specific bridges

#### Scenario: Companion notebook renders all 4 tabs

- **WHEN** `marimo edit notebooks/18_cianfhoghlaim_subject_registry.py`
  is run
- **THEN** all 4 tabs render against the live registry:
  - Tab 1 (Format doc): BAML schema + DuckDB table descriptions
  - Tab 2 (Nation comparison): subject count by jurisdiction
  - Tab 3 (Bridge explorer): concept multiselect → matching rows
  - Tab 4 (Drift detector): static status table + invocation command

#### Scenario: Canonical pipeline namespace shape

- **WHEN** a jurisdiction pipeline writes a LanceDB table
- **THEN** the table name SHALL match the canonical shape
  `cianfhoghlaim.education.<jurisdiction>.<stage>[.<board>].<subject>[.<variant>]`
- **AND** the same shape SHALL be used for DuckLake namespaces
- **AND** the same shape SHALL be used for the Dagster 2-axis partition
  scope (`<jurisdiction>__<stage>__<subject>__<board>__<qualification_level>__<language>`)