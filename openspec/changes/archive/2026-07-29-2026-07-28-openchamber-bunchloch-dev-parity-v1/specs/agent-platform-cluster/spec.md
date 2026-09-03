# `agent-platform-cluster` capability delta

## ADDED Requirements

### Requirement: OpenChamber uses the existing Bunchloch OpenCode server

The agent-platform cluster SHALL support OpenChamber as a Bunchloch development
surface backed by the existing host OpenCode `1.17.9` server. OpenChamber MUST
use an explicit external-server configuration with `OPENCODE_HOST`,
`OPENCODE_PORT=4096`, and `OPENCODE_SKIP_START=true`, and MUST NOT create a
parallel bundled OpenCode runtime for this surface.

#### Scenario: The external host is the sole OpenCode runtime

- **WHEN** OpenChamber is started for Bunchloch development
- **THEN** requests are sent to the host OpenCode server at port `4096`
- **AND** no in-container OpenCode process is started or used as a fallback

### Requirement: Host OpenCode sessions and MCP configuration remain authoritative

The cluster SHALL preserve the host OpenCode server as the owner of OpenCode
sessions, project metadata, enabled MCP configuration, and related credentials.
OpenChamber MUST consume those resources through the external server rather than
copying, rehydrating, or shadowing them in its own config volume.

#### Scenario: Existing sessions are visible through OpenChamber

- **WHEN** the host OpenCode server has an existing session for
  `/Users/cianmacandeisigh/dev/kings_college_galway`
- **THEN** OpenChamber can list and reopen that session through the external
  server
- **AND** the session resolves to the identical absolute repository path

#### Scenario: Enabled MCP list is preserved

- **WHEN** the host OpenCode server exposes its enabled MCP list
- **THEN** OpenChamber displays or can query the same enabled MCP names and
  statuses through the external server
- **AND** no MCP credential or configuration is duplicated into the
  OpenChamber-owned persistent volume

### Requirement: Agent-surface parity verification

The agent-platform cluster SHALL provide a verification procedure for the
Bunchloch OpenChamber surface that checks OpenChamber `/health`, host OpenCode
`/global/health`, session visibility, the enabled MCP list, the identical
repository mount, git availability, and loopback-only binding. The procedure
MUST fail if any parity check fails or if plaintext secrets are detected.

#### Scenario: Full parity verification passes

- **WHEN** the verification procedure runs after both services start
- **THEN** OpenChamber `/health` and OpenCode `/global/health` return HTTP 200
- **AND** an existing host session opens at the canonical repository path with
  the expected enabled MCP list
- **AND** git, secret, mount, and loopback checks all pass

#### Scenario: A parity check fails

- **WHEN** the external server is unavailable, a session is missing, an MCP
  list differs, or a security check fails
- **THEN** the verification procedure exits non-zero
- **AND** it reports the failed check without printing secret values
