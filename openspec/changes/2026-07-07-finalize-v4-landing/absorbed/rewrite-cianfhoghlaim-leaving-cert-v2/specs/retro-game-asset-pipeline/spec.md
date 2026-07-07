# Delta: retro-game-asset-pipeline

## ADDED Requirements

### Requirement: ROM/library ingest

The system SHALL read the existing `romm` library (`bonneagar/stacks/romm/`)
and `Drop-OSS/drop` library for any retro entries outside Romm's native
schema, and SHALL yield a typed `retro_library` DLT resource. The library
SHALL be conditioned on NCCA learning outcomes — never on the source games'
literal assets.

#### Scenario: Romm library ingested as retro_library

- **GIVEN** the operator owns 50+ ROMs in the Romm library at `romm.cianfhoghlaim.ie`
- **WHEN** the DLT source `dlt/retro/library.py` runs
- **THEN** it yields ≥50 `retro_library` rows, one per ROM
- **AND** each row carries `{rom_id, title, platform, sha256, transferable_to_subject: NCCA-Subject[]}` where `transferable_to_subject` is the list of NCCA subjects this ROM's design patterns transfer to

### Requirement: Headless screenshot capture

The system SHALL drive the games via deterministic macro scripts through
the new `libretro-retroarch` stack (Mesen, snes9x, gambatte, mgba,
genesis_plus_gx, pcsx_rearmed). The system SHALL capture PNGs at every
scene transition + every 5 s of gameplay. The screenshots SHALL be saved
via `ludusavi`-managed save states.

#### Scenario: Number Munchers screenshots captured

- **GIVEN** Number Munchers is loaded in the libretro Mesen core
- **WHEN** the macro script runs for 60 s
- **THEN** the screenshot pipeline produces ≥12 PNGs at scene transitions
- **AND** each PNG has a metadata row in the `retro_screenshots` DLT resource with `{rom_id, scene_id, captured_at, scene_metadata}`

### Requirement: SAM3 + SAM-3D-Objects segmentation

The system SHALL segment the sprites + UI regions via **SAM3**
(`facebook/sam3`) — each PNG SHALL be decomposed into typed
`SegmentationMask` records. The system SHALL also synthesise 3D objects
from sprite masks via SAM-3D-Objects (`facebook/sam-3d-objects`).

#### Scenario: Hades boon-selection scene segmented

- **GIVEN** the screenshot of Hades' boon-selection scene
- **WHEN** SAM3 segments the scene with the prompt "boon-card"
- **THEN** the system produces 3 SegmentationMask records (one per boon choice)
- **AND** each mask carries `{mask_id, scene_id, prompt, score, transferable_to_subject}`

### Requirement: VLM design-pattern extraction

The system SHALL extract typed design patterns via the canonical
**Bolmo / Molmo2 / Qwen3-VL** VLM backbone + a BAML function
`ExtractGameDesignPattern(image, game_ctx) -> GameDesignPattern`. The
patterns SHALL be embedded into the `oideachais.retro.design_patterns`
LanceDB table (BGE-large-en-v1.5, 1024-dim) via a v1 CocoIndex App that
reuses the shared `_lifespan.py`.

#### Scenario: Number Munchers drill pattern extracted

- **GIVEN** a screenshot of a Number Munchers drill scene
- **WHEN** `b.ExtractGameDesignPattern(screenshot, "number-munchers", {"subject": "mathematics", "lo_code": "LC-MATHS-LO-2.4"})` runs
- **THEN** the function returns a `GameDesignPattern` with `{pedagogy_pattern: "drill", sprite_archetype: "character-pacman-like", ui_layout: "grid", transferable_to_subject: ["mathematics"], evidence: {screenshot_id, scene_id, scene_metadata}}`
- **AND** the CocoIndex v1 App embeds the pattern into LanceDB with the BGE-large-en-v1.5 1024-dim embedding

### Requirement: Subject-conditioned 2D asset generation

The system SHALL generate subject-conditioned 2D educational assets via
the canonical VLM backbone + Qwen-Image / Flux / Z-Image / FIBO via
InvokeAI. The output SHALL land at
`stedding/asset_generation/2d/<subject>/<asset_id>.png`.

#### Scenario: Mathematics drill sprite generated

- **GIVEN** the Number Munchers drill pattern + the Mathematics LO `LC-MATHS-LO-2.4`
- **WHEN** the FIBO asset generator runs the Mathematics prompt template
- **THEN** it produces ≥1 PNG at `stedding/asset_generation/2d/mathematics/<asset_id>.png`
- **AND** the PNG is uploaded to `s3://cianfhoghlaim-asset-v2/2d/mathematics/<asset_id>.png`

### Requirement: Subject-conditioned 3D asset generation

The system SHALL generate 3D meshes via Microsoft TRELLIS.2-4B + Facebook
SAM-3D-Objects. The output SHALL be uploaded to
`s3://cianfhoghlaim-asset-v2/3d/<subject>/<asset_id>.{glb,usdz}`.

#### Scenario: Mathematics 3D symbol generated

- **GIVEN** the Number Munchers sprite + the Mathematics LO `LC-MATHS-LO-2.4`
- **WHEN** the 3D asset pipeline runs
- **THEN** it produces ≥1 GLB at `s3://cianfhoghlaim-asset-v2/3d/mathematics/<asset_id>.glb`
- **AND** the asset is uploaded via signed R2 URL to the Cianfhoghlaim OS asset gallery

### Requirement: Catalogue + delivery surface

The system SHALL render the catalogue as:
- A marimo notebook at `notebooks/leaving_cert/retro_assets.py` for teacher curation
- A Storybook workspace at `packages/game-assets-storybook/` for the game-asset-facing variant
- A Hermes nightly cron `retro_digest` for new entries

#### Scenario: Catalogue renders per-subject design patterns

- **GIVEN** the marimo notebook at `notebooks/leaving_cert/retro_assets.py`
- **WHEN** the user opens the Mathematics tab
- **THEN** the catalogue lists ≥1 `GameDesignPattern` row per Number Munchers drill scene
- **AND** each row has a click-through link to the generated 2D + 3D asset