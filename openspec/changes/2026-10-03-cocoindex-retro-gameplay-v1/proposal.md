# Change: 2026-10-03-cocoindex-retro-gameplay-v1

## Why

The `baml_src/media/gameplay_descriptor.baml` already defines typed
schemas (`GameplayPowerEvent` + `GameplayVisualGrammar` + `GameplayPalette`
+ `GameplayGenre`) for cataloguing the **design patterns** (not the
literal assets) of retro educational games (Hades / Hades 2 / WoW /
Golden Sun / Pokémon). The `retro-game-design-catalogue` spec describes
a `retro_design_pattern_embedding` CocoIndex flow + an
`ExtractGameplayDescriptor` BAML function + SAM3 sprite segmentation —
none of which exist as code.

Without this change, the Tuatha British Isles MMO can use literal
pixel art but can't riff on the proven design patterns of its
predecessors (rogue-lite boon systems, match-three power progression,
JRPG Djinn summons). The educational MMO loses its biggest
inspiration surface.

This is Plan 3 of the convergence saga
(`openspec/plans/2026-10-01-convergence-saga-v1.md`).

## What Changes

### Code — new (~7 files)
- `baml_src/media/extract_design_pattern.baml` — the new BAML function
  `ExtractGameplayPattern` (per-game screenshot → typed design pattern)
- `cocoindex_flows/media/retro_design_embedding.py` — the missing CocoIndex App
  (per-game patterns in `lance://media.retro_design_patterns`)
- `agents/adk/tools/retro_capture.py` — the libretro + ludusavi screenshot wrapper
- `agents/adk/tools/retro_pattern_extractor.py` — the BAML → typed pattern tool
- `agents/adk/retro_pattern_agent.py` — the ADK agent that catalogues retro patterns
- `scripts/retro_capture.py` — the CLI for headless libretro capture
- `notebooks/dashboards/retro_patterns.py` — the marimo pattern browser

### New BAML classes (in `extract_design_pattern.baml`)
- `RetroGameplayPattern` — the unified pattern record
- `GameplayPowerEvent` (already exists in gameplay_descriptor.baml — re-export)
- `GameplayVisualGrammar` (already exists — re-export)
- `GameplayPalette` (already exists — re-export)
- `GameplayGenre` (already exists — re-export)
- `RetroPatternSource` — provenance (ROM sha256 + screenshot sha256 + save state)

### New CocoIndex table
- `lance://media.retro_design_patterns` — keyed by `(platform, game_id, scene_type)`

### Reference surfaces
- `baml_src/media/gameplay_descriptor.baml` — the existing schemas (re-exported)
- `openspec/specs/retro-game-design-catalogue/spec.md` — the existing spec
- `bonneagar/stacks/libretro-retroarch/` — the libretro stack (deferred to Plan 5 bring-up)
- `bonneagar/stacks/sam3-server/` — the SAM3 stack (deferred to Plan 5 bring-up)
- `agents/workflows/_render_assets_node.py` — the shared Pillar 4 node from Plan 2

## What this does NOT ship
- The actual libretro capture (deferred — libretro stack not yet on bunchloch)
- The actual SAM3 sprite segmentation (deferred — sam3-server stack not yet on bunchloch)
- Tuatha sprite bank generation (deferred to Plan 7 + Plan 8)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
