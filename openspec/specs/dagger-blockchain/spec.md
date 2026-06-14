# Blockchain CI Capability

## Purpose

`dagger-blockchain` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.


## Background
CI/CD functions for SpacetimeDB WASM modules, Solana programs (Anchor), and Ethereum contracts (Foundry/Alloy).

| Feature | Description |
|---------|-------------|
| SpacetimeDB | WASM module compilation and deployment |
| Solana | Anchor program building and testing |
| Ethereum | Foundry/Alloy contract development |
| Full Pipeline | All platforms in sequence |

## Requirements

### Requirement: SpacetimeDB Module CI

The system SHALL build and deploy SpacetimeDB WASM modules.

#### Scenario: Build WASM Modules
- **GIVEN** source directory and module list
- **WHEN** `spacetimedb.build()` is executed
- **THEN** WASM modules are compiled

#### Scenario: Generate TypeScript Bindings
- **GIVEN** source directory and module name
- **WHEN** `spacetimedb.generateBindings()` is executed
- **THEN** TypeScript client code is generated

#### Scenario: Deploy Module
- **GIVEN** source, module, host, and identity token
- **WHEN** `spacetimedb.deploy()` is executed
- **THEN** module is published to SpacetimeDB instance

### Requirement: Solana Program CI

The system SHALL build and deploy Solana programs.

#### Scenario: Build Anchor Programs
- **GIVEN** source directory
- **WHEN** `solana.build()` is executed
- **THEN** Solana programs are compiled

#### Scenario: Run Anchor Tests
- **GIVEN** source directory
- **WHEN** `solana.test()` is executed
- **THEN** Anchor integration tests run

#### Scenario: Deploy to Devnet
- **GIVEN** source, program name, and keypair
- **WHEN** `solana.deploy()` is executed
- **THEN** program deploys to Solana devnet

### Requirement: Ethereum Contract CI

The system SHALL build and test Ethereum contracts.

#### Scenario: Build Alloy Bindings
- **GIVEN** source directory
- **WHEN** `ethereum.buildBindings()` is executed
- **THEN** Rust contract bindings compile

#### Scenario: Run Rust Tests
- **GIVEN** source directory
- **WHEN** `ethereum.test()` is executed
- **THEN** contract tests run

#### Scenario: Deploy Contract
- **GIVEN** source, contract path, RPC URL, and private key
- **WHEN** `ethereum.deploy()` is executed
- **THEN** contract deploys via Forge

### Requirement: Full Blockchain Pipeline

The system SHALL run complete blockchain CI across all platforms.

#### Scenario: Full Pipeline
- **GIVEN** source directory
- **WHEN** `fullPipeline()` is executed
- **THEN** SpacetimeDB, Solana, and Ethereum builds and tests run

## API Reference

| Function | Parameters | Returns |
|----------|------------|---------|
| `spacetimedb.build()` | source, modules[] | string |
| `spacetimedb.generateBindings()` | source, moduleName | string |
| `spacetimedb.deploy()` | source, moduleName, host, identityToken | string |
| `spacetimedb.test()` | source | string |
| `solana.build()` | source | string |
| `solana.test()` | source | string |
| `solana.deploy()` | source, programName, keypair | string |
| `solana.upgrade()` | source, programId, keypair | string |
| `solana.generateClient()` | source | string |
| `ethereum.buildBindings()` | source | string |
| `ethereum.test()` | source | string |
| `ethereum.deploy()` | source, contractPath, rpcUrl, privateKey | string |
| `ethereum.verify()` | source, contractAddress, chain | string |
| `fullPipeline()` | source | string |

## Implementation References

| Component | Path |
|-----------|------|
| Main Module | `dagger-blockchain is DEFERRED to a followup OpenSpec change` |

## Related Specs

- [dagger-ci](../dagger-ci/spec.md) - General CI orchestration
