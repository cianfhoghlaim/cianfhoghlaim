# cocoindex-retro-gameplay Specification

## Purpose
`cocoindex-retro-gameplay` is the contract for cataloguing the **design
patterns** (not the literal assets) of retro educational games so the
Tuatha British Isles MMO designers can riff on them. The pipeline
captures a screenshot via libretro, segments it via SAM3, extracts a
typed design pattern via BAML, and stores it in a CocoIndex-mounted
LanceDB table for the marimo dashboard to browse.

Per the 2026-10-03-cocoindex-retro-gameplay-v1 saga change (Plan 3 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

## ADDED Requirements

### Requirement: 5 platforms + 6 games of pattern coverage

The system MUST provide a `retro_library` DLT resource that lists every
game entry from the existing `romm` (v3.x) library AND from the new
`Drop-OSS/drop` stack. Each row MUST include the canonical
`game_id`, `platform`, `title`, `year`, `igdb_id`,
`cover_art_url`, `rom_sha256`, `save_state_paths[]`, and MUST be keyed
by `(platform, game_id)`.

The first iteration MUST support 6 canonical retro games across 5
platforms: `number_munchers` (NES), `oregon_trail` (Apple II),
`where_in_the_world_is_carmen_sandiego` (DOS), `pokemon_red` (GB),
`golden_sun` (GBA), `hades` (Switch via libretro snes9x).

#### Scenario: A new ROM is added to ROMM
- **GIVEN** an operator has added a new retro game to the ROMM library at `romm.cianfhoghlaim.ie`
- **WHEN** the `retro_library_watcher` Dagster sensor polls `GET /api/roms`
- **THEN** a new row is appended to the `retro_library` DLT resource
- **AND** the `retro_screenshots` materialisation runs within the same sensor tick

### Requirement: Headless screenshot capture via libretro

The system MUST provide a `retro_screenshots` DLT resource that drives
each retro game through the `libretro-retroarch` headless stack and
captures one PNG per scene transition + one PNG every 5 seconds during
gameplay. Each row MUST include the `platform`, `game_id`,
`level_index`, `scene_id`, `frame_id`, `scene_type` (one of `"title" |
"menu" | "gameplay" | "boss" | "minigame" | "end"`), the PNG `path`
(relative to `stedding/ingest_queue/retro/`), and the PNG `sha256`.
Save states MUST be loaded via `ludusavi`.

#### Scenario: Number Munchers title screen captured
- **GIVEN** the `number_munchers` game is in the `retro_library` resource with `platform = "nes"` and `rom_sha256 = "abc..."`
- **WHEN** the `retro_screenshots` asset materialises
- **THEN** ≥1 row is produced with `scene_type = "title"` and the PNG stored at `stedding/ingest_queue/retro/nes/number_munchers/title.png`
- **AND** the row's `sha256` matches the PNG file's actual SHA-256

### Requirement: Typed design pattern extraction via BAML

The system MUST provide an `ExtractGameplayPattern` BAML function (in
`baml_src/media/extract_design_pattern.baml`) that takes a single
screenshot + the surrounding session log and returns a typed
`RetroGameplayPattern` record with:
- `game_id` + `platform` (the source)
- `genre` (rogue_like / mmorpg / jrpg / monster_tamer / puzzle / language_learning / match_three / other)
- `power_events` (list of `GameplayPowerEvent`: actor + element + power_source + trigger + scale_tier + cost + consequence + counter)
- `visual_grammar` (`GameplayVisualGrammar`: composition + panel_or_shot_type + motion_lines + camera + silhouette + focal_hierarchy)
- `palette` (`GameplayPalette`: dominant_hex + accent_hex + emissive_hex + per_element_palette + contrast_strategy)
- `source` (`RetroPatternSource`: platform + game_id + rom_sha256 + screenshot_sha256 + save_state_path + macro_script)
- `ingested_at` (ISO 8601 timestamp)

The function MUST be called via the canonical `baml_client.baml_client.sync_client.b.ExtractGameplayPattern(...)` path.

#### Scenario: Hades boon extracted from screenshot
- **GIVEN** a screenshot of a Hades boon selection screen at `stedding/ingest_queue/retro/switch/hades/boon_zeus_lightning.png`
- **WHEN** `ExtractGameplayPattern(screenshot_b64=<base64>)` is called
- **THEN** the returned `RetroGameplayPattern` includes `genre = "rogue_like"`
- **AND** the `power_events` list has ≥1 entry with `element = "air"` + `power_source = "Olympian boon"` + `actor = "Zagreus"`

### Requirement: SAM3 sprite segmentation (against the sam3-server stack)

The system MUST provide a `sam3_segment` tool (in
`agents/adk/tools/retro_pattern_extractor.py`) that takes the screenshot
path + a list of optional class hints + sends it to the
`sam3-server` stack (`http://sam3-server:8080/v1/segment`) and returns a
list of typed segments `{bbox: [x, y, w, h], class: str, score: float}`.

When the `sam3-server` stack is not reachable (offline dev mode), the
tool MUST fall back to a stub that returns a single bounding box
covering the entire image (the pattern is captured at the whole-screen
level, not per-sprite).

#### Scenario: SAM3 segments a Hades boon screen
- **WHEN** `sam3_segment(screenshot_path=".../hades/boon_zeus.png", classes=["boon_icon", "character_portrait", "ui_button"])` is called
- **AND** the `sam3-server` stack is up
- **THEN** the response has ≥3 segments (one per class)
- **AND** the segments are passed to `ExtractGameplayPattern` as context

#### Scenario: SAM3 offline fallback
- **WHEN** `sam3_segment(...)` is called
- **AND** the `sam3-server` stack is unreachable
- **THEN** the response has 1 segment covering the full image
- **AND** `ExtractGameplayPattern` runs against the full-screen fallback

### Requirement: Pattern catalog in LanceDB via CocoIndex

The system MUST provide a CocoIndex flow at
`cocoindex_flows/media/retro_design_embedding.py` that indexes the
`RetroGameplayPattern` records into the LanceDB table
`media.retro_design_patterns` (keyed by `(platform, game_id,
scene_id)`). The flow MUST conform to the canonical R1-R4 conformance
contract (per the cocoindex flow doc).

A marimo dashboard at `notebooks/dashboards/retro_patterns.py` MUST
display the catalog (per-game + per-scene breakdown + the palette + the
power events).

#### Scenario: Pattern browsed in marimo
- **GIVEN** 6 patterns stored in `media.retro_design_patterns` (one per game)
- **WHEN** the operator opens `notebooks/dashboards/retro_patterns.py` in Marimo
- **THEN** the dashboard shows a table with 6 rows (game + genre + palette hex + power event count)
- **AND** clicking a row expands to show the full `GameplayVisualGrammar` + `GameplayPalette`
