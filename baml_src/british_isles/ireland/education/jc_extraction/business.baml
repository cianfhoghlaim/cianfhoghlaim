// BAML schema: Business Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Business-specific discriminator for the canonical NCCA junior cycle
// subject area (the 4 strands: Personal Finance, Enterprise, Our Economy,
// Our Community).

enum BusJCDiscriminator {
  STRAND_PERSONAL_FINANCE  @description("Personal Finance strand (JC-BUS-LO-NNN)")
  STRAND_ENTERPRISE        @description("Enterprise strand (JC-BUS-LO-NNN)")
  STRAND_OUR_ECONOMY       @description("Our Economy strand (JC-BUS-LO-NNN)")
  STRAND_OUR_COMMUNITY     @description("Our Community strand (JC-BUS-LO-NNN)")
  CROSS_STRAND             @description("Topic spans multiple strands")
}

class BusinessSpec {
  subject string @description("Always 'business'")
  lo_code_prefix string @description("Always 'JC-BUS-LO'")
  primary_strand BusJCDiscriminator @description("Dominant NCCA JC Business Studies strand")
  strand_count int @description("Always 4 for JC Business Studies")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  has_cba bool @description("Always true (Business in Action project)")
  cba_count int @description("Usually 1 (Business in Action)")
}

function ExtractBusinessSpec(
  input: string,
) -> BusinessSpec {
  client ExtractEn
    prompt #"{{ _.role('user') }} Extract business spec from {{ input }}"#


}
