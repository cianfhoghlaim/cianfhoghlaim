# pipeline-ciancheiltis-celtic-bilingual Specification

## ADDED Requirements

### Requirement: 5 Celtic-language bilingual pairs + EU-IE dimension

The system SHALL provide bilingual materialised coverage for the
following 5 Celtic-language pairs + 1 EU dimension:

  1. `en-cy` — Welsh (Cymraeg)
  2. `en-gd` — Scottish Gaelic (Gàidhlig)
  3. `en-ga NI` — Irish in Northern Ireland
  4. `en-gv` — Manx (Gaelg)
  5. `en-br` — Breton (Brezhoneg)
  6. `en-ga EU` — Irish at EU institutions

#### Scenario: Every Celtic pair has ≥100 materialised rows

- **WHEN** the `ciancheiltis_dlt:sync-all` mise task runs
- **THEN** every one of the 5 Celtic pairs + the EU dimension MUST
  materialise ≥100 rows within the daily sync window
- **AND** the daily count MUST be visible at the canonical
  `ciancheiltis.celtic_pair_count` MotherDuck Dive card

### Requirement: 6-phase staging

The system SHALL provide the 6-phase staging template applied to
every Celtic jurisdiction:

  Phase 1 — local sources (gov.wales / gov.scot / nidirect / etc.)
  Phase 2 — classification (10-theme taxonomy)
  Phase 3 — BAML extraction
  Phase 4 — CocoIndex embedding
  Phase 5 — Marimo + A2UI surface
  Phase 6 — cross-pipeline integration

#### Scenario: Phase 1 + Phase 2 ship per jurisdiction

- **WHEN** a new Celtic jurisdiction is added
- **THEN** phases 1 + 2 (local sources + classification) MUST be in
  place before any further phase work begins
- **AND** the BAML extraction prompt MUST be reused from the canonical
  `baml_src/ciancheiltis/processing/celtic_pair_extraction.baml` (NOT
  a per-jurisdiction bespoke prompt)

### Requirement: Canonical file layout `dlt_sources/ciancheiltis/`

The system SHALL provide the canonical `dlt_sources/ciancheiltis/`
file layout (sibling to `dlt_sources/british_isles/`) with one
subdirectory per Celtic pair + one `__init__.py` + one `_base.py`.

#### Scenario: New pair follows the canonical layout

- **WHEN** a new Celtic pair is added (e.g. Cornish `en-cornish`)
- **THEN** the developer MUST follow the canonical layout:
  `dlt_sources/ciancheiltis/<pair>/{__init__.py,_base.py,source.py}`
- **AND** the wholesale-copy from `dlt_sources/british_isles/_shared/`
  MUST be cited in the new pair's `_base.py` docstring
