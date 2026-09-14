// BAML schema: Gaeilge Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Gaeilge-specific discriminator for the canonical NCCA junior cycle
// subject area (the 3 strands: Éisteacht agus Labhairt, Léamh, Scríbhneoireacht).

enum GaelJCDiscriminator {
  STRAND_EISTEACHT   @description("Éisteacht agus Labhairt strand (JC-GAEL-LO-NNN)")
  STRAND_LEAMH       @description("Léamh strand (JC-GAEL-LO-NNN)")
  STRAND_SCRIBHNEOIREACHT @description("Scríbhneoireacht strand (JC-GAEL-LO-NNN)")
  PRESCRIBED_LITRICH  @description("Prescribed Irish-language literature")
  CROSS_STRAND       @description("Topic spans multiple strands")
}

class GaeilgeSpec {
  subject string @description("Always 'gaeilge'")
  lo_code_prefix string @description("Always 'JC-GAEL-LO'")
  primary_strand GaelJCDiscriminator @description("Dominant NCCA JC Gaeilge strand for this syllabus")
  strand_count int @description("Always 3 for JC Gaeilge")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  is_bilingual bool @description("True — JC Gaeilge captures bilingual EN/GA LOs")
  has_prescribed_texts bool @description("Always true (Irish-language prescribed texts)")
  has_cba bool @description("Always true (CBA 1 + CBA 2)")
}

function ExtractGaeilgeSpec(
  input: string,
) -> GaeilgeSpec {
  client ExtractEn
    prompt #"{{ _.role('user') }} Extract gaeilge spec from {{ input }}"#


}
