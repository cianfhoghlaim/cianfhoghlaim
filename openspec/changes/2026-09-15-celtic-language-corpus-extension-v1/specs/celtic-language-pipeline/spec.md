## ADDED Requirements

### Requirement: 11 Source Groups (Scots + Cornish + Manx + Corpas CC)

The system SHALL extend the celtic-language-pipeline to 11 source groups.

#### Scenario: Source group count is 11
- **WHEN** the user runs `openspec list --specs | grep celtic-language-pipeline`
- **THEN** the spec body SHALL list 11 source groups

### Requirement: OntoLex-Lemon Cognify Edges

The system SHALL register 3 OntoLex-Lemon edge types in the Cognee cognify pipeline.

#### Scenario: Cognify edges exist
- **WHEN** the user queries `cognee.edges("translationOf")`
- **THEN** the query returns at least 100 Celtic translation pairs

### Requirement: .vrt Parser Helper

The system SHALL provide `dlt/language/_shared/vrt_parser.py` for parsing
CQPweb verticalised text files.

#### Scenario: Parser imports cleanly
- **WHEN** the user runs `from dlt.language._shared.vrt_parser import parse`
- **THEN** the import succeeds