# Tuatha Platform Capability

## Purpose

`tuatha-platform` is a capability of the Cianfhoghlaim platform. The
corresponding source code lives at `tuatha/` (the Celtic educational
MMO + crypto platform, ~15K+ LOC, registered as a top-level uv
workspace member). See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This is the first openspec spec for the tuatha quadrant.

## Background

The tuatha quadrant houses the Celtic educational MMO (Massively
Multiplayer Online game) and the `crypteolas` crypto data platform.
The 4 sub-modules are:

- `tuatha/game/` — the Babylon.js game front-end (the MMO client)
- `tuatha/crates/` — the Rust + SpacetimeDB game engine (the MMO
  server)
- `tuatha/crypteolas/` — the crypto data platform (uses Bitcoin,
  Ethereum, Solana, SpacetimeDB as a settlement layer)
- `tuatha/ui/` — the TanStack Start front-end for the educational
  game and the BAML-driven Celtic content extraction

The tuatha quadrant is registered in the root `dg.toml` as a
Dagster code-location (with `tuatha/dg.toml` for the local code-location
config). The BAML schemas for the tuatha UI components are in
`baml_src/ui_components.baml` and `baml_src/image_generation.baml`.

The tuatha content extends into croilar: the croilar personal-portfolio
site has a `game` subproject that consumes the tuatha MMO content, and
the 3 personas (aleyum, cianfhoghlaim, carlcashman) each have a
`wow` or `Hades II` content surface (see `tuatha/wow/` and
`tuatha/Hades II/`).
## Requirements
### Requirement: 4 sub-modules

The system SHALL declare 4 sub-modules in `tuatha/`:
`game/` (Babylon.js front-end), `crates/` (Rust + SpacetimeDB game
engine), `crypteolas/` (crypto data platform), `ui/` (TanStack Start
front-end).

#### Scenario: Sub-modules import

- **GIVEN** the venv is installed via `uv sync`
- **WHEN** a user runs `uv run python -c "import tuatha"`
- **THEN** the import succeeds

### Requirement: Babylon.js game front-end

The system SHALL provide a Babylon.js game front-end in `tuatha/game/`
for the Celtic educational MMO.

#### Scenario: Babylon.js scene renders

- **GIVEN** the Babylon.js scene at `tuatha/game/scenes/celtic_world.ts`
- **WHEN** the game is launched
- **THEN** the scene renders the Celtic world (Túatha Dé Danann
  characters, Irish landscape, BAML-driven NPC dialogue)

### Requirement: Rust + SpacetimeDB game engine

The system SHALL provide a Rust + SpacetimeDB game engine in
`tuatha/crates/` for the MMO server.

#### Scenario: SpacetimeDB server starts

- **GIVEN** the SpacetimeDB server module at
  `tuatha/crates/game_server/src/lib.rs`
- **WHEN** `cargo run --release` runs
- **THEN** the SpacetimeDB server starts on port 3000
- **AND** the server registers the Celtic-world tables (Player,
  NPC, Quest, Achievement)

### Requirement: Crypteolas crypto data platform

The system SHALL provide a crypto data platform at
`tuatha/crypteolas/` that uses Bitcoin, Ethereum, Solana, and
SpacetimeDB as a settlement layer for in-game transactions.

#### Scenario: In-game transaction settles

- **GIVEN** a player completes a quest and earns 100 CELT (the
  in-game currency)
- **WHEN** the crypteolas module processes the transaction
- **THEN** the transaction is signed with the player's wallet
- **AND** the transaction is settled on SpacetimeDB
- **AND** the player's CELT balance is updated

### Requirement: TanStack Start UI

The system SHALL provide a TanStack Start UI at `tuatha/ui/` for the
educational game and the BAML-driven Celtic content extraction.

#### Scenario: BAML UI component renders

- **GIVEN** a BAML `UIComponent` extracted by the
  `b.ExtractUIComponent` function (see `oideachais-baml-schemas` spec)
- **WHEN** the UI renders the component
- **THEN** the component is rendered with the appropriate props and
  layout

### Requirement: Dagster code-location registration

The system SHALL register tuatha as a Dagster code-location in the
root `dg.toml` (via `tuatha/dg.toml`).

