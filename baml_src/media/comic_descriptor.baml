// comic_descriptor.baml
// Medium-agnostic MediaDescriptor schema + the Class A
// (Hickman Marvel run) extractor function.
//
// The 7-axis descriptor (power_event, visual_grammar, palette
// is the canonical record type emitted by every per-medium
// extractor. All descriptors ship with `shippable: false`
// enforced.
//
// Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
//             design.md § 1 (the 7-axis schema)
//             spec.md § media-intel-corpus Requirement 2 (the schema)

class Element {
  earth string
  air string
  water string
  fire string
  spirit string
  none string
}

class ScaleTier {
  personal string
  local string
  regional string
  continental string
  planetary string
  cosmic string
}

class ParticleClass {
  dust string
  ember string
  mist string
  spark string
  lattice string
  ash string
  ink string
  glyph string
  none string
}

class Density {
  sparse string
  moderate string
  dense string
  overwhelming string
}

class PowerEvent {
  actor string?
  element Element
  power_source string?
  trigger string?
  scale_tier ScaleTier
  cost string?
  consequence string?
  counter string?
}

class VisualGrammar {
  composition string?
  panel_or_shot_type string?
  motion_lines string?
  camera string?
  silhouette string?
  focal_hierarchy string?
}

class Palette {
  dominant_hex string[]
  accent_hex string[]
  emissive_hex string[]
  per_element_palette map<string, string[]>
  contrast_strategy string?
}

class VfxVocabulary {
  particle_class ParticleClass
  density Density
  trail_behavior string?
  dissipation string?
  light_interaction string?
}

class NarrativeBeat {
  arc_position string?
  beat_significance string?
}

class Transferability {
  in_game_mechanic string?
  anam_cost int?
  palette_token string?
  particle_effect string?
}

class DerivationClass {
  description_only string
  derivative string
  fair_use_quote string
}

class Provenance {
  rights_holder string
  licence string
  derivation_class DerivationClass
  shippable false
  shippable_art_path string?
}

class MediaDescriptor {
  work string
  medium "comic"
  language string
  source_url string
  source_timestamp string

  power_event PowerEvent
  visual_grammar VisualGrammar
  palette Palette
  vfx_vocabulary VfxVocabulary
  narrative_beat NarrativeBeat
  transferability Transferability
  provenance Provenance
}

// Class A — Comics (Hickman Marvel run)
// Default VLM: qwen3-vl-8b (resolved via MODEL_REGISTRY
// family=ocr_vision, role=media_descriptor). No hardcoded
// model strings.

function ExtractComicDescriptor(
  image: image,
  caption_text: string,
  source_url: string,
  source_page: int,
  work: string,
  language: string,
  evidence: string
) -> MediaDescriptor {
  client MediaIntelPrimary
  prompt #"
    You are a medium-agnostic visual + narrative analyst for
    the Cianfhoghlaim reference-corpus. You are reading a
    panel from {{ work }} (the Jonathan Hickman Marvel run).
    The panel image and its caption text are provided.

    Extract the 7-axis MediaDescriptor from this panel:

    1. power_event — the actor, the element, the source of
       power, the trigger, the scale tier, the cost, the
       consequence, the counter. If the panel shows no
       power use, set element to "none" and the other
       fields to null.
    2. visual_grammar — the composition, the panel/shot
       type, the motion lines, the camera, the silhouette,
       the focal hierarchy.
    3. palette — the dominant hex colours, the accent hex
       colours, the emissive hex colours, the per-element
       palette mapping, the contrast strategy.
    4. vfx_vocabulary — the particle class, the density,
       the trail behaviour, the dissipation, the light
       interaction. For comics, the particle class is
       typically "spark" (Hickman's data-pages) or "ash"
       (Battleworld panels) or "none".
    5. narrative_beat — the arc position (which of the 6
       Hickman publications), the beat significance.
    6. transferability — the in-game mechanic, the anam cost
       (always 0 for comics — no in-game cost from a comic
       panel), the palette token, the particle effect.
       Leave null for v1; the downstream Celtic-MMO design
       will populate these.
    7. provenance — the rights holder (Marvel Comics), the
       licence (always "fair-use-description" for comics in
       this corpus), the derivation class
       ("description_only" — NEVER "derivative" — we never
       re-render comic panels), the shippable field (always
       false), the shippable_art_path (always null).

    The caption text is:
    {{ caption_text }}

    The source URL is:
    {{ source_url }}

    The source page is:
    {{ source_page }}

    The language is:
    {{ language }}

    The verbatim evidence excerpt from the caption is:
    {{ evidence }}

    Return the typed MediaDescriptor.
  "#
}
