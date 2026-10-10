// media_power_system.baml
// The cross-media power/magic-system descriptor — the canonical BAML
// contract for the media-intel expansion beyond retro games.
//
// Per the 2026-10-10-media-intel-and-curriculum-hydration-v1 saga change
// (Plan A of openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md).
//
// The descriptor is DESCRIPTION-ONLY (shippable = false) — it never
// carries a source pixel, keyframe, or panel. It captures HOW a power or
// magic system is *visualised* and *staged* across four media families:
//
//   • game      — Hades 1/2 (Olympian boons)
//   • animation — Avatar: The Last Airbender (bending)
//   • comic     — X-Men (mutant powers)
//   • prose     — The Wheel of Time (the One Power) [see wheel_of_time.baml]
//   • film      — reserved
//
// The output is alignment-ready for two Leaving Certificate subjects:
//   • Art — the comparative study of how power is visualised (palette,
//           composition, visual grammar)
//   • English — the comparative study (theme / cultural context / genre /
//           general vision)
//
// Reference:
//   openspec/specs/retro-game-design-catalogue/spec.md (the predecessor)
//   openspec/specs/tuatha-british-isles-mmo/spec.md (the consumer)
//   baml_src/media/gameplay_descriptor.baml (the retro-game class)

// ----------------------------------------------------------------------------
// Enums
// ----------------------------------------------------------------------------

enum PowerSystemKind {
  DivineBoon        // Hades — Olympian boons
  ElementalBending  // Avatar: The Last Airbender — the four elements
  MutantGene        // X-Men — the X-gene / mutation
  Channeling        // Wheel of Time — saidin / saidar / the One Power
  Cosmic            // reserved (Asgardian / Phoenix-tier)
  Other
}

enum MediaMedium {
  Game
  Animation
  Comic
  Prose
  Film
}

enum ElementalAxis {
  Earth
  Air
  Water
  Fire
  Spirit
  Metal
  Lightning
  Blood
  NoElement @alias("None")
}

enum PowerScaleTier {
  Personal
  Local
  Regional
  Continental
  Planetary
  Cosmic
}

// ----------------------------------------------------------------------------
// The 7-axis descriptor
// ----------------------------------------------------------------------------

class PowerUseEvent {
  actor string?                    @description("Who wields the power, e.g. 'Zagreus', 'Katara', 'Jean Grey', 'Rand al'Thor'")
  power_name string                @description("The canonical name of the power, e.g. 'Divine Strike', 'Waterbending', 'Telekinesis', 'Balefire'")
  power_system PowerSystemKind
  element ElementalAxis
  source string?                   @description("Where the power comes from, e.g. 'Olympian boon', 'innate bending', 'X-gene mutation', 'the One Power'")
  trigger string?                  @description("How it is invoked, e.g. 'skill-bar hotkey', 'martial forms', 'focus + concentration', 'weaving flows'")
  scale_tier PowerScaleTier
  cost string?                     @description("What it costs, e.g. 'boon slot', 'stamina + breath', 'mental strain', 'saidin taint'")
  consequence string?              @description("The narrative/physical consequence of use")
  counter string?                  @description("What counters it, e.g. 'cooldown timer', 'elemental counter-bending', 'power-dampening collar', 'a stronger channeler'")
  narrative_beat string?           @description("The story beat the use occurs in")
}

class PaletteSignature {
  dominant_hex string[]                              @description("The 3-6 dominant hex colours of the scene")
  accent_hex string[]                                @description("The accent hex colours")
  emissive_hex string[]                              @description("The emissive (glow / particle) hex colours")
  per_element_palette map<string, string[]>          @description("Per-element palette keyed by ElementalAxis value")
  contrast_strategy string?                          @description("e.g. 'warm emissive on cool pigment', 'high-key aerial perspective'")
  palette_art_note string?                           @description("The Leaving Cert Art comparative-study note on the palette")
}

class MediaVisualGrammar {
  medium MediaMedium
  composition string?             @description("The compositional structure of the scene")
  shot_type string?               @description("e.g. 'isometric', 'third-person', '2D sprite', 'wide establishing shot', 'splash page'")
  motion_vocabulary string?       @description("The animation/line vocabulary of the power, e.g. 'arc burst', 'flowing ribbon', 'crackling web'")
  camera string?                  @description("e.g. 'fixed camera', 'follow camera', 'dynamic Dutch angle', 'panel gutter'")
  silhouette string?              @description("The silhouette/pose language of the power-user")
  focal_hierarchy string?         @description("Where the eye is led, e.g. 'player-focal HUD hierarchy', 'speaker-focal', 'power-focal")
}

class ComparativeStudyLens {
  // The 4 Leaving Certificate English Comparative Study modes + the Art note.
  theme_or_issue string?          @description("English comparative — e.g. 'power and responsibility'")
  cultural_context string?        @description("English comparative — e.g. 'Irish / global / diaspora'")
  literary_genre string?          @description("English comparative — e.g. 'fantasy quest', 'superhero drama'")
  general_vision string?          @description("English comparative — the text's general vision / worldview")
  art_comparative string?         @description("Art comparative study — how this work visualises power vs. a peer work")
}

