// extract_design_pattern.baml
// The Plan 3 BAML contract for extracting typed RetroGameplayPattern
// records from retro-game screenshots.
//
// Per the 2026-10-03-cocoindex-retro-gameplay-v1 saga change (Plan 3 of
// openspec/plans/2026-10-01-convergence-saga-v1.md).

class RetroGameplayPattern {
  pattern_id string                   @description("Deterministic: sha256(platform + game_id + scene_id + screenshot_sha256)[:16]")
  game_id string                      @description("The canonical retro_library game_id (e.g. 'hades')")
  scene_id string                     @description("title | menu | gameplay | boss | minigame | end | custom")
  title string                        @description("The human-readable title of the scene")
  genre string                        @description("rogue_like | mmorpg | jrpg | monster_tamer | puzzle | language_learning | match_three | other")
  power_events_json string            @description("The GameplayPowerEvent list serialised as JSON")
  visual_grammar_json string          @description("The GameplayVisualGrammar serialised as JSON")
  palette_json string                 @description("The GameplayPalette serialised as JSON")
  design_notes string                 @description("Free-form design notes (1-2 sentences)")
  source_screenshot_path string       @description("Path to the source screenshot")
  source_rom_sha256 string            @description("The ROM SHA-256")
  extracted_at string                 @description("ISO 8601 timestamp of extraction")
  stub boolean                        @description("True when running offline")
}

function ExtractDesignPattern(
  screenshot_b64 string    @description("Base64-encoded PNG"),
  session_log string?      @description("Optional session log"),
  game_id string           @description("The canonical retro_library game_id"),
  scene_id string          @description("title | menu | gameplay | boss | minigame | end | custom"),
  game_genre string        @description("The known GameGenre"),
) -> RetroGameplayPattern {
  client "Primary"
  prompt #"
    You are extracting the design pattern from a single retro-game
    screenshot for the Cianfhoghlaim British Isles MMO designers.

    Produce a RetroGameplayPattern record with the full schema.
  "
}

__all__ = ["RetroGameplayPattern", "ExtractDesignPattern"]
