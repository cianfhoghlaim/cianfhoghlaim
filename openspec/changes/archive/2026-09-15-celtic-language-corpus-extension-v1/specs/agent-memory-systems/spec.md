## ADDED Requirements

### Requirement: OntoLex-Lemon Edge Types

The system SHALL register 3 OntoLex-Lemon edge types in the Cognee cognify
pipeline: `cognateOf`, `translationOf`, `hasCognateIn`.

The edges SHALL be queryable via the Cognee REST API and SHALL be
materialised when the cognify pipeline runs against any of the 11
celtic-language-pipeline source groups.

#### Scenario: Edges registered in cognify config
- **WHEN** the user runs `mise run cognee:cognify`
- **THEN** the output SHALL contain at least 100 `cognateOf` edges
- **THEN** the output SHALL contain at least 100 `translationOf` edges