# Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: oideachais_pipeline DltLoadCollectionComponent

The `oideachais_pipeline` asset group SHALL be declared as a
single `dagster_dlt.DltLoadCollectionComponent` instance at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs/oideachais_pipeline/defs.yaml`.

The Component SHALL wrap a single `dlt.source` factory at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs/oideachais_pipeline/loads.py`
that yields 4 DLT resources (one per Ireland education cycle:
early_childhood, primary, junior_cycle, senior_cycle).

The Component SHALL be auto-discovered by the parent
`dagster.DefsFolderComponent` at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs.yaml`.

The Component SHALL be tagged with `layer: "1_ingestion"` and
`partition_strategy: "language_x_subject"` to signal that the
downstream layer-2 assets should partition by (language, subject).

#### Scenario: a Dagster user runs the 4-cycle pipeline

- **GIVEN** the `dagster dev` webserver is running on port 3335
- **WHEN** the user materialises the `oideachais_pipeline` asset group
- **THEN** all 4 Ireland education cycles materialise in parallel
  (one DLT run per cycle) with MultiPartitions by (language, subject)
