# `indexing-and-cognition` capability spec — bonneagar-iac-merge-komodo-pangolin-infisical delta

The `indexing-and-cognition` capability spec governs the CCC
v1 code search + Cognee knowledge graph + OpenCode
agent/MCP registry.

This delta cross-references the new IaC at
`bonnegar/iac/` (the IaC is the orchestration surface for
the 3 systems that the cognify + indexing layers depend on).

## ADDED Requirements

### Requirement: Cross-reference the new IaC

The system SHALL cross-reference the new IaC at
`bonnegar/iac/` from the `indexing-and-cognition` capability
docs.

#### Scenario: IaC is the orchestration surface for the cognify + indexing layers

- **WHEN** a developer reads the `indexing-and-cognition` spec
- **THEN** the spec SHALL mention `bonnegar/iac/` as the
  orchestrator of the 3 systems (Komodo + Pangolin + Infisical)
  that the CCC code search + Cognee knowledge graph + OpenCode
  agent/MCP registry depend on
- **AND** the spec SHALL cross-reference the new
  `bonneagar-iac-merge` capability

## MODIFIED Requirements

*(None — the change only ADDs the cross-reference.)*

## REMOVED Requirements

*(None.)*
