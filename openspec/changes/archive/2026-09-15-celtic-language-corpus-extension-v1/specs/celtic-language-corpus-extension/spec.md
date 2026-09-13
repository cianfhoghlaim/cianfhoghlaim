## ADDED Requirements

### Requirement: 4 New Source Groups (Scots + Cornish + Manx + Corpas na Gàidhlig)

The system SHALL extend the celtic-language-pipeline from 9 source groups
to 11 by adding 4 new DLT source groups under `dlt/language/`.

#### Scenario: 4 New source groups ingest
- **WHEN** the user invokes `mise run dlt:scots`
- **THEN** the source SHALL ingest ≥10,000 Scots records from DSL
- **WHEN** the user invokes `mise run dlt:cornish`
- **THEN** the source SHALL ingest ≥50,000 Cornish records

### Requirement: .vrt Parser Helper

The system SHALL provide `dlt/language/_shared/vrt_parser.py` for parsing
CQPweb verticalised text files.

#### Scenario: .vrt parser parses Corpas na Gàidhlig
- **WHEN** the user invokes `vrt_parser.parse(corpas_cc_file_path)`
- **THEN** the parser returns a list of `Token` objects

### Requirement: OntoLex-Lemon Cognify Edges

The system SHALL register 3 new edge types in the Cognee cognify pipeline:
`cognateOf`, `translationOf`, `hasCognateIn`.

#### Scenario: Cognify output contains new edge types
- **WHEN** the user invokes `mise run cognee:cognify`
- **THEN** the cognify output SHALL contain `cognateOf` edges linking cognate words

### Requirement: 5 BAML Functions for CEFR Analytics

The system SHALL provide 5 BAML functions in `baml/celtic/corpus.baml`:
`ExtractCefrReadinessScore`, `ExtractMutationDensityIndex`,
`ExtractAcquisitionVelocity`, `ExtractErrorHotspot`, `ExtractL1InterferenceMap`.

#### Scenario: All 5 functions codegen
- **WHEN** the user runs `baml-cli generate`
- **THEN** all 5 functions SHALL have Pydantic V2 class equivalents