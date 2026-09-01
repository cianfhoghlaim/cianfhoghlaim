// prose_descriptor.baml
// Class B (Wheel of Time) extractor function.
//
// The Wheel of Time is the 0-pixel control group: it proves
// the medium-agnostic descriptor schema works on a work with
// no visual component. The `vfx_vocabulary.particle_class`
// is set to `ink` for prose-as-medium (the only medium that
// uses `ink`); the `visual_grammar.composition` becomes a
// paragraph of text rather than a panel coordinate.
//
// Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
//             design.md § 1.3 (prose-as-medium special case)
//             spec.md § media-intel-acquisition-plan Requirement 2

class WheelOfTimePowerEvent {
  actor string?            // e.g. "Rand al'Thor", "Egwene al'Vere"
  element "earth" | "air" | "water" | "fire" | "spirit" | "none"
  power_source string?      // e.g. "saidar", "saidin", "One Power", "True Power"
  trigger string?          // e.g. "deliberate channel", "angreal-amplified", "ta'veren"
  scale_tier "personal" | "local" | "regional" | "continental" | "planetary" | "cosmic"
  cost string?             // e.g. "burning out", "stilling", "untethering from the Source"
  consequence string?
  counter string?          // e.g. "shielding", "stillness", "bonding"
}

class WheelOfTimeVisualGrammar {
  composition string?       // A paragraph of text describing the prose composition
  panel_or_shot_type string? // "n/a — prose-as-medium" or "first-person POV" or "omniscient"
  motion_lines string?       // The narrative pacing descriptor
  camera string?             // The narrative perspective (POV character or omniscient)
  silhouette string?         // The character silhouettes-as-described
  focal_hierarchy string?    // The narrative focus (which character carries the scene)
}

class ProsePalette {
  dominant_hex string[]     // empty for prose (no visual)
  accent_hex string[]       // empty for prose
  emissive_hex string[]     // empty for prose
  per_element_palette map<string, string[]>  // the 5 element palette mapping (from the prose description)
  contrast_strategy string?  // n/a
}

class WheelOfTimeVfxVocabulary {
  particle_class "dust" | "ember" | "mist" | "spark" | "lattice" | "ash" | "ink" | "glyph" | "none"
  density "sparse" | "moderate" | "dense" | "overwhelming"
  trail_behavior string?    // narrative pacing descriptor
  dissipation string?       // narrative resolution descriptor
  light_interaction string?  // n/a for prose
}

class WheelOfTimeNarrativeBeat {
  arc_position string?      // e.g. "Book 1: The Eye of the World", "Book 4: The Shadow Rising"
  beat_significance string?
}

class WheelOfTimeTransferability {
  in_game_mechanic string?  // e.g. "channeller_class_initiation", "angreal_empowerment"
  anam_cost int?            // 0 for prose
  palette_token string?     // null for v1
  particle_effect string?   // null for v1
}

class WheelOfTimeProvenance {
  rights_holder string       // "Robert Jordan" (deceased) + "Brandon Sanderson" (for books 12-14)
  licence string             // "fair-use-description"
  derivation_class "description_only" | "derivative" | "fair_use_quote"
  shippable false
  shippable_art_path string?
}

class WheelOfTimeMediaDescriptor {
  work string                // "The Wheel of Time"
  medium "prose"
  language string            // "en" (the Wheel of Time has no other-language editions in this corpus v1)
  source_url string
  source_timestamp string

  power_event WheelOfTimePowerEvent
  visual_grammar WheelOfTimeVisualGrammar
  palette ProsePalette
  vfx_vocabulary WheelOfTimeVfxVocabulary
  narrative_beat WheelOfTimeNarrativeBeat
  transferability WheelOfTimeTransferability
  provenance WheelOfTimeProvenance
}

// Class B — Prose (Wheel of Time)
// Default VLM: qwen3.6-27b-mtp (resolved via MODEL_REGISTRY
// family=ocr_vision, role=prose_descriptor). No hardcoded
// model strings.

function ExtractProseDescriptor(
  text: string,
  source_url: string,
  source_paragraph: int,
  work: string,
  language: string,
  evidence: string
) -> WheelOfTimeMediaDescriptor {
  client MediaIntelPrimary
  prompt #"
    You are a medium-agnostic narrative + magic-system analyst
    for the Cianfhoghlaim reference-corpus. You are reading a
    passage from {{ work }} (the Wheel of Time).

    The Wheel of Time is the 0-pixel control group — there are
    no images. The schema is medium-agnostic: the
    `vfx_vocabulary.particle_class` defaults to "ink" for
    prose-as-medium; the `visual_grammar.composition` becomes
    a paragraph of text rather than a panel coordinate.

    The 5 magic-system axes (saidar / saidin / Tel'aran'rhiod /
    One Power / Aes Sedai) are surface-cited from the prose.

    Extract the 7-axis WheelOfTimeMediaDescriptor from this
    passage:

    1. power_event — the actor, the element (mapped to one of
       the 6 enum values; the "spirit" element maps to the
       World of Dreams / Tel'aran'rhiod + the True Power
       analogue), the power source (saidar / saidin / True
       Power), the trigger, the scale tier, the cost
       (burning out / stilling / untethering from the
       Source), the consequence, the counter (shielding /
       stillness / bonding).
    2. visual_grammar — the composition is a paragraph of
       text describing the prose composition; the
       panel_or_shot_type is "n/a — prose-as-medium" or
       "first-person POV" or "omniscient"; the motion_lines
       is the narrative pacing descriptor; the camera is
       the narrative perspective; the silhouette is the
       character silhouettes-as-described; the focal
       hierarchy is the narrative focus.
    3. palette — the dominant_hex / accent_hex / emissive_hex
       / contrast_strategy are all n/a for prose. The
       per_element_palette mapping IS populated (the 5
       elements' associated prose descriptions, derived
       from the Wheel of Time).
    4. vfx_vocabulary — the particle_class is "ink"; the
       density is the narrative pacing descriptor; the
       trail_behavior is the narrative pacing descriptor;
       the dissipation is the narrative resolution
       descriptor; the light_interaction is "n/a for prose".
    5. narrative_beat — the arc_position is the Wheel of
       Time book + chapter reference; the beat_significance
       is the narrative beat significance.
    6. transferability — the in_game_mechanic is set to
       something like "channeller_class_initiation" or
       "angreal_empowerment" or "ta'veren_pull"; the anam_cost
       is 0 for prose; the palette_token + particle_effect
       are null for v1.
    7. provenance — the rights holder is "Robert Jordan" +
       "Brandon Sanderson" (for books 12-14); the licence is
       "fair-use-description"; the derivation class is
       "fair_use_quote" (we are quoting a short passage);
       the shippable field is always false; the
       shippable_art_path is always null.

    The text is:
    {{ text }}

    The source URL is:
    {{ source_url }}

    The source paragraph is:
    {{ source_paragraph }}

    The language is:
    {{ language }}

    The verbatim evidence excerpt is:
    {{ evidence }}

    Return the typed WheelOfTimeMediaDescriptor.
  "#
}
