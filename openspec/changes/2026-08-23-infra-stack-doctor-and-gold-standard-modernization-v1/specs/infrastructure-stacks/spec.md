## ADDED Requirements

### Requirement: stack-gold-standard-audit

The dev environment SHALL expose a `devops:stack:gold-standard-audit`
task that runs `scripts/stack-doctor.sh --strict` and fails CI if any
stack at `bonneagar/stacks/*/` is missing any of the 6 GOLD_STANDARD
files (compose.yaml + sidecar.yaml + secrets.env + pangolin.yaml +
blueprint.yaml + .env.example).

#### Scenario: stack passes the gold-standard audit

- **WHEN** `mise run devops:stack:gold-standard-audit` runs
- **AND** every stack has all 6 GOLD_STANDARD files
- **THEN** the command MUST exit 0

#### Scenario: stack fails the gold-standard audit

- **WHEN** `mise run devops:stack:gold-standard-audit` runs
- **AND** any stack is missing ≥ 1 GOLD_STANDARD file
- **THEN** the command MUST exit 1
- **AND** the output MUST list each missing file per offending stack

### Requirement: stack-drift-report

The dev environment SHALL expose a `devops:stack:drift-report` task that
emits a per-stack drift summary (informational, never fails).

#### Scenario: drift report always exits 0

- **WHEN** `mise run devops:stack:drift-report` runs
- **THEN** the command MUST exit 0 (regardless of drift)
- **AND** the output MUST list each stack + its missing files