## MODIFIED Requirements

### Requirement: Marimo notebooks reference canonical post-v4 source namespaces

The system SHALL use canonical post-v4 namespaces for the
Ireland/law data referenced in marimo dashboards.

The marimo dashboards SHALL reference the canonical post-v4 namespaces
when ingesting Ireland/law data, with NO references to the legacy
`cianfhoghlaim.baml.ie.*` or `cianfhoghlaim.dlt.british_isles.ie.*` paths in
the notebook source.

- **BAML** — `cianfhoghlaim.baml.education.law.<schema>`
- **DLT** — `cianfhoghlaim.dlt.british_isles.ireland.education.law.<source>`

#### Scenario: The `ie_law_explorer` notebook points at canonical paths

- **GIVEN** the `notebooks/ie_law_explorer.py` marimo
  notebook
- **WHEN** the notebook reads the Ireland/law BAML extraction rows
- **THEN** the notebook code SHALL reference
  `baml/education/law/*.baml` (canonical)
- **AND** SHALL NOT reference the legacy
  `baml/ie/law/*.baml` path

#### Scenario: A marimo rerun after migration hits the canonical lakehouse tables

- **GIVEN** the DLT→BAML→CocoIndex→LanceDB→MotherDuck pipeline has
  materialised the Ireland/law rows under the canonical
  `cianfhoghlaim.law.ireland.*` schema
- **WHEN** the user reopens the `ie_law_explorer` marimo notebook
- **THEN** the notebook SHALL load the Ireland/law rows from the
  canonical schema (no broken references to the legacy namespaces)

#### Scenario: No legacy `baml.ie` references in any marimo notebook

- **WHEN** a developer runs
  `grep -rn 'baml.ie\.\|baml/ie/' --include='*.py' notebooks/`
- **THEN** zero matches SHALL be returned