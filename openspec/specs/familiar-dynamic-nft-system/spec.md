# Familiar Dynamic NFT System Capability

## Purpose

`familiar-dynamic-nft-system` is the Convex + Anam Progression Agent
+ AG-UI card surface that lets each player mint a unique Familiar
NFT per Celtic mythological creature they discover. The card evolves
as the player visits Ogham stones, completes mythology quests, and
levels up curriculum outcomes.

This capability is referenced by:
- `openspec/changes/2026-09-29-familiar-dynamic-nft-system-v1`
- `openspec/changes/2026-09-08-ogham-celtic-stones-pipeline-v1`

## Requirements

### Requirement: Convex tables

The system SHALL maintain 4 Convex tables: `familiars`,
`anam_particles`, `familiar_evolution_log`, `ogham_stones` (the
last shared with the ogham pipeline).

### Requirement: Anam Progression Agent

The system SHALL expose an `Anam Progression Agent` that watches
`anam_particles` writes and emits `familiar_evolution_log` rows when
a particle count threshold is crossed.

### Requirement: AG-UI Familiar card

The system SHALL emit an AG-UI Familiar card on the player's
profile page that shows the creature name, mythology citation, and
evolution history.

### Requirement: Soulbound invariant

Every Familiar SHALL be soulbound to its original player — no
transfer is permitted (per the Learn-to-Earn x402 credential pipeline).
