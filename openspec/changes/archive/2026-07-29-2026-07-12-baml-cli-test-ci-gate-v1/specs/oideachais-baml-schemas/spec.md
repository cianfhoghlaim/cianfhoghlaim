## ADDED Requirements

### Requirement: baml-cli test CI hard gate

The system SHALL run `baml-cli test` as a hard GitHub Actions CI gate on every pull request and push targeting `pick-4-biep-v1` or `main`.

#### Scenario: Pull request runs BAML tests

- **GIVEN** a pull request targets `pick-4-biep-v1` or `main`
- **WHEN** GitHub Actions evaluates `.github/workflows/baml-test.yaml`
- **THEN** the `baml-test` job SHALL install the Python/uv/mise runtime and dependencies
- **AND** the job SHALL run `mise run baml:test` from `cianfhoghlaim/`
- **AND** `mise run baml:test` SHALL invoke `uv run baml-cli test`
- **AND** a non-zero `baml-cli test` exit code SHALL fail the job and block merge.

#### Scenario: Push runs BAML tests

- **GIVEN** a commit is pushed to `pick-4-biep-v1` or `main`
- **WHEN** GitHub Actions evaluates `.github/workflows/baml-test.yaml`
- **THEN** the `baml-test` job SHALL run `mise run baml:test` from `cianfhoghlaim/`
- **AND** the workflow SHALL upload the captured CLI output under the `baml-test-results` artifact with 30-day retention.

#### Scenario: Manual dispatch runs BAML tests

- **GIVEN** a maintainer starts `.github/workflows/baml-test.yaml` via `workflow_dispatch`
- **WHEN** the workflow runs
- **THEN** it SHALL execute the same `mise run baml:test` hard gate used for PRs and branch pushes.
