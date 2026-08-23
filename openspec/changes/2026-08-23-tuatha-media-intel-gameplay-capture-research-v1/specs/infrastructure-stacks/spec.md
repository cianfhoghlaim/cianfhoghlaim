# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: `comfyui` stack (ComfyUI node-graph image gen)

The system SHALL provide a `comfyui` Docker Compose stack
at `bonneagar/stacks/comfyui/` with the 6-file
GOLD_STANDARD pattern (`compose.yaml`, `sidecar.yaml`,
`secrets.env`, `pangolin.yaml`, `blueprint.yaml`,
`.env.example`).

The stack SHALL wire ComfyUI to the `unsloth-serve` stack
+ HuggingFace models from the *same providers* as the
OCR_VISION-24 family (Flux, Z-Image-Turbo, Qwen-Image,
FIBO per the `celtic-asset-generation` spec).

The stack SHALL expose the ComfyUI REST API at
`comfyui.cianfhoghlaim.ie:8188` (the Locket sidecar at
`:8181` is the existing lakehouse port — ComfyUI uses the
distinct `:8188` to avoid collision).

#### Scenario: A ComfyUI generation request is made

- **GIVEN** a `MediaDescriptor` row exists with
  `transferability.palette_token = "earth"`,
  `transferability.particle_effect = "spark"`
- **WHEN** the `celtic-asset-generation` exporter calls
  the ComfyUI REST API with the
  `comfyui_workflows/earth_spark.json` workflow
- **THEN** ComfyUI returns the generated sprite atlas
- **AND** the response is logged to
  `firecrawl_meta.scrapes` (if any Firecrawl call was
  involved) + to the ComfyUI access log

### Requirement: `libretro-retroarch` stack (headless libretro + 6 cores)

The system SHALL provide a `libretro-retroarch` Docker
Compose stack at `bonneagar/stacks/libretro-retroarch/`
with the 6-file GOLD_STANDARD pattern.

The stack SHALL bundle the 6 canonical libretro cores:
`mesen` (NES), `snes9x` (SNES), `gambatte` (GB),
`mgba` (GBA), `genesis_plus_gx` (Genesis), `pcsx_rearmed`
(PS1). The stack SHALL expose the libretro netcommand
interface for deterministic macro-driven gameplay capture.

The stack SHALL be the runtime for the
`retro-game-design-catalogue` spec's `retro_screenshots`
DLT resource.

#### Scenario: A Golden Sun screenshot is captured

- **GIVEN** the `golden_sun` ROM is in the `romm` library
- **AND** the `libretro-retroarch` stack is running with
  the `mgba` core
- **WHEN** the `retro_screenshots` Dagster sensor runs
  the `golden_sun_title_to_venus_lighthouse.py` macro
- **THEN** the libretro netcommand interface loads the ROM
  + the `ludusavi` save state (slot 1)
- **AND** the screenshot capture loop runs for 60 seconds
- **AND** ≥12 PNGs are written to
  `stedding/ingest_queue/retro/gba/golden_sun/`

### Requirement: `sam3-server` stack (Facebook SAM3 image segmentation)

The system SHALL provide a `sam3-server` Docker Compose
stack at `bonneagar/stacks/sam3-server/` with the 6-file
GOLD_STANDARD pattern. The stack SHALL host
`facebook/sam3` (Apache 2.0) and SHALL expose a REST API
for prompt-based image segmentation.

The stack SHALL be the runtime for the
`SegmentGameScreenshot` BAML function (per the
`retro-game-design-catalogue` spec).

#### Scenario: A sprite is segmented from a Golden Sun screenshot

- **GIVEN** a Golden Sun screenshot is in the
  `stedding/ingest_queue/retro/gba/golden_sun/` queue
- **WHEN** the `SegmentGameScreenshot` BAML function
  calls the `sam3-server` API with
  `image: <png>`, `prompt: "the Djinn sprite in the center
  of the screen"`
- **THEN** the API returns a `SegmentationMask` with the
  Djinn sprite isolated
- **AND** the mask is stored in the
  `retro_sprite_masks` Convex table

### Requirement: `sam3d-objects-server` stack (Facebook SAM-3D-Objects)

The system SHALL provide a `sam3d-objects-server` Docker
Compose stack at `bonneagar/stacks/sam3d-objects-server/`
with the 6-file GOLD_STANDARD pattern. The stack SHALL
host `facebook/sam-3d-objects` (Apache 2.0) and SHALL
expose a REST API for sprite-to-3D conversion.

The stack SHALL be the runtime for the `SpriteTo3D` BAML
function (per the `retro-game-design-catalogue` spec).

#### Scenario: A Djinn sprite is converted to a 3D mesh

- **GIVEN** a Djinn sprite mask is in the
  `retro_sprite_masks` Convex table
- **WHEN** the `SpriteTo3D` BAML function calls the
  `sam3d-objects-server` API with
  `sprite_mask: <mask>`, `sprite_image: <png>`, `format: "glb"`
- **THEN** the API returns a 3D mesh (`.glb` file) of the
  Djinn
- **AND** the mesh is staged to Garage S3 (the
  `lakehouse` stack's S3 backend)
