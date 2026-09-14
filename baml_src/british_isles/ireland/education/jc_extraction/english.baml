// BAML schema: English Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// English-specific discriminator for the canonical NCCA junior cycle
// subject area (the 3 strands: Oral Language, Reading, Writing).

enum EngJCDiscriminator {
  STRAND_ORAL       @description("Oral Language strand (JC-ENGL-LO-NNN)")
  STRAND_READING    @description("Reading strand (JC-ENGL-LO-NNN)")
  STRAND_WRITING    @description("Writing strand (JC-ENGL-LO-NNN)")
  PRESCRIBED_TEXT   @description("Prescribed text analysis (poetry / prose / drama)")
  CROSS_STRAND      @description("Topic spans multiple strands")
}

class EnglishSpec {
  subject string @description("Always 'english'")
  lo_code_prefix string @description("Always 'JC-ENGL-LO'")
  primary_strand EngJCDiscriminator @description("Dominant NCCA JC English strand for this syllabus")
  strand_count int @description("Always 3 for JC English")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  has_prescribed_texts bool @description("Always true for JC English")
  prescribed_text_count int? @description("Number of prescribed texts (poetry, prose, drama)")
  has_cba bool @description("Always true (CBA 1 + CBA 2)")
}

function ExtractEnglishSpec(
  input: string,
) -> EnglishSpec {  client ExtractEn
    prompt #"{{ _.role('user') }} Extract english spec from {{ input }}"#

  catch_all (err) {
    EnglishSpec {
      lo_code_prefix "JC-ENGL-LO",
      strand_count 3,
      total_learning_outcomes 0,
      has_prescribed_texts true,
      has_cba true,
    }
  }
}
