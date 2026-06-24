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

The system SHALL provide an **educational-achievement ledger**
at `tuatha/crypteolas/achievements/` (rebranded from the v0
"Crypteolas crypto data platform" per Phase 6 of the 6-phase
refactor plan). The ledger holds **skill-tree badges**, NOT
a financial token.

Per the user's plan: "crypto = educational achievements
(not finance)". The ledger metadata includes:

- The curriculum framework (NCCA / CfE / CfW / CCEA / SQA)
- The level (e.g. JC4 / CfE Third Level / Progression Step 3)
- The learning outcome code (e.g. "JC English OL — LO 2.4")
- The date earned + the agent that issued the badge
- The evidence (a 3-sentence reflection from the player)

x402 micropayments remain in the tech stack but are
**reserved for gated game features only** (cosmetics,
premium quests, paid DLC) — never for educational content.
The v0 financial-token flow (Bitcoin / Ethereum / Solana
settlement) is preserved for the optional paid-DLC path.

#### Scenario: A player earns a skill-tree badge

- **GIVEN** a player completes a NCCA Junior Cycle Gaeilge
  Vocabulary Level 3 quest
- **WHEN** the `quest_guide_agent` validates the completion
- **THEN** the crypteolas ledger records a badge with:
  - `framework: "NCCA"`
  - `level: "JC3"`
  - `subject: "Gaeilge"`
  - `competency: "Vocabulary"`
  - `learning_outcome_code: "JC-Gaeilge-LO-2.4"`
  - `date_earned: <today>`
  - `agent_issuer: "quest_guide_agent"`
  - `evidence: <3-sentence player reflection>`

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

### Requirement: Pent-Elemental Cosmology + Anam Cara

The `tuatha-mmo` skill SHALL model the in-game cosmology
on the five classical Celtic elements (Spirit, Water,
Fire, Earth, Air) plus the **Anam Cara** mechanic. The
`tuatha/game/` quadrant module MUST consume the same
cosmology. The cosmology drives:

- The 5 playable classes
- The 5 quest tracks
- The Soul Level progression system
- The Geasa vow system (binding promises with real
  in-game consequences)

#### Scenario: A new quest content pack is added

- **GIVEN** a developer wants to add a "Water" quest pack
  (river spirits + sovereignty)
- **WHEN** they look at `.agents/skills/tuatha-mmo/SKILL.md`
  + the Anam Cara reference at
  `.agents/skills/tuatha-mmo/references/mythology-pent-elemental-cosmology.md`
- **THEN** the developer sees:
  - The 5 elements (Spirit / Water / Fire / Earth / Air)
  - The Anam Cara mechanic (soulbound NFT + binding vow)
  - The 5 quest tracks (one per element)
  - The Geasa system (binding + status)
- **AND** the new quest pack can be added without
  re-deriving the cosmology

### Requirement: x402 + SIWE + Crypteolas Federated Learning

The `tuatha-mmo` skill SHALL wire together the 3 crypto
primitives (x402 payments, SIWE auth, Crypteolas
federated learning) into the MMO economy. The canonical
flow:

1. Player signs in via SIWE (Ethereum wallet) → Pocket ID
   OIDC JWT
2. Player buys in-game item → x402 HTTP 402 paywall
3. Player's model is updated locally (Flower) → federated
   round on Crypteolas infrastructure

The three protocols share the same wallet identity
(sovereign game state in SpacetimeDB, the
`AnamCara-NFT`).

#### Scenario: A player buys a soulbound NFT

- **GIVEN** a player is on the Tuatha MMO dashboard with
  a valid SIWE session
- **AND** the player clicks "Purchase Anam Cara NFT"
- **WHEN** the FastAPI endpoint receives the request
- **THEN** the endpoint returns HTTP 402 with the
  x402-payment-required header
- **AND** the player signs the payment authorization
- **AND** the endpoint mints the Anam Cara NFT (ERC-5114
  SBT) on Solana via Metaplex Core
- **AND** the new NFT is bound to the player's SIWE
  wallet in SpacetimeDB

#### Scenario: A new Crypteolas federated round starts

- **GIVEN** the Crypteolas Flower server has scheduled a
  new training round
- **WHEN** 5+ player clients check in
- **THEN** the server distributes the current model
  weights
- **AND** each client trains locally on its private data
- **AND** the clients return only the gradient updates
  (not the data)
- **AND** the server aggregates the gradients
- **AND** the updated model is signed and stored in
  SpacetimeDB for the next round

### Requirement: British Isles formative assessment focus

The system SHALL implement the British Isles formative
assessment pedagogical framework documented in
`.agents/skills/british-isles-formative-assessment/`. The
framework has 4 components:

1. **5 British Isles curriculum frameworks** (NCCA IE / CfE
   SCT / CfW WLS / CCEA NI / SQA SCT post-16) — each
   framework is a "realm" in the Pent-Elemental Cosmology
   (Spirit / Water / Fire / Earth / Air + Anam Cara).
2. **4 formative feedback channels** (the 4 tuatha ADK
   agents at `oideachais/agents/adk/`: Celtic Tutor,
   Mythology Narrator, Quest Guide, Research Assistant).
   Each agent delivers per-quest, per-response,
   per-misconception feedback. The player always leaves
   with progress + feedback, never a binary right/wrong.
3. **3 quest types** — language quests, cultural quests,
   story quests. Each has a completion criterion that
   maps to a learning outcome from the relevant national
   curriculum.
4. **4 graduated hint levels** — Level 1: subtle nudge →
   Level 2: specific guidance → Level 3: direct but
   incomplete → Level 4: step-by-step. The Quest Guide
   agent starts at Level 1 and escalates as the player
   makes unsuccessful attempts.

The framework is **formative, not summative**. The
Leaving Cert / GCSE / A-Level summative exams are out
of scope. The MMO gives continuous feedback during
learning, not a final grade at the end of a term.

#### Scenario: A player completes a formative language quest

- **GIVEN** a player is on a JC Gaeilge vocabulary
  collection quest
- **WHEN** the player attempts the quest
- **THEN** the `celtic_tutor_agent` delivers per-response
  formative feedback (live pronunciation + grammar)
- **AND** the `quest_guide_agent` provides graduated
  hints (Level 1: subtle nudge if stuck; escalates to
  Level 4: step-by-step after 3 unsuccessful attempts)
- **AND** upon completion, the `quest_guide_agent`
  validates the transfer test (reproduce the answer in 3
  different contexts) and issues a skill-tree badge via
  the crypteolas ledger
- **AND** the player always leaves with progress +
  feedback, never a binary right/wrong

#### Scenario: A player works across all 5 British Isles frameworks

- **GIVEN** a player has earned at least 1 badge in each
  of the 5 frameworks (NCCA / CfE / CfW / CCEA / SQA)
- **WHEN** the player revisits the MMO dashboard
- **THEN** the player sees a "Cross-British-Isles
  Achiever" badge (1 per Pent-Elemental Cosmology
  realm: Spirit / Water / Fire / Earth / Air)
- **AND** the badge records the 5 source-framework
  badges + the date the cross-framework achievement
  was earned

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
