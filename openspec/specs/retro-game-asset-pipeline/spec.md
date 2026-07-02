# Retro Game Asset Pipeline Capability

## Purpose

`retro-game-asset-pipeline` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`cianfhoghlaim/meaisinfhoghlaim/segmentation/` (SAM3 + SAM-3D-Objects
wrappers) + `cianfhoghlaim/dlt/retro/` (DLT sources for ROM/library +
screenshots + design patterns + asset generation) +
`cianfhoghlaim/baml/retro/` (BAML extraction schemas) +
`cianfhoghlaim/cocoindex/` (v1 embedding Apps for design patterns
+ asset generation) + `cianfhoghlaim/dagster/` (asset groups +
sensors) + `cianfhoghlaim/notebooks/retro_assets.py` (marimo
catalogue) + `s3://cianfhoghlaim-asset-v2/{2d,3d}/` (the asset
buckets).

This is the canonical openspec spec for the retro-game-asset pipeline.
It is a re-publish of `retro-game-design-catalogue` integrated with the
new Cianfhoghlaim Leaving Cert portal's Diagram Generator + 3D Asset
Gallery. The assets are conditioned on NCCA learning outcomes +
bilingual EN + GA syllabus content, NOT on the source games' literal
assets.

## Background

The retro-game-asset pipeline drives the educational asset generator for
the Cianfhoghlaim platform. It uses retro educational games (Number
Munchers, Oregon Trail, Carmen Sandiego) as design-pattern sources —
never as literal asset sources.

The 6 Requirements are:
1. ROM/library ingest from Romm + Drop-OSS/drop
2. Headless screenshot capture via libretro cores
3. SAM3 + SAM-3D-Objects segmentation
4. VLM design-pattern extraction via Bolmo / Molmo2 / Qwen3-VL + BAML
5. Subject-conditioned 2D asset generation via Flux / Z-Image / Qwen-Image / FIBO
6. Subject-conditioned 3D asset generation via TRELLIS.2-4B + SAM-3D-Objects
7. Catalogue + delivery via marimo + Storybook + Hermes cron

## Requirements

### Requirement: ROM/library ingest

The system SHALL read the existing `romm` library and `Drop-OSS/drop`
library and yield a typed `retro_library` DLT resource.

#### Scenario: Romm library ingested as retro_library

- **GIVEN** the operator owns 50+ ROMs in the Romm library at `romm.cianfhoghlaim.ie`
- **WHEN** the DLT source `dlt/retro/library.py` runs
- **THEN** it yields ≥50 `retro_library` rows, one per ROM

### Requirement: Headless screenshot capture

The system SHALL drive the games via deterministic macro scripts through
the new `libretro-retroarch` stack and capture PNGs at every scene
transition + every 5 s of gameplay.

#### Scenario: Number Munchers screenshots captured

- **GIVEN** Number Munchers is loaded in the libretro Mesen core
- **WHEN** the macro script runs for 60 s
- **THEN** the screenshot pipeline produces ≥12 PNGs at scene transitions

### Requirement: SAM3 + SAM-3D-Objects segmentation

The system SHALL segment the sprites + UI regions via SAM3 and synthesise
3D objects from sprite masks via SAM-3D-Objects.

#### Scenario: Hades boon-selection scene segmented

- **GIVEN** the screenshot of Hades' boon-selection scene
- **WHEN** SAM3 segments the scene with the prompt "boon-card"
- **THEN** the system produces 3 SegmentationMask records

### Requirement: VLM design-pattern extraction

The system SHALL extract typed design patterns via the canonical
Bolmo / Molmo2 / Qwen3-VL VLM backbone + the BAML function
`ExtractGameDesignPattern`.

#### Scenario: Number Munchers drill pattern extracted

- **GIVEN** a screenshot of a Number Munchers drill scene
- **WHEN** `b.ExtractGameDesignPattern(screenshot, "number-munchers", {"subject": "mathematics", "lo_code": "LC-MATHS-LO-2.4"})` runs
- **THEN** the function returns a `GameDesignPattern` with the design pattern

### Requirement: Subject-conditioned 2D asset generation

The system SHALL generate subject-conditioned 2D educational assets via
Qwen-Image / Flux / Z-Image / FIBO via InvokeAI.

#### Scenario: Mathematics drill sprite generated

- **GIVEN** the Number Munchers drill pattern + the Mathematics LO `LC-MATHS-LO-2.4`
- **WHEN** the FIBO asset generator runs the Mathematics prompt template
- **THEN** it produces ≥1 PNG at `stedding/asset_generation/2d/mathematics/<asset_id>.png`

### Requirement: Subject-conditioned 3D asset generation

The system SHALL generate 3D meshes via TRELLIS.2-4B + SAM-3D-Objects.

#### Scenario: Mathematics 3D symbol generated

- **GIVEN** the Number Munchers sprite + the Mathematics LO `LC-MATHS-LO-2.4`
- **WHEN** the 3D asset pipeline runs
- **THEN** it produces ≥1 GLB at `s3://cianfhoghlaim-asset-v2/3d/mathematics/<asset_id>.glb`

### Requirement: Catalogue + delivery surface

The system SHALL render the catalogue as a marimo notebook + a
Storybook workspace + a Hermes nightly cron.

#### Scenario: Catalogue renders per-subject design patterns

- **GIVEN** the marimo notebook at `notebooks/leaving_cert/retro_assets.py`
- **WHEN** the user opens the Mathematics tab
- **THEN** the catalogue lists ≥1 `GameDesignPattern` row per Number Munchers drill scene

## See also

- [cianfhoghlaim-leaving-cert-portal](../cianfhoghlaim-leaving-cert-portal/spec.md) — the consuming portal
- [oideachais-baml-schemas](../oideachais-baml-schemas/spec.md) — the BAML extraction patterns
- [oideachais-cocoindex-v1-migration](../oideachais-cocoindex-v1-migration/spec.md) — the v1 CocoIndex App pattern