# Delta: tuatha-platform (deprecated alias → cianfhoghlaim-educational-mmo)

## MODIFIED Requirements

### Requirement: Capability is now cianfhoghlaim-educational-mmo (deprecated alias)

The system SHALL treat this `tuatha-platform` spec as a
**deprecated alias** for the canonical
`cianfhoghlaim-educational-mmo` spec. The Tuatha-themed
files (`tuatha-mmo`, `tuatha-platform`, `tuatha-achievement-ledger`,
`tuatha-mcp-server-tools`) SHALL be renamed to the `cianfhoghlaim-mmo`,
`cianfhoghlaim-platform`, `cianfhoghlaim-achievement-ledger`,
`cianfhoghlaim-mcp-server-tools` skills respectively. The historic
files SHALL remain in `.agents/skills_backup/` for archaeology but
SHALL be excluded from `mise run lint:skills`.

#### Scenario: Skill rename complete

- **GIVEN** the rename tasks in
  `openspec/changes/cianfhoghlaim-educational-mmo-v1/tasks.md` Phase 2
  are complete
- **WHEN** the user runs `mise run lint:skills`
- **THEN** the count is 127/127 pass (was 123/123 before the rename + new skill)

#### Scenario: tuatha-platform spec is deprecated alias

- **GIVEN** the new `cianfhoghlaim-educational-mmo` spec is canonical
- **WHEN** a developer references `tuatha-platform` in a PR
- **THEN** the `tuatha-platform` spec returns the deprecation notice
- **AND** the developer is redirected to `cianfhoghlaim-educational-mmo`

## REMOVED Requirements

### Requirement: 4 sub-modules (`game/` + `crates/` + `sruth/crypteolas/` + `ui/`)

**Reason**: superseded by the cianfhoghlaim consolidation (v4, 2026-06-28)
and the `cianfhoghlaim-educational-mmo` rebuild (2026-06-30). The
`tuatha/` quadrant has been merged into `cianfhoghlaim/agents/` and the
historic `tuatha/`-named code paths are renamed.
**Migration**: see the v4 consolidation change
`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` and the new
`cianfhoghlaim-educational-mmo` spec.

### Requirement: Babylon.js game front-end

**Reason**: superseded by TanStack Start 2D client (per user choice
of faster MVP). The Babylon.js 7 + WebGPU pattern remains in
`.agents/skills_backup/tuatha-mmo/SKILL.md` as archaeology.
**Migration**: TanStack Start 2D client at
`cianfhoghlaim/web/apps/cianfhoghlaim-mmo/`. The 3D Babylon.js client
is deferred to v2 (no concrete date).

### Requirement: Rust + SpacetimeDB game engine

**Reason**: superseded by Hono + Convex + BetterAuth for v1.
**Migration**: Hono API at `cianfhoghlaim/web/hono-api/`, Convex for
real-time state. SpacetimeDB v2 is deferred to v2.

### Requirement: Crypteolas crypto data platform

**Reason**: the financial-token framing of Crypteolas is not the goal.
The achievement-ledger pattern is reused (off-chain `SkillTreeBadge`)
but the financial token is not.
**Migration**: `cianfhoghlaim/badges/` (hybrid off-chain badge + on-chain
Merkle anchor). The educational credits are issued by the platform as
quest-completion rewards, not as a financial instrument.

### Requirement: Pent-Elemental Cosmology

**Reason**: superseded by NCCA Subject Cosmology (8 subject-themed
realms, no mythological framing).
**Migration**: 8 subject realms in
`cianfhoghlaim/web/apps/cianfhoghlaim-mmo/src/routes/realm/<subject>.tsx`.