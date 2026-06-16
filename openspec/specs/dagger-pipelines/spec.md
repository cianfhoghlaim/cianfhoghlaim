# Dagger Pipelines Capability

## Purpose

`dagger-pipelines` is a capability of the Cianfhoghlaim platform. The
corresponding source code lives at `infrastructure/dagger/` (Python root
+ TypeScript submodule). See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This spec was consolidated from the 5 separate `dagger-ci`, `dagger-forgejo`,
`dagger-komodo`, `dagger-cloudflare`, and `dagger-gitops` specs. Each
former spec is now a section (Requirement) of this one spec. The deferred
`dagger-blockchain` spec is removed (Rust toolchain + GPU support deferred
indefinitely).

## Background

Polyglot CI/CD pipeline orchestration via Dagger (Python root +
TypeScript submodule). Three high-level pipelines (infra, web, data) ×
test/build/deploy/rollback, with Locket secret injection, Forgejo +
Komodo integration, and Cloudflare Pages / Workers deployment. The
Dagger Python SDK provides the per-pipeline runtime; the TS submodule
provides the Cloudflare-specific bindings.

## Requirements

### Requirement: Polyglot CI pipeline

The system SHALL provide a polyglot CI pipeline (Python, TypeScript,
Rust) orchestrated via Dagger.

#### Scenario: CI pipeline runs

- **GIVEN** a push to the main branch
- **WHEN** the Dagger CI pipeline runs
- **THEN** the pipeline runs the Python test suite, the TypeScript
  build, and the Rust build
- **AND** the pipeline exits 0 only if all 3 sub-pipelines succeed

### Requirement: Forgejo automation

The system SHALL automate Forgejo (the self-hosted Git server) via the
Dagger Forgejo module.

#### Scenario: Forgejo PR automation

- **GIVEN** a PR opened on the Forgejo instance
- **WHEN** the Dagger Forgejo module runs
- **THEN** the module sets the PR status, adds the appropriate labels,
  and triggers the CI pipeline

### Requirement: Komodo orchestration

The system SHALL orchestrate Komodo (the self-hosted infrastructure
manager) via the Dagger Komodo module.

#### Scenario: Komodo deploy procedure

- **GIVEN** a merge to main
- **WHEN** the Dagger Komodo module runs the `deploy-oideachais-bunchloch`
  procedure
- **THEN** the module triggers the Komodo procedure and waits for
  completion

### Requirement: Cloudflare deployment

The system SHALL deploy the oideachais web app and the croilar apps to
Cloudflare Pages + Workers via the Dagger Cloudflare module.

#### Scenario: Cloudflare Pages deploy

- **GIVEN** a successful CI pipeline
- **WHEN** the Dagger Cloudflare module runs
- **THEN** the module builds the oideachais web app and the croilar
  apps and deploys them to Cloudflare Pages

### Requirement: GitOps pipeline

The system SHALL run the 8-step GitOps pipeline (Forgejo + Komodo +
Cloudflare + Locket) on every merge to main.

#### Scenario: 8-step GitOps

- **GIVEN** a merge to main
- **WHEN** the GitOps pipeline runs
- **THEN** the pipeline runs all 8 steps in order:
  1. Trigger CI
  2. Build Docker images
  3. Push to ghcr.io
  4. Trigger Komodo procedure
  5. Wait for stack health check
  6. Deploy to Cloudflare Pages
  7. Run smoke tests
  8. Notify on success/failure

## Cross-references

- [`infrastructure/dagger/`](../../infrastructure/dagger/) (Python root)
- [`infrastructure/dagger/typescript/`](../../infrastructure/dagger/typescript/) (TS submodule)
- [`infrastructure/komodo/procedures/`](../../infrastructure/komodo/procedures/) (Komodo procedures)
- [`.agents/skills/dagger/SKILL.md`](../../.agents/skills/dagger/SKILL.md)
- [`.agents/skills/devops-architect/SKILL.md`](../../.agents/skills/devops-architect/SKILL.md)
