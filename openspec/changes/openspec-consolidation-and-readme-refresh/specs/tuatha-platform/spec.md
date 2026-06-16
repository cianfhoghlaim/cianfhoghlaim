## ADDED Requirements

The `tuatha-platform` capability is the first openspec spec for the
tuatha quadrant. The full Requirements + Scenarios are in the
canonical spec at `openspec/specs/tuatha-platform/spec.md`.

### Requirement: 4 sub-modules

The system SHALL declare 4 sub-modules in `tuatha/`:
`game/` (Babylon.js front-end), `crates/` (Rust + SpacetimeDB game
engine), `crypteolas/` (crypto data platform), `ui/` (TanStack Start
front-end).

#### Scenario: Sub-modules import

- **WHEN** a user runs `uv run python -c "import tuatha"`
- **THEN** the import succeeds

### Requirement: Babylon.js + Rust + SpacetimeDB

The system SHALL provide a Babylon.js game front-end and a Rust +
SpacetimeDB game engine for the Celtic educational MMO.

#### Scenario: MMO server starts

- **WHEN** `cargo run --release` runs in `tuatha/crates/game_server/`
- **THEN** the SpacetimeDB server starts on port 3000

### Requirement: Crypteolas crypto platform

The system SHALL provide a crypto data platform at
`tuatha/crypteolas/` that uses Bitcoin, Ethereum, Solana, and
SpacetimeDB as a settlement layer for in-game transactions.

#### Scenario: In-game transaction settles

- **WHEN** a player completes a quest and earns 100 CELT
- **THEN** the crypteolas module processes the transaction via
  SpacetimeDB

### Requirement: BAML Celtic content extraction

The system SHALL provide BAML extraction for Celtic content via
`baml_src/ui_components.baml` and `baml_src/image_generation.baml`.

#### Scenario: Celtic image generated

- **WHEN** `b.GenerateImage("a Celtic round tower at sunset")` is called
- **THEN** the function returns a `GeneratedImage` with the image URL

### Requirement: Croilar consumer integration

The system SHALL expose the tuatha content to the croilar
personal-portfolio platform.

#### Scenario: croilar consumes tuatha content

- **WHEN** a tuatha quest is published
- **THEN** the croilar `game` subproject renders the quest with the
  tuatha Babylon.js scene
