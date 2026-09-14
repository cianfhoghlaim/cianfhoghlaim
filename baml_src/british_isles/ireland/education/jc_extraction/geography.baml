// BAML schema: Geography Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Geography-specific discriminator for the canonical NCCA junior cycle
// subject area (the 3 strands: Exploring the Physical World, Exploring
// the Human World, Exploring Sustainability).

enum GeogJCDiscriminator {
  STRAND_PHYSICAL    @description("Exploring the Physical World strand (JC-GEOG-LO-NNN)")
  STRAND_HUMAN       @description("Exploring the Human World strand (JC-GEOG-LO-NNN)")
  STRAND_SUSTAIN     @description("Exploring Sustainability strand (JC-GEOG-LO-NNN)")
  CROSS_STRAND       @description("Topic spans multiple strands")
}

class GeographySpec {
  subject string @description("Always 'geography'")
  lo_code_prefix string @description("Always 'JC-GEOG-LO'")
  primary_strand GeogJCDiscriminator @description("Dominant NCCA JC Geography strand for this syllabus")
  strand_count int @description("Always 3 for JC Geography")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  has_cba bool @description("Always true (Geographical Investigation)")
  cba_count int @description("Usually 1 (Geographical Investigation)")
}

function ExtractGeographySpec(
  input: string,
) -> GeographySpec {  client ExtractEn
    prompt #"{{ _.role('user') }} Extract geography spec from {{ input }}"#

  catch_all (err) {
    GeographySpec {
      lo_code_prefix "JC-GEOG-LO",
      strand_count 3,
      total_learning_outcomes 0,
      has_cba true,
      cba_count 1,
    }
  }
}
