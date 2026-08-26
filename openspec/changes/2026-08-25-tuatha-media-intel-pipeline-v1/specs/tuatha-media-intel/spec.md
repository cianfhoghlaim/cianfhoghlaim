# Spec Delta: tuatha-media-intel

## ADDED Requirements

### Requirement: The pipeline ingests game / comic / GBA captures into typed BAML records

The system SHALL provide a capture → VLM → embedding → Lance pipeline
that turns frames produced by the macOS-native ScreenCaptureKit capture
daemon, the GBA headless mGBA controller, and the comic book CBZ
ingestor into typed BAML rows in the following schemas:

- `HadesBoon` — god, tier, slot, effect, color, particle_motion,
  bounding box, run/frame metadata.
- `ComicParticleFrame` — issue_id, page, panel_id, particle_form,
  color, motion_description, character_attribution, optional
  source_page_url.
- `GbaMagicSystem` — game, room_id, djinn_name, psynergy_name,
  element, effect_text, color, sprite_description.

#### Scenario: Manual Hades capture produces a HadesBoon row

- **WHEN** the operator opens Hades on macOS 15+
- **AND** the Swift `tuatha-capture` daemon is running (LaunchAgent
  `com.ci.tuatha.capture` active)
- **THEN** the daemon SHALL emit keyframe JPEGs to
  `~/Library/Application Support/tuatha/captures/<run_id>/`
  at a baseline rate of 1 fps
- **AND** the CocoIndex `tuatha_hades_boons` flow SHALL re-extract
  each keyframe via BAML `ExtractHadesBoon`
- **AND** the resulting row SHALL land in the Lance table
  `cianfhoghlaim.tuatha.hades.boons` with `boon_id` as primary key.

#### Scenario: Comic book CBZ ingest produces ComicParticleFrame rows

- **WHEN** the operator runs `tuatha-capture-python comic <cbz_dir> <out_dir>`
- **THEN** the comic ingestor SHALL render each page to PNG
- **AND** extract a k-means-6 dominant palette per page
- **AND** the CocoIndex `tuatha_comic_particles` flow SHALL re-extract
  each page via BAML `ExtractComicParticle` with `bias_mode=description_heavy`.

### Requirement: The pipeline emits no raw copyrighted material to the repository

The system SHALL enforce the `shippable: false` invariant from the
`tuatha` skill: no captured game frame, comic book page, or BLOB blob
SHOULD be committed to the public monorepo.

#### Scenario: Full-resolution assets stay in the Pangolin-private volume

- **WHEN** the Swift daemon writes to
  `~/Library/Application Support/tuatha/captures/<run_id>/`
- **THEN** the CocoIndex flow SHALL mount only a downsampled thumb
  (≤1024px JPEG for hades / ≤768px JPEG for comic / ≤480px PNG for gba)
  in the Lance fat table `thumb_blob` column
- **AND** the full-resolution files SHALL remain in the Pangolin-private
  `s3://cianfhoghlaim-tuatha-raw/<source>/` bucket with a 7-day TTL.

### Requirement: All VLM calls route through MODEL_REGISTRY

The system SHALL resolve every vision model string via
`MODEL_REGISTRY.resolve(family, role)` and SHALL NOT hardcode any model
string in extractor code.

#### Scenario: The hades_boons pipeline selects the M4-Max optimal VLM

- **WHEN** the operator starts the stack on an M4 Max macOS host
- **THEN** the `tuatha_hades_boons` flow SHALL resolve
  `MODEL_REGISTRY.resolve("ocr_vision", "tier2_medium")` → `qwen3-vl-8b`
- **AND** the BAML `HadesBoonClient` SHALL call llama-swap at
  `${LLAMASWAP_URL}`.

### Requirement: The pipeline is observable via Langfuse + RAGAS

The system SHALL wrap every BAML extraction + CocoIndex flow in a
Langfuse `@observe(as_type="generation")` span, and SHALL gate the
`anam_particles_v1` Dagster asset on a RAGAS asset_check
(`ragas_anam_color_anchor`).

#### Scenario: The RAGAS asset_check blocks a low-quality join

- **WHEN** the RAGAS asset `ragas_anam_color_anchor` evaluates the
  `anam_particles_v1` table
- **AND** the score falls below 0.85
- **THEN** the asset materialization SHALL fail with severity=WARN
  (or ERROR if explicitly configured).

### Requirement: The Hermes Phase 2 stub is gated by an env var

The system SHALL keep the `tuatha_capture_agent` Hermes control loop
disabled by default (gated by `TUATHA_HERMES_ENABLED=false`); Phase 2
activation SHALL require an explicit operator override.

#### Scenario: Phase 1 keeps the agent inert

- **WHEN** `TUATHER_HERMES_ENABLED=false` (default)
- **THEN** the agent SHALL return `{"status": "phase_1"}` on any
  capture request
- **AND** the Swift daemon SHALL still run (it doesn't depend on Hermes).

### Requirement: The system supports a RAGAS-grade cross-source join

The system SHALL provide the `anam_particles_app` CocoIndex v1 App
that reads from the 3 source tables (hades / comic / gba) via DuckDB
federation + lance_scan() and emits rows into
`cianfhoghlaim.tuatha.anam_particles`.

#### Scenario: The join maps an Hades boon to a Tuatha Dé deity + ANAM color

- **WHEN** the operator has >= 1 row in any of the 3 source tables
- **AND** runs `mise run cocoindex:update tuatha_anam_particles`
- **THEN** the BAML `MapToAnamParticle` function SHALL map each source row
  to a `celtic_deity` + `anam_color_hex` + `anam_motion`
- **AND** the row SHALL be written to
  `cianfhoghlaim.tuatha.anam_particles` with `anam_id` as primary key.
