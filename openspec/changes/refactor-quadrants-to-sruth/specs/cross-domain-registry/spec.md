## MODIFIED Requirements

### Requirement: DLT source filesystem layout

The system SHALL place DLT source modules under
`sruth/oideachais/dlt_sources/<domain>/<nation>/` where `<domain>`
∈ {`education`, `medicine`, `law`, `statistics`, `site_analysis`} and
`<nation>` ∈ {`ie`, `ni`, `en`, `sct`, `wls`, `iom`, `jey`, `ggy`}.

#### Scenario: Culture DLT source path

- **GIVEN** the culture DLT source for Ireland
- **WHEN** locating the source file
- **THEN** the path is `sruth/oideachais/dlt_sources/domains/culture/ie/heritage_source.py`
  (the legacy root-level `oideachais/dlt_sources/culture/ie/heritage_source.py`
  is gone)
- **AND** the source declares `resources = [...]` with the 8 culture
  resource names (`royal_connections`, `leath_cuinn`, `english_invasion`,
  `deisi_origins`, `aos_si`, `tuatha_de_danann`, `cian_lineage`,
  `toponymic_evidence`)

#### Scenario: 3-tier hierarchy for all DLT sources

- **GIVEN** every DLT source in the platform
- **WHEN** reading the source's filesystem path
- **THEN** the path follows `<sruth_root>/<flow>/dlt_sources/<domain>/<nation>/<entity>.py`
  where `<sruth_root>` is `sruth/oideachais` for oideachais sources,
  `sruth/meaisinfhoghlaim` for AI/ML sources, `sruth/crypteolas` for
  crypteolas-specific sources, or `sruth/tuatha` for tuatha-specific sources

### Requirement: Dagster asset key preservation

The system SHALL preserve all existing Dagster asset keys across the
sruth/ refactor — no rename of `oideachais.*` keys to `sruth_oideachais.*`
keys is permitted (legacy asset keys stay valid).

#### Scenario: Existing asset key unchanged

- **GIVEN** the 228 Dagster assets in `sruth/oideachais/dagster_defs/`
- **WHEN** comparing the asset keys pre- and post-refactor
- **THEN** keys like `oideachais.leabharlann.books.embedding`,
  `oideachais.culture.heritage.leath_cuinn`,
  `oideachais.gaois.duchas.cognify` are byte-identical pre and post
- **AND** the asset key namespace does NOT change to `sruth_oideachais.*`

#### Scenario: Dagster auto-discovery still works

- **GIVEN** the refactored filesystem
- **WHEN** running `dg dev` against the `sruth/oideachais` code-location
- **THEN** the 228 assets are auto-discovered from
  `sruth/oideachais/dagster_defs/assets/`
- **AND** no `@asset(key_prefix=...)` annotations are added or renamed

### Requirement: Cognee dataset name preservation

The system SHALL preserve all existing Cognee dataset names across the
sruth/ refactor — no rename of `oideachais`, `leabharlann`,
`culture_heritage` etc. is permitted.

#### Scenario: Existing Cognee dataset unchanged

- **GIVEN** the 6 Cognee datasets (`oideachais`, `leabharlann`,
  `culture_heritage`, `croilar`, `tuatha`, `infrastructure`)
- **WHEN** comparing the dataset names pre- and post-refactor
- **THEN** all 6 names are byte-identical pre and post
- **AND** the `cognee add()` calls inside `sruth/oideachais/cognee_integration/*.py`
  still pass `dataset_name="oideachais"` (NOT `sruth_oideachais`)

### Requirement: CocoIndex mount_table_target paths preserved

The system SHALL preserve CocoIndex `mount_table_target` paths and
table names across the sruth/ refactor.

#### Scenario: Culture CocoIndex App unchanged

- **GIVEN** `sruth/oideachais/cocoindex_flows/culture_heritage_embedding.py`
  (the 12th v1 CocoIndex App, registered in
  `extend-culture-heritage-to-8-articles`)
- **WHEN** reading the `mount_table_target` call
- **THEN** the table name is still `culture_heritage_embeddings`
  (NOT `sruth_oideachais_culture_heritage_embeddings`)
- **AND** the namespace argument preserves the `oideachais` prefix

### Requirement: MotherDuck pipeline references

The system SHALL record in the openspec spec that MotherDuck blueprints
use the `sruth/<flow>/` path convention.

#### Scenario: MotherDuck blueprint uses sruth/ paths

- **GIVEN** `infrastructure/stacks/motherduck/blueprint.yaml`
- **WHEN** reading the pipeline references
- **THEN** the file contains `pipeline: sruth/oideachais`,
  `pipeline: sruth/crypteolas`, etc. (NOT `pipeline: oideachais`)
- **AND** the blueprint pre-dated the refactor but already uses the
  sruth/ convention (forward-looking)