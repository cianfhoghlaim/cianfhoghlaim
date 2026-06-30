# Delta: retro-game-design-catalogue

## ADDED Requirements

### Requirement: ROMM + Drop-OSS library ingest

The system SHALL provide a `retro_library` DLT resource that lists
every game entry from the existing `romm` (v3.x) library AND from the
new `Drop-OSS/drop` stack. Each row SHALL include the canonical
`game_id`, `platform`, `title`, `year`, `igdb_id`,
`cover_art_url`, `rom_sha256`, `save_state_paths[]`, and SHALL be
keyed by `(platform, game_id)`. The resource SHALL be read-only with
respect to the source libraries and SHALL NOT write back to ROMM or
Drop-OSS.

#### Scenario: A new ROM is added to ROMM

- **GIVEN** an operator has added a new retro game to the ROMM
  library at `romm.cianfhoghlaim.ie`
- **WHEN** the `retro_library_watcher` Dagster sensor polls
  `GET /api/roms` and finds the new ROM
- **THEN** a new row is appended to the `retro_library` DLT resource
  with `platform`, `game_id`, `title`, `rom_sha256`,
  `save_state_paths[]`
- **AND** the `retro_screenshots` materialisation runs for the new
  game within the same sensor tick

#### Scenario: A game is in Drop-OSS but not in ROMM

- **GIVEN** a retro game is listed in `Drop-OSS/drop` at
  `drop.cianfhoghlaim.ie` but is missing from ROMM
- **WHEN** the `retro_library` source materialises
- **THEN** the row is yielded from the Drop-OSS source
- **AND** the row's `source_library = "drop-oss"` (whereas the
  ROMM-sourced rows have `source_library = "romm"`)

### Requirement: Headless screenshot capture via libretro

The system SHALL provide a `retro_screenshots` DLT resource that drives
each retro game through the `libretro-retroarch` headless stack and
captures one PNG per scene transition + one PNG every 5 seconds during
gameplay. Each row SHALL include the
`platform`, `game_id`, `level_index`, `scene_id`, `frame_id`,
`scene_type` (one of `"title" | "menu" | "gameplay" | "boss" |
"minigame" | "end"`), the PNG `path` (relative to
`stedding/ingest_queue/retro/`), and the PNG `sha256`. Save states
SHALL be loaded via `ludusavi` (the existing
`bonneagar/stacks/ludusavi/` volume mount). The first iteration SHALL
support the 6 platforms NES, SNES, GB, GBA, Genesis, PS1 via their
canonical libretro cores (`mesen`, `snes9x`, `gambatte`, `mgba`,
`genesis_plus_gx`, `pcsx_rearmed`).

#### Scenario: Number Munchers title screen captured

- **GIVEN** the `number_munchers` game is in the `retro_library`
  resource with `platform = "nes"` and `rom_sha256 = "abc..."`
- **WHEN** the `retro_screenshots` asset materialises
- **THEN** ≥1 row is produced with `scene_type = "title"` and the PNG
  stored at `stedding/ingest_queue/retro/nes/number_munchers/title.png`
- **AND** the row's `sha256` matches the PNG file's actual SHA-256

#### Scenario: Deterministic macro reaches the first level

- **GIVEN** the `oregon_trail` macro script
  `oregon_trail_title_to_choose_path.py` is registered
- **WHEN** the macro runs on libretro
- **THEN** ≥5 PNGs are captured covering the title screen → main menu
  → choose-your-path screen
- **AND** all 3 frame transitions are typed as `scene_type`
  (`"title" → "menu" → "gameplay"`)

#### Scenario: Save state is restored from ludusavi

- **GIVEN** `ludusavi` has a save state for `number_munchers` slot 7
- **WHEN** the screenshot capture loop runs
- **THEN** `ludusavi restore --game number_munchers --slot 7` is
  executed before the macro starts
- **AND** the resulting screenshots reflect the loaded save state
  (verified by a checksum of the visible game-state pixels)

### Requirement: SAM3 + SAM-3D-Objects segmentation

The system SHALL provide BAML functions
`SegmentGameScreenshot(image: Image, prompt: str, ...) -> SegmentationMask`
and
`SpriteTo3D(sprite_mask: SegmentationMask, sprite_image: Image, format: "glb" | "usdz") -> str`
backed by the `sam3-server` (`facebook/sam3`, Apache 2.0) and
`sam3d-objects-server` (`facebook/sam-3d-objects`, Apache 2.0) stacks.
The Python wrapper SHALL live at
`cianfhoghlaim/meaisinfhoghlaim/segmentation/sam3.py` and
`sam3d-objects.py`. Each segmentation call SHALL produce a typed
`SegmentationMask` with `masks: list[Mask]` and the
`SpriteTo3D` call SHALL output to `s3://cianfhoghlaim-asset-v2/3d/`
for the 3D-path consumers.

