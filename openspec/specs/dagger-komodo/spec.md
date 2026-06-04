# Komodo SDK Wrapper Capability

## Overview

Programmatic access to Komodo Core API for Git provider management, stack deployment, procedure execution, resource sync triggers, and server management.

| Feature | Description |
|---------|-------------|
| Git Providers | Account registration for deployment sources |
| Stack Management | Docker Compose stack lifecycle |
| Procedures | Automated operation execution |
| Resource Sync | Git-to-infrastructure synchronization |

## Requirements

### Requirement: Git Provider Management

The system SHALL manage Git provider accounts for Komodo.

#### Scenario: Create Git Provider
- **GIVEN** domain, username, and token
- **WHEN** `createGitProvider()` is executed
- **THEN** provider account is created in Komodo

#### Scenario: List Git Providers
- **WHEN** `listGitProviders()` is executed
- **THEN** all configured providers are returned

### Requirement: Stack Management

The system SHALL manage Docker Compose stacks through Komodo.

#### Scenario: Deploy Stack
- **GIVEN** stack name
- **WHEN** `deployStack()` is executed
- **THEN** stack is deployed to target server

#### Scenario: Stack Lifecycle
- **GIVEN** stack name
- **WHEN** `startStack()`, `stopStack()`, or `restartStack()` is executed
- **THEN** stack state changes accordingly

#### Scenario: Get Stack Details
- **GIVEN** stack name
- **WHEN** `getStack()` is executed
- **THEN** stack configuration and status is returned

### Requirement: Procedure Execution

The system SHALL execute Komodo procedures.

#### Scenario: Run Procedure
- **GIVEN** procedure name
- **WHEN** `runProcedure()` is executed
- **THEN** procedure executes on configured targets

### Requirement: Resource Sync

The system SHALL trigger resource synchronization.

#### Scenario: Run Sync
- **GIVEN** sync name
- **WHEN** `runSync()` is executed
- **THEN** resources are synchronized from Git

### Requirement: Server Management

The system SHALL query server information.

#### Scenario: List Servers
- **WHEN** `listServers()` is executed
- **THEN** all managed servers are returned

#### Scenario: Server Stats
- **GIVEN** server name
- **WHEN** `getServerStats()` is executed
- **THEN** server metrics are returned

## API Reference

| Function | Parameters | Returns |
|----------|------------|---------|
| `createGitProvider()` | domain, username, token | string |
| `listGitProviders()` | - | string |
| `deployStack()` | stackName | string |
| `startStack()` | stackName | string |
| `stopStack()` | stackName | string |
| `restartStack()` | stackName | string |
| `getStack()` | stackName | string |
| `listStacks()` | - | string |
| `runProcedure()` | procedureName | string |
| `getProcedure()` | procedureName | string |
| `listProcedures()` | - | string |
| `runSync()` | syncName | string |
| `getSync()` | syncName | string |
| `listSyncs()` | - | string |
| `listServers()` | - | string |
| `getServer()` | serverName | string |
| `getServerStats()` | serverName | string |
| `runBuild()` | buildName | string |
| `listBuilds()` | - | string |
| `health()` | - | string |
| `version()` | - | string |

## Implementation References

| Component | Path |
|-----------|------|
| Main Module | `infrastructure/dagger/src/infrastructure/__init__.py (calls bonny.komodo_redeploy) or infrastructure/dagger/ts_submodules/bonneagar/src/komodo.ts` |
| Stack Configs | `bonneagar/komodo/stacks/` |

## Related Specs

- [dagger-gitops](../dagger-gitops/spec.md) - GitOps pipeline
- [infrastructure-stacks](../infrastructure-stacks/spec.md) - Stack configurations
