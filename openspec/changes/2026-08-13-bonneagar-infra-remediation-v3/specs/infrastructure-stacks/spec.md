## ADDED Requirements

### Requirement: Resource-sync repo-namespace consistency

The system SHALL ensure that every Komodo resource-sync TOML file at
`bonneagar/komodo/resource-syncs/*.toml` declares the same `repo =`
value. The canonical repo SHALL be `cianfhoghlaim/bonneagar` (the
post-2026-07-17 v7-flatten canonical Git namespace). A
`mise run lint:komodo:resource-sync-repo-consistency` CI gate SHALL
fail the build if any resource-sync's `repo =` value differs from
`cianfhoghlaim/bonneagar` (or a documented `repo =` exception in
`openspec/specs/infrastructure-stacks/exceptions.toml`).

#### Scenario: All 4 resource-syncs declare the canonical repo

- **GIVEN** the 4 resource-sync TOML files at
  `bonneagar/komodo/resource-syncs/{arm1-oci,bunchloch,cross-cutting,storage-infrastructure}.toml`
- **WHEN** `mise run lint:komodo:resource-sync-repo-consistency` runs
- **THEN** all 4 files SHALL declare
  `repo = "cianfhoghlaim/bonneagar"`
- **AND** the lint passes with 0 errors

#### Scenario: A stale `cliste/bonneagar` reference is caught

- **GIVEN** a developer accidentally changes
  `bonneagar/komodo/resource-syncs/storage-infrastructure.toml:14`
  back to `repo = "cliste/bonneagar"` (the pre-v7 GitHub namespace)
- **WHEN** `mise run lint:komodo:resource-sync-repo-consistency` runs
- **THEN** the lint fails with
  `stale_repo_namespace: storage-infrastructure.toml:14 declares
  'cliste/bonneagar' — must be 'cianfhoghlaim/bonneagar' per the v7
  flatten (2026-07-17)`
- **AND** the developer is forced to fix the value before the change
  can ship

#### Scenario: Storage-infrastructure sync polls the canonical repo

- **GIVEN** `storage-infrastructure.toml` declares
  `repo = "cianfhoghlaim/bonneagar"`
- **WHEN** the Komodo Core polls the storage-infrastructure sync
- **THEN** the sync successfully discovers the latest TOML files at
  `bonneagar/komodo/{servers,stacks,procedures,actions,resource-syncs}/*.toml`
  in the canonical repo
- **AND** newly-added `komodo/stacks/<new>.toml` files are
  auto-registered within 60s of the next poll cycle
