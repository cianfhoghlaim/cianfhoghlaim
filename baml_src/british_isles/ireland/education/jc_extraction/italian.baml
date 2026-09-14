// BAML schema: Italian Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Italian-specific discriminator for the canonical NCCA junior cycle
// subject area (the 4 communicative strands: Comprensione orale,
// Produzione orale, Comprensione scritta, Produzione scritta).

enum ItalJCDiscriminator {
  STRAND_COMPRENSIONE_ORALE    @description("Comprensione orale (JC-ITAL-LO-NNN)")
  STRAND_PRODUZIONE_ORALE      @description("Produzione orale (JC-ITAL-LO-NNN)")
  STRAND_COMPRENSIONE_SCRITTA  @description("Comprensione scritta (JC-ITAL-LO-NNN)")
  STRAND_PRODUZIONE_SCRITTA    @description("Produzione scritta (JC-ITAL-LO-NNN)")
  CROSS_STRAND                 @description("Topic spans multiple strands")
}

class ItalianSpec {
  subject string @description("Always 'italian'")
  lo_code_prefix string @description("Always 'JC-ITAL-LO'")
  primary_strand ItalJCDiscriminator @description("Dominant NCCA JC Italian communicative strand")
  strand_count int @description("Always 4 for JC Italian")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  cefr_target_level string @description("Target CEFR level (typically A2 / B1 by end of JC)")
  has_cba bool @description("Always true (CBA 1 + CBA 2 oral + written)")
}

function ExtractItalianSpec(
  input: string,
) -> ItalianSpec {  client ExtractEn
    prompt #"{{ _.role('user') }} Extract italian spec from {{ input }}"#

  catch_all (err) {
    ItalianSpec {
      lo_code_prefix "JC-ITAL-LO",
      strand_count 4,
      total_learning_outcomes 0,
      cefr_target_level "A2-B1",
      has_cba true,
    }
  }
}
