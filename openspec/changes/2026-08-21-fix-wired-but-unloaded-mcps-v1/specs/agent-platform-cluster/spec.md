# Delta: agent-platform-cluster

## MODIFIED Requirements

### Requirement: MCP server runtime integrity contract

The system SHALL guarantee that every MCP server entry in
`opencode.json` and `.mcp.json` with `enabled: true` successfully
registers its tools at agent runtime within 5 seconds of session
start.

The contract is enforced by the `mise run lint:mcp-runtime` CI gate,
which:
1. Enumerates every `enabled: true` MCP entry across both configs
2. Checks for a corresponding `mcp:smoke:*` task (fails if missing)
3. Runs each `mcp:smoke:*` task with a 5-second timeout
4. Fails the build if any task exits non-zero

#### Scenario: All wired MCPs register within 5 seconds

- **GIVEN** 12 MCPs are `enabled: true` in `opencode.json` + `.mcp.json`
- **AND** each has a corresponding `mcp:smoke:*` task
- **WHEN** `mise run lint:mcp-runtime` runs as part of CI
- **THEN** all 12 smoke tasks pass
- **AND** the task exits 0
- **AND** the agent runtime has 12 MCPs worth of tools available

#### Scenario: A wired MCP fails to register (catches a regression)

- **GIVEN** an `enabled: true` MCP entry has a runtime crash (e.g.
  `dlt-workspace-mcp` because `.dlt/.workspace` is missing)
- **WHEN** `mise run lint:mcp-runtime` runs
- **THEN** the corresponding `mcp:smoke:*` task times out at 5 s
- **AND** the CI gate fails with "MCP `<name>` failed to register within 5s"
- **AND** the developer is forced to fix the gap before merge

#### Scenario: A new MCP entry has no smoke test (catches a missing test)

- **GIVEN** a developer adds a new `enabled: true` MCP entry to
  `opencode.json`
- **AND** no corresponding `mcp:smoke:<name>` task exists
- **WHEN** `mise run lint:mcp-runtime` runs
- **THEN** the task fails with "no smoke test for MCP entry `<name>`"
- **AND** the developer is forced to write the smoke test before merge