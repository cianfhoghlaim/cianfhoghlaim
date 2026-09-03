## ADDED Requirements

### Requirement: M1-M4 milestones do not trigger deferred L3 assets

The `mise run biep:v3:m0..m4` milestone entrypoints SHALL NOT trigger
any L3 asset that has `automation_condition: Manual()` (the cognify +
federated_ocr subset). This is the canonical BIEP v3 "happy path"
contract — the lakehouse + BIEP layers L1-L2 + L4-L5 are sufficient
for the 12 Ireland LC cohorts + 88 Ireland JC cohorts + 147 England
A-Level + 129 England GCSE assets.

The L3 cognify + federated_ocr assets are reserved for the deferred
deliverables (per the open openspec change
`bring-cognify-stack-to-lakehouse-cluster`).

#### Scenario: M1 (Ireland LC) does not trigger L3 cognify assets

- **WHEN** `mise run biep:v3:m1` runs
- **THEN** the materialisation set contains 12 Ireland LC cohort assets
- **AND** zero `3_model_lifecycle/cognify/*` assets
- **AND** zero `3_model_lifecycle/federated_ocr/*` assets
- **AND** the 3 asset checks (`ireland_lc_documents_ingested_check`, `ireland_lc_extractions_ragas_check`, `ireland_lc_lance_chunks_check`) pass

#### Scenario: M2 (Ireland JC) does not trigger L3 cognify assets

- **WHEN** `mise run biep:v3:m2` runs
- **THEN** the materialisation set contains the 140 Ireland JC cohort assets
- **AND** zero `3_model_lifecycle/cognify/*` assets
- **AND** the milestone exits 0

### Requirement: The 3 L3 cognify assets + 1 L3 federated_ocr asset are documented as deferred

The system MUST document the 3 L3 components (`KCGCognifyComponent`,
`CognifyIngestSensorsComponent`, `CelticFederatedOcrComponent`) in their
respective Component docstrings as "deferred to the cognify stack
bringup openspec change". Operators discover their deferred status via
the new `scripts/dagster_load_smoke.py` companion (which prints the
manual-only badges).

#### Scenario: The L3 cognify assets are tagged manual-only in Dagster

- **WHEN** `dg list defs --json | jq '.[] | select(.key | startswith("3_model_lifecycle/cognify")) | .automation_condition' | sort -u` runs
- **THEN** the output is `["manual"]` (the only automation condition across the cognify assets)

#### Scenario: The L3 federated_ocr asset is tagged manual-only in Dagster

- **WHEN** `dg list defs --json | jq '.[] | select(.key | startswith("3_model_lifecycle/federated_ocr")) | .automation_condition' | sort -u` runs
- **THEN** the output is `["manual"]` (the only automation condition across the federated_ocr assets)