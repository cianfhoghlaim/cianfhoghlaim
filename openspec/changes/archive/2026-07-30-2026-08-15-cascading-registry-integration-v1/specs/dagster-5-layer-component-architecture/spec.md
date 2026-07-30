# Spec delta: `dagster-5-layer-component-architecture`

This delta is part of the openspec change
`2026-08-15-cascading-registry-integration-v1`. It updates the
5-layer Dagster Component Architecture to reference the 10
`JurisdictionAssetsBase` subclasses.

## ADDED Requirements

### Requirement: Dagster 5-layer architecture MUST reference the 10 JurisdictionAssetsBase subclasses

The system SHALL update `openspec/specs/dagster-5-layer-component-architecture/spec.md`
to reference the 10 `JurisdictionAssetsBase` subclasses at
`orchestration/defs/2_materials/_base/<jurisdiction>_assets.py`. Each
emits one canonical `<jurisdiction>_documents_ingested` Dagster asset
backed by the corresponding `<jurisdiction>_jurisdiction_pipeline`.

#### Scenario: Dagster definitions.py loads the 10 jurisdiction assets

- **GIVEN** the 10 `JurisdictionAssetsBase` subclasses created in commits
  `4ea9c1eed` + `64659a6ad`
- **WHEN** `mise run dagster:dev` launches
- **THEN** the 10 assets (`ireland_documents_ingested`, `england_documents_ingested`, etc.) appear in the Dagster UI
- **AND** they are registered in `orchestration/definitions.py` via the "Jurisdiction-level ingestion assets" section

#### Scenario: The 5-layer architecture registers the 3 CocoIndex factories

- **GIVEN** the 3 CocoIndex factory L3 Component `defs.yaml` files at:
  - `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_factory/defs.yaml`
  - `orchestration/defs/3_model_lifecycle/cocoindex_v1/ireland_lc_factory/defs.yaml`
  - `orchestration/defs/3_model_lifecycle/cocoindex_v1/biep_parity_factory/defs.yaml`
- **WHEN** the Dagster `dg.load_defs()` walks the tree
- **THEN** the 3 factory components emit their 40 + 11 + 8 = 59 Apps
- **AND** each factory's Apps conform to R1+R2+R3+R4
