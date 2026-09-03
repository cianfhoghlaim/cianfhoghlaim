## MODIFIED Requirements

### Requirement: 8 per-subject CocoIndex Apps → 1 parameterised

The system SHALL provide a single parameterised CocoIndex v1 App
`cocoindex/subjects/lc_subject_embedding.py` that drives all 6 LC subjects
via `cocoindex/subjects/lc_subject_config.yaml`. The 7 deprecated
per-subject `<subject>_embedding.py` files SHALL be removed and the
canonical surface SHALL be the parameterised flow + the unchanged
`cross_subject_competency_embedding.py`.

#### Scenario: CocoIndex v1 app count is 2 (parameterised + cross-subject)

- **WHEN** `dg list code-locations` runs after the dedup
- **THEN** exactly **2** CocoIndex v1 apps are listed for the LC subjects:
  `lc_subject_embedding` (parameterised, drives 6 subjects) +
  `cross_subject_competency_embedding` (genuinely different)
- **AND** the 7 deprecated per-subject `<subject>_embedding.py` files are deleted

#### Scenario: LanceDB table names preserved

- **GIVEN** the existing `oideachais.lc.mathematics.hl_en` LanceDB table
  was populated by the deprecated `cocoindex/subjects/mathematics_embedding.py`
- **WHEN** the parameterised `lc_subject_embedding.py` runs with subject=mathematics
- **THEN** the same `oideachais.lc.mathematics.hl_en` table MUST be populated
  (zero data migration required)

#### Scenario: 6 LC subject rows in the YAML config

- **WHEN** the 6 LC subjects (mathematics, chemistry, geography, english,
  gaeilge, computer_science) need materialisation
- **THEN** the `lc_subject_config.yaml` MUST list all 6 with their
  canonical `dagster_asset_key` mapping
- **AND** the parameterised flow MUST drive each from a single config row