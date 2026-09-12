## MODIFIED Requirements

### Requirement: Host OpenCode sessions and MCP configuration remain authoritative

The cluster SHALL preserve the host OpenCode server as the owner of OpenCode
sessions, project metadata, enabled MCP configuration, and related credentials.
OpenChamber MUST consume those resources through the external server rather than
copying, rehydrating, or shadowing them in its own config volume.

#### Scenario: Existing sessions are visible through OpenChamber

- **WHEN** the host OpenCode server has an existing session for
  `/Users/cianmacandeisigh/dev/cianfhoghlaim`
- **THEN** OpenChamber can list and reopen that session through the external
  server
- **AND** the session resolves to the identical absolute repository path

#### Scenario: Enabled MCP list is preserved

- **WHEN** the host OpenCode server exposes its enabled MCP list
- **THEN** OpenChamber displays or can query the same enabled MCP names and
  statuses through the external server
- **AND** no MCP credential or configuration is duplicated into the
  OpenChamber-owned persistent volume

#### Scenario: Legacy KCG session paths are not consulted

- **WHEN** the legacy `/Users/cianmacandeisigh/dev/kings_college_galway`
  directory no longer exists on the host (per the
  `2026-09-12-kcg-legacy-folder-retirement-v1` archive)
- **THEN** the host OpenCode server SHALL NOT report sessions whose
  project path is `/Users/cianmacandeisigh/dev/kings_college_galway`
- **AND** OpenChamber session listings SHALL contain only sessions whose
  project path lives under `/Users/cianmacandeisigh/dev/cianfhoghlaim`
  (or other live repositories on the host)