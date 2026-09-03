# Change: SpacetimeDB + Babylon.js ADR Clean Break (formalise rejection + archive orphaned scaffolding)

## Why

The Cianfhoghlaim platform has accumulated orphaned Rust crate scaffolding
from the previous `sruth/tuatha/` sub-project:

- `agents/api/_rust_crates/stdb-modules/tuath-game/` (SpacetimeDB module)
- `agents/api/_rust_crates/services/nft-relayer/` (SpacetimeDB→Solana relayer)
- `agents/api/_rust_crates/solana/` (Solana RPC client)
- `agents/api/_rust_crates/wgpu/` (wgpu shader crate)

These crates:

- Bypass the centralised Cargo workspace (`agents/api/_rust_crates/`)
- Reference SpacetimeDB 1.11 (older than the active 1.13 release)
- Have no Dagster asset wiring them
- Have no agent that calls them
- Have no Convex equivalent (the active stack uses Convex)

Similarly, the `web/apps/tuatha-ui/` Babylon.js dependencies:

- Are explicitly rejected by the active `cianfhoghlaim-educational-mmo`
  spec ("No Babylon.js, no SpacetimeDB")
- Are not used by any active Convex route
- Add ~87MB to the workspace

This change formalises the rejection in an ADR + archives the orphaned
scaffolding.

## What changes

- **tuatha-platform spec** (NEW capability, replacing the
  retired 2026-07-06 version): the canonical spec for the
  tuatha quadrant post-v7 with 4 explicit Requirements +
  2 ADRs (SpacetimeDB rejection + Babylon.js retirement).

- **Archive orphaned Rust crates** (capability
  `infrastructure-stacks`): move
  `agents/api/_rust_crates/stdb-modules/tuath-game/` +
  `agents/api/_rust_crates/services/nft-relayer/` +
  `agents/api/_rust_crates/solana/` to
  `bonneagar/iac/_archive/rust-crates-2026-10/`.

- **Retire Babylon.js from tuatha-ui** (capability
  `agentic-frontend-frameworks`): remove all Babylon.js
  imports from `web/apps/tuatha-ui/`; remove the Babylon.js
  skill from `.agents/skills/babylonjs/`; mark the skill as
  deprecated.

## Out of scope

- The Sruth research artifacts (these are point-in-time docs).
- The Web3 token layer (already rejected).

## Dependencies

```markdown
## Dependencies

`Blocked by: 2026-09-01-celtic-mythology-content-system-v1` (the parent change that absorbs the tuatha quadrant's mythology content).

`Blocked by: 2026-09-29-familiar-dynamic-nft-system-v1` (the Familiar Dynamic NFT System uses Convex exclusively).

`Affected repos: cianfhoghlaim`
```

## Impact

- Affected specs:
  - NEW: `tuatha-platform` (4 ADDED Requirements)
  - `agentic-frontend-frameworks` (1 ADDED Requirement)
  - `infrastructure-stacks` (1 ADDED Requirement)
- Affected code/config:
  - `bonneagar/iac/_archive/rust-crates-2026-10/` (NEW)
  - `agents/api/_rust_crates/stdb-modules/` (DELETE)
  - `agents/api/_rust_crates/services/nft-relayer/` (DELETE)
  - `agents/api/_rust_crates/solana/` (DELETE)
  - `web/apps/tuatha-ui/` (REMOVE Babylon.js imports + deps)
  - `web/apps/tuatha-ui/package.json` (REMOVE @babylonjs/* packages)
  - `.agents/skills/babylonjs/SKILL.md` (DEPRECATED → redirect)