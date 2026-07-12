# bonneagar-iac-merge — MODIFIED Requirements

> **MODIFIED** by `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/`.

The flat-to-root change originally drafted in this spec is **reverted**:
the IaC stays in the `bonneagar/` subdirectory. The user clarified
mid-run that the `bonneagar/` subdir should be preserved, not flattened
to repo root.

## MODIFIED Requirements

### Requirement: Unified TypeScript IaC at bonneagar/iac/

The unified TypeScript IaC SHALL live at `bonneagar/iac/` (NOT at the
repo root). All `iac/` paths in this and other specs are now
interpreted as `bonneagar/iac/` (relative to the repo root).

#### Scenario: The IaC source tree lives at bonneagar/iac/

- **WHEN** a developer reads `bonneagar/iac/clients/komodo-client.ts`
- **THEN** the `KomodoClient` class SHALL expose 18 methods (unchanged)
- **AND** the IaC SHALL be reachable from the root via
  `bun run --cwd bonneagar iac:<command>` (per the root
  `package.json` scripts)

#### Scenario: The IaC's package.json is at bonneagar/

- **WHEN** a developer reads `bonneagar/package.json`
- **THEN** the `iac`, `iac:plan`, `iac:deploy`, `iac:bootstrap`,
  `iac:teardown`, `iac:health` scripts SHALL delegate to
  `iac/cli.ts <subcommand>`

### Requirement: iac:bootstrap at repo root

The IaC `iac:bootstrap` SHALL be reachable from the cianfhoghlaim repo
root via the `package.json` script `iac:bootstrap`, delegating to
`bun run --cwd bonneagar iac:bootstrap`. The previous v7 plan had this
deleting the `--cwd bonneagar` shim; that is reverted.

#### Scenario: Root-level iac:bootstrap is callable

- **WHEN** a developer runs `bun run iac:bootstrap` from the
  cianfhoghlaim repo root
- **AND** the `bun run --cwd bonneagar iac:bootstrap` delegation
  succeeds
- **THEN** the IaC SHALL execute the bootstrap sequence
- **AND** the exit code SHALL be 0 on success

### Requirement: Cross-repo sync convention

Every openspec change SHALL include a `cross-repo-sync.md` file that
lists the commit hashes + branches + ordered tasks needed in each repo,
when the change touches more than one of the remaining 2 repos
(cianfhoghlaim + leabharlann). The bonneagar repo is no longer a
separate repo — it's a subdirectory of cianfhoghlaim.

#### Scenario: A change touches cianfhoghlaim + leabharlann

- **WHEN** a developer creates a change that edits both repos
- **THEN** `openspec/changes/<id>/cross-repo-sync.md` SHALL exist
- **AND** it SHALL list the commit plan for each repo
- **AND** it SHALL be referenced from the change's `proposal.md`

#### Scenario: A change is single-repo (cianfhoghlaim)

- **WHEN** a developer creates a change that only edits
  cianfhoghlaim
- **THEN** the `cross-repo-sync.md` file is OPTIONAL
- **AND** the proposal.md `## Dependencies` section SHALL declare
  `Affected repos: cianfhoghlaim` for clarity

### Requirement: NEW — Bonneagar remote renamed to archive-bonneagar

After the v7 landing, the `bonneagar` GitHub remote SHALL be renamed
to `archive-bonneagar`. This prevents accidental mis-pushes to the
standalone bonneagar repo and signals that it's now a frozen archive
of the pre-v7 IaC history.

#### Scenario: Bonneagar remote is renamed

- **WHEN** `git remote -v` is run after v7 lands
- **THEN** the only `archive-bonneagar` remote SHALL be visible
- **AND** its URL SHALL be `https://github.com/cianfhoghlaim/bonneagar.git`
  (unchanged)
- **AND** the local repo SHALL refuse to push to `archive-bonneagar`
  unless explicitly overridden via `git push --force` or via
  removing the `archive-bonneagar` remote first

## ADDED Requirements

### Requirement: Bonneagar subdirectory preservation

The `bonneagar/` subdirectory at the repo root SHALL contain the full
IaC: 88 Docker Compose stacks + the unified TypeScript IaC + the
Komodo resource-syncs + the Pangolin config + the audit scripts +
the IaC's own pyproject.toml.

#### Scenario: Bonneagar subdir is preserved across merges

- **WHEN** any future change touches IaC files
- **AND** the change is committed to the v7 main branch
- **THEN** the IaC files SHALL continue to live at `bonneagar/{iac,stacks,
  komodo,pangolin,...}/` paths
- **AND** the root `package.json` SHALL retain the `--cwd bonneagar`
  delegation in the `iac:*` scripts
