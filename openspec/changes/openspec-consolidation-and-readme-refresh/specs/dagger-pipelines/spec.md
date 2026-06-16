## ADDED Requirements

The `dagger-pipelines` capability is consolidated from the 5 separate
`dagger-ci`, `dagger-forgejo`, `dagger-komodo`, `dagger-cloudflare`,
`dagger-gitops` specs. The full Requirements + Scenarios are in the
canonical spec at `openspec/specs/dagger-pipelines/spec.md`.

### Requirement: Polyglot CI pipeline

The system SHALL provide a polyglot CI pipeline (Python, TypeScript,
Rust) orchestrated via Dagger.

#### Scenario: CI pipeline runs

- **WHEN** the Dagger CI pipeline runs on a push to main
- **THEN** the Python test suite, TypeScript build, and Rust build
  all run

### Requirement: Forgejo automation

The system SHALL automate Forgejo via the Dagger Forgejo module.

#### Scenario: Forgejo PR automation

- **WHEN** a PR is opened on the Forgejo instance
- **THEN** the Dagger Forgejo module sets the PR status, adds labels,
  and triggers the CI pipeline

### Requirement: Komodo orchestration

The system SHALL orchestrate Komodo via the Dagger Komodo module.

#### Scenario: Komodo deploy procedure

- **WHEN** the Dagger Komodo module runs the `deploy-oideachais-bunchloch`
  procedure
- **THEN** the module triggers the Komodo procedure and waits for
  completion

### Requirement: Cloudflare deployment

The system SHALL deploy the oideachais web app and the croilar apps
to Cloudflare Pages + Workers via the Dagger Cloudflare module.

#### Scenario: Cloudflare Pages deploy

- **WHEN** the Dagger Cloudflare module runs
- **THEN** the module builds the oideachais web app and the croilar
  apps and deploys them to Cloudflare Pages

### Requirement: GitOps pipeline

The system SHALL run the 8-step GitOps pipeline (Forgejo + Komodo +
Cloudflare + Locket) on every merge to main.

#### Scenario: 8-step GitOps

- **WHEN** a merge to main happens
- **THEN** the GitOps pipeline runs all 8 steps in order
