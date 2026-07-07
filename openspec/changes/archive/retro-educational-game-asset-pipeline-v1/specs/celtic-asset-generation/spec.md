# Delta: celtic-asset-generation

## ADDED Requirements

### Requirement: 5th Asset Generation Pipeline (retro_design_patterns directory)

The system SHALL organise educational asset generation under a 5th
INDEPENDENT pipeline at
`cianfhoghlaim/assets/asset_generation/retro_design_patterns/` in
addition to the 4 existing pipelines (`official_documents/`,
`subject_assets/`, `language_assets/`, `exporters/`). This 5th
pipeline MUST be independently runnable from Dagster and MUST NOT
trigger the other 4 pipelines.

The 5th pipeline SHALL execute the 6 stages:

1. **ROMM + Drop-OSS library ingest** — read the existing `romm`
   v3.x library + the `Drop-OSS/drop` stack (the `drop` stack is
   fixed in this change), yielding a `retro_library` DLT resource.
2. **Headless screenshot capture** — drive each game through the
   `libretro-retroarch` stack via deterministic macros, capturing
   PNGs via the `ludusavi` save-state bridge, yielding
   `retro_screenshots`.
3. **SAM3 + SAM-3D-Objects segmentation** — call the new
   `sam3-server` + `sam3d-objects-server` stacks via the
   `meaisinfhoghlaim/segmentation/` wrapper, yielding typed
   `SegmentationMask` records.
4. **VLM design-pattern extraction** — call the canonical
   Bolmo / Molmo2 / Qwen3-VL VLM backbone through a new
   `ExtractGameDesignPattern` BAML function, yielding typed
   `GameDesignPattern` records with per-subject
   `transferable_to_subject` tags.
5. **CocoIndex v1 embedding** — embed the `GameDesignPattern`
   text in the shared `oideachais.retro.design_patterns`
   LanceDB table using `BAAI/bge-large-en-v1.5` (per
   `openspec/specs/cocoindex-v1-migration/spec.md`).
6. **Subject-conditioned asset generation (2D + 3D in parallel)**
   — call `GenerateSubjectAsset` (2D) + `SynthesizeAsset3D` (3D)
   from the new
   `cianfhoghlaim/baml/retro/asset_prompt_generation.baml`, with
   outputs staged to `stedding/asset_generation/2d/` (MMO v1)
   and `s3://cianfhoghlaim-asset-v2/3d/` (MMO v2).

The 5th pipeline SHALL reuse `subject_assets/` for asset templates,
`language_assets/` for bilingual EN + GA typing, and `exporters/`
for the MMO client delivery (per the existing 3 of the 4 existing
pipelines). All stages SHALL be subject-aware — the pipeline MUST
emit per-NCCA-subject outputs for the 8 subjects: mathematics,
applied_mathematics, chemistry, geography, history, english,
gaeilge, computer_science.

#### Scenario: Retro design pattern extraction runs end-to-end on Number Munchers

- **GIVEN** Number Munchers is present in the `retro_library`
  resource with `platform = "nes"` and `rom_sha256 = "abc..."`
- **WHEN** the operator materialises the
  `retro_design_patterns_number_munchers` Dagster asset
- **THEN** Stage 1 yields the `retro_library` row
- **AND** Stage 2 yields ≥5 `retro_screenshots` rows (title,
  menu, ≥1 gameplay, ≥1 minigame, end)
- **AND** Stage 3 yields ≥1 `SegmentationMask` per screenshot
- **AND** Stage 4 yields ≥1 `GameDesignPattern` per screenshot,
  each with `transferable_to_subject` containing `"mathematics"`
  (because Number Munchers is a math drill game)
- **AND** Stage 5 embeds each pattern in
  `oideachais.retro.design_patterns` LanceDB
- **AND** Stage 6 emits ≥1 `AssetPrompt` per screenshot,
  conditional on the matched `LC-MATHS-LO-2.4` (or wider)

#### Scenario: Asset generation produces a chemistry molecule 2D + a geography 3D

- **GIVEN** the design-pattern catalogue has ≥10 patterns
  cross-referenced to chemistry LOs AND ≥10 patterns to geography
  LOs
- **WHEN** the operator materialises
  `retro_asset_generation_2d_chemistry` + `retro_asset_generation_3d_geography`
- **THEN** the 2D asset lands at
  `stedding/asset_generation/2d/chemistry/<asset_id>.png`
- **AND** the 3D asset lands at
  `s3://cianfhoghlaim-asset-v2/3d/geography/<asset_id>.glb`
- **AND** the 2D asset is mirrored in the `subject_assets/`
  pipeline's input (so it appears in the same marimo dashboard
  as the chemistry diagrams generated today)
- **AND** the 3D asset appears in the `exporters/` pipeline's
  `v2/3d/` staging list (consumable by the deferred MMO v2
  Babylon.js client)

#### Scenario: 5th pipeline does NOT trigger the other 4

- **GIVEN** the operator ONLY materialises the
  `retro_design_patterns_*` asset group
- **WHEN** the materialisation completes
- **THEN** the 4 existing pipelines (`official_documents/`,
  `subject_assets/`, `language_assets/`, `exporters/`) SHALL
  NOT be triggered
- **AND** the marimo dashboard reflects ONLY the retro-pattern
  updates, not any syllabus-asset changes

#### Scenario: Gaeilge source game populates bilingual pattern text

- **GIVEN** an Irish-language retro source game is in the
  `retro_library` resource
- **WHEN** the `ExtractGameDesignPattern` BAML function runs
  with `game_ctx.language = "ga"`
- **THEN** the returned `GameDesignPattern.BilingualPatternText.text_ga`
  is non-null
- **AND** `text_en = null` (mirroring the Gaeilge-only pattern
  from `openspec/specs/ncca-formative-assessment/spec.md`)

#### Scenario: Provenance is copyright-safe

- **GIVEN** any asset generated from the 5th pipeline
- **WHEN** the operator runs the per-asset copyright-safety check
  (CLIP-similarity to source + SSIM to sprite mask)
- **THEN** the CLIP-similarity score is ≤ 0.55 (the v1 threshold)
- **AND** the SSIM score is ≤ 0.4 (the v1 threshold)
- **AND** the provenance metadata records the source
  `retro_library` row + the source `retro_screenshots` row +
  the source `GameDesignPattern` row