#### Scenario: Code-location loads

- **GIVEN** the root `dg.toml` is configured with the tuatha
  code-location
- **WHEN** `dg dev` starts the Dagster UI
- **THEN** the tuatha code-location appears in the UI

### Requirement: BAML Celtic content extraction

The system SHALL provide BAML extraction for Celtic content via
`baml_src/ui_components.baml` and `baml_src/image_generation.baml`.

#### Scenario: UI component extracted

- **GIVEN** a UI mockup screenshot of a Celtic-themed component
- **WHEN** `b.ExtractUIComponent` is called
- **THEN** the function returns a `UIComponent` with the
  Celtic-themed props

#### Scenario: Celtic image generated

- **GIVEN** an image prompt "a Celtic round tower at sunset"
- **WHEN** `b.GenerateImage` is called
- **THEN** the function returns a `GeneratedImage` with the prompt
  and the image URL (stored in Cloudflare R2)

### Requirement: Croilar consumer integration

The system SHALL expose the tuatha content to the croilar
personal-portfolio platform.

#### Scenario: croilar consumes tuatha content

- **GIVEN** a tuatha quest "The Battle of Moytura" is published
- **WHEN** the croilar `game` subproject renders the player's
  personal game history
- **THEN** the croilar site displays the quest with the tuatha
  Babylon.js scene

### Requirement: Modal burst-training handoff

The system SHALL support handing off ML training jobs that
exceed MacBook M4 capacity (>13B parameter models, multi-GPU
training, or full-corpus processing) to Modal's H100 GPU pool,
with the trained artifacts synced back to Garage S3 for
llama-swap local serving.

#### Scenario: Modal H100 training handoff

- **GIVEN** a BAML extraction / Unsloth / TRL training script
  configured for local execution on `bunchloch` (M4 Mac)
- **WHEN** the training run is wrapped in a Modal decorator
  (`@app.function(gpu="H100", timeout=7200)`) and executed
  via `modal run --detach training.py`
- **THEN** Modal SHALL provision an H100, execute the
  training, and upload the resulting model artifacts to the
  configured S3 bucket
- **AND** the artifacts SHALL be downloadable back to
  `bunchloch` for llama-swap serving

### Requirement: Babylon.js game client (3D)

The system SHALL provide a Babylon.js-based 3D game client
at `tuatha/game/` for the Celtic Educational MMO, rendering
interactive 3D learning environments (mathematical concepts
spatially, Celtic language family tree, gamified study areas)
via WebGL + WebGPU with Havok physics, particle systems, and
GLTF 2.0 asset loading.

#### Scenario: 3D scene renders

- **GIVEN** a student launches the Tuatha MMO client at
  `tuatha/game/`
- **WHEN** the Babylon.js Engine + Scene + ArcRotateCamera
  initialise and the GLTFLoader loads the scene assets
- **THEN** the 3D classroom / mathematical-concept / Celtic-language
  scene SHALL render at ≥60 fps on a modern GPU
- **AND** the Convex real-time state sync SHALL drive NPC
  positions, BAML-extracted dialogue, and Dagster-pipeline
  asset updates

## Cross-references

- [`tuatha/`](../../tuatha/) (the MMO + crypto quadrant)
- [`tuatha/README.md`](../../tuatha/README.md) (the overview)
- [`tuatha/AGENTS.md`](../../tuatha/AGENTS.md) (the developer-quick-reference, created by this change)
- [`tuatha/dg.toml`](../../tuatha/dg.toml) (the local Dagster code-location config)
- [`baml_src/ui_components.baml`](../../baml_src/ui_components.baml) (the UI component BAML)
- [`baml_src/image_generation.baml`](../../baml_src/image_generation.baml) (the image generation BAML)
- [`croilar/apps/web/`](../../croilar/apps/web/) (the croilar consumer)
- [`openspec/specs/oideachais-baml-schemas/spec.md`](../oideachais-baml-schemas/spec.md) (the shared BAML stack)
- [`openspec/specs/agentic-frontend-frameworks/spec.md`](../agentic-frontend-frameworks/spec.md) (the shared TanStack Start stack)