#### Scenario: A screenshot is segmented

- **GIVEN** a `retro_screenshots` row with `scene_type = "menu"` and
  `game_id = "carmen_sandiego"`
- **WHEN** the `SegmentGameScreenshot` BAML function is called with
  `prompt = "every UI element with text overlay"`
- **THEN** a `SegmentationMask` is returned with ≥3 masks
  (one per UI region: evidence board, action buttons, location map)

#### Scenario: A sprite mask is converted to 3D

- **GIVEN** a sprite mask from `number_munchers.title` and the title
  PNG as `sprite_image`
- **WHEN** `SpriteTo3D(mask, image, format = "glb")` is called
- **THEN** a `.glb` file is uploaded to
  `s3://cianfhoghlaim-asset-v2/3d/number_munchers/title.glb`
- **AND** the file is ≤ 5 MB and includes UV-mapped sprite pixels

### Requirement: VLM design-pattern extraction

The system SHALL provide a BAML function
`ExtractGameDesignPattern(image: Image, game_ctx: GameContext) -> GameDesignPattern`
backed by the canonical Bolmo / Molmo2 / Qwen3-VL VLM backbone (per
`openspec/specs/celtic-asset-generation/spec.md` and
`openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`). The function SHALL
return a typed `GameDesignPattern` with the
`UIPattern[]`, `SpriteArchetype[]`,
`PedagogyPattern[]`, `BilingualPatternText`, and a per-subject
`transferable_to_subject: list[str]` (one or more of the 8 NCCA
subjects). The extraction MUST populate both `text_en` and `text_ga`
when the source game has a GA equivalent. The function SHALL write the
typed result to the `retro_design_patterns` DLT resource. A CocoIndex
v1 App SHALL embed the patterns (BGE-large-en-v1.5, 1024-dim) into
the `oideachais.retro.design_patterns` LanceDB table.

#### Scenario: Carmen Sandiego yields NCCA-relevant patterns

- **GIVEN** a `retro_screenshots` row from
  `carmen_sandiego.scene_evidence_board`
- **WHEN** the `ExtractGameDesignPattern` BAML function runs
- **THEN** the `GameDesignPattern` has ≥1 `UIPattern` typed as
  `"evidence_board"` AND ≥1 `SpriteArchetype` typed as `"character"`
  AND ≥1 `PedagogyPattern` typed as `"exploration"`
- **AND** `transferable_to_subject` contains `"history"` and
  `"english"` AND `"gaeilge"` (because the puzzle format maps to
  multiple NCCA subjects)
- **AND** the row is embedded in
  `oideachais.retro.design_patterns` LanceDB table with a
  BGE-large-en-v1.5 1024-dim vector

#### Scenario: Gaeilge source game populates bilingual fields

- **GIVEN** a `retro_screenshots` row from an Irish-language retro
  source (e.g., `An Ghaeilge Bheo`)
- **WHEN** the BAML function runs with `game_ctx.language = "ga"`
- **THEN** the resulting `BilingualPatternText.text_ga` is non-null
- **AND** `BilingualPatternText.text_en = null` (mirroring the
  existing Gaeilge-only pattern from
  `openspec/specs/ncca-formative-assessment/spec.md`)

### Requirement: Subject-conditioned asset generation (2D + 3D in parallel)

The system SHALL provide a `GenerateSubjectAsset` BAML function
dispatching per subject (`chemistry`, `geography`, `mathematics`,
`history`, `english`, `gaeilge`, `computer_science`,
`applied_mathematics`) and an `SynthesizeAsset3D` BAML function
dispatching per subject, with the 2D function targeting one of
`flux`, `z-image-turbo`, `qwen-image`, `fibo` (callable via the
existing `invokeai` stack + the new `fibo-server` stack + the existing
`mlx-omni` Qwen-Image path) and the 3D function targeting
`microsoft/TRELLIS.2-4B` + `facebook/sam-3d-objects` via the
`trellis-server` + `sam3d-objects-server` stacks. The function SHALL
take `(syllabus_lo: LearningOutcome, design_pattern: GameDesignPattern,
sprite_mask: SegmentationMask)` and return an
`AssetPrompt { positive_prompt, negative_prompt, model, seed }` for
2D, or a `"glb" | "usdz"` path for 3D. The 2D output SHALL land at
`stedding/asset_generation/2d/<subject>/<asset_id>.png` and the 3D
output SHALL land at
`s3://cianfhoghlaim-asset-v2/3d/<subject>/<asset_id>.{glb,usdz}`.

