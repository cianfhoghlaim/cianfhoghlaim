## ADDED Requirements

### Requirement: pangolin-infisical-upgrade-tasks

The dev environment SHALL expose 2 upgrade-check tasks for the Pangolin
reverse proxy + the Infisical secret manager.

#### Scenario: pangolin:upgrade shows the latest version

- **WHEN** `mise run devops:pangolin:upgrade` runs
- **THEN** the command MUST surface the latest Pangolin version
- **AND** the command MUST print the changelog URL

#### Scenario: infisical:upgrade shows the latest version

- **WHEN** `mise run devops:infisical:upgrade` runs
- **THEN** the command MUST surface the latest Infisical version
- **AND** the command MUST print the changelog URL