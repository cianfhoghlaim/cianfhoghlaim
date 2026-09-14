// BAML schema: German Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// German-specific discriminator for the canonical NCCA junior cycle
// subject area (the 4 communicative strands: Hörverstehen, Sprechen,
// Leseverstehen, Schreiben).

enum GerJCDiscriminator {
  STRAND_HOERVERSTEHEN  @description("Hörverstehen (JC-GERM-LO-NNN)")
  STRAND_SPRECHEN       @description("Sprechen (JC-GERM-LO-NNN)")
  STRAND_LESEVERSTEHEN  @description("Leseverstehen (JC-GERM-LO-NNN)")
  STRAND_SCHREIBEN      @description("Schreiben (JC-GERM-LO-NNN)")
  CROSS_STRAND          @description("Topic spans multiple strands")
}

class GermanSpec {
  subject string @description("Always 'german'")
  lo_code_prefix string @description("Always 'JC-GERM-LO'")
  primary_strand GerJCDiscriminator @description("Dominant NCCA JC German communicative strand")
  strand_count int @description("Always 4 for JC German")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  cefr_target_level string @description("Target CEFR level (typically A2 / B1 by end of JC)")
  has_cba bool @description("Always true (CBA 1 + CBA 2 oral + written)")
}

function ExtractGermanSpec(
  input: string,
) -> GermanSpec {  client ExtractEn
    prompt #"{{ _.role('user') }} Extract german spec from {{ input }}"#

  catch_all (err) {
    GermanSpec {
      lo_code_prefix "JC-GERM-LO",
      strand_count 4,
      total_learning_outcomes 0,
      cefr_target_level "A2-B1",
      has_cba true,
    }
  }
}
