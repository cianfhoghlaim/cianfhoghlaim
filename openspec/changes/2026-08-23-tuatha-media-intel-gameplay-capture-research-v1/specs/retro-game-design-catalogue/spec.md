# Spec Delta: retro-game-design-catalogue

## ADDED Requirements

### Requirement: 4 new work-class sources for the `ExtractGameDesignPattern` BAML function

The system SHALL extend the existing `ExtractGameDesignPattern`
BAML function with 4 new work-class source surfaces:

1. **Comics** — `comic_game_design_pattern` (Class A)
   - 5 v1 sources: Jonathan Hickman's Marvel run (FF
     #570-611, FF #1-23, Future Foundation, Avengers 2012,
     New Avengers 2013, Infinity, Secret Wars 2015, House
     of X, Powers of X, X-Men 2019, Krakoa crossovers)
   - 5 v2 stubbed sources: Morrison `Batman Incorporated`,
     Tomasi `Super Sons`, Johns `Green Lantern`, Valiant
     `Harbinger`, Gillen `The Power Fantasy`
2. **Prose** — `prose_game_design_pattern` (Class B)
   - 1 v1 source: The Wheel of Time (the 0-pixel control;
     the saidar/saidin gendered magic + the Aes Sedai
     institution + the White Tower / Black Ajah social
     structure + the Whitecloak / Children of the Light
     antagonist design + the Forsaken as boons-by-tier
     analogues)
3. **Moving media** — `animation_game_design_pattern` (Class C)
   - 1 v1 source: Avatar: The Last Airbender + The Legend
     of Korra + the Aang-film continuity
4. **Games** — `gameplay_game_design_pattern` (Class D)
   - 1 v1 source: Hades 1 + Hades 2 + World of Warcraft +
     Golden Sun (GBA via `romm`) + Pokémon (GB/GBA) +
     DragonBox (iOS) + Duolingo (iOS) + Bejeweled (iOS)
   - Per-title ownership audit required for v2 (per the
     `media-intel-corpus` legal capture boundary)

#### Scenario: A Wheel of Time passage is processed for game design

- **GIVEN** the `retro_prose_wot` DLT source materialises
  a Wheel of Time passage (e.g. Rand al'Thor's first
  channelling in The Eye of the World)
- **WHEN** the `ExtractGameDesignPattern` BAML function
  runs with `medium = "prose"`, `vlm_primary = "qwen3.6-27b-mtp"`
  (the prose-specialist model per
  `multimodal-code-and-media-intel` spec)
- **THEN** the function emits a `GameDesignPattern` record
  with `magic_system: "one_power"`, `gender_split:
  ["saidar", "saidin"]`, `institutions: ["Aes Sedai",
  "Asha'man", "White Tower"]`, `antagonists:
  ["Forsaken", "Dark One"]`
- **AND** the record's `transferability.in_game_mechanic`
  is `4_plus_1_gender_agnostic_chanelling` (the WoT → Tuatha
  transfer)

### Requirement: 4 missing Docker Compose stacks stood up

The system SHALL provide 4 new 6-file GOLD_STANDARD stacks
at `bonneagar/stacks/`:

- `comfyui/` (ComfyUI node-graph image gen wired to
  `unsloth-serve` + HF models from the *same providers* as
  the OCR_VISION-24 family)
- `libretro-retroarch/` (headless libretro + 6 cores:
  Mesen, snes9x, gambatte, mgba, genesis_plus_gx,
  pcsx_rearmed)
- `sam3-server/` (Facebook SAM3 image segmentation, Apache
  2.0)
- `sam3d-objects-server/` (Facebook SAM-3D-Objects, Apache
  2.0)

Each stack SHALL pass `mise run devops:validate-stacks`.

#### Scenario: The `libretro-retroarch` stack is deployed

- **GIVEN** the stack files at
  `bonneagar/stacks/libretro-retroarch/` are committed
- **WHEN** the `mise run devops:validate-stacks` gate runs
- **THEN** the gate reports the stack as PASS
- **AND** the Komodo procedure
  `deploy-libretro-retroarch-{bunchloch,arm1-oci}.toml`
  SHALL deploy the stack to both target hosts
- **AND** the Locket sidecar SHALL inject the
  `libretro-retroarch` secrets from Infisical

#### Scenario: The `sam3-server` stack is integrated with the retro screenshot capture

- **GIVEN** the `libretro-retroarch` stack has captured
  PNGs of Golden Sun scenes
- **WHEN** the `SegmentGameScreenshot` BAML function
  (already defined in the `retro-game-design-catalogue`
  spec) calls the `sam3-server` API
- **THEN** the `sam3-server` returns a `SegmentationMask`
  with `masks: list[Mask]` for each Djinn sprite
- **AND** the captured sprite masks are stored in the
  `retro_sprite_masks` Convex table
