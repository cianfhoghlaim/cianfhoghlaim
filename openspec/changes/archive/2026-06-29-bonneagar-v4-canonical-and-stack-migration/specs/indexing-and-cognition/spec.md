# `indexing-and-cognition` capability spec — bonneagar-v4-canonical-and-stack-migration delta

The `indexing-and-cognition` capability spec governs the CCC
v1 code search + Cognee knowledge graph + OpenCode
agent/MCP registry. After the migration, the IaC TypeScript
client (which is part of the cognition surface) is at
`bonneagar/iac/komodo/` with the `package.json` hoisted to
the root.

## ADDED Requirements

### Requirement: IaC TypeScript client at `bonneagar/iac/komodo/`

The system SHALL expose the IaC TypeScript client at
`bonneagar/iac/komodo/` (5 files: `config.ts`,
`komodo-rpc.ts`, `deploy-stacks.ts`, `create-resources.ts`,
`read-state.ts`) with the manifest at `bonneagar/package.json`
(the root).

#### Scenario: IaC scripts are runnable from the root

- **WHEN** a developer runs `bun run iac:deploy-stacks` (or
  any of the 4 alias scripts) from the `bonneagar/` root
- **THEN** the script SHALL execute correctly (no path
  resolution issues)
- **AND** the script SHALL output a summary of the
  servers + stacks + resource-syncs + private resources
  created

#### Scenario: IaC reads cianfhoghlaim-project tag

- **WHEN** `bun run iac:deploy-stacks` runs
- **THEN** the script SHALL read every stack in
  `bonneagar/stacks/*/compose.yaml`
- **AND** every stack entry SHALL have a `project:cianfhoghlaim`
  tag (or no tag for personal/utility stacks)
- **AND** the script SHALL be runnable with
  `--project=cianfhoghlaim` to deploy only the
  cianfhoghlaim-relevant stacks

## MODIFIED Requirements

*(None — the change only ADDs the new IaC location; the
CCC + Cognee + OpenCode registry surface is unchanged.)*

## REMOVED Requirements

*(None.)*
