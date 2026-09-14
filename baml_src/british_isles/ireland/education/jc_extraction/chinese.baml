// BAML schema: Chinese Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Chinese-specific discriminator for the canonical NCCA junior cycle
// subject area (the 4 communicative strands: Listening, Speaking,
// Reading, Writing) plus the Hanzi / character literacy sub-strand that
// is unique to Chinese at JC level.

enum ChinJCDiscriminator {
  STRAND_LISTENING  @description("Listening (听) (JC-CHN-LO-NNN)")
  STRAND_SPEAKING   @description("Speaking (说) (JC-CHN-LO-NNN)")
  STRAND_READING    @description("Reading (读) (JC-CHN-LO-NNN)")
  STRAND_WRITING    @description("Writing (写) (JC-CHN-LO-NNN)")
  STRAND_LITERACY   @description("Hanzi (汉字) character literacy sub-strand")
  CROSS_STRAND      @description("Topic spans multiple strands")
}

class ChineseSpec {
  subject string @description("Always 'chinese'")
  lo_code_prefix string @description("Always 'JC-CHN-LO'")
  primary_strand ChinJCDiscriminator @description("Dominant NCCA JC Chinese communicative strand")
  strand_count int @description("5 strands for JC Chinese (4 communicative + literacy)")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  cefr_target_level string @description("Target CEFR level (typically A2 by end of JC)")
  has_cba bool @description("Always true (CBA 1 + CBA 2 oral + written)")
  has_hanzi_literacy bool @description("Always true — Chinese has unique hanzi literacy sub-strand")
}

function ExtractChineseSpec(
  input: string,
) -> ChineseSpec {
  client ExtractEn
    prompt #"{{ _.role('user') }} Extract chinese spec from {{ input }}"#


}
