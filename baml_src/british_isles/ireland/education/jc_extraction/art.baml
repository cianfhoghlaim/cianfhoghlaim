// BAML schema: Art Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Art-specific discriminator for the canonical NCCA junior cycle
// subject area (the 4 strands: Drawing, Paint & Colour, Print, Clay /
// Fabric & Construction / 3D).

enum ArtJCDiscriminator {
  STRAND_DRAWING   @description("Drawing strand (JC-ART-LO-NNN)")
  STRAND_PAINT     @description("Paint and Colour strand (JC-ART-LO-NNN)")
  STRAND_PRINT     @description("Print strand (JC-ART-LO-NNN)")
  STRAND_CRAFT_3D  @description("Clay / Fabric / 3D Construction strand (JC-ART-LO-NNN)")
  CROSS_STRAND     @description("Topic spans multiple strands")
}

class ArtSpec {
  subject string @description("Always 'art'")
  lo_code_prefix string @description("Always 'JC-ART-LO'")
  primary_strand ArtJCDiscriminator @description("Dominant NCCA JC Art strand")
  strand_count int @description("Always 4 for JC Art")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  has_cba bool @description("Always true (CBA 1 + CBA 2 portfolio pieces)")
  cba_count int @description("Usually 2 (portfolio-based CBAs)")
  is_studio_based bool @description("Always true for JC Art")
}

function ExtractArtSpec(
  input: string,
) -> ArtSpec {
  client ExtractEn
    prompt #"{{ _.role('user') }} Extract art spec from {{ input }}"#


}
