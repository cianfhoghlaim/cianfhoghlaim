// wheel_of_time.baml
// The Wheel of Time per-chapter power-usage schema.
//
// Per the 2026-10-10-media-intel-and-curriculum-hydration-v1 saga change
// (Plan A of openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md).
//
// The Wheel of Time (Robert Jordan, Tor Books) is a 14-volume prose
// series. This contract defines ONE row per chapter, so the corpus can
// later answer "when is the One Power used, by whom, and to what effect"
// per chapter — the prose sibling of the image-bearing
// MediaPowerDescriptor in media_power_system.baml.
//
// The row is DESCRIPTION-ONLY (shippable = false): a chapter summary +
// indexed references only, never a verbatim passage beyond short quotes.
//
// Reference:
//   baml_src/media/media_power_system.baml (the shared ComparativeStudyLens)
//   openspec/specs/retro-game-design-catalogue/spec.md (the predecessor)

// ----------------------------------------------------------------------------
// WoT-specific enums
// ----------------------------------------------------------------------------

enum WotPowerSystem {
  OnePowerSaidar      // the female half of the One Power
  OnePowerSaidin      // the male half of the One Power (tainted)
  TruePower           // the True Power of the Dark One
  Wolfbrother         // wolf-sense / telepathic wolf-bond
  Dreamwalking        // Tel'aran'rhiod / the World of Dreams
  TaVerenEffect       // the ta'veren pattern-warping
  Other
}

enum WotFlow {
  Air
  Fire
  Earth
  Water
  Spirit
}

// ----------------------------------------------------------------------------
// The per-chapter records
// ----------------------------------------------------------------------------

class WotPowerUseEvent {
  channeler string?               @description("Who channels, e.g. 'Rand al'Thor', 'Moiraine Damodred', 'Nynaeve al'Meara'")
  system WotPowerSystem
  flows WotFlow[]                 @description("The five flows woven, e.g. [air, fire, water]")
  weave_name string?              @description("The named weave, e.g. 'Balefire', 'Healing', 'Gateway', 'Calling Lightning'")
  effect string                   @description("What the weave does in the chapter")
  consequence string?             @description("The cost / consequence, e.g. 'saidin taint', 'weave-exhaustion', 'burned channeler'")
  page_ref string?                @description("The chapter-relative reference (e.g. 'ch12-p3') — never a verbatim passage")
  scene_id string                 @description("The chapter + scene id, e.g. 'tEotW-ch12-fleeing-two-rivers'")
}

class WotCharacterMention {
  name string
  role string?                    @description("e.g. 'channeler', 'Warder', 'Aes Sedai', 'ta'veren'")
  affiliation string?             @description("e.g. 'Two Rivers', 'White Tower', 'Aiel', 'Seanchan'")
  first_appearance bool?          @description("True if this chapter is the character's first appearance")
}

class WotChapterSchema {
  chapter_id string               @description("Deterministic: '<book_slug>-ch<chapter_number>'")
  book string                     @description("The book title, e.g. 'The Eye of the World'")
  book_index int                  @description("1..14 (or 0 for New Spring)")
  chapter_number int
  chapter_title string
  pov_character string            @description("The point-of-view character of the chapter")

  summary string                  @description("A 3-5 sentence neutral summary (description-only)")
  power_events WotPowerUseEvent[]
  characters WotCharacterMention[]
  locations string[]              @description("The locations the chapter visits")
  themes string[]                 @description("The thematic motifs, e.g. ['prophecy', 'trust', 'the taint']")

  comparative_lens ComparativeStudyLens @description("Shared with media_power_system.baml — the LC English Comparative Study modes")

  language string
  source_edition string           @description("e.g. 'Tor paperback 1990'")
  source_isbn string?
  provenance MediaPowerProvenance @description("Shared with media_power_system.baml — always shippable = false")

  extracted_at string
  stub bool
}

// ----------------------------------------------------------------------------
// The extraction function (prose — text in, typed chapter out)
// ----------------------------------------------------------------------------

function ExtractWotChapterSchema(
  chapter_text: string            @description("The chapter's text (never stored — description only)"),
  book: string                    @description("The book title, e.g. 'The Eye of the World'"),
  book_index: int                 @description("1..14 (or 0 for New Spring)"),
  chapter_number: int,
  chapter_title: string,
  rights_holder: string           @description("The original publisher, e.g. 'Tor Books'")
) -> WotChapterSchema {
  client MediaIntelPrimary
  prompt #"
    You are a prose corpus analyst for the Cianfhoghlaim reference
    corpus. You are reading ONE chapter of The Wheel of Time:
    {{ book }} (book {{ book_index }}), chapter {{ chapter_number }},
    "{{ chapter_title }}".

    Produce a single WotChapterSchema row. This is DESCRIPTION-ONLY:
    summarise + index, never reproduce more than a short quote.

    Required:
    1. chapter_id ("<book_slug>-ch{{ chapter_number }}"), book,
       book_index, chapter_number, chapter_title, pov_character.
    2. summary — 3-5 neutral sentences.
    3. power_events[] — every use of a WotPowerSystem in the chapter:
       the channeler, the system, the flows (of air/fire/earth/water/
       spirit), the weave_name, the effect, the consequence, a
       chapter-relative page_ref (never a verbatim passage), and the
       scene_id.
    4. characters[] — every character mentioned, with role + affiliation
       + whether it is a first appearance.
    5. locations[] — the places the chapter visits.
    6. themes[] — the thematic motifs.
    7. comparative_lens — theme_or_issue, cultural_context,
       literary_genre, general_vision (the LC English Comparative Study
       modes).
    8. provenance — rights_holder "{{ rights_holder }}", licence
       "fair-use-description", derivation_class "description_only",
       shippable false, shippable_art_path null.
    9. language, source_edition, source_isbn, extracted_at, stub.

    The chapter text is:
    {{ chapter_text }}
  "#
}

// ----------------------------------------------------------------------------
// Test case
// ----------------------------------------------------------------------------

test tEotW_ch12 {
  functions [ExtractWotChapterSchema]
  args {
    chapter_text "Moiraine channels to shield the group as Trollocs attack the inn at Emond's Field..."
    book "The Eye of the World"
    book_index 1
    chapter_number 12
    chapter_title "Dust on the Wind"
    rights_holder "Tor Books"
  }
}
