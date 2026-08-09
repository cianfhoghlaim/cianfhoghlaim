## ADDED Requirements

### Requirement: Infrastructure Scanner Subdomain

The system SHALL extend the british-isles-education-pipeline-v3 with
5 new DLT sources under `dlt/infrastructure/`.

#### Scenario: Subdomain registered
- **WHEN** the user runs `openspec list --specs | grep british-isles-education-pipeline-v3`
- **THEN** the spec body SHALL list the infrastructure scanner subdomain with 5 DLT sources

### Requirement: Celtic Stones Scanner Subdomain

The system SHALL extend the british-isles-education-pipeline-v3 with
2 new DLT sources under `dlt/language/`: `cisp/`, `megalithic_portal/`.

#### Scenario: Subdomain registered
- **WHEN** the user runs `openspec list --specs | grep british-isles-education-pipeline-v3`
- **THEN** the spec body SHALL list the Celtic stones scanner subdomain with 2 DLT sources