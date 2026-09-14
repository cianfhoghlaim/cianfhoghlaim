// BAML schema: Japanese Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Japanese-specific discriminator for the canonical NCCA junior cycle
// subject area (the 4 communicative strands: Listening, Speaking,
// Reading, Writing) plus the hiragana / katakana / kanji literacy
// sub-strand that is unique to Japanese at JC level.

enum JapJCDiscriminator {
  STRAND_LISTENING  @description("Listening (JC-JPN-LO-NNN)")
  STRAND_SPEAKING   @description("Speaking (JC-JPN-LO-NNN)")
  STRAND_READING    @description("Reading (JC-JPN-LO-NNN)")
  STRAND_WRITING    @description("Writing (JC-JPN-LO-NNN)")
  STRAND_LITERACY   @description("Hiragana / Katakana / Kanji literacy sub-strand")
  CROSS_STRAND      @description("Topic spans multiple strands")
}

class JapaneseSpec {
  subject string @description("Always 'japanese'")
  lo_code_prefix string @description("Always 'JC-JPN-LO'")
  primary_strand JapJCDiscriminator @description("Dominant NCCA JC Japanese communicative strand")
  strand_count int @description("5 strands for JC Japanese (4 communicative + literacy)")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  cefr_target_level string @description("Target CEFR level (typically A2 by end of JC)")
  has_cba bool @description("Always true (CBA 1 + CBA 2 oral + written)")
  has_kanji_literacy bool @description("Always true — Japanese has unique kanji literacy sub-strand")
}

function ExtractJapaneseSpec(
  input: string,
) -> JapaneseSpec {
  client ExtractEn
    prompt #"{{ _.role('user') }} Extract japanese spec from {{ input }}"#


}
