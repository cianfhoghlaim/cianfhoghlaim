## MODIFIED Requirements

### Requirement: Identical absolute repository mount

The Bunchloch OpenChamber development stack SHALL mount the host repository
`/Users/cianmacandeisigh/dev/cianfhoghlaim` at that identical absolute
path inside the container. The stack MUST preserve the path identity used by
the host OpenCode server so session directory filters, worktrees, and git
operations resolve to the same project.

#### Scenario: Session project paths resolve identically

- **WHEN** a user opens the canonical repository from OpenChamber
- **THEN** the external OpenCode server receives
  `/Users/cianmacandeisigh/dev/cianfhoghlaim` as the project path
- **AND** git status and file discovery operate on the host checkout rather
  than a container-only path

#### Scenario: Legacy KCG mount path is retired

- **WHEN** the legacy `/Users/cianmacandeisigh/dev/kings_college_galway`
  directory no longer exists on the host (per the
  `2026-09-12-kcg-legacy-folder-retirement-v1` archive)
- **THEN** the OpenChamber dev container SHALL NOT expect a mount at that
  path
- **AND** all session-directory resolution SHALL fall back to the
  canonical `/Users/cianmacandeisigh/dev/cianfhoghlaim` mount