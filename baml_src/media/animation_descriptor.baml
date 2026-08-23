// animation_descriptor.baml
// Class C (Avatar: The Last Airbender + The Legend of Korra
// + the Aang-film continuity) extractor function.
//
// The 4+1 element vocabulary (air / water / fire / earth /
// spirit) is surface-cited from the Wikipedia article. The
// bending sub-disciplines (metal / blood / lightning /
// healing / sand / energy) are captured via the
// `power_event` axis.
//
// Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
//             design.md § 1.3 (the 4+1 element mapping)
//             spec.md § media-intel-acquisition-plan Requirement 3

class AvatarElement {
  earth
  air
  water
  fire
  spirit
  none
}

class BendingSubdiscipline {
  // The sub-discipline of bending the actor is using. "none"
  // for non-bending; "spirit" for the Avatar State /
  // energybending.
  metal
  blood
  lightning
  healing
  sand
  lavabending
  combustion
  flight
  energy
  none
}

class AnimationPowerEvent {
  actor string?             // e.g. "Aang", "Korra", "Zuko", "Katara", "Toph"
  element AvatarElement
  subdiscipline BendingSubdiscipline
  power_source string?      // e.g. "Avatar State", "Lion Turtle", "comet-boosted firebending"
  trigger string?           // e.g. "stance → gesture → effect chain"
  scale_tier "personal" | "local" | "regional" | "continental" | "planetary" | "cosmic"
  cost string?              // e.g. "exhaustion", "spiritual burnout", "chi-blocking"
  consequence string?
  counter string?           // e.g. "chi-blocking", "metal-cuffs", "spirit vines"
}

class AnimationVisualGrammar {
  composition string?
  panel_or_shot_type string? // e.g. "wide shot", "POV shot", "speed-line cut"
  motion_lines string?       // The motion vocabulary descriptor
  camera string?             // The cinematic camera
  silhouette string?
  focal_hierarchy string?
}

class AnimationPalette {
  dominant_hex string[]
  accent_hex string[]
  emissive_hex string[]
  per_element_palette map<string, string[]>  // the 4 nation-colour + 1 spirit-colour mapping
  contrast_strategy string?
}

class AnimationVfxVocabulary {
  particle_class "dust" | "ember" | "mist" | "spark" | "lattice" | "ash" | "ink" | "glyph" | "none"
  density "sparse" | "moderate" | "dense" | "overwhelming"
  trail_behavior string?    // e.g. "ember trail", "water ripple", "earth shard", "air streak"
  dissipation string?
  light_interaction string?  // e.g. "luminance shift on firebending", "glow on Avatar State"
}

class AnimationNarrativeBeat {
  arc_position string?      // e.g. "ATLA S1E3: The Southern Air Temple", "Korra S4 finale"
  beat_significance string?
}

class AnimationTransferability {
  in_game_mechanic string?  // e.g. "bending_class_initiation", "avatar_state_unlock"
  anam_cost int?            // 0 for animation
  palette_token string?     // null for v1
  particle_effect string?   // null for v1
}

class AnimationProvenance {
  rights_holder string       // e.g. "Nickelodeon Animation Studios" (ATLA) or "ViacomCBS" (Korra) or "Paramount Pictures" + "Nickelodeon" (Aang film)
  licence string
  derivation_class "description_only" | "derivative" | "fair_use_quote"
  shippable false
  shippable_art_path string?
}

class AnimationMediaDescriptor {
  work string                // "Avatar: The Last Airbender" / "The Legend of Korra" / "Aang film"
  medium "animation"
  language string            // "en" (the canonical source for ATLA is the English audio)
  source_url string
  source_timestamp string

  power_event AnimationPowerEvent
  visual_grammar AnimationVisualGrammar
  palette AnimationPalette
  vfx_vocabulary AnimationVfxVocabulary
  narrative_beat AnimationNarrativeBeat
  transferability AnimationTransferability
  provenance AnimationProvenance
}

// Class C — Animation (ATLA + Korra + Aang film)
// Default VLM: molmo2-8b (resolved via MODEL_REGISTRY
// family=ocr_vision, role=animation_descriptor). No
// hardcoded model strings.

function ExtractAnimationDescriptor(
  image: image,
  audio: string?,
  subtitle: string?,
  source_url: string,
  source_frame: int,
  work: string,
  language: string,
  evidence: string,
) -> AnimationMediaDescriptor {
  client MediaIntelPrimary
  prompt #"
    You are a medium-agnostic visual + narrative analyst for
    the Cianfhoghlaim reference-corpus. You are reading a
    frame from {{ work }} (the Avatar animated property —
    ATLA, Korra, or the Aang-film continuity).

    The frame image is provided, plus any audio transcript
    and subtitle text.

    The 4+1 element vocabulary (air / water / fire / earth /
    spirit) is surface-cited from the Wikipedia article. The
    bending sub-disciplines (metal / blood / lightning /
    healing / sand / lavabending / combustion / flight /
    energy) are captured via the `subdiscipline` field on
    the `power_event` axis.

    Extract the 7-axis AnimationMediaDescriptor from this
    frame:

    1. power_event — the actor, the element (mapped to one
       of the 5 enum values), the subdiscipline, the power
       source, the trigger, the scale tier, the cost, the
       consequence, the counter.
    2. visual_grammar — the composition, the panel/shot
       type (e.g. "wide shot", "POV shot", "speed-line cut"),
       the motion vocabulary descriptor, the cinematic
       camera, the silhouette, the focal hierarchy.
    3. palette — the dominant hex colours, the accent hex
       colours, the emissive hex colours, the per-element
       palette mapping (the 4 nation-colour + 1 spirit-
       colour mapping), the contrast strategy.
    4. vfx_vocabulary — the particle class, the density, the
       trail behaviour (e.g. "ember trail", "water ripple",
       "earth shard", "air streak"), the dissipation, the
       light interaction.
    5. narrative_beat — the arc position (e.g. "ATLA
       S1E3: The Southern Air Temple", "Korra S4 finale"),
       the beat significance.
    6. transferability — the in_game_mechanic (e.g.
       "bending_class_initiation", "avatar_state_unlock"),
       the anam cost (0 for animation), the palette token +
       particle effect (null for v1).
    7. provenance — the rights holder (e.g. "Nickelodeon
       Animation Studios" for ATLA, "ViacomCBS" for Korra,
       "Paramount Pictures" + "Nickelodeon" for the Aang
       film), the licence ("fair-use-description"), the
       derivation class ("description_only"), the shippable
       field (always false), the shippable_art_path (always
       null).

    The subtitle text is:
    {{ subtitle }}

    The source URL is:
    {{ source_url }}

    The source frame is:
    {{ source_frame }}

    The language is:
    {{ language }}

    The verbatim evidence excerpt is:
    {{ evidence }}

    Return the typed AnimationMediaDescriptor.
  "#
}