#### Scenario: 2D chemistry molecule asset is generated

- **GIVEN** a `LearningOutcome` `LC-CHEM-LO-2.4` (chemistry) and a
  matched `GameDesignPattern` from `carmen_sandiego`
- **WHEN** `GenerateSubjectAsset(subject = "chemistry", ...)` runs
  with `model = "flux"`
- **THEN** the resulting PNG lands at
  `stedding/asset_generation/2d/chemistry/<asset_id>.png`
- **AND** the asset is referenced by `<subject>` papers in the MMO
  client (TanStack Start 2D)

#### Scenario: 3D geography coast asset is generated

- **GIVEN** a `LearningOutcome` `LC-GEOG-LO-3.7` (geography — coastal
  processes) and a `SpriteArchetype` for "tile: rock-formation"
- **WHEN** `SynthesizeAsset3D(subject = "geography", ..., format = "glb")`
  runs
- **THEN** a `.glb` file lands at
  `s3://cianfhoghlaim-asset-v2/3d/geography/coast_drift.glb`
- **AND** the same call with `format = "usdz"` produces a parallel
  `.usdz` at the same key prefix

#### Scenario: Homoage-style art is distinct from source

- **GIVEN** any 2D asset generated from
  `GenerateSubjectAsset(subject = "chemistry", ...)`
- **WHEN** the operator runs the copyright-safety check
- **THEN** the per-asset CLIP-similarity score to the source
  `retro_screenshots` row is ≤ 0.55 (the v1 threshold)
- **AND** the per-asset structural-similarity (SSIM) score to the
  source sprite mask is ≤ 0.4

### Requirement: Catalogue delivery (marimo dashboard + Storybook + pxlkit + retroassembly)

The system SHALL expose the design-pattern catalogue through:

1. A marimo notebook at
   `cianfhoghlaim/notebooks/retro_game_design_catalogue.py`
   rendering per-pattern thumbnails + bilingual labels + click-through
   to the generated assets.
2. A Storybook workspace at
   `packages/game-assets-storybook/` rebuilt as a static export and
   served by the (fixed) `storybook` stack.
3. A `retroassembly` import pipeline that uploads the atlases +
   metadata after every materialisation.
4. A pxlkit sprite-atlas pipeline that produces one
   `stedding/asset_generation/2d/<subject>/atlas.png` per subject
   per materialisation.

The Storybook workspace, the marimo dashboard, and the MMO teacher
view (per
`openspec/specs/cianfhoghlaim-educational-mmo/spec.md`) SHALL all
reference the same `oideachais.retro.design_patterns` LanceDB table.

#### Scenario: The marimo dashboard renders the catalogue

- **GIVEN** the `retro_design_patterns` DLT resource has ≥10 typed
  patterns after Phase 3 materialisation
- **WHEN** the operator runs
  `marimo edit cianfhoghlaim/notebooks/retro_game_design_catalogue.py`
- **THEN** the notebook renders a table with ≥10 rows
- **AND** each row has a thumbnail (the segmented sprite), a
  bilingual label, a `transferable_to_subject` tag list, and a
  link to the generated asset in `stedding/asset_generation/2d/`

#### Scenario: Storybook static export builds clean

- **GIVEN** the operator runs `bun run build` in
  `packages/game-assets-storybook/`
- **WHEN** the build completes
- **THEN** `packages/game-assets-storybook/storybook-static/` is
  populated with ≥3 sidebar categories (one per design-pattern
  type)
- **AND** the (fixed) `storybook` stack serves the export at
  `storybook.cianfhoghlaim.ie`

#### Scenario: pxlkit atlas is regenerated

- **GIVEN** a `GenerateSubjectAsset` materialisation has just added
  4 new PNGs to `stedding/asset_generation/2d/chemistry/`
- **WHEN** the asset-generation Dagster group materialises
- **THEN** `stedding/asset_generation/2d/chemistry/atlas.png` is
  regenerated via the pxlkit CLI
- **AND** the atlas contains the 4 new PNGs in a grid layout (one
  per sprite category)
