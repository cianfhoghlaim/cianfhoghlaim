# CI Orchestration Capability

## Purpose

`dagger-ci` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.


## Background
Full deployment pipeline orchestration for Ansible, Docker Compose, and polyglot CI (Python, TypeScript, Rust).

| Feature | Description |
|---------|-------------|
| Polyglot CI | Python (pytest, pyright, ruff), TypeScript (tsc, eslint), Rust (cargo, clippy) |
| Ansible Integration | Playbook execution with inventory and tag support |
| Docker Compose | Validation and configuration generation |
| Health Checks | Pre/post deployment verification |

## Requirements

### Requirement: Full Pipeline Execution

The system SHALL orchestrate complete CI/CD pipelines with validation and health checks.

#### Scenario: Full Deployment Pipeline
- **GIVEN** Ansible directory, Compose directory, and SSH credentials
- **WHEN** `runPipeline()` is executed
- **THEN** linting, validation, health checks, and deployment complete in sequence

#### Scenario: Dry Run Mode
- **GIVEN** dryRun flag is true
- **WHEN** pipeline is executed
- **THEN** deployment is skipped but validation completes

### Requirement: Polyglot CI

The system SHALL test Python, TypeScript, and Rust projects in containerized environments.

#### Scenario: Python CI
- **GIVEN** a source directory with Python code
- **WHEN** `testPython()` is executed
- **THEN** pytest, pyright, and ruff checks run with uv runtime

#### Scenario: TypeScript CI
- **GIVEN** a source directory with TypeScript code
- **WHEN** `testTypescript()` is executed
- **THEN** tsc and eslint checks run with Bun runtime

#### Scenario: Rust CI
- **GIVEN** a source directory with Rust code
- **WHEN** `testRust()` is executed
- **THEN** cargo build, test, and clippy checks run

### Requirement: Targeted Deployment

The system SHALL deploy specific infrastructure components independently.

#### Scenario: Observability Stack
- **GIVEN** Ansible directory and SSH key
- **WHEN** `deployObservability()` is executed
- **THEN** observability stack deploys to target host

#### Scenario: Storage Stack
- **GIVEN** Ansible directory and SSH key
- **WHEN** `deployStorage()` is executed
- **THEN** storage stack (PostgreSQL, DuckDB, LanceDB) deploys

## API Reference

| Function | Parameters | Returns |
|----------|------------|---------|
| `runPipeline()` | ansibleDir, composeDir, sshKey, opToken, targetHosts, dryRun | string |
| `ci()` | source | string |
| `testPython()` | source | string |
| `testTypescript()` | source | string |
| `testRust()` | source | string |
| `deployObservability()` | ansibleDir, sshKey, host | string |
| `deployStorage()` | ansibleDir, sshKey, host | string |
| `deployHetzner()` | ansibleDir, sshKey, domain | string |
| `buildAll()` | source | string |

## Implementation References

| Component | Path |
|-----------|------|
| Main Module | `infrastructure/dagger/src/__init__.py (UnifiedPipeline) or infrastructure/dagger/ts_submodules/bonneagar/src/ci.ts (TS submodule)` |
| Python CI | `infrastructure/dagger/src/infrastructure/__init__.py or infrastructure/dagger/ts_submodules/bonneagar/src/python.ts` |
| TypeScript CI | `infrastructure/dagger/src/web/__init__.py or infrastructure/dagger/ts_submodules/bonneagar/src/typescript.ts` |
| Rust CI | `infrastructure/dagger/src/shared/containers.py (rust_container) or infrastructure/dagger/ts_submodules/bonneagar/src/rust.ts` |

## Related Specs

- [dagger-gitops](../dagger-gitops/spec.md) - GitOps pipeline setup
- [dagger-komodo](../dagger-komodo/spec.md) - Komodo orchestration
