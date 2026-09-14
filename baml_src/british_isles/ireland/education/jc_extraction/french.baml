// BAML schema: French Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// French-specific discriminator for the canonical NCCA junior cycle
// subject area (the 4 communicative strands: Compréhension de l'oral,
// Production de l'oral, Compréhension de l'écrit, Production de l'écrit).

enum FrenJCDiscriminator {
  STRAND_COMPREHENSION_ORAL   @description("Compréhension de l'oral (JC-FREN-LO-NNN)")
  STRAND_PRODUCTION_ORAL      @description("Production de l'oral (JC-FREN-LO-NNN)")
  STRAND_COMPREHENSION_ECRIT  @description("Compréhension de l'écrit (JC-FREN-LO-NNN)")
  STRAND_PRODUCTION_ECRIT     @description("Production de l'écrit (JC-FREN-LO-NNN)")
  CROSS_STRAND                @description("Topic spans multiple strands")
}

class FrenchSpec {
  subject string @description("Always 'french'")
  lo_code_prefix string @description("Always 'JC-FREN-LO'")
  primary_strand FrenJCDiscriminator @description("Dominant NCCA JC French communicative strand")
  strand_count int @description("Always 4 for JC French")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  cefr_target_level string @description("Target CEFR level (typically A2 / B1 by end of JC)")
  has_cba bool @description("Always true (CBA 1 + CBA 2 oral + written)")
}

function ExtractFrenchSpec(
  input: string,
) -> FrenchSpec {  client ExtractEn
    prompt #"{{ _.role('user') }} Extract french spec from {{ input }}"#

  catch_all (err) {
    FrenchSpec {
      lo_code_prefix "JC-FREN-LO",
      strand_count 4,
      total_learning_outcomes 0,
      cefr_target_level "A2-B1",
      has_cba true,
    }
  }
}
