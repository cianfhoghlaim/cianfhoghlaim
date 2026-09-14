// BAML schema: Spanish Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Spanish-specific discriminator for the canonical NCCA junior cycle
// subject area (the 4 communicative strands: Comprensión oral,
// Expresión oral, Comprensión escrita, Expresión escrita).

enum SpanJCDiscriminator {
  STRAND_COMPRENSION_ORAL  @description("Comprensión oral (JC-SPAN-LO-NNN)")
  STRAND_EXPRESION_ORAL    @description("Expresión oral (JC-SPAN-LO-NNN)")
  STRAND_COMPRENSION_ESCRITA @description("Comprensión escrita (JC-SPAN-LO-NNN)")
  STRAND_EXPRESION_ESCRITA @description("Expresión escrita (JC-SPAN-LO-NNN)")
  CROSS_STRAND             @description("Topic spans multiple strands")
}

class SpanishSpec {
  subject string @description("Always 'spanish'")
  lo_code_prefix string @description("Always 'JC-SPAN-LO'")
  primary_strand SpanJCDiscriminator @description("Dominant NCCA JC Spanish communicative strand")
  strand_count int @description("Always 4 for JC Spanish")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  cefr_target_level string @description("Target CEFR level (typically A2 / B1 by end of JC)")
  has_cba bool @description("Always true (CBA 1 + CBA 2 oral + written)")
}

function ExtractSpanishSpec(
  input: string,
) -> SpanishSpec {
  client ExtractEn
    prompt #"{{ _.role('user') }} Extract spanish spec from {{ input }}"#


}
