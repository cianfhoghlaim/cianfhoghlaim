# Stack Audit Capability

## Overview

Every Docker Compose stack under `infrastructure/stacks/*/*/` MUST follow the 6-file GOLD_STANDARD pattern. A root-level auditor (`scripts/stack-doctor.sh`) reports per-stack compliance on every CI run, gated by a turbo task.

## Requirements

### Requirement: 6-File Pattern Compliance
The system SHALL audit every stack directory under `infrastructure/stacks/*/*/` against the 6-file pattern.

#### Scenario: Critical — no compose or blueprint
- **WHEN** a stack has neither `compose.yaml` nor `blueprint.yaml`
- **THEN** `stack-doctor` SHALL report it as CRITICAL and exit 1

#### Scenario: Critical — compose fails to parse
- **WHEN** `docker compose -f compose.yaml --env-file .env.example config --quiet` fails
- **THEN** `stack-doctor` SHALL report it as CRITICAL

#### Scenario: Warning — missing sidecar
- **WHEN** a stack has `compose.yaml` but no `sidecar.yaml`
- **THEN** `stack-doctor` SHALL report it as WARNING (Locket not wired)

#### Scenario: Warning — empty secrets.env
- **WHEN** a stack's `secrets.env` contains zero `{{ infisical:// }}` references
- **THEN** `stack-doctor` SHALL report it as WARNING (secrets not sourced from Infisical)

#### Scenario: Info — :latest tags
- **WHEN** a stack's `compose.yaml` uses any `image: foo:latest` line
- **THEN** `stack-doctor` SHALL report the count of `:latest` occurrences as INFO

#### Scenario: Info — missing healthchecks
- **WHEN** a stack has more than 1 service and zero `healthcheck:` blocks
- **THEN** `stack-doctor` SHALL report it as INFO (debugging will be hard)

### Requirement: CI Integration via Turbo
The system SHALL run `stack-doctor` as part of `mise turbo validate-stacks` and as a `bun run validate-stacks` script.

#### Scenario: Turbo task wired
- **WHEN** the operator runs `bunx turbo run validate-stacks`
- **THEN** turbo SHALL execute `bash scripts/stack-doctor.sh` from the repo root
- **AND** a non-zero exit code (CRITICAL found) SHALL fail the turbo run

#### Scenario: JSON output for CI
- **WHEN** the operator runs `bash scripts/stack-doctor.sh --json`
- **THEN** the output SHALL be a valid JSON object with `critical`, `warning`, `info` counts and arrays of stack-level findings

### Requirement: Locket Sidecar Coverage
The system SHALL provide Locket secret injection to every stack that has `compose.yaml`.

#### Scenario: New stack is added
- **WHEN** a new stack directory is created with `compose.yaml`
- **THEN** the operator MUST also add `sidecar.yaml` and `secrets.env` with `{{ infisical:///... }}` references
- **AND** `stack-doctor` SHALL flag any stack missing `sidecar.yaml` as a WARNING

### Requirement: Pangolin Private Resource Pattern
The system SHALL route every web-facing stack through the Pangolin private resource pattern (Olm VPN + Pocket ID SSO).

#### Scenario: Stack exposes a web UI
- **WHEN** a stack has any service with a `ports:` declaration and a web UI
- **THEN** its `pangolin.yaml` MUST use the 6-label `pangolin.private-resources.<repo>.*` pattern
- **AND** its `blueprint.yaml` MUST mirror that pattern

### Requirement: Health Endpoint Scrapability
The system SHALL be able to scrape `/health` (or equivalent) from every long-running service.

#### Scenario: Healthcheck added
- **WHEN** a stack's `compose.yaml` adds a `healthcheck:` block to a service
- **AND** the service exposes `/health` on a known port
- **THEN** the new `infrastructure/stacks/infrastructure/monitoring/config/prometheus.yml` SHALL include the service as a scrape target
