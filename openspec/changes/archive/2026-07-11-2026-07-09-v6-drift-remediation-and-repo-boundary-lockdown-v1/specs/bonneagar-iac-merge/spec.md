## ADDED Requirements

### Requirement: Cross-repo sync convention

Every openspec change SHALL include a `cross-repo-sync.md` file
that lists the commit hashes + branches + ordered tasks needed
in each repo, when the change touches more than one of the 3
repos (cianfhoghlaim + bonneagar + leabharlann).

#### Scenario: A change touches cianfhoghlaim + bonneagar

- **WHEN** a developer creates a change that edits both repos
- **THEN** `openspec/changes/<id>/cross-repo-sync.md` SHALL exist
- **AND** it SHALL list the commit plan for each repo
- **AND** it SHALL be referenced from the change's `proposal.md`

#### Scenario: A change is single-repo

- **WHEN** a developer creates a change that only edits
  cianfhoghlaim
- **THEN** the `cross-repo-sync.md` file is OPTIONAL
- **AND** the proposal.md `## Dependencies` section SHALL
  declare `Affected repos: cianfhoghlaim` for clarity

### Requirement: iac:bootstrap at root

The IaC `iac:bootstrap` SHALL be reachable from the
cianfhoghlaim repo root via the `package.json` script
`iac:bootstrap`, delegating to `bun run --cwd bonneagar iac:bootstrap`.

#### Scenario: Root-level iac:bootstrap is callable

- **WHEN** a developer runs `bun run iac:bootstrap` from the
  cianfhoghlaim repo root
- **THEN** the IaC SHALL execute the bootstrap sequence
- **AND** the exit code SHALL be 0 on success

#### Scenario: iac:bootstrap supports --dry-run

- **WHEN** a developer runs `bun run iac:bootstrap --dry-run`
- **THEN** the IaC SHALL print the diff and SHALL NOT mutate
  any remote system

### Requirement: Dependencies field in proposal.md

Every openspec change's `proposal.md` SHALL include a
`## Dependencies` section that lists `Blocked by: <change-id>`
edges for topo ordering.

#### Scenario: A change depends on a not-yet-archived change

- **WHEN** a developer writes a new change that depends on a
  previously-authored change still in `openspec/changes/`
- **THEN** the new change's proposal.md SHALL declare
  `Blocked by: <change-id>` in its `## Dependencies` section
- **AND** the new change SHALL NOT be archived until the
  blocker is archived

#### Scenario: A change has no dependencies

- **WHEN** a developer writes a new change that has no
  ordering constraint
- **THEN** the proposal.md SHALL declare `Blocked by: none`
  in its `## Dependencies` section