class MediaPowerProvenance {
  rights_holder string            @description("The original publisher, e.g. 'Supergiant Games', 'Nickelodeon / Paramount', 'Marvel Comics', 'Tor Books'")
  licence string                  @description("The licence posture, e.g. 'fair-use-description'")
  derivation_class "description_only" | "derivative" | "fair_use_quote"
  shippable false                 @description("ALWAYS false — description-only, never a source pixel/panel/frame")
  shippable_art_path string?      @description("ALWAYS null for v1")
}

class MediaPowerDescriptor {
  descriptor_id string            @description("Deterministic: sha256(work + scene_id + medium + extracted_at)[:16]")
  work string                     @description("e.g. 'Hades', 'Avatar: The Last Airbender', 'X-Men', 'The Wheel of Time'")
  medium MediaMedium
  scene_id string                 @description("The scene / episode / issue / chapter identifier")
  language string                 @description("The canonical capture language (usually 'en')")

  power_event PowerUseEvent
  palette PaletteSignature
  visual_grammar MediaVisualGrammar
  comparative_lens ComparativeStudyLens

  design_notes string             @description("1-2 sentences of design notes for the Tuatha MMO designers")
  provenance MediaPowerProvenance

  source_url string               @description("The source reference URL (never carries the pixels)")
  source_timestamp string
  extracted_at string             @description("ISO 8601 timestamp")
  stub bool                       @description("True when running offline")
}

// ----------------------------------------------------------------------------
// The extraction function (image-bearing media: game / animation / comic)
// ----------------------------------------------------------------------------

function ExtractMediaPowerDescriptor(
  image: image                    @description("A single frame / panel / screenshot (never stored — description only)"),
  work: string                    @description("e.g. 'Hades', 'Avatar: The Last Airbender', 'X-Men'"),
  scene_id: string                @description("The episode / issue / scene / chapter id"),
  medium: string                  @description("game | animation | comic | film"),
  power_system: string            @description("The PowerSystemKind, e.g. 'divine_boon', 'elemental_bending', 'mutant_gene'"),
  rights_holder: string           @description("The original publisher"),
  evidence: string                @description("Verbatim visual evidence the extraction is grounded in")
) -> MediaPowerDescriptor {
  client MediaIntelPrimary
  prompt #"
    You are a medium-agnostic power/magic-system analyst for the
    Cianfhoghlaim reference corpus. You are reading a single frame from
    {{ work }} ({{ medium }}), scene {{ scene_id }}.

    The known power system is: {{ power_system }}.

    Extract the 7-axis MediaPowerDescriptor. This is DESCRIPTION-ONLY:
    describe how the power is *visualised* and *staged*, never reproduce
    the artwork.

    1. power_event — actor, power_name, power_system, element (the
       ElementalAxis), source (e.g. 'Olympian boon', 'innate bending',
       'X-gene mutation'), trigger, scale_tier, cost, consequence,
       counter, narrative_beat.
    2. palette — 3-6 dominant hex, accent hex, emissive hex, the
       per_element_palette map (keyed by ElementalAxis), the contrast
       strategy, and a palette_art_note phrased for the Leaving
       Certificate Art comparative study.
    3. visual_grammar — composition, shot_type, motion_vocabulary,
       camera, silhouette, focal_hierarchy.
    4. comparative_lens — theme_or_issue, cultural_context,
       literary_genre, general_vision (the Leaving Certificate English
       Comparative Study modes) + the art_comparative note.
    5. design_notes — 1-2 sentences for the Tuatha MMO designers.
    6. provenance — rights_holder = "{{ rights_holder }}", licence
       "fair-use-description", derivation_class "description_only",
       shippable false, shippable_art_path null.
    7. descriptor_id (deterministic), work, medium, scene_id, language,
       source_url, source_timestamp, extracted_at.

    The verbatim visual evidence is:
    {{ evidence }}

    Cite visual evidence only; never invent powers not visible in the frame.
  "#
}

// ----------------------------------------------------------------------------
// Test cases (run via `baml-cli test`)
// ----------------------------------------------------------------------------

test avatar_katara_waterbending {
  functions [ExtractMediaPowerDescriptor]
  args {
    image "avatar_katara_waterbending.png"
    work "Avatar: The Last Airbender"
    scene_id "s01e01-the-boy-in-the-iceberg"
    medium "animation"
    power_system "elemental_bending"
    rights_holder "Nickelodeon / Paramount"
    evidence "Katara raises a column of water from the sea, a curved ribbon of water lit pale blue."
  }
}

test xmen_jean_grey_telekinesis {
  functions [ExtractMediaPowerDescriptor]
  args {
    image "xmen_jean_grey_telekinesis.png"
    work "X-Men"
    scene_id "uncanny-x-men-101"
    medium "comic"
    power_system "mutant_gene"
    rights_holder "Marvel Comics"
    evidence "A psychic aura surrounds the figure; debris lifts in a radiating pattern; pink emissive glow."
  }
}

test hades_athena_boon {
  functions [ExtractMediaPowerDescriptor]
  args {
    image "hades_athena_divine_strike.png"
    work "Hades"
    scene_id "tartarus-boon-selection"
    medium "game"
    power_system "divine_boon"
    rights_holder "Supergiant Games"
    evidence "A boon card for Athena's Divine Strike; blue-grey emissive particles arc from the icon."
  }
}
