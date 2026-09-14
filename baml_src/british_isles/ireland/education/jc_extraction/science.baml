// BAML schema: Science Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Science-specific discriminator for the canonical NCCA junior cycle
// subject area (the 4 strands: Nature of Science, Physical World,
// Biological World, Chemical World).

enum SciJCDiscriminator {
  STRAND_NATURE        @description("Nature of Science strand (JC-SCI-LO-NNN)")
  STRAND_PHYSICAL      @description("Physical World strand (JC-SCI-LO-NNN)")
  STRAND_BIOLOGICAL    @description("Biological World strand (JC-SCI-LO-NNN)")
  STRAND_CHEMICAL      @description("Chemical World strand (JC-SCI-LO-NNN)")
  STRAND_EARTH_SPACE   @description("Earth and Space strand (JC-SCI-LO-NNN)")
  CROSS_STRAND         @description("Topic spans multiple strands")
}

class ScienceSpec {
  subject string @description("Always 'science'")
  lo_code_prefix string @description("Always 'JC-SCI-LO'")
  primary_strand SciJCDiscriminator @description("Dominant NCCA JC Science strand for this syllabus")
  strand_count int @description("Always 4 for JC Science")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  has_cba bool @description("Always true (CBA 1 + CBA 2)")
  cba_count int @description("Usually 2 (Extended Experimental Investigation + Science in Society Investigation)")
}

function ExtractScienceSpec(
  input: string,
) -> ScienceSpec {  client ExtractEn
    prompt #"{{ _.role('user') }} Extract science spec from {{ input }}"#

  catch_all (err) {
    ScienceSpec {
      lo_code_prefix "JC-SCI-LO",
      strand_count 4,
      total_learning_outcomes 0,
      has_cba true,
      cba_count 2,
    }
  }
}
