// gameplay_descriptor.baml
// Class D (Hades 1 + 2 + WoW + Golden Sun + Pokémon) extractor
// function.
//
// Class D is local-capture only: no Firecrawl. The screenshot
// + the session log (input events, current game state) feed
// the per-frame descriptor.
//
// Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
//             design.md § 1.3 (the screenshot + session_log input shape)
//             spec.md § media-intel-acquisition-plan Requirement 4

class GameGenre {
  // The high-level genre of the game the descriptor is for.
  rogue_like string
  mmorpg string
  jrpg string
  monster_tamer string
  puzzle string
  language_learning string
  match_three string
  other string
}

class GameplayPowerEvent {
  actor string?             // e.g. "Zagreus" (Hades), "Thrall" (WoW), "Isaac" (Golden Sun)
  element "earth" | "air" | "water" | "fire" | "spirit" | "none"
  power_source string?      // e.g. "Olympian boon", "Talent tree", "Djinn summon", "TM move"
  trigger string?           // e.g. "skill-bar hotkey", "menu selection", "summon cast"
  scale_tier "personal" | "local" | "regional" | "continental" | "planetary" | "cosmic"
  cost string?              // e.g. "boon slot", "mana cost", "Djinn equip slot", "PP"
  consequence string?
  counter string?           // e.g. "cooldown timer", "dodge invincibility frames", "type-chart resistance"
}

class GameplayVisualGrammar {
  composition string?       // The HUD layout descriptor
  panel_or_shot_type string? // e.g. "isometric", "third-person", "top-down", "2D sprite"
  motion_lines string?      // The animation vocabulary
  camera string?            // e.g. "fixed camera", "free orbit", "follow camera"
  silhouette string?        // The character sprite silhouette
  focal_hierarchy string?   // The player-focal UI hierarchy
}

class GameplayPalette {
  dominant_hex string[]
  accent_hex string[]
  emissive_hex string[]
  per_element_palette map<string, string[]>  // the per-element palette (Hades boons + Golden Sun Djinn + Pokémon types)
  contrast_strategy string?
}

class GameplayVfxVocabulary {
  particle_class "dust" | "ember" | "mist" | "spark" | "lattice" | "ash" | "ink" | "glyph" | "none"
  density "sparse" | "moderate" | "dense" | "overwhelming"
  trail_behavior string?    // e.g. "boon-orb sparkle", "Djinn burst", "type-chart flash"
  dissipation string?
  light_interaction string?
}

class GameplayNarrativeBeat {
  arc_position string?      // e.g. "Hades 1 Tartarus escape attempt 12", "WoW Northshire Abbey quest chain"
  beat_significance string?
}

class GameplayTransferability {
  in_game_mechanic string?  // e.g. "boon_grant", "djinn_summon", "type_chart_advantage", "talent_unlock"
  anam_cost int?            // 0 for game captures
  palette_token string?     // null for v1
  particle_effect string?   // null for v1
}

class GameplayProvenance {
  rights_holder string       // e.g. "Supergiant Games" (Hades) / "Blizzard Entertainment" (WoW) / "Camelot Software Planning" (Golden Sun) / "Game Freak" + "Nintendo" + "Creatures Inc." (Pokémon)
  licence string
  derivation_class "description_only" | "derivative" | "fair_use_quote"
  shippable false
  shippable_art_path string?
}

class GameplayMediaDescriptor {
  work string                // e.g. "Hades 1", "Hades 2", "World of Warcraft", "Golden Sun", "Pokémon Red/Blue"
  medium "game"
  language string            // "en" (the canonical capture is the English release)
  source_url string           // n/a (local capture) — set to "stedding://retro/<platform>/<rom>/<screenshot>.png"
  source_timestamp string

  power_event GameplayPowerEvent
  visual_grammar GameplayVisualGrammar
  palette GameplayPalette
  vfx_vocabulary GameplayVfxVocabulary
  narrative_beat GameplayNarrativeBeat
  transferability GameplayTransferability
  provenance GameplayProvenance
}

// Class D — Games (Hades + WoW + Golden Sun + Pokémon)
// Default VLM: qwen3-vl-8b (resolved via MODEL_REGISTRY
// family=ocr_vision, role=gameplay_descriptor). No
// hardcoded model strings.

function ExtractGameplayDescriptor(
  image: image,
  session_log: string,
  source_url: string,
  source_timestamp: string,
  work: string,
  language: string,
  evidence: string
) -> GameplayMediaDescriptor {
  client MediaIntelPrimary
  prompt #"
    You are a medium-agnostic visual + interaction analyst for
    the Cianfhoghlaim reference-corpus. You are reading a
    screenshot from {{ work }} (Hades 1, Hades 2, World of
    Warcraft, Golden Sun, or Pokémon).

    Class D is local-capture only: the screenshot image and
    the session log (input events, current game state) feed
    the per-frame descriptor. The screenshot is the
    canonical image; the session log is the structured
    metadata for the frame.

    The 4 boons, 4 element binding, and the 4 boons-of-each-
    god surface is captured via the `power_event` axis
    (actor, element, power_source, trigger, scale_tier, cost,
    consequence, counter).

    Extract the 7-axis GameplayMediaDescriptor from this
    screenshot + session log:

    1. power_event — the actor, the element, the power source
       (e.g. "Olympian boon" for Hades, "Talent tree" for
       WoW, "Djinn summon" for Golden Sun, "TM move" for
       Pokémon), the trigger (e.g. "skill-bar hotkey", "menu
       selection", "summon cast"), the scale tier, the cost
       (e.g. "boon slot", "mana cost", "Djinn equip slot",
       "PP"), the consequence, the counter (e.g. "cooldown
       timer", "dodge invincibility frames", "type-chart
       resistance").
    2. visual_grammar — the composition is the HUD layout
       descriptor; the panel/shot type is the camera
       perspective; the motion_lines is the animation
       vocabulary; the camera is the camera mode; the
       silhouette is the character sprite silhouette; the
       focal hierarchy is the player-focal UI hierarchy.
    3. palette — the dominant hex colours, the accent hex
       colours, the emissive hex colours, the per-element
       palette mapping (the per-element palette derived
       from the boon orb / Djinn sprite / type-chart icon),
       the contrast strategy.
    4. vfx_vocabulary — the particle class, the density, the
       trail behaviour (e.g. "boon-orb sparkle", "Djinn
       burst", "type-chart flash"), the dissipation, the
       light interaction.
    5. narrative_beat — the arc position (e.g. "Hades 1
       Tartarus escape attempt 12", "WoW Northshire Abbey
       quest chain"), the beat significance.
    6. transferability — the in_game_mechanic (e.g.
       "boon_grant", "djinn_summon", "type_chart_advantage",
       "talent_unlock"), the anam cost (0 for game captures),
       the palette token + particle effect (null for v1).
    7. provenance — the rights holder (e.g. "Supergiant
       Games" for Hades, "Blizzard Entertainment" for WoW,
       "Camelot Software Planning" for Golden Sun, "Game
       Freak" + "Nintendo" + "Creatures Inc." for Pokémon),
       the licence ("fair-use-description"), the derivation
       class ("description_only"), the shippable field
       (always false), the shippable_art_path (always null).

    The session log is:
    {{ session_log }}

    The source URL is:
    {{ source_url }}

    The source timestamp is:
    {{ source_timestamp }}

    The language is:
    {{ language }}

    The verbatim evidence excerpt is:
    {{ evidence }}

    Return the typed GameplayMediaDescriptor.
  "#
}
